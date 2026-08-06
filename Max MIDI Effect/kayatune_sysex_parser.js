autowatch = 1;

inlets = 2;
outlets = 3;

// Outlet 0: absolute transpose value
// Outlet 1: status/debug text
// Outlet 2: musical key name
// Inlet 0: raw SysEx bytes from sysexin
// Inlet 1: restored transpose state from the Live parameter

var buffer = [];
var notes = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
];
var baseNote = 9; // A
var state = new Global("KayatuneGlobalTransposeStandalone");
if (typeof state.transpose === "undefined") {
    state.transpose = 0;
}
var currentTranspose = Number(state.transpose) || 0;

function msg_int(value) {
    value = Number(value);

    if (inlet === 1) {
        set_current(value);
        return;
    }

    if (value === 240) {
        buffer = [240];
        return;
    }

    if (buffer.length === 0) {
        return;
    }

    buffer.push(value);

    if (value === 247) {
        parsePacket(buffer);
        buffer = [];
    }
}

function list() {
    var values = arrayfromargs(arguments);
    for (var i = 0; i < values.length; i++) {
        msg_int(values[i]);
    }
}

function set_current(value) {
    value = Number(value);
    if (isNaN(value)) {
        return;
    }
    currentTranspose = Math.max(-12, Math.min(12, Math.round(value)));
    state.transpose = currentTranspose;
}

function parsePacket(packet) {
    // Confirmed Kayatune/Yamaha parameter message:
    // F0 43 10 7F 1C 07 00 00 01 VALUE F7
    var expectedPrefix = [240, 67, 16, 127, 28, 7, 0, 0, 1];

    if (packet.length !== 11) {
        return;
    }

    for (var i = 0; i < expectedPrefix.length; i++) {
        if (packet[i] !== expectedPrefix[i]) {
            return;
        }
    }

    if (packet[10] !== 247) {
        return;
    }

    var transpose = packet[9] - 64;
    if (transpose < -12 || transpose > 12) {
        return;
    }

    applyAbsoluteTranspose(transpose);

    var noteIndex = ((baseNote + transpose) % 12 + 12) % 12;
    var noteName = notes[noteIndex];

    outlet(2, noteName);
    outlet(1, "Kayatune " + transpose + " / " + noteName);
    outlet(0, transpose);
}

function applyAbsoluteTranspose(targetTranspose) {
    targetTranspose = Number(targetTranspose);
    var delta = targetTranspose - currentTranspose;

    if (delta === 0) {
        state.transpose = targetTranspose;
        return;
    }

    var changed = 0;
    var skipped = 0;

    try {
        var song = new LiveAPI("live_set");
        var trackCount = song.getcount("tracks");

        for (var trackIndex = 0; trackIndex < trackCount; trackIndex++) {
            var trackPath = "live_set tracks " + trackIndex;
            var track = new LiveAPI(trackPath);
            var trackNameValue = track.get("name");
            var trackName = valueToString(trackNameValue);

            // Add [NP] anywhere in the track name to exclude that track.
            if (trackName.indexOf("[NP]") !== -1) {
                skipped++;
                continue;
            }

            var slotCount = track.getcount("clip_slots");
            for (var slotIndex = 0; slotIndex < slotCount; slotIndex++) {
                var slotPath = trackPath + " clip_slots " + slotIndex;
                var slot = new LiveAPI(slotPath);
                var hasClip = Number(firstValue(slot.get("has_clip")));
                if (!hasClip) {
                    continue;
                }

                var clip = new LiveAPI(slotPath + " clip");
                if (!clip || clip.id === 0) {
                    continue;
                }

                var isAudio = Number(firstValue(clip.get("is_audio_clip")));
                if (!isAudio) {
                    continue;
                }

                var currentPitch = Number(firstValue(clip.get("pitch_coarse")));
                if (isNaN(currentPitch)) {
                    continue;
                }

                var nextPitch = Math.max(-48, Math.min(48, currentPitch + delta));
                clip.set("pitch_coarse", nextPitch);
                changed++;
            }
        }

        currentTranspose = targetTranspose;
        state.transpose = targetTranspose;
        outlet(1, "Transposed " + changed + " audio clips; excluded tracks " + skipped);
    } catch (error) {
        outlet(1, "Live API error: " + error);
    }
}

function firstValue(value) {
    if (value instanceof Array) {
        return value.length ? value[0] : 0;
    }
    return value;
}

function valueToString(value) {
    if (value instanceof Array) {
        return value.join(" ");
    }
    return String(value);
}

function reset() {
    applyAbsoluteTranspose(0);
    outlet(2, notes[baseNote]);
    outlet(0, 0);
}
