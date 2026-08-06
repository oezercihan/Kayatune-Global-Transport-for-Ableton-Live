#!/usr/bin/env python3
"""Kayatune SysEx -> Launchpad Duo Sync localhost bridge.

Version 1.2.0
- Watches all available MIDI inputs.
- Reconnects automatically after hot-plugging.
- Shows a small status window when Tk is available.
"""
from __future__ import annotations

import argparse
import queue
import socket
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

try:
    import mido
except ImportError:
    print("Missing dependency: mido/python-rtmidi. Run Install.command first.")
    raise SystemExit(2)

UDP_HOST = "127.0.0.1"
UDP_PORT = 45831
MIN_TRANSPOSE = -12
MAX_TRANSPOSE = 12
SCAN_INTERVAL_SECONDS = 2.0
DUPLICATE_GUARD_SECONDS = 0.25
# Mido strips F0/F7. Confirmed Kayatune absolute-value message:
# F0 43 10 7F 1C 07 00 00 01 <value+0x40> F7
PREFIX = (0x43, 0x10, 0x7F, 0x1C, 0x07, 0x00, 0x00, 0x01)
KEYS_FROM_A = ("A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#")


def decode_kayatune(message: "mido.Message") -> Optional[int]:
    if message.type != "sysex":
        return None
    data = tuple(int(x) for x in message.data)
    if len(data) != 9 or data[:8] != PREFIX:
        return None
    value = data[8] - 0x40
    return value if MIN_TRANSPOSE <= value <= MAX_TRANSPOSE else None


def key_name(value: int) -> str:
    return KEYS_FROM_A[value % 12]


@dataclass
class RuntimeState:
    inputs: Dict[str, "mido.ports.BaseInput"] = field(default_factory=dict)
    current_value: Optional[int] = None
    last_source: str = "—"
    message_count: int = 0
    last_sent_at: float = 0.0
    status: str = "Starting"
    lock: threading.RLock = field(default_factory=threading.RLock)


class Companion:
    def __init__(self, event_queue: "queue.Queue[tuple]", include: str = "") -> None:
        self.events = event_queue
        self.include = include.lower().strip()
        self.state = RuntimeState()
        self.stop_event = threading.Event()
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._last_value: Optional[int] = None
        self._last_sent = 0.0

    def _port_callback(self, port_name: str):
        def callback(message: "mido.Message") -> None:
            value = decode_kayatune(message)
            if value is None:
                return
            now = time.monotonic()
            with self.state.lock:
                # The same absolute SysEx may reach more than one monitored path.
                if value == self._last_value and now - self._last_sent < DUPLICATE_GUARD_SECONDS:
                    return
                self._last_value = value
                self._last_sent = now
                self.udp.sendto(f"LDS1:{value}".encode("ascii"), (UDP_HOST, UDP_PORT))
                self.state.current_value = value
                self.state.last_source = port_name
                self.state.message_count += 1
                self.state.last_sent_at = time.time()
                self.state.status = "Kayatune detected"
            self.events.put(("transpose", value, port_name))
        return callback

    def _eligible(self, name: str) -> bool:
        return not self.include or self.include in name.lower()

    def rescan(self) -> None:
        try:
            available = {name for name in mido.get_input_names() if self._eligible(name)}
        except Exception as error:
            self.events.put(("error", f"MIDI scan failed: {error}"))
            return

        with self.state.lock:
            current = set(self.state.inputs)

        # Close ports that disappeared.
        for name in sorted(current - available):
            with self.state.lock:
                port = self.state.inputs.pop(name, None)
            if port is not None:
                try:
                    port.close()
                except Exception:
                    pass
                self.events.put(("port_closed", name))

        # Open newly available ports. Failure on one port must not stop the others.
        for name in sorted(available - current):
            try:
                port = mido.open_input(name, callback=self._port_callback(name))
            except Exception as error:
                self.events.put(("port_error", name, str(error)))
                continue
            with self.state.lock:
                self.state.inputs[name] = port
                self.state.status = "Listening"
            self.events.put(("port_opened", name))

        with self.state.lock:
            if not self.state.inputs:
                self.state.status = "Waiting for MIDI input"
            names = tuple(sorted(self.state.inputs))
        self.events.put(("ports", names))

    def run(self) -> None:
        self.events.put(("started",))
        while not self.stop_event.is_set():
            self.rescan()
            self.stop_event.wait(SCAN_INTERVAL_SECONDS)
        self.close()

    def close(self) -> None:
        self.stop_event.set()
        with self.state.lock:
            ports = list(self.state.inputs.values())
            self.state.inputs.clear()
        for port in ports:
            try:
                port.close()
            except Exception:
                pass
        self.udp.close()


