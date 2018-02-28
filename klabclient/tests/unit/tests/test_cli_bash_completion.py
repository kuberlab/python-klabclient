
import klabclient.tests.unit.base_shell_test as base


class TestCLIBashCompletionV2(base.BaseShellTests):
    def test_bash_completion(self):
        bash_completion, stderr = self.shell('bash-completion')

        self.assertIn('bash-completion', bash_completion)
        self.assertFalse(stderr)
