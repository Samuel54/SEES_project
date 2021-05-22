import base64
from binascii import unhexlify
from os import urandom, path

from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256
from Crypto.Protocol.KDF import bcrypt, bcrypt_check
from Crypto.PublicKey import ECC, RSA
from Crypto.Util import Padding


class Cryptography:

    __passphrase = ""

    @staticmethod
    def set_passphrase(passphrase):
        Cryptography.__passphrase = passphrase

    @staticmethod
    def get_passphrase():
        return Cryptography.__passphrase

    @staticmethod
    def cipher(key, data):
        iv = Cryptography.random_bytes(16)
        key_bytes = str.encode(key)
        data_bytes = str.encode(data)
        cipher = AES.new(key_bytes, AES.MODE_GCM, iv)
        padded_data = Padding.pad(data_bytes, 16, style='pkcs7')
        ciphertext = cipher.encrypt(padded_data)
        return base64.b64encode(iv), base64.b64encode(ciphertext)

    @staticmethod
    def decipher(key, ciphertext, iv):
        decoded_iv = base64.decodebytes(iv)
        decoded_ciphertext = base64.decodebytes(ciphertext)
        key_bytes = str.encode(key)
        cipher = AES.new(key_bytes, AES.MODE_GCM, decoded_iv)
        data = cipher.decrypt(decoded_ciphertext)
        try:
            unpadded_data = Padding.unpad(data, 16, style='pkcs7')
        except ValueError:
            return None
        return unpadded_data

    @staticmethod
    def load_key(file):
        f = open(file, 'r')
        return RSA.import_key(f.read())

    @staticmethod
    def generate_key(filename, passphrase=None):
        key = ECC.generate(curve='P-256')
        if not path.isfile(filename):
            file = open(filename, 'wt')
            if passphrase is None:
                file.write(key.export_key(format='PEM'))
            else:
                file.write(key.export_key(format='PEM', passphrase=passphrase, use_pkcs8=True))
            file.close()
        return key

    @staticmethod
    def random_bytes(length):
        return urandom(length)

    @staticmethod
    def hash_data(data):
        first_hash = SHA3_256.new()
        first_hash.update(str.encode(data))
        encoded = base64.b64encode(first_hash.digest())
        return bcrypt(encoded, 12, Cryptography.random_bytes(16))

    @staticmethod
    def verify_hash(value, stored_hash):
        first_hash = SHA3_256.new()
        first_hash.update(str.encode(value))
        test_hash = base64.b64encode(first_hash.digest())
        try:
            byte_hash = unhexlify(stored_hash).decode('ascii')
            bcrypt_check(test_hash, byte_hash)
            return True
        except ValueError:
            return False
