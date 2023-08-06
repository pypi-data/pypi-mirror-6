
# Copyright (c) 2013, Kevin Greenan (kmgreen2@gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.  THIS SOFTWARE IS PROVIDED BY
# THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pyeclib
from pyeclib.ec_iface import ECDriver
import unittest
import random
import string
import sys
import os

class TestNullDriver(unittest.TestCase):

  def setUp(self):
    self.null_driver = ECDriver("pyeclib.core.ECNullDriver", k=8, m=2)

  def tearDown(self):
    pass

  def test_null_driver(self):
    self.null_driver.encode('')
    self.null_driver.decode([])
    

class TestStripeDriver(unittest.TestCase):
  def setUp(self):
    self.stripe_driver = ECDriver("pyeclib.core.ECStripingDriver", k=8, m=0)

  def tearDown(self):
    pass
    
class TestPyECLibDriver(unittest.TestCase):

  def __init__(self, *args):
    self.file_sizes = ["100-K"]
    self.num_iterations = 100

    unittest.TestCase.__init__(self, *args)
  
  def setUp(self):

    if not os.path.isdir("test_files"):
      os.mkdir("./test_files")

    for size_str in self.file_sizes:
      filename = "test_file.%s" % size_str
      fp = open("test_files/%s" % filename, "w")

      size_desc = size_str.split("-")

      size = int(size_desc[0])

      if (size_desc[1] == 'M'):
        size *= 1000000
      elif (size_desc[1] == 'K'):
        size *= 1000

      buffer = ''.join(random.choice(string.letters) for i in range(size))

      fp.write(buffer)
      fp.close()

  def tearDown(self):
    for size_str in self.file_sizes:
      filename = "test_files/test_file.%s" % size_str
      os.unlink(filename)
    os.rmdir("./test_files")

  def test_small_encode(self):
    pyeclib_drivers = []
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_vand"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=11, m=2, type="rs_vand"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=10, m=2, type="rs_vand"))

    encode_strs = ["a", "hello", "hellohyhi", "yo"]

    for pyeclib_driver in pyeclib_drivers:
      for encode_str in encode_strs:
          encoded_fragments = pyeclib_driver.encode(encode_str)
          decoded_str = pyeclib_driver.decode(encoded_fragments)
          
          self.assertTrue(decoded_str == encode_str)
  
  def test_verify_fragment_algsig_chksum_fail(self):
    pyeclib_drivers = []
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_vand", chksum_type="algsig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=3, type="rs_vand", chksum_type="algsig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=6, type="flat_xor_4", chksum_type="algsig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=10, m=5, type="flat_xor_4", chksum_type="algsig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=10, m=5, type="flat_xor_3", chksum_type="algsig"))

    filesize = 1024*1024*3

    file_str = ''.join(random.choice(string.letters) for i in range(filesize))
    fragment_to_corrupt = random.randint(0, 12)

    for pyeclib_driver in pyeclib_drivers:
      fragments = pyeclib_driver.encode(file_str) 

      fragment_metadata_list = []

      i = 0
      for fragment in fragments:
        if i == fragment_to_corrupt:
          corrupted_fragment = fragment[:100] + chr(ord(fragment[100]) + 1) + fragment[101:]
          fragment_metadata_list.append(pyeclib_driver.get_metadata(corrupted_fragment))
        else:
          fragment_metadata_list.append(pyeclib_driver.get_metadata(fragment))
        i += 1

      self.assertTrue(pyeclib_driver.verify_stripe_metadata(fragment_metadata_list) != -1)

  def test_verify_fragment_inline_succeed(self):
    pyeclib_drivers = []
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_vand", chksum_type="algsig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=3, type="rs_vand", chksum_type="algsig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=6, type="flat_xor_4", chksum_type="algsig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=10, m=5, type="flat_xor_4", chksum_type="algsig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=10, m=5, type="flat_xor_3", chksum_type="algsig"))
    
    filesize = 1024*1024*3

    file_str = ''.join(random.choice(string.letters) for i in range(filesize))

    for pyeclib_driver in pyeclib_drivers:
      fragments = pyeclib_driver.encode(file_str) 

      fragment_metadata_list = []

      for fragment in fragments:
        fragment_metadata_list.append(pyeclib_driver.get_metadata(fragment))

      self.assertTrue(pyeclib_driver.verify_stripe_metadata(fragment_metadata_list) == -1)

  def test_verify_fragment_inline_chksum_fail(self):
    pyeclib_drivers = []
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_vand", chksum_type="inline"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=3, type="rs_vand", chksum_type="inline"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=4, type="rs_vand", chksum_type="inline"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_cauchy_orig", chksum_type="inline"))
    
    filesize = 1024*1024*3

    file_str = ''.join(random.choice(string.letters) for i in range(filesize))
    fragment_to_corrupt = random.randint(0, 12)

    for pyeclib_driver in pyeclib_drivers:
      fragments = pyeclib_driver.encode(file_str) 

      fragment_metadata_list = []

      i = 0
      for fragment in fragments:
        if i == fragment_to_corrupt:
          corrupted_fragment = fragment[:100] + chr(ord(fragment[100]) + 1) + fragment[101:]
          fragment_metadata_list.append(pyeclib_driver.get_metadata(corrupted_fragment))
        else:
          fragment_metadata_list.append(pyeclib_driver.get_metadata(fragment))
        i += 1

      self.assertTrue(pyeclib_driver.verify_stripe_metadata(fragment_metadata_list) == fragment_to_corrupt)

  def test_verify_fragment_inline_chksum_succeed(self):
    pyeclib_drivers = []
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_vand", chksum_type="inline"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=3, type="rs_vand", chksum_type="inline"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=4, type="rs_vand", chksum_type="inline"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_cauchy_orig", chksum_type="inline"))
    
    filesize = 1024*1024*3

    file_str = ''.join(random.choice(string.letters) for i in range(filesize))
        
    for pyeclib_driver in pyeclib_drivers:
      fragments = pyeclib_driver.encode(file_str) 

      fragment_metadata_list = []

      for fragment in fragments:
        fragment_metadata_list.append(pyeclib_driver.get_metadata(fragment))

      self.assertTrue(pyeclib_driver.verify_stripe_metadata(fragment_metadata_list) == -1)
    
  def test_get_segment_info(self):
    pyeclib_drivers = []
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_vand"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=11, m=2, type="rs_vand"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=10, m=2, type="rs_vand"))

    file_sizes = [1024*1024, 2*1024*1024, 10*1024*1024, 10*1024*1024+7]
    segment_sizes = [3*1024, 1024*1024]
    segment_strings = {}

    #
    # Generate some test segments for each segment size.
    # Use 2 * segment size, because last segment may be
    # greater than segment_size
    #
    char_set = string.ascii_uppercase + string.digits
    for segment_size in segment_sizes:
      segment_strings[segment_size] = ''.join(random.choice(char_set) for i in range(segment_size*2))
    
    for pyeclib_driver in pyeclib_drivers:
      for file_size in file_sizes:
        for segment_size in segment_sizes:
          #
          # Compute the segment info
          #
          segment_info = pyeclib_driver.get_segment_info(file_size, segment_size)

          num_segments = segment_info['num_segments'] 
          segment_size = segment_info['segment_size'] 
          fragment_size = segment_info['fragment_size'] 
          last_segment_size = segment_info['last_segment_size'] 
          last_fragment_size = segment_info['last_fragment_size'] 

          computed_file_size = ((num_segments-1) * segment_size) + last_segment_size

          #
          # Verify that the segment sizes add up
          #
          self.assertTrue(computed_file_size == file_size)

          encoded_fragments = pyeclib_driver.encode(segment_strings[segment_size][:segment_size])

          #
          # Verify the fragment size
          #
          self.assertTrue(fragment_size == len(encoded_fragments[0]))

          if last_segment_size > 0:
            encoded_fragments = pyeclib_driver.encode(segment_strings[segment_size][:last_segment_size])

            #
            # Verify the last fragment size, if there is a last fragment
            #
            self.assertTrue(last_fragment_size == len(encoded_fragments[0]))
  
  def test_rs(self):
    pyeclib_drivers = []
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_vand"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=2, type="rs_cauchy_orig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=3, type="rs_vand"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=3, type="rs_cauchy_orig"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=12, m=6, type="flat_xor_4"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=10, m=5, type="flat_xor_4"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=10, m=5, type="flat_xor_3"))
    pyeclib_drivers.append(ECDriver("pyeclib.core.ECPyECLibDriver", k=9, m=5, type="flat_xor_3"))

    for pyeclib_driver in pyeclib_drivers:
      for file_size in self.file_sizes:
        filename = "test_file.%s" % file_size
        fp = open("test_files/%s" % filename, "r")
  
        whole_file_str = fp.read()
    
        orig_fragments=pyeclib_driver.encode(whole_file_str)
  
  
        for iter in range(self.num_iterations):
          num_missing = 2
          idxs_to_remove = []
          fragments = orig_fragments[:]
          for j in range(num_missing):
            idx = random.randint(0, 13)
            if idx not in idxs_to_remove:
              idxs_to_remove.append(idx)
          
          # Reverse sort the list, so we can always
          # remove from the original index 
          idxs_to_remove.sort(lambda x,y: y-x)
          for idx in idxs_to_remove:
            fragments.pop(idx)
  
          #
          # Test decoder (send copy, because we want to re-use
          # fragments for reconstruction)
          #
          decoded_string = pyeclib_driver.decode(fragments[:])
  
          self.assertTrue(whole_file_str == decoded_string)

          #
          # Test reconstructor
          #
          reconstructed_fragments = pyeclib_driver.reconstruct(fragments, idxs_to_remove)

          self.assertTrue(reconstructed_fragments[0] == orig_fragments[idxs_to_remove[0]])

if __name__ == '__main__':
    unittest.main()
