import subprocess
import sys

import yaml

from cli.common.const.common_path import LOCAL_KCTL_TOOL


class KctlWrapper:

    def __init__(self, kctl_config_path: str, kctl_executable_path: str = None):
        self._kctl_config_path = kctl_config_path
        if kctl_executable_path is None:
            self._kctl_executable = str(LOCAL_KCTL_TOOL)
        else:
            self._kctl_executable = kctl_executable_path

    def __kubectl_command_builder(self, basic_command: str, resource=None, name=None, container_name=None,
                                  namespace=None, flags=None, with_definition=False):

        command = [self._kctl_executable, '--kubeconfig', self._kctl_config_path, basic_command]
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

    def get(self, kind, name=None, namespace=None):
        command = self.__kubectl_command_builder('get', resource=kind, name=name, namespace=namespace,
                                                 flags=['-o', 'yaml'])
        get_process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=sys.stderr)
        objects = yaml.safe_load(get_process.stdout)
        if get_process.wait() != 0:
            raise Exception
        return objects
