# Installation

## Requirements

- Ableton Live 12.x
- Max for Live
- Kayatune
- A MIDI interface that forwards SysEx

## Install

1. Download and extract the release ZIP.
2. Keep these files together:

   - `Kayatune Global Transpose Standalone.amxd`
   - `kayatune_sysex_parser.js`

3. Copy the `Max MIDI Effect` folder to a permanent location in your Ableton User Library.
4. Drag the `.amxd` onto a MIDI track.
5. Select the MIDI input receiving Kayatune SysEx.
6. Set **Monitor** to **In**.

## Test

- Kayatune 0 → device shows A / 0
- Kayatune +1 → device shows A# / +1
- Kayatune +2 → device shows B / +2
- Kayatune -1 → device shows G# / -1

All Session View audio clips should follow the same transpose amount. Tracks containing `[NP]` remain unchanged.
