from pathlib import Path

from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from cli.common.const.const import LOCAL_FOLDER


class KeyManager:
    """Cryptographic key management wrapper to standardise key management."""

    @staticmethod
    def create_rsa_keys(key_name: str = "cgdevx-rsa"):
        """
        Create keypair
        :return:
            """

        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048
        )

        pk = KeyManager._process_key(key, key_name)

        return pk

    @staticmethod
    def create_ed_keys(key_name: str = "cgdevx-rsa"):
        """
        Create keypair
        :return:
            """

        key = Ed25519PrivateKey.generate()

        pk = KeyManager._process_key(key, key_name)

        return pk

    @staticmethod
    def _process_key(key, key_name):
        private_key = key.private_bytes(
            encoding=crypto_serialization.Encoding.PEM,
            format=crypto_serialization.PrivateFormat.PKCS8,
            encryption_algorithm=crypto_serialization.NoEncryption()
        )
        public_key = key.public_key().public_bytes(
            encoding=crypto_serialization.Encoding.OpenSSH,
            format=crypto_serialization.PublicFormat.OpenSSH
        )
        with open(Path().home() / LOCAL_FOLDER / f'{key_name}.pem', "w") as private_key_file:
            private_key_file.write(private_key.decode())
        pk = public_key.decode()
        with open(Path().home() / LOCAL_FOLDER / f'{key_name}.pub', "w") as public_key_file:
            public_key_file.write(pk)
        return pk
