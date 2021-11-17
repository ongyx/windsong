# coding: utf8

import windsong


def test_lyre():
    lyre = windsong.Lyre("tests/bach_prelude.mid")
    print(lyre.export())
