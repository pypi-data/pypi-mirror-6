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

import xbob.db.lfw
import facereclib

lfw_directory = "[YOUR_LFW_DIRECTORY]"
lfw_annotation_directory = "[YOUR_LFW_ANNOTATION_DIRECTORY]"

database = facereclib.databases.DatabaseXBob(
    database = xbob.db.lfw.Database(),
    name = 'lfw',
    original_directory = lfw_directory,
    original_extension = ".jpg",
    annotation_directory = lfw_annotation_directory,
    annotation_type = 'named',

    all_files_options = { 'world_type' : 'unrestricted' },
    extractor_training_options = { 'world_type' : 'unrestricted' },
    projector_training_options = {'world_type' : 'unrestricted' },
    enroller_training_options = { 'world_type' : 'unrestricted' },

    protocol = 'view1'
)
