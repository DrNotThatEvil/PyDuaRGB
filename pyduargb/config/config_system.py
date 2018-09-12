from __future__ import print_function, absolute_import
import os, configparser, logging

from ..logging import *
from ..meta import Singleton
from .types import *

logger = get_logger(__file__)

CUR_PATH = os.path.dirname(os.path.realpath(__file__))
REQUIRED = {
    'main': [
        'spidev',
        'leds',
        'chiptype'
    ]
}

CONFIG_TYPES  = {
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
    'slaves': [
        ['key', ConfigStringType],
    ],
    'master': [
        ['ip', ConfigIpType],
        ['key', ConfigStringType]
    ]
}

class ConfigSystem(Singleton):
    def __init__(self, config_path, default_config=None):
        self.def_conf_path = os.path.join(CUR_PATH, "default.ini")
        self.config_path = config_path

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
            raise Exception("Configruation not correct. Missing required" + 
                            "section/value")

        logger.info("Checking config value types...")
        if(not self._validate_config_values()):
            raise Exception("Could not load config.")

        logger.info("Configuration file loaded...")

    def _validate_required_config(self):
        for key, value in REQUIRED.items():
            if(key not in self.main_config.sections() and 
                key not in self.default_config.sections):
                return False

            for option in REQUIRED[key]: 
                if(option not in self.main_config.options(key) and
                    option not in self.default_config.options(key)):
                    return False
         
        return True
    
    def _validate_config_values(self):
        for section in self.main_config.sections():
            if(section not in CONFIG_TYPES):
                continue

            for key, value in CONFIG_TYPES[section]:
                config_type = value

                if(not key in self.main_config.options(section)):
                    continue

                if(not config_type.validate(self.main_config.get(section,
                    key))):
                    # Option is not configured correctly.
                    # Lets log it and try to take the default value
                    logger.warn(("Config option {0}.{1} set to wrong type. " +
                            "Type should be '{2}'").format(
                                section, key, config_type.get_type_name()
                            ))
                    if(config_type.get_help_string() != False):
                        logger.info("Type '{0}' help: {1}".format(
                                config_type.get_type_name(),
                                config_type.get_help_string()
                            )
                        )

                    logger.warn("Trying to get default value" + 
                                " for setting '{0}'".format(key))

                    if(not self.default_config.has_section(section)):
                        logger.error("Could not load option" + 
                                    " {0} from default config".format(key))
                        if (section in REQUIRED.keys()):
                            return False
                        continue
                    
                    if(not self.default_config.has_option(section, key)):
                        logger.error("Could not load option" + 
                        " {0} from default config".format(key))
                        if (section in REQUIRED.keys()):
                            return False
                        continue
        return True

    def get_option(self, section, option):
        config_names = ["main", "default"]
        configs = [self.main_config, self.default_config]
        config = configs[0]

        for x in range(len(configs)):
            if(not configs[x].has_section(section)):
                # logger.warn(("Could not load section " + 
                #    "{0} from {1} config!").format(section, config_names[x]))
                if(x == (len(configs)-1)):
                    return False
                
                logger.info(("Trying to load from " + 
                        "{0} config...").format(config_names[x+1]))
                continue
        
            if(not configs[x].has_option(section, option)):
                logger.warn("Could not load option " +
                        "{0} from {1} config!".format(option, config_names[x]))
                if(x == (len(configs)-1)):
                    return False
        
                logger.info("Trying to load from " + 
                        "{0} config...".format(config_names[x+1]))
                continue

            if(section in CONFIG_TYPES):
                for config_type in CONFIG_TYPES[section]:
                    if(config_type[0] == option):
                        return config_type[1](configs[x].get(section, option))

            return configs[x].get(section, option)
