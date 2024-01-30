import hashlib
import os.path
import platform
import re
import shutil
import stat
from zipfile import ZipFile

import requests

from common.const.common_path import LOCAL_TOOLS_FOLDER, LOCAL_TF_TOOL, LOCAL_KCTL_TOOL
from common.const.const import KUBECTL_VERSION, TERRAFORM_VERSION
from common.tracing_decorator import trace
from services.tf_wrapper import TfWrapper


class DependencyManager:
    tf_base_path = f'https://releases.hashicorp.com/terraform/{TERRAFORM_VERSION}/'
    tf_mac_i_url = f'terraform_{TERRAFORM_VERSION}_darwin_amd64.zip'
    tf_mac_as_url = f'terraform_{TERRAFORM_VERSION}_darwin_arm64.zip'
    tf_windows_url = f'terraform_{TERRAFORM_VERSION}_windows_amd64.zip'
    tf_linux_url = f'terraform_{TERRAFORM_VERSION}_linux_amd64.zip'
    tf_sha = f'terraform_{TERRAFORM_VERSION}_SHA256SUMS'
    tf_sha_sig = f'terraform_{TERRAFORM_VERSION}_SHA256SUMS.sig'

    kctl_version = f'v{KUBECTL_VERSION}'
    kctl_mac_i_url = f'https://dl.k8s.io/release/{kctl_version}/bin/darwin/amd64/kubectl'
    kctl_mac_as_url = f'https://dl.k8s.io/release/{kctl_version}/bin/darwin/arm64/kubectl'
    kctl_windows_url = f'https://dl.k8s.io/release/{kctl_version}/bin/windows/amd64/kubectl.exe'
    kctl_linux_url = f'https://dl.k8s.io/release/{kctl_version}/bin/linux/amd64/kubectl'
    kctl_sha_prefix = ".sha256"

    # Regular expression matches a line containing a hexadecimal hash, spaces, and a filename
    r = re.compile(r'(^[0-9A-Fa-f]+)\s+(\S.*)$')

    @staticmethod
    def _get_filename_from_content_description(cd):
        """
        Get filename from content-disposition
        """
        if not cd:
            return None
        file_name = re.findall('filename=(.+)', cd)
        if len(file_name) == 0:
            return None
        return file_name[0]

    @staticmethod
    def _download_file(url: str, path: str = ""):
        """
        Download file from url
        """
        r = requests.get(url, allow_redirects=True)
        with open(path, 'wb') as df:
            df.write(r.content)
        return path

    @staticmethod
    def _unzip_file(file: str, path: str):
        """
        Unzip file/folder from path
        """
        with ZipFile(file, 'r') as z_file:
            z_file.extractall(path=path)

    @staticmethod
    def _validate_checksum(file: str, checksum: str):
        """
        Validate file checksum
        """
        sha256_hash = hashlib.sha256()
        with open(file, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

            file_checksum = sha256_hash.hexdigest()

            if file_checksum == checksum:
                # OK
                return True
            else:
                # BAD CHECKSUM
                return False

    @staticmethod
    @trace()
    def check_tf():
        if os.path.exists(LOCAL_TF_TOOL):
            tf = TfWrapper()
            if tf.version() == TERRAFORM_VERSION:
                return True

        return False

    @staticmethod
    @trace()
    def check_kubectl():
        # TODO: extract and check kubectl version
        if os.path.exists(LOCAL_KCTL_TOOL):
            return True
        else:
            return False

    @trace()
    def install_tf(self):
        tmp_folder = self._prepare_temp_folder()

        file_name = None
        if platform.system() == "Darwin":
            if platform.machine() == "x86_64":
                file_name = self.tf_mac_i_url
            if platform.machine() == "arm64":
                file_name = self.tf_mac_as_url
        if platform.system() == "Windows":
            file_name = self.tf_windows_url
        if platform.system() == "Linux":
            file_name = self.tf_linux_url

        download_url = self.tf_base_path + file_name

        tf_file_path = self._download_file(download_url, tmp_folder / file_name)
        sha_file_path = self._download_file(self.tf_base_path + self.tf_sha, tmp_folder / self.tf_sha)
        checksum = self._extract_sha(sha_file_path, file_name)

        if not self._validate_checksum(tf_file_path, checksum):
            raise Exception("Bad checksum")

        self._unzip_file(file=tf_file_path, path=LOCAL_TOOLS_FOLDER)

        self._change_permissions(LOCAL_TF_TOOL)

        shutil.rmtree(tmp_folder)

        return str(LOCAL_TF_TOOL)

    def _extract_sha(self, sha_file_path, file_name):
        checksum = None
        with open(sha_file_path) as sf:
            for line in sf:
                m = self.r.match(line)
                if m:
                    checksum = m.group(1)
                    filename = m.group(2)
                    if filename == file_name:
                        break
        return checksum

    @trace()
    def install_kubectl(self):
        tmp_folder = self._prepare_temp_folder()
        download_url = None
        file_name = "kubectl"
        if platform.system() == "Darwin":
            if platform.machine() == "x86_64":
                download_url = self.kctl_mac_i_url
            if platform.machine() == "arm64":
                download_url = self.kctl_mac_as_url
        if platform.system() == "Windows":
            download_url = self.kctl_windows_url
            file_name = "kubectl.exe"
        if platform.system() == "Linux":
            download_url = self.kctl_linux_url

        kctl_file_path = self._download_file(download_url, tmp_folder / file_name)

        sha_file_path = self._download_file(download_url + self.kctl_sha_prefix,
                                            tmp_folder / f'{file_name}{self.kctl_sha_prefix}')
        with open(sha_file_path) as sf:
            checksum = sf.readline()

        if not self._validate_checksum(kctl_file_path, checksum):
            raise Exception("Bad checksum")

        shutil.move(kctl_file_path, LOCAL_KCTL_TOOL)

        self._change_permissions(LOCAL_KCTL_TOOL)

        shutil.rmtree(tmp_folder)

        return str(LOCAL_KCTL_TOOL)

    @staticmethod
    def _change_permissions(path):
        st = os.stat(path)
        os.chmod(path,
                 st.st_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    @staticmethod
    def _prepare_temp_folder():
        tmp_folder = LOCAL_TOOLS_FOLDER / ".tmp"
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)
        os.makedirs(tmp_folder)
        return tmp_folder
