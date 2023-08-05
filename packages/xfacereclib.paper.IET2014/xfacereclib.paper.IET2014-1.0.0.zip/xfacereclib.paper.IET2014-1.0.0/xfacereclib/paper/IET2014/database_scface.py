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

import xbob.db.scface
import facereclib

### IMPORTANT!
# Adapt the following two directories:

# The directory where the images of the SCface database are found
scface_directory = "[YOUR_SC_FACE_IMAGE_DIRECTORY]"


# Setup for SCface database, combined ZT-probe files
combined = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.scface.Database(),
    name = 'scface',
    original_directory = scface_directory,
    original_extension = ".jpg",
    has_internal_annotations = True,
    protocol = 'combined',
    projector_training_options = { 'subworld': 'twothirds' }
)

# Setups for SCface database, separate ZT-probe files
close = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.scface.Database(),
    name = 'scface',
    original_directory = scface_directory,
    original_extension = ".jpg",
    has_internal_annotations = True,
    protocol = 'close',

    projector_training_options = { 'subworld': 'twothirds' },
    z_probe_options = { 'distances': 3 }
)

medium = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.scface.Database(),
    name = 'scface',
    original_directory = scface_directory,
    original_extension = ".jpg",
    has_internal_annotations = True,
    protocol = 'medium',

    projector_training_options = { 'subworld': 'twothirds' },
    z_probe_options = { 'distances': 2 }
)

far = facereclib.databases.DatabaseXBobZT(
    database = xbob.db.scface.Database(),
    name = 'scface',
    original_directory = scface_directory,
    original_extension = ".jpg",
    has_internal_annotations = True,
    protocol = 'far',

    projector_training_options = { 'subworld': 'twothirds' },
    z_probe_options = { 'distances': 1 }
)


