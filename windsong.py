# coding: utf8
"""Transform MIDI files into keyboard keys for Genshin Impact instruments."""

import argparse
import logging
import math

import mido  # type: ignore

__version__ = "0.1.2"

# the C major scale key positions relative to C.
C_MAJOR = [0, 2, 4, 5, 7, 9, 11]

# map of keyboard keys to the octaves
LETTERS = ["zxcvbnm", "asdfghj", "qwertyu"]
ORDER = {c: i for i, c in enumerate("".join(LETTERS))}
ORDER["-"] = -1

# the vaild lyre key range, between C3 and B5.
KEY_RANGE = range(48, 83)

_log = logging.getLogger(__name__)


def clean(chord):
    # this removes any duplicate keys in the chord
    # and then sorts it from lowest to highest key
    return "".join(sorted(set(chord), key=lambda c: ORDER[c]))


def in_range(note):
    return KEY_RANGE.start <= note.note <= KEY_RANGE.stop


def is_major(note):
    return (note.note % 12) in C_MAJOR


def is_start(note):
    try:
        return note.type == "note_on" and note.velocity != 0
    except AttributeError:
        return False


def to_letter(note):
    offset = note.note - KEY_RANGE.start
    return LETTERS[offset // 12][C_MAJOR.index(offset % 12)]


class Bar:
    def __init__(self, chords=None):
        self.chords = [] if chords is None else chords

    def text(self):
        return " ".join([clean(chord) for chord in self.chords])


class Part:
    def __init__(self, events: mido.MidiTrack, tpb: int, transpose: int):
        self.events = events
        self.tpb = tpb
        self.sig = 0
        self.transpose = transpose

    def parse(self, adjust=False):
        clock_prev = 0
        clock = 0
        bar = 0
        bars = [Bar()]
        chord = []

        for event in self.events:
            clock += event.time

            if event.type == "time_signature":
                self.sig = event.numerator

            if not is_start(event):
                _log.debug(f"{event} is not a note_on event, skipping")
                continue

            # if the delta time between the previous and current event hasen't changed,
            # they are playing simultaneously
            # once the time increases, a new chord is created
            if clock != clock_prev:
                bars[-1].chords.append("".join(chord))
                chord.clear()

            if self.transpose:
                event.note += self.transpose

            if not is_major(event) or (not in_range(event) and not adjust):
                _log.info(f"{event} is a sharp/flat or out of range")
                chord.append("-")

            else:
                if adjust:
                    # adjust the note until it is within C3 to B5
                    offset = 0
                    if event.note < KEY_RANGE.start:
                        offset = 12 * math.ceil((KEY_RANGE.start - event.note) / 12)
                    elif event.note > KEY_RANGE.stop:
                        offset = -12 * math.ceil((event.note - KEY_RANGE.stop) / 12)
                    event.note += offset

                chord.append(to_letter(event))

            try:
                current_bar = (clock // self.tpb) // self.sig
            except ZeroDivisionError:
                current_bar = 0

            if current_bar > bar:
                # new bar
                bars.append(Bar())
                bar = current_bar

            clock_prev = clock

        return bars


class Lyre:
    def __init__(self, fname: str, transpose: int = 0, merge: bool = True):
        self.midi = mido.MidiFile(fname)
        self.parts = []

        # collect all events into one track
        if merge:
            self.midi.tracks = [mido.merge_tracks(self.midi.tracks)]

        for track in self.midi.tracks:
            self.parts.append(Part(track, self.midi.ticks_per_beat, transpose))

    def export(self, adjust: bool = False) -> str:
        buf = []

        for index, part in enumerate(self.parts):
            # make sure the time signature carries over to the next part
            if index != 0 and not part.sig:
                part.sig = self.parts[index - 1].sig

            buf.append((part.events.name or f"({index})") + ":")

            for bar in part.parse(adjust=adjust):
                buf.append(bar.text())

            buf.append("")

        return "\n".join(buf).strip("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("midi_file", help="the midi file to transform")
    parser.add_argument("-s", "--save-to", help="where to save the keys to")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug logs")
    parser.add_argument(
        "-n",
        "--no-merge",
        action="store_true",
        help="don't merge all tracks into one (not recommended)",
    )
    parser.add_argument(
        "-a",
        "--adjust",
        action="store_true",
        help="adjust the octave of notes outside the range to be within C3-B5",
    )
    parser.add_argument(
        "-t",
        "--transpose",
        help="transpose the midi notes by a number of semitones",
        type=int,
        default=0,
    )

    args = parser.parse_args()

    # setup logging
    logging.basicConfig()
    _log.setLevel(logging.INFO)
    if args.debug:
        _log.setLevel(logging.DEBUG)

    lyre = Lyre(args.midi_file, transpose=args.transpose, merge=not args.no_merge)
    export = lyre.export(adjust=args.adjust)

    if args.save_to:
        with open(args.save_to, "w") as f:
            f.write(export)
    else:
        print(export)


if __name__ == "__main__":
    main()
