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

import xbob.db.gbu
import facereclib

mbgc_v1_directory = "[YOUR_MBGC-V1_DIRECTORY]"

database = facereclib.databases.DatabaseXBob(
    database = xbob.db.gbu.Database(),
    name = "gbu",
    original_directory = mbgc_v1_directory,
    original_extension = ".jpg",
    has_internal_annotations = True,
    protocol = 'Good',

    all_files_options = { 'subworld': 'x8' },
    extractor_training_options = { 'subworld': 'x8' },
    projector_training_options = { 'subworld': 'x8' },
    enroller_training_options = { 'subworld': 'x8' }
)
