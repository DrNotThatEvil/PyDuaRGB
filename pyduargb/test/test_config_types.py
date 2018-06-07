# PyduaRGB: The python daemon for your ledstrip needs.
# Copyright (C) 2018 wilvin@wilv.in

# This program is free software: you can redistribute it and/or modify
# it under the terms of GNU Lesser General Public License version 3
# as published by the Free Software Foundation, Only version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function, absolute_import
import os
import pytest

from ..config import types
from ..chips import ALL_CHIPS

def test_correct_string_type():
    stringtype = types.ConfigStringType
    if(not stringtype.validate("ThisIsAString")):
        pytest.fail("Correct ConfigStringType validate returned False")

def test_string_type_with_ip():
    stringtype = types.ConfigStringType
    if(stringtype.validate("127.0.0.1")):
        pytest.fail("Ip address passed a ConfigStringType!")

def test_string_type_with_file():
    stringtype = types.ConfigStringType
    if(stringtype.validate("/dev/null")):
        pytest.fail("FilePath passed a ConfigStringType!")

def test_string_type_with_rgb():
    stringtype = types.ConfigStringType
    if(stringtype.validate("rgb")):
        pytest.fail("RGBMap passed a ConfigStringType!")

def test_string_type_with_chip():
    stringtype = types.ConfigStringType

    for chip in ALL_CHIPS:
        if(stringtype.validate(chip)):
            pytest.fail("ChipType {0} passed a ConfigStringType!".format(chip))

def test_string_type_with_int():
    stringtype = types.ConfigStringType
    if(stringtype.validate("1337")):
        pytest.fail("Int passed a ConfigStringType!")

def test_correct_rgbmap():
    rgbmap = types.RGBMapConfigType
    if(not rgbmap.validate("rgb") or not rgbmap.validate("RGB")):
        pytest.fail("Correct rgbmap returned False!")

def test_incorrect_rgbmap():
    rgbmap = types.RGBMapConfigType
    if(rgbmap.validate("rgBB") or rgbmap.validate("981")):
        pytest.fail("Incorrect rgbmap returned True!")

def test_correct_filetype():
    filetype = types.ConfigFileType
    if(not filetype.validate("/dev/null")):
        pytest.fail("Correct filetype returned False!")

def test_incorrect_filetype():
    filetype = types.ConfigFileType
    if(filetype.validate("King Kong grizzly bears")):
        pytest.fail("Incorrect filetype returned True!")

def test_correct_inttype():
    inttype = types.ConfigIntType
    if(not inttype.validate("1337")):
        pytest.fail("Correct filetype returned False!")

def test_incorrect_inttype():
    inttype = types.ConfigIntType
    if(inttype.validate("Man so much fun those ledstrips!")):
        pytest.fail("Incorrect filetype returned True!")

def test_correct_inttype():
    iptype = types.ConfigIpType
    if(not iptype.validate("127.0.0.1")):
        pytest.fail("Correct ip returned False!")

def test_incorrect_inttype():
    iptype = types.ConfigIpType
    if(iptype.validate("Cool story bro nice and short")):
        pytest.fail("Incorrect iptype returned True!")

def test_correct_chip_type():
    chiptype = types.ConfigChipType

    for chip in ALL_CHIPS:
        if(not chiptype.validate(chip)):
            pytest.fail("Correct chip '{0}' made the Chiptype validate fail!".format(chip))

def test_incorrect_chip_type():
    chiptype = types.ConfigChipType

    if(chiptype.validate('SPa821')):
        pytest.fail("Incorrect chip '{0}' made the Chiptype validate pass!".format(chip))
