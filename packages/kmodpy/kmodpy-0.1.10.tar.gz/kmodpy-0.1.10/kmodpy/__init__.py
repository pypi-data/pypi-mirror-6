# Copyright (C) 2014 Chrysostomos Nanakos <chris@include.gr>
#
# This file is part of kmodpy.
#
# kmodpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kmodpy.  If not, see <http://www.gnu.org/licenses/>.


"Python interface to kmod API"

from .version import __version__
try:
    from .kmod import Kmod
except ImportError:
    pass
