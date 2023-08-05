"""
EZCrypto RSA module
"""

import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher.PKCS1_v1_5 import PKCS115_Cipher
from ezcrypto.helpers import PlainText
from ezcrypto.helpers import CipherText

class RSAKey(object):

    def __init__(self, pem):
        self._key = RSA.importKey(pem)

    @classmethod
    def __load_key_from_file(cls, path_to_key):
        fp = open(path_to_key, 'r')
        data = ''.join(fp.readlines())
        fp.close()
        return data

    @classmethod
    def __save_key_to_file(cls, path_to_key, data):
        fp = open(path_to_key, 'w+')
        fp.write(data)
        fp.close()

    def load_from_pem(cls, pem):
        self._key = RSA.importKey(pem)

    def export_as_pem(self):
        return self._key.exportKey('PEM')

    @classmethod
    def load_from_pem_file(cls, path_to_key):
        data = cls.__load_key_from_file(path_to_key)
        return cls(data)

    def save_to_pem_file(self, path_to_key):
        data = self.export_as_pem()
        self.__save_key_to_file(path_to_key, data)

    def export_as_der(self):
        return self._key.exportKey('DER')

    def export_as_openssh(self):
        return self._key.exportKey('OpenSSH')

    def encrypt(self, data):
        plaintext = PlainText(data, size=128)
        encryption_callable = lambda x: self._key.encrypt(x, '')[0]
        ciphertext = plaintext.encrypt(encryption_callable)
        return ciphertext

    def decrypt(self, ciphertext):
        decryption_callable = lambda x: self._key.decrypt(x)
        return ciphertext.decrypt(decryption_callable)

    def encrypt_as_base64(self, data):
        ciphertext = self.encrypt(data)
        return ciphertext.encode_as_base64()

    def decrypt_from_base64(self, data):
        ciphertext = CipherText()
        ciphertext.decode_from_base64(data)
        return self.decrypt(ciphertext)

    def get_hash(self, data):
        return str(hashlib.sha1(data).hexdigest())

    def verify(self, data, signature):
        return self._key.verify(data, (long(signature), None))

    def verify_after_hashing(self, data, signature):
        return self.verify(self.get_hash(data), signature)


class PublicKey(RSAKey):
    pass


class PrivateKey(RSAKey):

    @staticmethod
    def generate(size=1024):
        key = RSA.generate(size)
        return PrivateKey(key.exportKey('PEM'))

    def get_public_key(self):
        pem = self._key.publickey().exportKey('PEM')
        return PublicKey(pem)

    def sign(self, data):
        return str(self._key.sign(data, '')[0])

    def sign_after_hashing(self, data):
        return self.sign(self.get_hash(data))
