# Copyright (c) 2015, Andreas Donig <andreas@innwiese.de>
# All rights reserved.
#
# See LICENSE file for full license.


__all__ = []

def export(defn):
    globals()[defn.__name__] = defn
    __all__.append(defn.__name__)
    return defn

from .stack import Stack
