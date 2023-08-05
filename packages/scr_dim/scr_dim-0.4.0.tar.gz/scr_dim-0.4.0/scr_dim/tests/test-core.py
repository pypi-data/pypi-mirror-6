from nose.tools import *
import os
import tempfile
import collections
from scr_dim.core import ScrDim
from scr_dim.Config import ConfigBase

class DummyExecutor(object):
  def __init__(self):
    self.history = collections.defaultdict(lambda: [])

  def _add_record(self, cmd, *args):
    self.history[cmd].append(args)

  def connected_outputs(self):
    return ['out1', 'out2']

  def set_brightness(self, *args):
    self._add_record('set_brightness', *args)
    return True

  def load_icc(self, *args):
    self._add_record('load_ic', *args)
    return True


class DummyConfig(ConfigBase):
  def __init__(self):
    super().__init__()
    self.brightness = 0.5


def test_set_current():
  c = ScrDim(conf=DummyConfig(), cmd=DummyExecutor())
  nouts = len(c.cmd.connected_outputs())
  expected = c.conf.brightness
  res = c.get_cmd('set')()
  hist = c.cmd.history['set_brightness']
  ok_(res)
  eq_(nouts, len(hist))
  for n in range(nouts):
    eq_(hist[n][1], expected)


def test_set():
  c = ScrDim(conf=DummyConfig(), cmd=DummyExecutor())
  nouts = len(c.cmd.connected_outputs())
  expected = 0.88
  res = c.get_cmd('set')(expected)
  hist = c.cmd.history['set_brightness']
  ok_(res)
  eq_(nouts, len(hist))
  for n in range(nouts):
    eq_(hist[n][1], expected)


def test_inc():
  c = ScrDim(conf=DummyConfig(), cmd=DummyExecutor())
  nouts = len(c.cmd.connected_outputs())
  expected = c.conf.brightness * c.conf.inc_coeff[0]
  res = c.get_cmd('inc')()
  hist = c.cmd.history['set_brightness']
  ok_(res)
  eq_(nouts, len(hist))
  for n in range(nouts):
    eq_(hist[n][1], expected)


def test_dec():
  c = ScrDim(conf=DummyConfig(), cmd=DummyExecutor())
  nouts = len(c.cmd.connected_outputs())
  expected = c.conf.brightness * c.conf.dec_coeff[0]
  res = c.get_cmd('dec')()
  hist = c.cmd.history['set_brightness']
  ok_(res)
  eq_(nouts, len(hist))
  for n in range(nouts):
    eq_(hist[n][1], expected)


def test_inc_ntimes():
  c = ScrDim(conf=DummyConfig(), cmd=DummyExecutor())
  nouts = len(c.cmd.connected_outputs())
  coeff = c.conf.inc_coeff[0]
  expected = c.conf.brightness * coeff * coeff * coeff
  # any value that doesn't invoke max
  ntimes = 3
  res = c.get_cmd('inc')(ntimes)
  hist = c.cmd.history['set_brightness']
  ok_(res)
  eq_(nouts * ntimes, len(hist))
  eq_(hist[4][1], expected)
  eq_(hist[5][1], expected)


def test_dec_ntimes():
  c = ScrDim(conf=DummyConfig(), cmd=DummyExecutor())
  nouts = len(c.cmd.connected_outputs())
  coeff = c.conf.dec_coeff[0]
  expected = c.conf.brightness * coeff * coeff * coeff
  # any value that doesn't invoke min
  ntimes = 3
  res = c.get_cmd('dec')(ntimes)
  hist = c.cmd.history['set_brightness']
  ok_(res)
  eq_(nouts * ntimes, len(hist))
  eq_(hist[4][1], expected)
  eq_(hist[5][1], expected)



def test_inc_max():
  c = ScrDim(conf=DummyConfig(), cmd=DummyExecutor())
  _max = c.conf[c.conf.k_max]
  c.conf.brightness = _max * 0.99
  expected = _max
  nouts = len(c.cmd.connected_outputs())
  ntimes = 2
  res = c.get_cmd('inc')(ntimes)
  hist = c.cmd.history['set_brightness']
  ok_(res)
  eq_(nouts * ntimes, len(hist))
  for n in range(nouts * ntimes):
    eq_(hist[n][1], expected)


def test_dec_min():
  c = ScrDim(conf=DummyConfig(), cmd=DummyExecutor())
  _min = c.conf[c.conf.k_min]
  c.conf.brightness = _min * 1.01
  expected = _min
  nouts = len(c.cmd.connected_outputs())
  ntimes = 2
  res = c.get_cmd('dec')(ntimes)
  hist = c.cmd.history['set_brightness']
  ok_(res)
  eq_(nouts * ntimes, len(hist))
  for n in range(nouts * ntimes):
    eq_(hist[n][1], expected)
