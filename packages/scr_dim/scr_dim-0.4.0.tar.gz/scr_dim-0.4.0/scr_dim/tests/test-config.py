from nose.tools import *
from nose.exc import SkipTest
import shutil
import os
import tempfile
from scr_dim.Config import Config

# safe config directory path for test
tmp_confdir = os.path.join(tempfile.gettempprefix(), tempfile.gettempprefix() + 'scr_dim_test_dir')


def setup_cleandir():
  if not shutil.rmtree.avoids_symlink_attacks:
    raise SkipTest('platform does not support symlink-attack-free rmtree')
  if os.path.exists(tmp_confdir):
    shutil.rmtree(tmp_confdir)


@with_setup(setup_cleandir)
def test_dir_init():
  c = Config(conf_dir=tmp_confdir)
  eq_(tmp_confdir, c.conf_dir)
  ok_(os.path.isdir(c.conf_dir))


@with_setup(setup_cleandir)
def test_file_init():
  c = Config(conf_dir=tmp_confdir)
  # safety assert so that test doesn't purge default real config dir
  eq_(tmp_confdir, c.conf_dir)
  eq_(os.path.join(tmp_confdir, 'config'), c.conf_path)
  ok_(os.path.isfile(c.conf_path))


@with_setup(setup_cleandir)
def test_default_value():
  c = Config(conf_dir=tmp_confdir)
  eq_(tmp_confdir, c.conf_dir)  # safety assert
  assert_almost_equal(1.0, c['brightness'])
  eq_('default.icc', c[c.k_icc_path])
  ok_(not c[c.k_icc])


@with_setup(setup_cleandir)
def test_save_load():
  c1 = Config(conf_dir=tmp_confdir)
  eq_(tmp_confdir, c1.conf_dir)  # safety assert
  c1.update({
    'brightness': 0.5,
    c1.k_icc_path: 'alternate.icc',
  })
  c2 = Config(conf_dir=tmp_confdir)
  eq_(tmp_confdir, c2.conf_dir)  # safety assert
  assert_almost_equal(0.5, c2['brightness'])
  eq_('alternate.icc', c2[c2.k_icc_path])


@with_setup(setup_cleandir)
def test_partial_update():
  c = Config(conf_dir=tmp_confdir)
  eq_(tmp_confdir, c.conf_dir)  # safety assert
  c.update({
    c.k_value: 0.7,
    c.k_icc_path: 'my_profile.icc',
  })
  c.update({c.k_value: 0.5})
  assert_almost_equal(0.5, c[c.k_value])
  eq_('my_profile.icc', c[c.k_icc_path])
  c.update({c.k_icc_path: 'fallback_profile.icc'})
  assert_almost_equal(0.5, c[c.k_value])
  eq_('fallback_profile.icc', c[c.k_icc_path])


@with_setup(setup_cleandir)
def test_icc_abspath():
  c = Config(conf_dir=tmp_confdir)
  eq_(tmp_confdir, c.conf_dir)  # safety assert
  abspath = os.path.abspath(os.path.join(tempfile.gettempdir(), tempfile.gettempprefix() + 'alternate.icc'))
  c.update({ c.k_icc_path: abspath })
  eq_(abspath, c.icc_path)


@with_setup(setup_cleandir)
def test_icc_relpath():
  c = Config(conf_dir=tmp_confdir)
  eq_(tmp_confdir, c.conf_dir)  # safety assert
  relpath = os.path.join('my_icc_profiles', '..', 'prof.icc')
  c.update({ c.k_icc_path: relpath })
  eq_(os.path.abspath(os.path.join(c.conf_dir, relpath)), c.icc_path)
