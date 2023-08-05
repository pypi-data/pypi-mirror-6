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

import facereclib

# setup of the ISV face recognition algorithm as used in the SCface database
tool = facereclib.tools.ISV(
    # ISV parameters
    subspace_dimension_of_u = 80,
    # GMM parameters
    number_of_gaussians = 512,
    # by default, our features are normalized, so it does not need to be done here
    normalize_before_k_means = False
)
