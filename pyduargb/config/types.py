from __future__ import print_function, absolute_import
import os, socket

from ..chips import ALL_CHIPS

CONFIG_TYPES = []

#TODO: Make config types initiatable so they can be used as real usefull objects not only for validation.
#TODO: change the validate methods to static methods since they do not really initialization

class BaseConfigType():
    def init(self):
        pass

    def validate(self, data):
        return True

    def get_help_string(self):
        return False

class ConfigFileType(BaseConfigType):
    def validate(self, data):
        return os.path.isabs(data)

    def get_type_name(self):
        return "File"

class ConfigStringType(BaseConfigType):
    def validate(self, data):
        anythingElse = False
        for configtype in ALL_CONFIG_TYPES:
            if configtype == ConfigStringType:
                continue

            configtype_instance = configtype()
            if(configtype_instance.validate(data)):
                anythingElse = True
                break

        return (isinstance(data, str) and not anythingElse)

    def get_type_name(self):
        return "String"

class ConfigIntType(BaseConfigType):
    def validate(self, data):
        return data.isdigit()

    def get_type_name(self):
        return "int"

class RGBMapConfigType(BaseConfigType):
    def validate(self, data):
        if(len(data) != 3):
            return False

        if((data.count("r")+data.count("R")) != 1 or 
                (data.count("g")+data.count("G")) != 1 or 
                (data.count("b")+data.count("B")) != 1):
            return False

        return True
    
    def get_type_name(self):
        return "RGBMap"

class ConfigIpType(BaseConfigType):
    def validate(self, data):
        try:
            socket.inet_aton(data)
            return True
        except Exception as e:
            return False

    def get_type_name(self):
        return "ip"

class ConfigChipType(BaseConfigType):
    def validate(self, data):
        for chip in ALL_CHIPS:
            if chip.lower() == data.lower():
                return True
        return False

    def get_type_name(self):
        return "chip"

    def get_help_string(self):
        helpstr = "Valid options are: "
        for key in range(len(ALL_CHIPS)):
            chip = ALL_CHIPS[key]
            helpstr = helpstr + chip
            if(key < (len(ALL_CHIPS)-1)):
                helpstr = helpstr + " | "
        return helpstr


ALL_CONFIG_TYPES = [ConfigStringType, RGBMapConfigType, ConfigIpType, ConfigFileType, ConfigChipType, ConfigIntType]
