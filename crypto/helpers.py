import base64
from binascii import unhexlify
from os import urandom

from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256
from Crypto.Protocol.KDF import bcrypt, bcrypt_check
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util import Padding


class Cryptography:
    """
    Set of Cryptography helpers. Composed by:
     * Server's Passphrase getters and setters
     * Symmetric ciphering and deciphering (AES256)
     * Signing and Verification
     * Hashing (SHA3-256, BCrypt)
    """

    __passphrase = ""

    @staticmethod
    def set_passphrase(passphrase):
        """
        Method to define the Server's passphrase

        :param passphrase: Passphrase to be stored as the Server's one
        """

        Cryptography.__passphrase = passphrase

    @staticmethod
    def get_passphrase():
        """
        Method to fetch the server's passphrase

        :return: Server's passphrase
        """

        return Cryptography.__passphrase

    @staticmethod
    def cipher(key, data):
        """
        Method to cipher a given piece of data

        :param key: Key used in the symmetric cipher
        :param data: Data to be ciphered
        :return: Ciphered data
        """

        iv = Cryptography.random_bytes(16)
        key_bytes = str.encode(key)
        data_bytes = str.encode(data)
        cipher = AES.new(key_bytes, AES.MODE_GCM, iv)
        padded_data = Padding.pad(data_bytes, 16, style='pkcs7')
        ciphertext = cipher.encrypt(padded_data)
        return base64.b64encode(iv), base64.b64encode(ciphertext)

    @staticmethod
    def decipher(key, ciphertext, iv):
        """
        Method to decipher a given ciphertext

        :param key: Key used in the symmetric cipher
        :param ciphertext: Ciphertext to be deciphered
        :param iv: IV used in this cipher
        :return: Deciphered data
        """

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
    def sign(key, data):
        """
        Method to sign a give piece of data

        :param key: Private key used to sign the data
        :param data: Data to be signed
        :return: Signature
        """

        private_key = RSA.import_key(key)
        signer = PKCS1_v1_5.new(private_key)
        return signer.sign(Cryptography.hash(data))

    @staticmethod
    def verify_signature(key, data, signed_data):
        """
        Method to verify a given signature

        :param key: Public key used to verify the signature
        :param data: Data that was signed
        :param signed_data: Signature that needs to be verified
        :return: True if the signature is valid, false otherwise
        """

        cert = RSA.import_key(key)
        verifier = PKCS1_v1_5.new(cert.public_key())
        return verifier.verify(Cryptography.hash(data), signed_data)

    @staticmethod
    def random_bytes(length):
        """
        Method to generate n random bytes

        :param length: Number of bytes to be generated
        :return: Array of random bytes with the length requested
        """
        return urandom(length)

    @staticmethod
    def hash(data):
        """
        Method to hash (SHA3_256)

        :param data: Data to be hashed
        :return: Hash of the data
        """
        digest = SHA3_256.new()
        digest.update(data.encode())
        return digest

    @staticmethod
    def verify_sha3_256(data, hash):
        """
        Method to compare verify if a given data results in a given hash (SHA3_256)

        :param data: Data that will be computed
        :param hash: Hash to be compared
        :return: True if the data results in the given hash, false otherwise
        """

        digest = SHA3_256.new()
        digest.update(data.encode())
        return base64.b64encode(digest.digest()) == hash

    @staticmethod
    def hash_data(data):
        """
        Method to perform a BCrypt of the data

        :param data: Data to be hashed
        :return: BCrypt of the data
        """

        first_hash = SHA3_256.new()
        first_hash.update(str.encode(data))
        encoded = base64.b64encode(first_hash.digest())
        return bcrypt(encoded, 12, Cryptography.random_bytes(16))

    @staticmethod
    def verify_hash(value, stored_hash):
        """
        Method to compare a give piece of data with an hash (BCrypt)

        :param value: Data to be compared
        :param stored_hash: BCrypt to be compared
        :return: True if the data results in the give BCrypt, false otherwise
        """

        first_hash = SHA3_256.new()
        first_hash.update(str.encode(value))
        test_hash = base64.b64encode(first_hash.digest())
        try:
            byte_hash = unhexlify(stored_hash).decode('ascii')
            bcrypt_check(test_hash, byte_hash)
            return True
        except ValueError:
            return False
