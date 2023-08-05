import os
import argparse
import re
import operator
from scr_dim.ProcLock import ProcLock
from scr_dim.Config import Config
from scr_dim.Executor import Executor

script_dir = os.path.realpath(os.path.dirname(__file__))


class ScrDim(object):
  """core logic to manipulate screen brightness"""

  def __init__(self, conf=Config(), cmd=Executor()):
    self.conf = conf
    self.cmd= cmd

  def _set_brightness(self, val):
    self.conf.brightness = val
    # do not pass val arg to cmd since brightness got possibly truncated by conf
    return all(self.cmd.set_brightness(t, self.conf.brightness) \
        for t in self.cmd.connected_outputs())

  def _mod_brightness(self, op, *val):
    return self._set_brightness(op(self.conf.brightness, *val))

  @property
  def command_names(self):
    if not hasattr(self, '_cmd_names') or not self._cmd_names:
      cmd_re = re.compile('^cmd_(.*)$')
      self._cmd_names = [
          m.group(1) for m in filter(None, map(cmd_re.match, dir(self)))]
    return self._cmd_names

  def get_cmd(self, cmd):
    return getattr(self, 'cmd_%s' % cmd)

  def cmd_inc(self, steps=1, *_):
    return all([self._mod_brightness(self.conf.op, *self.conf.inc_coeff) \
        for _ in range(int(steps))])

  def cmd_dec(self, steps=1, *_):
    return all([self._mod_brightness(self.conf.op, *self.conf.dec_coeff) \
        for _ in range(int(steps))])

  def cmd_reset(self, force_icc=None, *_):
    res = self._set_brightness(1.0)
    if force_icc or self.conf.icc:
      # going to ignore set_brightness return value
      if force_icc and os.path.isfile(force_icc):
        icc_path = force_icc
      else:
        icc_path = self.conf.icc_path
      # let it fail if the path is invalid
      return self.cmd.load_icc(self.conf.icc_path)
    else:
      return res

  def cmd_set(self, val=None, *_):
    val = float(val) if val else self.conf.brightness
    return self._set_brightness(val)


class Runner(ProcLock):
  """provide command line entry point"""

  def __init__(self, conf=Config()):
    self.core = ScrDim(conf=conf)
    super().__init__(os.path.join(conf.conf_dir, '.lockfile'))

  def main(self):
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=self.core.command_names)
    p.add_argument('cmd_args', nargs='*')
    args = p.parse_args()
    return 0 if self.core.get_cmd(args.cmd)(*args.cmd_args) else -1
