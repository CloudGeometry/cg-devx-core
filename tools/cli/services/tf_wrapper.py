import json
import os

from python_terraform import Terraform, IsNotFlagged

from common.const.common_path import LOCAL_TF_TOOL


class TfWrapper:

    def __init__(self, working_dir: str = None):
        if os.path.exists(LOCAL_TF_TOOL):
            self._tf = Terraform(terraform_bin_path=str(LOCAL_TF_TOOL),
                                 working_dir=working_dir,
                                 is_env_vars_included=True)
        else:
            raise Exception("No tf executable found")

    def change_working_dir(self, working_dir: str):
        self._tf.working_dir = working_dir

    def version(self):
        return_code, stdout, stderr = self._tf.version("-json")
        output = json.loads(stdout)
        if return_code != 0:
            raise Exception("tf executable failure", return_code, stderr)
        return output["terraform_version"]

    def init(self):
        return_code, stdout, stderr = self._tf.init()

        if return_code != 0:
            raise Exception("tf executable failure", return_code, stderr)

        return True

    def apply(self, variables: dict = None):
        self._tf.variables = variables

        # TODO: set capture_output=False and rewire tf logs
        return_code, stdout, stderr = self._tf.apply(skip_plan=True, input=False)

        if return_code != 0:
            raise Exception("tf executable failure", return_code, stderr)

        return True

    def output(self):
        output = {}
        tf_output = self._tf.output()
        for k, v in tf_output.items():
            output[k] = v["value"]
        return output

    def destroy(self):
        return_code, stdout, stderr = self._tf.destroy(force=IsNotFlagged, auto_approve=True, input=False)

        if return_code != 0:
            raise Exception("tf executable failure", return_code, stderr)

        return True
