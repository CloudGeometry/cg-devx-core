import hashlib
import re
from pathlib import Path
from zipfile import ZipFile

import requests

# loading the temp.zip and creating a zip object
from cli.common.const.const import LOCAL_FOLDER


class DependencyManager:
    tf_version = "1.3.9"
    tf_mac_i_url = f'https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_darwin_amd64.zip'
    tf_mac_as_url = f'https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_darwin_arm64.zip'
    tf_windows_url = f'https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_windows_amd64.zip'
    tf_linux_url = f'https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_linux_amd64.zip'
    tf_sha = f'https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_SHA256SUMS'
    tf_sha_sig = f'https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_SHA256SUMS.sig'

    kctl_version = "v1.27.4"
    kctl_mac_i_url = f'https://dl.k8s.io/release/{kctl_version}/bin/darwin/amd64/kubectl'
    kctl_mac_as_url = f'https://dl.k8s.io/release/{kctl_version}/bin/darwin/arm64/kubectl'
    kctl_windows_url = f'https://dl.k8s.io/release/{kctl_version}/bin/windows/amd64/kubectl.exe'
    kctl_linux_url = f'https://dl.k8s.io/release/{kctl_version}/bin/linux/amd64/kubectl'
    kctl_sha_prefix = "sha256"

    def _get_filename_from_content_description(self, cd):
        """
        Get filename from content-disposition
        """
        if not cd:
            return None
        file_name = re.findall('filename=(.+)', cd)
        if len(file_name) == 0:
            return None
        return file_name[0]

    def _download_file(self, url: str):
        """
        Download file from url
        """
        r = requests.get(url, allow_redirects=True)
        filename = self._get_filename_from_content_description(r.headers.get('content-disposition'))
        open(filename, 'wb').write(r.content)

    def _unzip_file(self, path: str):
        """
        Unzip file/folder from path
        """
        with ZipFile(Path().home() / LOCAL_FOLDER / "", 'r') as zObject:
            zObject.extractall(
                path=Path().home() / LOCAL_FOLDER / "")

    def _validate_checksum(self, file: str, checksum: str):
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
