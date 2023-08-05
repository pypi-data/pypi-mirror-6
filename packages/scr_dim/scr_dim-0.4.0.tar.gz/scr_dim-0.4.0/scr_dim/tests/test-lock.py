from nose.tools import *
import os
import tempfile
from scr_dim.ProcLock import ProcLock

# safe lockfile path for test
tmp_lockfile = os.path.join(tempfile.gettempdir(), tempfile.gettempprefix() + 'scr_dim_test')


@raises(Exception)
def test_inprocess_lock():
  try:
    a = ProcLock(tmp_lockfile)
    b = ProcLock(tmp_lockfile)
  except Exception as e:
    a.release()
    raise e


@raises(Exception)
def test_inprocess_lock_with():
  with ProcLock(tmp_lockfile):
    a = ProcLock(tmp_lockfile)


def test_can_lock_once():
  with ProcLock(tmp_lockfile):
    pass


def test_release_explicit():
  a = ProcLock(tmp_lockfile)
  a.release()
  with ProcLock(tmp_lockfile):
    pass


def test_release_with():
  with ProcLock(tmp_lockfile):
    pass
  with ProcLock(tmp_lockfile):
    pass
