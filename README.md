# windsong

Transform MIDI files into keyboard keys for [Genshin Impact](https://genshin.mihoyo.com) instruments.

## Install

`pip install windsong`, or for debugging/source install:

```
git clone https://github.com/ongyx/windsong && cd windsong
pip install flit  # if you don't have it yet
flit install -s
```

## Usage

Keys are dumped in the following format:

```
<track/part name>:
<chord 1> <chord 2>
<chord 3> <chord 4>
```

where one line is a bar of the midi song, depending on the time signature.

`windsong <midi-file>` will dump the keys to stdout.
You can save it to a file by `windsong -s keys.txt <midi-file>`.

More details can be found using `windsong --help`.
If an error occurs, please open an issue, run `windsong --debug <midi-file>` and paste the logs there.

## Caveats

Some restrictions apply due to limitations of the Genshin Impact instruments themselves:

- Only notes in the C major scale (C, D, E, F, G, A, B) can be played. No sharps or flats (yet).
  However, you can transpose notes with the `-t` option.
- Notes must be between C3 and B5.

Any invalid notes are replaced with a dash `-`.

## Credits/License

`tests/bach_prelude.mid` is synthesised by Roland Lopes, hosted at this [link](https://imslp.org/wiki/Prelude_and_Fugue_in_C_major%2C_BWV_846_(Bach%2C_Johann_Sebastian)).

windsong is licensed under the MIT license.
