"""
    flask_user.tokens
    -----------------
    This module contains Flask-User functions that deal with generating and verifying tokens.

    Tokens contain an encoded user ID and a signature.
    The signature is managed by the itsdangerous module.

    :copyright: (c) 2013 by Ling Thio
    :author: Ling Thio (ling.thio@gmail.com)
    :license: Simplified BSD License, see LICENSE.txt for more details.
"""

import base64
from Crypto.Cipher import AES
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner

class TokenManager():
    def __init__(self, app_secret):
        """
        Create a cypher to encrypt IDs and a signer to sign tokens.
        """
        # Create cypher to encrypt IDs
        key = app_secret + '0123456789abcdef'  # ensure >=16 characters
        sixteen_byte_key = key[0:16]  # get first 16 characters
        self.cipher = AES.new(sixteen_byte_key)

        # Create signer to sign tokens
        self.signer = TimestampSigner(app_secret)

    def encrypt_id(self, id):
        """
        Encrypts integer ID to url-safe base64 string
        """
        str1 = '%016d' % id                             # --> 16 byte integer string
        str2 = self.cipher.encrypt(str1)                # --> encrypted data
        str3 = base64.urlsafe_b64encode(str2)           # --> URL safe base64 string with '=='
        return str3[0:-2]                               # --> base64 string without '=='

    def decrypt_id(self, encrypted_id):
        """
        Decrypts url-safe base64 string to integer ID
        """
        # In Python2, encrypted_id is <type 'str'> and needs to be converted to bytes
        if type(encrypted_id)=='str':
            encrypted_id = encrypted_id.encode('ascii')

        try:
            str3 = encrypted_id + b'=='             # --> base64 string with '=='
            str2 = base64.urlsafe_b64decode(str3)   # --> encrypted data
            str1 = self.cipher.decrypt(str2)        # --> 16 byte integer string
            return int(str1)                        # --> integer id
        except Exception as e:                      # pragma: no cover
            print('!!!Exception in decrypt_id!!!')
            return 0

    def generate_token(self, user_id):
        """
        Return token with user_id, timestamp and signature
        """
        return self.signer.sign(self.encrypt_id(user_id))

    def verify_token(self, token, expiration_in_seconds):
        """
        Verify token and return (is_valid, has_expired, user_id).

        Returns (True, False, user_id) on success.
        Returns (False, True, None) on expired tokens.
        Returns (False, False, None) on invalid tokens.
        """
        try:
            data = self.signer.unsign(token, max_age=expiration_in_seconds)
            is_valid = True
            has_expired = False
            user_id = self.decrypt_id(data)
        except SignatureExpired:
            is_valid = False
            has_expired = True
            user_id = None
        except BadSignature:
            is_valid = False
            has_expired = False
            user_id = None
        return (is_valid, has_expired, user_id)