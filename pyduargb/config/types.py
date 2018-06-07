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
import socket

from ..chips import ALL_CHIPS, CHIP_LOOKUP

CONFIG_TYPES = []


# TODO: Make config types initiatable so they can be used as real usefull
# objects not only for validation.
# TODO: change the validate methods to static methods since they
# do not really need initialization


class BaseConfigType():
    def init(self):
        pass

    @staticmethod
    def validate(data):
        return True

    @staticmethod
    def get_help_string():
        return False


class ConfigFileType(BaseConfigType):
    def __init__(self, value):
        self.string_rep = value
        self.full_path = os.path.abspath(value)

    def get_str_value(self):
        return self.string_rep

    def get_full_path(self):
        return self.full_path

    @staticmethod
    def validate(data):
        return os.path.isabs(data)

    @staticmethod
    def get_type_name():
        return "File"


class ConfigStringType(BaseConfigType):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    @staticmethod
    def validate(data):
        anythingElse = False
        for configtype in ALL_CONFIG_TYPES:
            if configtype == ConfigStringType:
                continue

            if(configtype.validate(data)):
                anythingElse = True
                break

        return (isinstance(data, str) and not anythingElse)

    @staticmethod
    def get_type_name():
        return "String"


class ConfigIntType(BaseConfigType):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return int(self.value)

    @staticmethod
    def validate(data):
        return data.isdigit()

    @staticmethod
    def get_type_name():
        return "int"


class RGBMapConfigType(BaseConfigType):
    def __init__(self, value):
        self.value = value.lower()

    def get_value(self):
        return self.value

    @staticmethod
    def validate(data):
        if(len(data) != 3):
            return False

        if((data.count("r")+data.count("R")) != 1 or
                (data.count("g")+data.count("G")) != 1 or
                (data.count("b")+data.count("B")) != 1):
            return False

        return True

    @staticmethod
    def get_type_name():
        return "RGBMap"


class ConfigIpType(BaseConfigType):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    @staticmethod
    def validate(data):
        try:
            socket.inet_aton(data)
            return True
        except Exception as e:
            return False

    @staticmethod
    def get_type_name():
        return "ip"


class ConfigChipType(BaseConfigType):
    def __init__(self, value):
        self.string_rep = value.upper()

    def get_str_value(self):
        return self.string_rep

    def get_chip_obj(self):
        return CHIP_LOOKUP[self.string_rep]()

    @staticmethod
    def validate(data):
        for chip in ALL_CHIPS:
            if chip.lower() == data.lower():
                return True
        return False

    @staticmethod
    def get_type_name():
        return "chip"

    @staticmethod
    def get_help_string():
        helpstr = "Valid options are: "
        for key in range(len(ALL_CHIPS)):
            chip = ALL_CHIPS[key]
            helpstr = helpstr + chip
            if(key < (len(ALL_CHIPS)-1)):
                helpstr = helpstr + " | "
        return helpstr


ALL_CONFIG_TYPES = [
    ConfigStringType,
    RGBMapConfigType,
    ConfigIpType,
    ConfigFileType,
    ConfigChipType,
    ConfigIntType
]
