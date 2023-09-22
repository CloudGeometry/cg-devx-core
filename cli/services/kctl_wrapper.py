import subprocess
from pathlib import Path

import yaml

from cli.common.const.const import LOCAL_FOLDER


class KctlWrapper:
    @staticmethod
    def __kubectl_command_builder(basic_command: str, resource=None, name=None, container_name=None,
                                  namespace=None, flags=None, with_definition=False):

        kctl_executable = str(Path().home() / LOCAL_FOLDER / "tools" / "kubectl")
        command = [kctl_executable, basic_command]
        if resource:
            command.append(resource)
        if name:
            command.append(name)
        if container_name:
            command.extend(['-c', container_name])
        if namespace:
            command.extend(['--namespace', namespace])
        if flags:
            command.extend(flags)
        if with_definition:
            command.extend(['-f', '-'])
        return command

    @staticmethod
    def __run_command(command, *args, **kwargs):
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(yaml.dump(kwargs).encode())
        proc.stdin.close()
        if proc.wait() != 0:
            raise Exception(stderr)

    def run(self, command: str, *args, **kwargs):
        command = self.__kubectl_command_builder(command, *args, **kwargs)
        self.__run_command(command, *args, **kwargs)

    def create(self, definition, namespace=None):
        command = self.__kubectl_command_builder('create', namespace=namespace, with_definition=True)
        self.__run_command(command, definition)

    def apply(self, definition, namespace=None):
        command = self.__kubectl_command_builder('apply', namespace=namespace, flags=['--record'], with_definition=True)
        self.__run_command(command, definition)
