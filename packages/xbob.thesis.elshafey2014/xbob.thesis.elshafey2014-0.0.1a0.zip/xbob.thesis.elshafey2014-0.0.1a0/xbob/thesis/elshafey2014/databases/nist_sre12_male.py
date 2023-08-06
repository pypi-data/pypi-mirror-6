#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
#
# Copyright (C) 2013-2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xbob.db.nist_sre12
import facereclib

# Spear configuration files are used for feature extraction
# see xbob/thesis/elshafey2014/configurations/audio/nist_sre12/
nistsre12_directory = None 

database = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.nist_sre12.Database(),
    name = "nist_sre12",
    original_directory = nistsre12_directory,
    original_extension = ".sph",
    has_internal_annotations = False,
    protocol = 'male'
)
