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
import sys


CACHE_SIZE = 25000  # 25 Kb cache size.


class BaseChip(object):
    """The base chip for the a DuaRGB daemon

    This base chip should be extended by specific chips
    but must contain the following methods:

    TODO: WRITE ALL NESSECARY METHODS
    """

    CHIP_NAME = "base_chip"
    PIXEL_SIZE = 3
    PIXEL_BYTES = 2

    def __init__(self):
        super().__init__()
        self.gamma_select = 0  # Gamma correction selection
        self._caching_enabled = True
        self._cache = {}

    def _is_in_cache(self, hsh):
        return (self._caching_enabled and (hsh in self._cache))

    def _put_in_cache(self, hsh, data):
        if len(data) > CACHE_SIZE or not self._caching_enabled:
            # Can't fit in cache or cache is disabled.
            return

        # Schink cache until new data can fit in it
        # without going over CACHE_SIZE
        while((sys.getsizeof(self._cache) + len(data)) > CACHE_SIZE):
            if ((sys.getsizeof(self._cache) + len(data)) < CACHE_SIZE or
                    len(self._cache) == 0):
                break

            self._cache.popitem()
        self._cache[hsh] = data

    def set_caching(self, status):
        if self._caching_enabled != status:
            self.cache = {}
        self._caching_enabled = status

    @classmethod
    def get_chipname(cls):
        return cls.CHIP_NAME

    def calculate_gamma(pixel_in):
        raise NotImplementedError('Error: calcuate_gamma is not implemented!')

    def write_pixels(pixels, total_pixels, out):
        """Write pixels to the ledstrip.

        Arguments:
        pixels -- List of Pixels
        total_pixels -- The amount of pixels on the strip.
        out -- The output for the bytes
        """
        raise NotImplementedError('Error: Extension of baseclass is needed')
