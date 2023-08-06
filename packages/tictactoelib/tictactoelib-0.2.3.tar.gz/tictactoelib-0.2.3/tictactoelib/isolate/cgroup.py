import os

from tempfile import mkdtemp
from contextlib import contextmanager


class limit_ram:
    """Provides name of initialized cgroup with necessary memory limit"""
    def __init__(self, memlimit, cgroup, cgroup_path):
        self.memlimit = memlimit
        self.cgroup_path = cgroup_path
        self.cgroup = cgroup

    def __enter__(self):
        if self.memlimit is None:
            return
        memdir = os.path.join(self.cgroup_path, "memory", self.cgroup)
        self.tempdir = mkdtemp(dir=memdir)
        lbytes = os.path.join(self.tempdir, "memory.limit_in_bytes")
        with open(lbytes, 'w') as f:
            f.write(str(self.memlimit))
        return "memory:%s%s" % (self.cgroup, self.tempdir.replace(memdir, ''))

    def __exit__(self, exc_type, exc_value, traceback):
        if self.memlimit is None:
            return
        os.rmdir(self.tempdir)
