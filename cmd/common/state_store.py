"""Global parameter store."""
import os
from pathlib import Path

import yaml

from cmd.common.const.const import STATE_INPUT_PARAMS, LOCAL_FOLDER, STATE_CHECKPOINTS
from cmd.common.const.parameter_names import CLOUD_PROVIDER, GIT_PROVIDER, DNS_REGISTRAR
from cmd.common.enums.cloud_providers import CloudProviders
from cmd.common.enums.dns_registrars import DnsRegistrars
from cmd.common.enums.git_providers import GitProviders


class StateStore:
    __store: dict = {}

    def __init__(self, input_params={}):
        self.__store[STATE_INPUT_PARAMS] = input_params
        self.__store[STATE_CHECKPOINTS] = []

    @property
    def cloud_provider(self) -> CloudProviders:
        return self.__store[STATE_INPUT_PARAMS][CLOUD_PROVIDER]

    @property
    def git_provider(self) -> GitProviders:
        return self.__store[STATE_INPUT_PARAMS][GIT_PROVIDER]

    @property
    def dns_registrar(self) -> DnsRegistrars:
        return self.__store[STATE_INPUT_PARAMS][DNS_REGISTRAR]

    @dns_registrar.setter
    def dns_registrar(self, value):
        self.__store[STATE_INPUT_PARAMS][DNS_REGISTRAR] = value

    @classmethod
    def get_input_param(self, key):
        if key in self.__store[STATE_INPUT_PARAMS]:
            return self.__store[STATE_INPUT_PARAMS].get(key)
        else:
            return None

    @classmethod
    def update_input_params(self, input_params: dict):
        self.__store[STATE_INPUT_PARAMS].update(input_params)

    @classmethod
    def validate_input_params(self, validator):
        return validator(self)

    @classmethod
    def set_checkpoint(self, name: str):
        self.__store[STATE_CHECKPOINTS].push(name)

    @classmethod
    def save_checkpoint(self):
        file_path = Path().home() / LOCAL_FOLDER / "state.yaml"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w+") as outfile:
            yaml.dump(self.__store, outfile, default_flow_style=False)


def param_validator(paras: StateStore) -> bool:
    return True
