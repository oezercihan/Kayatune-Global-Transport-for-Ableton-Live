# 🎹 Kayatune Global Transpose for Ableton Live

Automatically synchronize Kayatune's transpose with Ableton Live.

Kayatune Global Transpose is a Max for Live device that receives transpose information directly from Kayatune via SysEx and instantly updates Ableton Live in real time.

Designed for live performers who use external keyboards together with Ableton Live and want all loops, backing tracks and instruments to stay in the same key without manually changing multiple devices.

---

## Features

- 🎹 Automatic Kayatune transpose detection
- ⚡ Real-time SysEx processing
- 🎼 Musical key detection
- 🎵 Global transpose for Ableton Live
- 📡 Built-in UDP output for external integrations
- 🎛️ Max for Live interface
- 🟢 Live performance optimized
- ⚙️ Plug & Play

---

## How it works

```
Kayatune
      │
      ▼
SysEx
      │
      ▼
Kayatune Global Transpose
(Max for Live)
      │
      ▼
UDP Output (optional)
      │
      ▼
Ableton Live
or external applications
```

---

## Current Features

- Reads transpose changes directly from Kayatune
- Detects the current musical key
- Displays transpose value
- Sends UDP messages to external software
- Very low latency
- Optimized for live performance

---

## Companion Projects

Kayatune Global Transpose works standalone.

It also integrates perfectly with:

- 🎛️ Launchpad Duo Sync Pro

More integrations can easily be added using the built-in UDP protocol.

---

## Requirements

- Ableton Live 12.x
- Max for Live
- Kayatune

---

## Installation

See:

📄 INSTALLATION.md

---

## Roadmap

- Configurable root key
- Sharp / Flat notation
- Custom themes
- OSC output
- MIDI output mode
- Automatic controller detection
- Additional integrations

---

## Contributing

Bug reports, feature requests and pull requests are always welcome.

If you find a bug or have an idea for an improvement, please open an Issue.

---

## License

MIT License
