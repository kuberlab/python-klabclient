
import os
import sys

from oslotest import base
import six

from klabclient import shell


class BaseShellTests(base.BaseTestCase):

    def shell(self, argstr):
        orig = (sys.stdout, sys.stderr)
        clean_env = {}
        _old_env, os.environ = os.environ, clean_env.copy()

        try:
            sys.stdout = six.moves.cStringIO()
            sys.stderr = six.moves.cStringIO()
            _shell = shell.KuberlabShell()
            _shell.run(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(0, exc_value.code)
        finally:
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout, sys.stderr = orig
            os.environ = _old_env

        return stdout, stderr
