#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
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
import numpy
from .. import utils
from .Preprocessor import Preprocessor
from .FaceCrop import FaceCrop

class TanTriggs (FaceCrop):
  """Crops the face (if desired) and applies Tan&Triggs algorithm"""

  def __init__(
      self,
      gamma = 0.2,
      sigma0 = 1,
      sigma1 = 2,
      size = 5,
      threshold = 10.,
      alpha = 0.1,
      **kwargs
  ):

    """Parameters of the constructor of this preprocessor:

    gamma, sigma0, sigma1, size, threshold, alpha
      Please refer to the [TT10]_ original paper (see FaceRecLib documentation).

    kwargs
      The parameters directly passed to the :class:`facereclib.preprocessing.FaceCrop` base class constructor.
    """

    # call base class constructor with its set of parameters
    FaceCrop.__init__(
        self,

        gamma = gamma,
        sigma0 = sigma0,
        sigma1 = sigma1,
        size = size,
        threshold = threshold,
        alpha = alpha,

        **kwargs
    )

    if self.m_perform_image_cropping:
      # input image will be the output of the face cropper
      self.m_tan_triggs_image = numpy.ndarray(self.m_cropped_image.shape, numpy.float64)
    else:
      # resolution of input image is not known yet
      self.m_tan_triggs_image = None

    self.m_tan_triggs = bob.ip.TanTriggs(gamma, sigma0, sigma1, size, threshold, alpha)


  def tan_triggs(self, image):
    """Performs the Tan&Triggs normalization to the given image"""
    # create image in desired shape, if necessary
    if self.m_tan_triggs_image is None or self.m_tan_triggs_image.shape != image.shape:
      self.m_tan_triggs_image = numpy.ndarray(image.shape, numpy.float64)

    # perform Tan&Triggs normalization
    self.m_tan_triggs(image, self.m_tan_triggs_image)

    return self.m_tan_triggs_image


  def __call__(self, image, annotations = None):
    """Reads the input image, normalizes it according to the eye positions, performs Tan&Triggs normalization, and writes the resulting image"""
    # crop the face using the base class method
    image = self.crop_face(image, annotations)

    # perform Tan&Triggs normalization
    tan_triggs_image = self.tan_triggs(image)

    if self.m_perform_image_cropping and annotations != None:
      # set the positions that were masked during face cropping to 0
      tan_triggs_image[self.m_cropped_mask == False] = 0.

    # save the image to file
    return tan_triggs_image



class TanTriggsVideo (Preprocessor):
  """Applies the Tan-Triggs algorithm to each frame in a video"""

  def __init__(
     self,
     gamma = 0.2,
     sigma0 = 1,
     sigma1 = 2,
     size = 5,
     threshold = 10.,
     alpha = 0.1,
     color_channel = 'gray',
  ):

    Preprocessor.__init__(self)
    self.m_color_channel = color_channel
    # prepare image normalization
    self.m_tan = bob.ip.TanTriggs(gamma, sigma0, sigma1, size, threshold, alpha)

  def read_original_data(self, video_file):
    """Reads the original image (in this case a utils.FrameContainer) from the given file"""
    return utils.video.FrameContainer(str(video_file))

  def __call__(self, frame_container, annotations = None):
    """For each frame in the VideoFrameContainer (read from input_file) applies the Tan-Triggs algorithm, then writes the resulting VideoFrameContainer to output_file. NOTE: annotations is ignored even if specified."""
    # Process each frame
    output_frame_container = utils.video.FrameContainer()
    for (frame_id, image, quality) in frame_container.frames():

      # Convert to grayscale if it seems necessary
      image = utils.gray_channel(image, self.m_color_channel)

      # Perform Tan-Triggs and store result
      tan_image = numpy.ndarray(image.shape, numpy.float64)
      self.m_tan(image, self.m_tan_image)
      output_frame_container.add_frame(frame_id, tan_image, quality)

    return output_frame_container

  read_data = read_original_data
