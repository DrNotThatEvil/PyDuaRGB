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
import configparser
import logging

from ..logging import *
from ..meta import Singleton
from .types import *
from .slaveconfig import SlaveConfig

logger = get_logger(__file__)

CUR_PATH = os.path.dirname(os.path.realpath(__file__))
REQUIRED = {
    'main': [
        'spidev',
        'leds',
        'chiptype'
    ]
}

CONFIG_TYPES = {
    'main': [
        ['spidev', ConfigFileType],
        ['rgbmap', RGBMapConfigType],
        ['leds', ConfigIntType],
        ['chiptype', ConfigChipType]
    ],
    'jsonrpc': [
        ['allow', ConfigIpType],
        ['port', ConfigIntType],
        ['apikey', ConfigStringType]
    ],
    'master': [
        ['ip', ConfigIpType],
        ['slavecount', ConfigIntType],
        ['disabled', ConfigIntType]
    ]
}


class ConfigSystem(Singleton):
    def __init__(self, config_path=None, default_config=None):
        if (self.__class__ not in self.__class__._instances
                and config_path is None
                and default_config is None):
            raise Exception('Error: ConfigSystem needs full initalization. ' +
                            'Before it can be accesed with no paramters')

        self.def_conf_path = os.path.join(CUR_PATH, "default.ini")
        self.config_path = config_path
        self.slave_configs = []

        if (default_config is not None):
            self.def_conf_path = default_config

        self.default_config = configparser.ConfigParser()
        if (not os.path.exists(self.def_conf_path)):
            raise IOError("Default config file not found.")

        if (not os.access(self.def_conf_path, os.R_OK)):
            raise IOError("Can't access default config.")

        if (not os.path.exists(os.path.realpath(self.config_path))):
            raise IOError("Configuration file not found.")

        if (not os.access(self.config_path, os.R_OK)):
            raise IOError("Can't access default config.")

        self.default_config.read(self.def_conf_path)

        self.main_config = configparser.ConfigParser()
        self.main_config.read(self.config_path)

        logger.info("Checking config for required paramaters...")
        if(not self._validate_required_config()):
            raise Exception(
                "Configruation not correct. Missing required section/value")

        logger.info("Checking config value types...")
        if(not self._validate_config_values()):
            raise Exception("Could not load config.")

        self._load_slaves()
        logger.info("Configuration file loaded...")

    def _validate_required_config(self):
        for key, value in REQUIRED.items():
            if(key not in self.main_config.sections()
                    and key not in self.default_config.sections):
                return False

            for option in REQUIRED[key]:
                if(option not in self.main_config.options(key)
                        and option not in self.default_config.options(key)):
                    return False

        return True

    def _validate_config_values(self):
        for section in self.main_config.sections():
            if(section not in CONFIG_TYPES):
                continue

            for key, value in CONFIG_TYPES[section]:
                config_type = value

                if(key not in self.main_config.options(section)):
                    continue

                if(not config_type.validate(
                        self.main_config.get(section, key))):
                    # Option is not configured correctly.
                    # Lets log it and try to take the default value
                    logger.warn(("Config option {0} set to wrong type." +
                                 "Type should be '{1}'").format(
                            key,
                            config_type.get_type_name())
                        )
                    if(config_type.get_help_string()):
                        logger.info("Type '{0}' help: {1}".format(
                            config_type.get_type_name(),
                            config_type.get_help_string())
                        )

                    logger.warn("Trying to get default" +
                                "value for setting '{0}'".format(key))

                    if(not self.default_config.has_section(section)):
                        logger.error("Could not load option" +
                                     "{0} from default config".format(key))
                        if (section in REQUIRED.keys()):
                            return False
                        continue

                    if(not self.default_config.has_option(section, key)):
                        logger.error("Could not load option" +
                                     "{0} from default config".format(key))
                        if (section in REQUIRED.keys()):
                            return False
                        continue
        return True

    def _load_slaves(self):
        if(not self.main_config.has_section('master')):
            return False

        if(not self.main_config.has_option('master', 'slavecount')):
            return False

        config_type = ConfigIntType
        if(not config_type.validate(
                self.main_config.get("master", "slavecount"))):
            logger.warn("slave count invalid, No slaves will be loaded.")
            return False

        slave_cnt = self.main_config.getint("master", "slavecount")
        for i in range(0, slave_cnt):
            logger.info("Getting config for slave{0}...".format(i))
            section = "slave{0}".format(i)

            if(not self.main_config.has_section(section)):
                logger.warning(section + " is not configured skipping slave.")
                continue

            if(not self.main_config.has_option(section, 'ip')):
                logger.warning(section + " ip not configured skipping slave.")
                continue

            ipType = ConfigIpType
            ip = self.main_config.get(section, 'ip')
            if(not ipType.validate(self.main_config.get(section, 'ip'))):
                logger.warning(section + " ip not a ip skipping slave.")
                continue

            mode = 'continue'
            if(not self.main_config.has_option(section, 'mode')):
                logger.warning(section + " mode not configured. Using default")
            else:
                modeType = ConfigStringType
                temp_mode = self.main_config.get(section, 'mode')
                if(not modeType.validate(temp_mode)):
                    logger.warning(section + " mode invalid. Using default")
                else:
                    mode = temp_mode

            self.slave_configs.append(SlaveConfig(i, ip, mode))
            logger.info("Slave configuration loaded for: " + section)

    def get_slave_configs(self):
        return self.slave_configs

    def get_option(self, section, option):
        config_names = ["main", "default"]
        configs = [self.main_config, self.default_config]
        config = configs[0]

        for x in range(len(configs)):
            if(not configs[x].has_section(section)):
                logger.warn("Could not load section " +
                            "'{0}' from '{1}' config!".format(
                                section, config_names[x]
                            ))
                if(x == (len(configs)-1)):
                    return False

                logger.info("Trying to load from '{0}' config...".format(
                                config_names[x+1])
                            )
                continue

            if(not configs[x].has_option(section, option)):
                logger.warn("Could not load option '{0}' from '{1}' config!"
                            .format(option, config_names[x]))
                if(x == (len(configs)-1)):
                    return False

                logger.info("Trying to load from '{0}' config...".format(
                                config_names[x+1])
                            )
                continue

            if(section in CONFIG_TYPES):
                for config_type in CONFIG_TYPES[section]:
                    if(config_type[0] == option):
                        return config_type[1](configs[x].get(section, option))

            return configs[x].get(section, option)
