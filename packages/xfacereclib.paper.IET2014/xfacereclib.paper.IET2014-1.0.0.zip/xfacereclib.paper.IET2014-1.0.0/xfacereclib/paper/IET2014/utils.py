#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Dec  9 19:09:06 CET 2013
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

import bob
import facereclib
import numpy

def split_score_file(score_file):
  """Reads a score file from the SCface database and splits it into the three different distance conditions."""
  # read the score file
  columns = bob.measure.load.four_column(score_file)
  positives = [[], [], []]
  negatives = [[], [], []]
  # iterate through the score file lines
  for line in columns:
    # extract the distance from the probe file name
    distance = int(line[2].split('/')[0][-1]) - 1
    # append either positive or negative score
    if line[0] == line[1]:
      positives[distance].append(line[3])
    else:
      negatives[distance].append(line[3])
  # return the score file split into the three distances
  return [numpy.array(n) for n in negatives], [numpy.array(p) for p in positives]


def evaluate_scores(neg_dev, pos_dev, neg_eval, pos_eval):
  """Evaluates the given set of development set and evaluation set scores and returns a tuple containing:
  (Cver_min_dev, Cver_min_eval, Cver_eval, Cver_0_dev, Cver_0_eval, Pfr_dev, Pfr_eval, Cllr_dev, Cllr_eval, Cllr_min_dev, Cllr_min_eval)
  """
  # compute C_ver^min on evaluation set
  threshold = bob.measure.min_hter_threshold(neg_eval, pos_eval)
  far,frr = bob.measure.farfrr(neg_eval, pos_eval, threshold)
  Cver_min_eval = (far + frr) / 2.

  # compute C_ver^min on development set and C_ver on evaluation set (using the same threshold)
  threshold = bob.measure.min_hter_threshold(neg_dev, pos_dev)
  far,frr = bob.measure.farfrr(neg_dev, pos_dev, threshold)
  Cver_min_dev = (far + frr) / 2.
  far,frr = bob.measure.farfrr(neg_eval, pos_eval, threshold)
  Cver_eval = (far + frr) / 2.

  # compute C_ver on threshold 0
  far,frr = bob.measure.farfrr(neg_dev, pos_dev, 0)
  Cver_0_dev = (far + frr) / 2.
  far,frr = bob.measure.farfrr(neg_eval, pos_eval, 0)
  Cver_0_eval = (far + frr) / 2.

  # compute FRR at threshold based on FAR = 1%
  threshold = bob.measure.far_threshold(neg_dev, pos_dev, 0.01)
  _,Pfr_dev = bob.measure.farfrr(neg_dev, pos_dev, threshold)
  threshold = bob.measure.far_threshold(neg_eval, pos_eval, 0.01)
  _,Pfr_eval = bob.measure.farfrr(neg_eval, pos_eval, threshold)

  # write results to console
  facereclib.utils.debug("- Verification performance: %3.3f %% Cver_min (dev) and: %3.3f %% Cver_min (eval) and: %3.3f %% Cver (eval)" % (Cver_min_dev * 100., Cver_min_eval * 100., Cver_eval * 100.))
  facereclib.utils.debug("- Verification performance at FAR 1%%: %3.3f %% Pfr (dev) and: %3.3f %% Pfr (eval)" % (Pfr_dev * 100., Pfr_eval * 100.))
  facereclib.utils.debug("- Verification performance at threshold 0: %3.3f %% Cver (dev) and: %3.3f %% Cver (eval)" % (Cver_0_dev * 100., Cver_0_eval * 100.))

  # compute Cllr and Cllr_min using Bob's implementation of the two measures
  Cllr_dev = bob.measure.calibration.cllr(neg_dev, pos_dev)
  Cllr_eval = bob.measure.calibration.cllr(neg_eval, pos_eval)
  Cllr_min_dev = bob.measure.calibration.min_cllr(neg_dev, pos_dev)
  Cllr_min_eval = bob.measure.calibration.min_cllr(neg_eval, pos_eval)

  # write results to console
  facereclib.utils.debug("- Calbration performance: %1.5f Cllr (dev) -- %1.5f Cllr_min (dev), %1.5f Cllr (eval) -- %1.5f Cllr_min (eval)" % (Cllr_dev, Cllr_min_dev, Cllr_eval, Cllr_min_eval))

  # return the collection of results
  return (Cver_min_dev, Cver_min_eval, Cver_eval, Cver_0_dev, Cver_0_eval, Pfr_dev, Pfr_eval, Cllr_dev, Cllr_eval, Cllr_min_dev, Cllr_min_eval)
