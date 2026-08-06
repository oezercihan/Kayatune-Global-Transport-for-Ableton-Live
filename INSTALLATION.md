# Installation

Installing Kayatune Global Transpose only takes a few minutes.

---

# Requirements

- Ableton Live 12.x
- Max for Live
- Kayatune

---

# 1. Download

Download the latest release from GitHub.

Extract the ZIP archive.

---

# 2. Install the Max for Live Device

Copy

```
Kayatune Global Transpose.amxd
```

to your Ableton User Library

or simply drag it onto any MIDI Track.

---

# 3. Connect Kayatune

Connect your keyboard as you normally would.

Start Kayatune.

No additional configuration is required.

---

# 4. Load the Device

Create a MIDI Track.

Load

```
Kayatune Global Transpose.amxd
```

onto the track.

The device will immediately start listening for Kayatune SysEx messages.

---

# 5. Verify Installation

Change the transpose value inside Kayatune.

The device should automatically display:

- Current musical key
- Current transpose value

If UDP output is enabled, the transpose value will also be transmitted automatically.

---

# Optional

Launchpad Duo Sync Pro can receive transpose updates automatically through the built-in UDP interface.

No additional configuration is required.

---

# Updating

Replace the existing

```
Kayatune Global Transpose.amxd
```

with the latest version.

---

# Troubleshooting

## No transpose detected

- Verify that Kayatune is running.
- Verify that your MIDI connection is working.
- Reload the Max for Live device.

---

## No SysEx messages

Ensure your MIDI interface forwards SysEx messages correctly.

---

## UDP integration not working

Verify that the receiving application is listening on the configured UDP port.

---

## Device not loading

Make sure Max for Live is installed and activated.

---

# Support

If you encounter any issues, please create a GitHub Issue and include:

- Ableton Live version
- Max version
- Operating system
- MIDI interface
- Screenshots (if applicable)
