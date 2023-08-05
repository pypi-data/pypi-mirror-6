import os
import fcntl
import threading

class ProcLock(object):
  """ makes sure that no parallel execution occurs"""
  # in-process lock
  _cache_lock = threading.Lock()
  # list of acquired inter-process lockfile
  _cache = []

  def __init__(self, path):
    self.path = os.path.abspath(path)
    with self._cache_lock:
      if self.path in self._cache:
        raise Exception("cannot lock same file twice")
      self.fp = open(self.path, 'w')
      fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
      self._cache.append(self.path)

  def __enter__(self):
    return self

  def release(self):
    """releases lock. safe to call multiple times"""
    with self._cache_lock:
      if not self.path in self._cache:
        return
      os.remove(self.path)
      fcntl.lockf(self.fp, fcntl.LOCK_UN)
      self.fp.close()
      self._cache.remove(self.path)

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.release()

  def __del__(self):
    self.release()
