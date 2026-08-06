autowatch = 1;

inlets = 1;
outlets = 3;

// Ausgang 0: Transpose-Zahl
// Ausgang 1: Debug-Text
// Ausgang 2: Notenname

var buffer = [];

var notes = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
];

// Grundton A
var baseNote = 9;

function msg_int(value) {
    value = Number(value);

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

function parsePacket(packet) {
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

    var noteIndex = ((baseNote + transpose) % 12 + 12) % 12;
    var noteName = notes[noteIndex];

    outlet(2, noteName);
    outlet(1, "Kayatune " + transpose + " / " + noteName);
    outlet(0, transpose);
}