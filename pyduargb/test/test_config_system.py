from __future__ import print_function, absolute_import
import os
import pytest

from ..config import config_system
from ..config.types import *

TEST_PATH = os.path.dirname(os.path.realpath(__file__))

def test_correct_config():
    try:
        configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'correct.ini'))
        config_system.ConfigSystem.destroy()
    except:
        pytest.fail("Got unexpected exception when correct config was loaded")

def test_file_not_found():
    with pytest.raises(IOError):
        configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'non_existent.ini'))

# TODO find a way to test READ access error.

def test_default_not_found():
    with pytest.raises(IOError):
        configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'correct.ini'), 
                os.path.join(TEST_PATH, 'non_existent.ini'))

# TODO find a way to test READ access on another default_config

def test_missing_required():
    with pytest.raises(Exception):
        configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'missing_required.ini'))

def test_missing_required_default_backup():
    try:
        configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'missing_required2.ini'))
        config_system.ConfigSystem.destroy()
    except:
        pytest.fail("Backup configuration did not contain a required backup value.")

def test_validate_correct_values():
    try:
        configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'correct.ini'))
        config_system.ConfigSystem.destroy()
    except Exception as e:
        if e.message == "Could not load config.":
            pytest.fail("Could not load correct config.")

def test_validate_inccorrect_values():
    with pytest.raises(Exception):
        configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'incorrect2.ini'))

def test_validate_inccorrect_values_backup():
    try:
        configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'incorrect3.ini'))
        config_system.ConfigSystem.destroy()
    except Exception as e:
        if e.message == "Could not load config.":
            pytest.fail("Could not load incorrect3.in config with backupable values.")

@pytest.mark.parametrize("section,option,conftype", [
    ('main', 'spidev', ConfigFileType),
    ('main', 'rgbmap', RGBMapConfigType),
    ('main', 'leds', ConfigIntType),
    ('main', 'chiptype', ConfigChipType),
    ('slaves', 'count', ConfigIntType), 
    ('master', 'allow', ConfigIpType),
    ('master', 'slavekey', ConfigStringType),
])
def test_configtypes(section, option, conftype):
    configsys = config_system.ConfigSystem(os.path.join(TEST_PATH, 'correct.ini'))
    assert isinstance(configsys.get_option(section, option), conftype) == True
    config_system.ConfigSystem.destroy()

