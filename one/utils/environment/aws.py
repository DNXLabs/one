import docker.utils
from os import path, getenv

from one.utils.config import get_workspace_value
from one.utils.parse_env import parse_env
from one.docker.container import Container
from one.docker.image import Image
from one.utils.environment import Environment
from .common import get_cli_root


class EnvironmentAws(Environment):
    def __init__(self):
        super().__init__()
        self.env_auth = {}
        self.env_assume = {}
        self.env_workspace = {}
        self.workspace = ''

    def build(self, workspace, force=False):
        if path.exists(get_cli_root() + '/credentials'):
            self.env_auth = docker.utils.parse_env_file(get_cli_root() + '/credentials')
        else:
            print('Please login before proceeding')
            raise SystemExit

        if workspace is not None and self.workspace == workspace and not force:
            return self

        self.workspace = workspace or getenv('WORKSPACE')
        print('Setting workspace to %s' % (self.workspace))

        aws_account_id = getenv('AWS_ACCOUNT_ID') or get_workspace_value(self.workspace, 'aws-account-id')
        aws_role = getenv('AWS_ROLE') or get_workspace_value(self.workspace, 'aws-role')
        aws_assume_role = get_workspace_value(self.workspace, 'aws-assume-role', 'false')

        self.env_workspace = {
            'TF_VAR_aws_role': aws_role,
            'TF_VAR_aws_account_id': aws_account_id,
            'WORKSPACE': self.workspace
        }

        if aws_assume_role.lower() == 'true':
            self.aws_assume_role(role=aws_role, account_id=aws_account_id)

        return self

    def aws_assume_role(self, role, account_id):
        print('Assuming role %s at %s' % (role, account_id))
        container = Container()
        image = Image()

        AWS_IMAGE = image.get_image('aws')
        envs = {
            'AWS_ROLE': role,
            'AWS_ACCOUNT_ID': account_id,
        }
        envs.update(self.env_auth)

        command = 'assume-role.sh'
        output = container.create(
            image=AWS_IMAGE,
            entrypoint='/bin/bash -c',
            command=command,
            volumes=['.:/work'],
            environment=envs,
            tty=False, stdin_open=False
        )

        self.env_assume = parse_env('\n'.join(output.splitlines()))
        return self.env_assume

    def get_env(self):
        return {**self.env_auth, **self.env_assume, **self.env_workspace}
