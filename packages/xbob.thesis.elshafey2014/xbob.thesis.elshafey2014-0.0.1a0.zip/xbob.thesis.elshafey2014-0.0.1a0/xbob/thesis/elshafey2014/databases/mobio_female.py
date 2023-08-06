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

import xbob.db.mobio
import facereclib
from xbob.thesis.elshafey2014.databases.DatabaseXBobZT_TNorm import DatabaseXBobZT_TNorm

mobio_image_directory = "[YOUR_MOBIO_IMAGE_DIRECTORY]"
mobio_annotation_directory = "[YOUR_MOBIO_ANNOTATION_DIRECTORY]"

database = DatabaseXBobZT_TNorm(
    database = xbob.db.mobio.Database(),
    name = "mobio",
    original_directory = mobio_image_directory,
    original_extension = ".png",
    annotation_directory = mobio_annotation_directory,
    annotation_type = 'eyecenter',
    protocol = 'laptop_mobile1-female',

    z_probe_options = { 'gender' : 'female' },
    t_norm_options = { 'gender' : 'female', 'subworld' : 'twothirds' },
)

