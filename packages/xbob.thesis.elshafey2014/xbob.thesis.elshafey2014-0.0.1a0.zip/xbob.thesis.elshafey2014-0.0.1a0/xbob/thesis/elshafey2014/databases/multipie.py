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

import xbob.db.multipie
import facereclib

multipie_image_directory = "[YOUR_MULTI-PIE_IMAGE_DIRECTORY]"
multipie_annotation_directory = "[YOUR_MULTI-PIE_ANNOTATION_DIRECTORY]"

database = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'E',
)

# FRONTAL
frontal_cams = ('19_0', '04_1', '05_0', '05_1', '13_0', '14_0', '08_0')
database_frontal = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P',

    all_files_options = {'cameras' : frontal_cams},
    extractor_training_options= {'cameras' : frontal_cams},
    projector_training_options= {'cameras' : frontal_cams},
    enroller_training_options = {'cameras' : frontal_cams},
)

database_P19_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P19_0',
)

database_P04_1 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P04_1',
)

database_P05_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P05_0',
)

database_P05_1 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P05_1',
)

database_P13_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P13_0',
)

database_P14_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P14_0',
)

database_P08_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P08_0',
)


# LEFT
left_cams = ('09_0', '11_0', '12_0')
database_left = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P',

    all_files_options = {'cameras' : left_cams},
    extractor_training_options= {'cameras' : left_cams},
    projector_training_options= {'cameras' : left_cams},
    enroller_training_options = {'cameras' : left_cams},
)

database_P09_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P09_0',
)

database_P11_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P11_0',
)

database_P12_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P12_0',
)


# RIGHT
right_cams = ('24_0', '01_0', '20_0')
database_right = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P',

    all_files_options = {'cameras' : right_cams},
    extractor_training_options= {'cameras' : right_cams},
    projector_training_options= {'cameras' : right_cams},
    enroller_training_options = {'cameras' : right_cams},
)

database_P24_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P24_0',
)

database_P01_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P01_0',
)

database_P20_0 = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P20_0',
)

pose_cams = frontal_cams + left_cams + right_cams
database_pose = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.multipie.Database(),
    name = "multipie",
    original_directory = multipie_image_directory,
    original_extension = ".png",
    annotation_directory = multipie_annotation_directory,
    annotation_type = 'multipie',
    protocol = 'P',

    all_files_options = {'cameras' : pose_cams},
    extractor_training_options= {'cameras' : pose_cams},
    projector_training_options= {'cameras' : pose_cams},
    enroller_training_options = {'cameras' : pose_cams},
)


