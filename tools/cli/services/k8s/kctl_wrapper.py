import subprocess

import yaml

from common.const.common_path import LOCAL_KCTL_TOOL
from common.tracing_decorator import trace


class KctlWrapper:

    def __init__(self, kctl_config_path: str, kctl_executable_path: str = None):
        self._kctl_config_path = kctl_config_path
        if kctl_executable_path is None:
            self._kctl_executable = str(LOCAL_KCTL_TOOL)
        else:
            self._kctl_executable = kctl_executable_path

    def __base_command(self, base_command=None, resource=None, container=None,
                       namespace=None, flags=None, cmd=None, with_definition=False):
        # kubectl[basic_command][RESOURCE_TYPE][NAME][flags]
        command = [self._kctl_executable, '--kubeconfig', self._kctl_config_path]
        if base_command:
            command.append(base_command)
        if resource:
            command.append(resource)
        if namespace:
            command += ['--namespace', namespace]
        if container:
            command += ['-c', container]
        if flags:
            command += flags
        if with_definition:
            command += ['-f', '-']
        return command

    @staticmethod
    def __run_command(command: [str], *args, **kwargs):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(yaml.dump(kwargs).encode())

        if proc.wait() != 0:
            raise Exception(stderr)
        return stdout.decode("utf-8")

    @trace()
    def run(self, command: str, *args, **kwargs):
        command = self.__base_command(command, *args, **kwargs)
        return self.__run_command(command, *args, **kwargs)

    @trace()
    def exec(self, pod: str, cmd: str, container: str = None, namespace: str = None, flags: [str] = None):
        # kubectl exec POD [-c CONTAINER] [-i] [-t] [flags] [-- COMMAND [args...]]
        command = self.__base_command(base_command="exec", resource=pod, namespace=namespace, container=container)

        command.append("-i")
        if flags:
            command += flags
        command += cmd.split(" ")

        return self.__run_command(command)
