#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <manuel.guenther@idiap.ch>
# Tue Jul 2 14:52:49 CEST 2013
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

"""This script evaluates the given score files and computes EER, HTER.
It also is able to plot CMC and ROC curves."""

from .. import utils
import argparse
import bob
import numpy, math
import os


def command_line_arguments(command_line_parameters):
  """Parse the program options"""

  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-d', '--dev-files', required=True, nargs='+', help = "A list of score files of the development set.")
  parser.add_argument('-e', '--eval-files', nargs='+', help = "A list of score files of the evaluation set; if given it must be the same number of files as the --dev-files.")

  parser.add_argument('-s', '--directory', default = '.', help = "A directory, where to find the --dev-files and the --eval-files")

  parser.add_argument('-D', '--dev-out-file', required=True, help = "The output file where to write the fused scores of the development set into")
  parser.add_argument('-E', '--eval-out-file', help = "The output file where to write the fused scores of the evaluation set into into")

  parser.add_argument('-n', '--mean-std-norm', action='store_true', help = "If given, the scores will be mean-std normalized before applying fusion")
  parser.add_argument('-r', '--sum-rule', action='store_true', help = "Use sum rule fusion instead of logistic regression")

  parser.add_argument('--self-test', action='store_true', help=argparse.SUPPRESS)

  utils.add_logger_command_line_option(parser)

  # parse arguments
  args = parser.parse_args(command_line_parameters)

  utils.set_verbosity_level(args.verbose)

  # some sanity checks:
  if args.eval_files and len(args.dev_files) != len(args.eval_files):
    utils.error("The number of --dev-files (%d) and --eval-files (%d) are not identical!" % (len(args.dev_files), len(args.eval_files)))

  if args.eval_files and not args.eval_out_file:
    utils.error("When --eval-files are specified, the --eval-out-file must be given as well!")

  # concatenate directory to dev and eval files
  if args.directory:
    args.dev_files = [os.path.join(args.directory, f) for f in args.dev_files]
    if args.eval_files:
      args.eval_files = [os.path.join(args.directory, f) for f in args.eval_files]


  return args


def fuse_scores(machine, score_files, output_file, mean, std):
  """Fuses the selected score files with the given machine and writes the results to the given file."""
  # read all score files; these score files need to have the scores in the same order.
  score_file_lines = [bob.measure.load.four_column(f) for f in score_files]

  utils.info("Writing fused score file %s" % output_file)

  # get the first score file as reference
  first = score_file_lines[0]
  score_count = len(first)
  # create output file
  output = open(output_file, 'w')
  # iterate over the client/probe pairs
  for i in range(score_count):
    # get the raw scores of all systems for this specific client/probe pair
    raw_scores = [(float(line[i][-1]) - mean[index]) / std[index] for index, line in enumerate(score_file_lines)]
    # fuse these scores into one value by using the given machine
    fused_score = machine(raw_scores)
    # write the fused score to file, using the reference client id, probe id and probe name
    output.write("%s %s %s %f\n" % (first[i][0] , first[i][1], first[i][2], fused_score))


def main(command_line_parameters=None):
  """Reads score files, computes error measures and plots curves."""

  args = command_line_arguments(command_line_parameters)

  score_parser = bob.measure.load.split_four_column

  # First, read the score files
  utils.info("Loading %d score files of the development set" % len(args.dev_files))
  scores_dev = [score_parser(f) for f in args.dev_files]

  if args.eval_files:
    utils.info("Loading %d score files of the evaluation set" % len(args.eval_files))
    scores_eval = [score_parser(f) for f in args.eval_files]

  mean = [0.] * len(args.dev_files)
  std = [1.] * len(args.dev_files)

  if args.mean_std_norm:
    utils.info("Computing mean and standard deviation of algorithms")
    # compute mean and std of development set scores
    for i in range(len(scores_dev)):
      dev = numpy.hstack(scores_dev[i])
      mean[i] = numpy.mean(dev)
      std[i] = numpy.std(dev)
      utils.debug("  .. algorithm %s: mean %f, std: %f" % (args.dev_files[i], mean[i], std[i]))
      scores_dev[i] = ((scores_dev[i][0] - mean[i]) / std[i], (scores_dev[i][1] - mean[i]) / std[i])
      if scores_eval:
        scores_eval[i] = ((scores_eval[i][0] - mean[i]) / std[i], (scores_eval[i][1] - mean[i]) / std[i])

  if not args.sum_rule:
    # train the fusion of all algorithms
    # get the positive and negative scores for the first i systems
    negatives = numpy.vstack([scores_dev[j][0] for j in range(len(scores_dev))]).T
    positives = numpy.vstack([scores_dev[j][1] for j in range(len(scores_dev))]).T

    # train a linear machine that will do the score fusion
    # using conjugated gradient logistic regression
    trainer = bob.trainer.CGLogRegTrainer(0.5, 1e-16, 100000)
    machine = trainer.train(negatives, positives)
  else:
    weights = numpy.ones((len(args.dev_files),1), numpy.float64)
    machine = bob.machine.LinearMachine(weights)

  utils.info("Fusion weights are \n%s \nwith bias \n%s" % (str(machine.weights), str(machine.biases)))

  # fuse the scores of the development and the evaluation set
  utils.info('Fusing scores for the development set to %s' % args.dev_out_file)
  utils.ensure_dir(os.path.dirname(args.dev_out_file))
  fuse_scores(machine, args.dev_files, args.dev_out_file, mean, std)
  if args.eval_files:
    utils.info('Fusing scores for the evaluation set to %s' % args.eval_out_file)
    utils.ensure_dir(os.path.dirname(args.eval_out_file))
    fuse_scores(machine, args.eval_files, args.eval_out_file, mean, std)


