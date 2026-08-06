# Kayatune Global Transpose Standalone v1.0.0

A Max for Live MIDI device that reads Kayatune transpose SysEx and transposes all Session View audio clips directly in Ableton Live.

## No Launchpad required

This version works without Launchpad Duo Sync Pro. Launchpad Duo Sync remains an optional companion for LED feedback and controller operation.

## Features

- Reads the confirmed Kayatune SysEx transpose value
- Applies the absolute value to all Session View audio clips
- Preserves individual clip offsets by applying only the required delta
- Stores the current transpose state with the Live Set
- Shows the musical key based on root note A
- Excludes tracks containing `[NP]`
- Limits global transpose to -12 … +12 semitones

## Installation

1. Keep the `.amxd` and `.js` files together in the same folder.
2. Copy the complete `Max MIDI Effect` folder into your Ableton User Library, or drag the `.amxd` directly onto a MIDI track.
3. Route the MIDI interface carrying Kayatune SysEx to that track.
4. Set the track Monitor to **In**.
5. Change transpose on Kayatune.

## Track exclusion

Add `[NP]` anywhere in a track name:

- `[NP] Drums`
- `Percussion [NP]`
- `FX [NP]`

MIDI clips are ignored automatically.

## Important

The device controls Session View audio clips. Arrangement clips are not changed in v2.0.0.

## Optional Launchpad integration

Use Launchpad Duo Sync Pro separately when you also want:

- transpose overlays on two Launchpads
- left/right arrow control
- dual Session Ring synchronization

Do not use the standalone device and the UDP-based Launchpad edition to transpose the same clips simultaneously unless one side's transposition engine is disabled.
