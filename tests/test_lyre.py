# coding: utf8

import windsong


def test_lyre():
    lyre = windsong.Lyre("tests/bach_prelude.mid")
    print(lyre.export())


def test_lyre_with_adjust():
    lyre = windsong.Lyre("tests/bach_prelude.mid")
    print(lyre.export(adjust=True))


def test_lyre_with_no_merge():
    lyre = windsong.Lyre("tests/bach_prelude.mid", merge=False)
    print(lyre.export())
