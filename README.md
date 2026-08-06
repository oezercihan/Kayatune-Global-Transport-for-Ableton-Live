# Kayatune Global Transpose

Ein Max-for-Live-MIDI-Device, das Kayatune-SysEx-Daten ausliest und den absoluten Transpose-Wert an **Launchpad Duo Sync Pro** überträgt.

## Funktionen

- Empfang der Kayatune-SysEx-Daten über `sysexin`
- Erkennung des absoluten Transpose-Werts
- Anzeige der aktuellen Tonart bezogen auf Grundton A
- Übertragung per lokaler UDP-Nachricht an Launchpad Duo Sync Pro
- Kein externer Companion erforderlich
- Optionaler Python-Companion als Fallback für Systeme, auf denen der direkte M4L-SysEx-Empfang nicht verwendet werden kann

## Abhängigkeit

Für die automatische Transposition der Ableton-Clips und die Launchpad-Anzeige wird benötigt:

**Launchpad Duo Sync Pro**

Das Remote Script empfängt die Nachricht:

```text
LDS1:<WERT>
```

auf `127.0.0.1:45831`.

## Installation

Siehe [INSTALLATION.md](INSTALLATION.md).

## Signalweg

```text
Kayatune
→ MIDI / SysEx
→ Kayatune Global Transpose.amxd
→ UDP LDS1:<WERT>
→ Launchpad Duo Sync Pro
→ Ableton-Clips + Launchpad-Anzeige
```

## Dateien

```text
Max MIDI Effect/
├── Kayatune Global Transpose.amxd
└── kayatune_sysex_parser.js
```

Die JavaScript-Datei muss neben der `.amxd` liegen, sofern das Device nicht mit eingebetteten Abhängigkeiten gespeichert beziehungsweise eingefroren wurde.

## Optionaler Companion

Der Ordner `Optional Companion` enthält eine alternative Python-Brücke. Sie ist für den normalen Max-for-Live-Betrieb nicht erforderlich.

Max-for-Live-Device und Companion sollten nicht gleichzeitig verwendet werden, weil beide denselben Transpose-Wert senden können.

## Lizenz

MIT License. Siehe [LICENSE](LICENSE).
