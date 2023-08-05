from nose.tools import *
import os
import tempfile
from scr_dim.Config import ConfigBase


def test_truncate():
  c = ConfigBase()
  assert_almost_equal(c.max_brightness, c._truncate_brightness(c.max_brightness + 1.0))
  assert_almost_equal(c.min_brightness, c._truncate_brightness(c.min_brightness - 1.0))
