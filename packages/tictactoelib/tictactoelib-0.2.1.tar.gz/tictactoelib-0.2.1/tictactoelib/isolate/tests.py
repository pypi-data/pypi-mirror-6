import os
import subprocess
from unittest import TestCase, skipUnless

from . import limit_ram


@skipUnless(os.path.isdir('/sys/fs/cgroup/memory/tictactoe'), 'no cgroups')
class CGroupTestCase(TestCase):
    def test_oom(self):
        """1024 bytes is not enough to initialize /bin/sh"""
        with limit_ram(1024, 'tictactoe', '/sys/fs/cgroup') as cg:
            cgdir = '/sys/fs/cgroup/%s' % cg.replace(':', '/')
            cg = ['cgexec', '-g', cg, '/bin/sh', '-c', 'exit 2']
            self.assertEqual(-11, subprocess.call(cg))
            self.assertTrue(os.path.isdir(cgdir))
        self.assertFalse(os.path.isdir(cgdir))

    def test_memory_ok(self):
        """1MB is enough to initialize /bin/sh"""
        with limit_ram(1 << 30, 'tictactoe', '/sys/fs/cgroup') as cg:
            cgdir = '/sys/fs/cgroup/%s' % cg.replace(':', '/')
            cg = ['cgexec', '-g', cg, '/bin/sh', '-c', 'exit 2']
            self.assertEqual(2, subprocess.call(cg))
            self.assertTrue(os.path.isdir(cgdir))
        self.assertFalse(os.path.isdir(cgdir))

    def test_cleanup_on_exc(self):
        try:
            with limit_ram(1 << 20, 'tictactoe', '/sys/fs/cgroup') as cg:
                cgdir = '/sys/fs/cgroup/%s' % cg.replace(':', '/')
                raise Exception("bac")
        except Exception:
            self.assertFalse(os.path.isdir(cgdir))
