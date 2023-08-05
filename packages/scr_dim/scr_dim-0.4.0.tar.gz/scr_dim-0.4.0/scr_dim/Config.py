import os
import json
import operator


class ConfigBase(object):
  k_min = 'brightness_max'
  k_max = 'brightness_min'
  k_op = 'step_operator'
  k_inc = 'step_coeff_inc'
  k_dec = 'step_coeff_dec'
  k_value = 'brightness'
  k_icc = 'icc_profile_load_on_reset'
  k_icc_path = 'icc_profile_path'

  def __init__(self):
    # TODO: validate config content for versioning
    self._conf = self._loadconf()
    if not self._conf:
      self._defaultconf()

  def _saveconf(self):
    pass

  def _loadconf(self):
    return {}

  def __getitem__(self, k):
    return self._conf[k]

  def update(self, dic):
    self._conf.update(dic)

  def _truncate_brightness(self, val):
    return min(max(val, self.min_brightness), self.max_brightness)

  @property
  def max_brightness(self):
    return self[self.k_max]

  @property
  def min_brightness(self):
    return self[self.k_min]

  @property
  def brightness(self):
    return self[self.k_value]

  @property
  def op(self):
    return getattr(operator, self[self.k_op])

  @property
  def inc_coeff(self):
    return self[self.k_inc]

  @property
  def dec_coeff(self):
    return self[self.k_dec]

  @brightness.setter
  def brightness(self, val):
    val = self._truncate_brightness(val)
    self.update({self.k_value: val})

  def _defaultconf(self):
    self._conf = {
        self.k_max: 1.0,
        self.k_min: 0.05,
        self.k_op: 'mul',
        self.k_inc: [1.08],
        self.k_dec: [0.926],
        self.k_value: 1.0,
        self.k_icc: False,
        self.k_icc_path: 'default.icc',
    }
    self._saveconf()


class Config(ConfigBase):
  """retrieves config values from filesystem"""

  def __init__(self, **kwargs):
    self.conf_dir = kwargs.get('conf_dir', \
        os.path.join(os.path.expanduser('~'), '.scr_dim'))
    self.conf_path = os.path.join(self.conf_dir, 'config')
    super().__init__()

  def _ensure_confdir(self):
    if not os.path.exists(self.conf_dir):
      try:
        os.makedirs(self.conf_dir)
      except IOError:
        pass
    if not os.path.isdir(self.conf_dir):
      raise Error('cannot create config directory at %s' \
          % self.conf_dir)

  def _loadconf(self):
    self._ensure_confdir()
    try:
      with open(self.conf_path, 'r') as fp:
        return json.load(fp)
    except:
      return None

  def _saveconf(self):
    self._ensure_confdir()
    with open(self.conf_path, 'w') as fp:
      enc = json.JSONEncoder(indent=2, separators=(',', ': '), sort_keys=True)
      fp.write(enc.encode(self._conf))

  def update(self, dic):
    self._conf.update(dic)
    self._saveconf()

  @property
  def icc(self):
    return self[self.k_icc]

  @property
  def icc_path(self):
    p = self[self.k_icc_path]
    if os.path.isdir(p):
      return p
    else:
      return os.path.abspath(os.path.join(self.conf_dir, p))

