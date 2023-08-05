#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Wed Dec  4 11:24:11 CET 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
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


### IMPORTANT!
# Adapt the following two directories:

# The directories where the images and the annotations of the MOBIO database are found
mobio_image_directory = "[YOUR_MOBIO_IMAGE_DIRECTORY]"
mobio_annotation_directory = "[YOUR_MOBIO_ANNOTATION_DIRECTORY]"

# The database setup that is used by the FaceRecLib to compute the face recognition experiments
database = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.mobio.Database(),
    name = "mobio",
    original_directory = mobio_image_directory,
    original_extension = ".png",
    annotation_directory = mobio_annotation_directory,
    annotation_type = 'eyecenter',
    protocol = 'mobile0-male',
    projector_training_options = { 'subworld' : 'twothirds-subsampled' }
)