def run_console(companion: Companion, events: "queue.Queue[tuple]") -> int:
    print("Launchpad Duo Sync – Kayatune Companion v1.2.0")
    print(f"Watching all matching MIDI inputs; sending to udp://{UDP_HOST}:{UDP_PORT}")
    print("Press Ctrl+C to stop.\n")
    thread = threading.Thread(target=companion.run, daemon=True)
    thread.start()
    try:
        while thread.is_alive():
            try:
                event = events.get(timeout=0.5)
            except queue.Empty:
                continue
            kind = event[0]
            if kind == "port_opened":
                print(f"Listening: {event[1]}")
            elif kind == "port_closed":
                print(f"Disconnected: {event[1]}")
            elif kind == "port_error":
                print(f"Skipped {event[1]}: {event[2]}")
            elif kind == "transpose":
                value, source = event[1], event[2]
                print(f"Kayatune {value:+d} ({key_name(value)}) -> Ableton [{source}]")
            elif kind == "error":
                print(f"ERROR: {event[1]}", file=sys.stderr)
    except KeyboardInterrupt:
        companion.close()
    thread.join(timeout=2.0)
    return 0


def run_dashboard(companion: Companion, events: "queue.Queue[tuple]") -> int:
    import base64
    import json
    import webbrowser
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    dashboard_port = 45832
    dashboard_html = base64.b64decode("PCFkb2N0eXBlIGh0bWw+PGh0bWwgbGFuZz0iZGUiPjxoZWFkPjxtZXRhIGNoYXJzZXQ9InV0Zi04Ij48bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2aWNlLXdpZHRoLGluaXRpYWwtc2NhbGU9MSI+PHRpdGxlPkxhdW5jaHBhZCBEdW8gU3luYyBDb21wYW5pb248L3RpdGxlPjxzdHlsZT46cm9vdHtjb2xvci1zY2hlbWU6ZGFya30qe2JveC1zaXppbmc6Ym9yZGVyLWJveH1ib2R5e21hcmdpbjowO21pbi1oZWlnaHQ6MTAwdmg7YmFja2dyb3VuZDojMTExMzE4O2NvbG9yOiNmNWY3ZmE7Zm9udC1mYW1pbHk6LWFwcGxlLXN5c3RlbSxCbGlua01hY1N5c3RlbUZvbnQsIlNlZ29lIFVJIixzYW5zLXNlcmlmO2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXI7cGFkZGluZzoyNHB4fS5jYXJke3dpZHRoOm1pbig3MjBweCwxMDAlKTtiYWNrZ3JvdW5kOiMxZDIxMjg7Ym9yZGVyOjFweCBzb2xpZCAjMzQzYjQ2O2JvcmRlci1yYWRpdXM6MThweDtwYWRkaW5nOjI4cHg7Ym94LXNoYWRvdzowIDIwcHggNjBweCAjMDAwOH1oMXtmb250LXNpemU6MjRweDttYXJnaW46MCAwIDIycHh9LnN0YXR1c3tkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxMHB4O21hcmdpbi1ib3R0b206MjRweH0uZG90e3dpZHRoOjEycHg7aGVpZ2h0OjEycHg7Ym9yZGVyLXJhZGl1czo1MCU7YmFja2dyb3VuZDojZjBhZDRlO2JveC1zaGFkb3c6MCAwIDE0cHggY3VycmVudENvbG9yfS5kb3Qub2t7YmFja2dyb3VuZDojMzlkOThhfS5ncmlke2Rpc3BsYXk6Z3JpZDtncmlkLXRlbXBsYXRlLWNvbHVtbnM6MTYwcHggMWZyO2dhcDoxM3B4IDIwcHh9LmxhYmVse2NvbG9yOiM5Y2E3Yjg7Zm9udC13ZWlnaHQ6NjUwfS52YWx1ZXtmb250LXdlaWdodDo1NjA7d2hpdGUtc3BhY2U6cHJlLXdyYXA7d29yZC1icmVhazpicmVhay13b3JkfS5waXRjaHtmb250LXNpemU6NTRweDtmb250LXdlaWdodDo4MDA7bGluZS1oZWlnaHQ6MX0ua2V5e2ZvbnQtc2l6ZToyOHB4O2ZvbnQtd2VpZ2h0Ojc1MH0uZm9vdGVye21hcmdpbi10b3A6MjRweDtwYWRkaW5nLXRvcDoxOHB4O2JvcmRlci10b3A6MXB4IHNvbGlkICMzNDNiNDY7Y29sb3I6IzljYTdiODtmb250LXNpemU6MTRweH1AbWVkaWEobWF4LXdpZHRoOjUyMHB4KXsuZ3JpZHtncmlkLXRlbXBsYXRlLWNvbHVtbnM6MWZyO2dhcDo1cHh9LmxhYmVse21hcmdpbi10b3A6MTBweH19PC9zdHlsZT48L2hlYWQ+PGJvZHk+PG1haW4gY2xhc3M9ImNhcmQiPjxoMT5MYXVuY2hwYWQgRHVvIFN5bmMgQ29tcGFuaW9uPC9oMT48ZGl2IGNsYXNzPSJzdGF0dXMiPjxzcGFuIGlkPSJkb3QiIGNsYXNzPSJkb3QiPjwvc3Bhbj48c3Ryb25nIGlkPSJzdGF0dXMiPlN0YXJ0ZXTigKY8L3N0cm9uZz48L2Rpdj48ZGl2IGNsYXNzPSJncmlkIj48ZGl2IGNsYXNzPSJsYWJlbCI+TUlESS1FaW5nw6RuZ2U8L2Rpdj48ZGl2IGlkPSJpbnB1dHMiIGNsYXNzPSJ2YWx1ZSI+U3VjaGXigKY8L2Rpdj48ZGl2IGNsYXNzPSJsYWJlbCI+VHJhbnNwb3NlPC9kaXY+PGRpdiBpZD0idHJhbnNwb3NlIiBjbGFzcz0idmFsdWUgcGl0Y2giPuKAlDwvZGl2PjxkaXYgY2xhc3M9ImxhYmVsIj5Ub25hcnQgKEJhc2lzIEEpPC9kaXY+PGRpdiBpZD0ia2V5IiBjbGFzcz0idmFsdWUga2V5Ij7igJQ8L2Rpdj48ZGl2IGNsYXNzPSJsYWJlbCI+TGV0enRlIFF1ZWxsZTwvZGl2PjxkaXYgaWQ9InNvdXJjZSIgY2xhc3M9InZhbHVlIj7igJQ8L2Rpdj48ZGl2IGNsYXNzPSJsYWJlbCI+TmFjaHJpY2h0ZW48L2Rpdj48ZGl2IGlkPSJtZXNzYWdlcyIgY2xhc3M9InZhbHVlIj4wPC9kaXY+PGRpdiBjbGFzcz0ibGFiZWwiPkFibGV0b24tQnJpZGdlPC9kaXY+PGRpdiBpZD0iYnJpZGdlIiBjbGFzcz0idmFsdWUiPuKAlDwvZGl2PjwvZGl2PjxkaXYgY2xhc3M9ImZvb3RlciI+RGllc2VzIEJyb3dzZXJmZW5zdGVyIGthbm4gd8OkaHJlbmQgZGVzIEF1ZnRyaXR0cyBnZcO2ZmZuZXQgYmxlaWJlbi4gRGllIFZlcmJpbmR1bmcgbMOkdWZ0IGF1c3NjaGxpZcOfbGljaCBsb2thbCBhdWYgZGllc2VtIE1hYy48L2Rpdj48L21haW4+PHNjcmlwdD5hc3luYyBmdW5jdGlvbiB1cGRhdGUoKXt0cnl7Y29uc3Qgcj1hd2FpdCBmZXRjaCgnL3N0YXR1cy5qc29uJyx7Y2FjaGU6J25vLXN0b3JlJ30pO2NvbnN0IHM9YXdhaXQgci5qc29uKCk7ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3N0YXR1cycpLnRleHRDb250ZW50PXMuc3RhdHVzO2RvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdpbnB1dHMnKS50ZXh0Q29udGVudD1zLmlucHV0cy5sZW5ndGg/cy5pbnB1dHMuam9pbignXG4nKTonS2VpbiB6dWfDpG5nbGljaGVyIE1JREktRWluZ2FuZyc7ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3RyYW5zcG9zZScpLnRleHRDb250ZW50PXMudHJhbnNwb3NlPT09bnVsbD8n4oCUJzoocy50cmFuc3Bvc2U+MD8nKycrcy50cmFuc3Bvc2U6U3RyaW5nKHMudHJhbnNwb3NlKSk7ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2tleScpLnRleHRDb250ZW50PXMua2V5O2RvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdzb3VyY2UnKS50ZXh0Q29udGVudD1zLnNvdXJjZTtkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnbWVzc2FnZXMnKS50ZXh0Q29udGVudD1zLm1lc3NhZ2VzO2RvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdicmlkZ2UnKS50ZXh0Q29udGVudD1zLmJyaWRnZTtkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnZG90JykuY2xhc3NOYW1lPSdkb3QgJysocy5pbnB1dHMubGVuZ3RoPydvayc6JycpfWNhdGNoKGUpe2RvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdzdGF0dXMnKS50ZXh0Q29udGVudD0nQ29tcGFuaW9uIG5pY2h0IGVycmVpY2hiYXInfX11cGRhdGUoKTtzZXRJbnRlcnZhbCh1cGRhdGUsNTAwKTs8L3NjcmlwdD48L2JvZHk+PC9odG1sPgo=")

    class DashboardHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            return

        def send_body(self, content_type: str, body: bytes, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/status.json":
                with companion.state.lock:
                    current = companion.state.current_value
                    payload = {
                        "status": companion.state.status,
                        "inputs": sorted(companion.state.inputs),
                        "transpose": current,
                        "key": key_name(current) if current is not None else "—",
                        "source": companion.state.last_source,
                        "messages": companion.state.message_count,
                        "bridge": f"127.0.0.1:{UDP_PORT}",
                    }
                self.send_body("application/json; charset=utf-8", json.dumps(payload).encode("utf-8"))
            elif self.path in ("/", "/index.html"):
                self.send_body("text/html; charset=utf-8", dashboard_html)
            else:
                self.send_body("text/plain; charset=utf-8", b"Not found", 404)

    try:
        server = ThreadingHTTPServer(("127.0.0.1", dashboard_port), DashboardHandler)
    except OSError as error:
        print(f"Dashboard could not start: {error}. Falling back to console mode.")
        return run_console(companion, events)

    worker = threading.Thread(target=companion.run, daemon=True)
    worker.start()
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    url = f"http://127.0.0.1:{dashboard_port}/"
    print("Launchpad Duo Sync – Kayatune Companion v1.2.0")
    print(f"Status dashboard: {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)
    try:
        while worker.is_alive():
            try:
                event = events.get(timeout=0.5)
            except queue.Empty:
                continue
            kind = event[0]
            if kind == "port_opened":
                print(f"Listening: {event[1]}")
            elif kind == "port_closed":
                print(f"Disconnected: {event[1]}")
            elif kind == "port_error":
                print(f"Skipped {event[1]}: {event[2]}")
            elif kind == "transpose":
                value, source = event[1], event[2]
                print(f"Kayatune {value:+d} ({key_name(value)}) -> Ableton [{source}]")
            elif kind == "error":
                print(f"ERROR: {event[1]}", file=sys.stderr)
    except KeyboardInterrupt:
        pass
    finally:
        companion.close()
        server.shutdown()
        server.server_close()
    worker.join(timeout=2.0)
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List MIDI inputs and exit")
    parser.add_argument("--console", action="store_true", help="Run without the status window")
    parser.add_argument("--include", default="", help="Optional MIDI input name substring filter")
    args = parser.parse_args()

    if args.list:
        print("MIDI inputs:")
        for name in mido.get_input_names():
            print(f"  {name}")
        return 0

    events: "queue.Queue[tuple]" = queue.Queue()
    companion = Companion(events, include=args.include)
    return run_console(companion, events) if args.console else run_dashboard(companion, events)


if __name__ == "__main__":
    raise SystemExit(main())
