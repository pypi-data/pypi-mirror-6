import subprocess
import re

class Executor(object):
  """actually chagnes OS settings"""
  _re = re.compile('([^\s]+) connected ')

  def connected_outputs(self):
    p = subprocess.Popen([
      'xrandr',
      '--current',
    ], stdout=subprocess.PIPE)
    o, _ = p.communicate()
    output_list = o.decode('utf-8').splitlines()
    return [
      m.group(1) for m in filter(None, map(self._re.match, output_list))
    ]

  def set_brightness(self, target_output, rate=1.0):
    return subprocess.call(['xrandr',
      '--output', target_output,
      '--brightness', '%f' % rate,
    ]) == 0

  def load_icc(self, profile_path, screen=0):
    return subprocess.call([
      'xcalib',
      '-d', ':%d' % screen,
      profile_path,
    ]) == 0
