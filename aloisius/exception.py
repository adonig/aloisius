# Copyright (c) 2015, Andreas Donig <andreas@innwiese.de>
# All rights reserved.
#
# See LICENSE file for full license.

from . import export


@export
class StackException(Exception):
    pass
