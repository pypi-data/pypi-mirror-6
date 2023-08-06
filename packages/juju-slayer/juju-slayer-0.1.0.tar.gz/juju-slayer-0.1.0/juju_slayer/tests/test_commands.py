import mock
import os
import tempfile
import unittest
import yaml

from juju_slayer.commands import (
    BaseCommand,
    Bootstrap,
    AddMachine,
    TerminateMachine,
    DestroyEnvironment)


from juju_slayer.provider import SSHKey, Instance
from juju_slayer.exceptions import ConfigError
from juju_slayer.tests.base import Base


class CommandBase(Base):

    def setUp(self):
        self.config = mock.MagicMock()
        self.provider = mock.MagicMock()
        self.env = mock.MagicMock()

    def setup_env(self, conf=None):
        self.provider.get_ssh_keys.return_value = [
            SSHKey({'id': 1, 'label': 'abc'})]
        self.config.series = "precise"
        with tempfile.NamedTemporaryFile(delete=False) as f:
            self.config.get_env_conf.return_value = f.name
            self.config.get_env_name.return_value = 'softlayer'
            if conf is None:
                conf = {
                    'environments': {
                        'softlayer': {
                            'type': 'null',
                            'bootstrap-host': None}}}
            f.write(yaml.safe_dump(conf))
            f.flush()
            self.addCleanup(lambda: os.remove(f.name))


class BaseCommandTest(CommandBase):

    def setUp(self):
        super(BaseCommandTest, self).setUp()
        self.cmd = BaseCommand(self.config, self.provider, self.env)

    def test_get_ssh_keys(self):
        self.provider.get_ssh_keys.return_value = [
            SSHKey({'id': 1, 'label': 'abc'}),
            SSHKey({'id': 32, 'label': 'bcd'})]
        self.assertEqual(
            self.cmd.get_slayer_ssh_keys(),
            [1, 32])

    def test_check_preconditions_okay(self):
        self.setup_env()
        self.assertEqual(self.cmd.check_preconditions(), [1])

    def test_check_preconditions_host_exist(self):
        self.setup_env({
            'environments': {
                'softlayer': {
                    'type': 'null',
                    'bootstrap-host': '1.1.1.1'}}})
        try:
            self.cmd.check_preconditions()
        except ConfigError, e:
            self.assertIn('already has a bootstrap-host', str(e))
        else:
            self.fail("existing bootstrap-host should raise error")

    def test_check_preconditions_host_invalid_provider(self):
        self.setup_env({
            'environments': {
                'softlayer': {
                    'type': 'ec2',
                    'bootstrap-host': None}}})
        try:
            self.cmd.check_preconditions()
        except ConfigError, e:
            self.assertIn("provider type is 'ec2' must be 'null'", str(e))

    def test_check_preconditions_host_invalid_env_conf(self):
        self.setup_env({'a': 1})
        try:
            self.cmd.check_preconditions()
        except ConfigError, e:
            self.assertIn('Invalid environments.yaml', str(e))

    def test_check_preconditions_no_named_env(self):
        self.setup_env({'environments': {}})
        try:
            self.cmd.check_preconditions()
        except ConfigError, e:
            self.assertIn(
                "Environment 'softlayer' not in environments.yaml", str(e))


class BootstrapTest(CommandBase):

    def setUp(self):
        super(BootstrapTest, self).setUp()
        self.cmd = Bootstrap(self.config, self.provider, self.env)

    @mock.patch('juju_slayer.ops.ssh')
    def test_bootstrap(self, mock_ssh):
        self.setup_env()
        self.env.is_running.return_value = False
        self.config.series = "precise"

        mock_ssh.check_ssh.return_value = True
        mock_ssh.update_instance.return_value = True

        self.provider.get_instance.return_value = Instance(dict(
            id=2121,
            hostname='slayer-13290123j13',
            primaryIpAddress="10.0.2.1"))
        self.cmd.run()

        mock_ssh.check_ssh.assert_called_once_with('10.0.2.1')
        mock_ssh.update_instance.assert_called_once_with('10.0.2.1')
    # TODO
    # test existing named host / ie precondition check for live env
    # test for jenv bootstrap (also in test_environment.py)


class AddMachineTest(CommandBase):

    def setUp(self):
        super(AddMachineTest, self).setUp()
        self.cmd = AddMachine(self.config, self.provider, self.env)

    def test_add_machine(self):
        self.setup_env()
        self.cmd.run()


class TerminateMachineTest(CommandBase):

    def setUp(self):
        super(TerminateMachineTest, self).setUp()
        self.cmd = TerminateMachine(self.config, self.provider, self.env)

    def test_terminate_machine(self):
        self.setup_env()
        self.env.status.return_value = {
            'machines': {
                '1': {
                    'dns-name': '10.0.1.23',
                    'instance-id': 'manual:ip_address'}
            }}
        self.provider.get_instances.return_value = [
            Instance(dict(
                id=221, hostname="slayer-123123",
                primaryIpAddress="10.0.1.23")),
            Instance(dict(
                id=258, hostname="slayer-209123",
                primaryIpAddress="10.0.1.103"))]
        self.config.options.machines = ["1"]
        self.cmd.run()
        self.provider.terminate_instance.assert_called_once_with(221)


class DestroyEnvironmentTest(CommandBase):

    def setUp(self):
        super(DestroyEnvironmentTest, self).setUp()
        self.cmd = DestroyEnvironment(self.config, self.provider, self.env)

    @mock.patch('juju_slayer.commands.time')
    def test_destroy_environment(self, mock_time):
        self.setup_env()
        self.env.status.return_value = {
            'machines': {
                '0': {
                    'dns-name': '10.0.1.23',
                    'instance-id': 'manual:ip_address'},
                '1': {
                    'dns-name': '10.0.1.25',
                    'instance-id': 'manual:ip_address'}
            }}
        self.provider.get_instances.return_value = [
            Instance(dict(
                id=221, hostname="slayer-123123",
                primaryIpAddress="10.0.1.23")),
            Instance(dict(
                id=258, hostname="slayer-209123",
                primaryIpAddress="10.0.1.25"))]

        # Destroy Env has a sleep / mock it out.
        mock_time.sleep.return_value = None
        self.cmd.run()
        self.assertEqual(
            self.provider.terminate_instance.call_args_list,
            [mock.call(258), mock.call(221)])
        self.env.terminate_machines.assert_called_once_with(['1'])

if __name__ == '__main__':
    unittest.main()
