import base64
import os
import re

__author__ = 'alex'

from M2Crypto import BIO, RSA, EVP, RC4, X509


def _cleanup_key(key):

    if isinstance(key, unicode):
        key = bytes(key)

    key = key.strip()
    key = re.sub('\s*[\r\n]+\s*', '\n', key)
    key = re.sub('^\s*$', '', key, re.MULTILINE)
    key = re.sub('\n+', '\n', key)
    key = re.sub('^\s+', '', key, re.MULTILINE)
    return key

def load_pem_private_key(privateKey):
#    bio =
#    return RSA.load_key_bio(BIO.MemoryBuffer(privateKey))
    return privateKey


def load_pem_public_key(publicKey):
    bio = BIO.MemoryBuffer(_cleanup_key(publicKey))
    return RSA.load_pub_key_bio(bio)

def load_pem_cert_public_key(cert):
    bio = BIO.MemoryBuffer(_cleanup_key(cert))
    return X509.load_cert_bio(bio).get_pubkey().get_rsa()

def ssl_sign(string, privateKey):
    signEvp = EVP.load_key_string(_cleanup_key(privateKey))
    signEvp.sign_init()
    signEvp.sign_update(string)
    return signEvp.sign_final()

def ssl_verify(sting, signature, pubkey):
    verifyEVP = EVP.PKey()
    verifyEVP.assign_rsa(pubkey)
    verifyEVP.verify_init()
    verifyEVP.verify_update(sting)
    return verifyEVP.verify_final(signature) == 1

def rsa_public2private_encrypt(data, publicKey):
    return publicKey.public_encrypt(data, RSA.pkcs1_padding)

def rsa_public2private_decrypt(data, privateKey):
    return RSA.load_key_bio(BIO.MemoryBuffer(privateKey)).private_decrypt(data, RSA.pkcs1_padding)

def rc4_encrypt(data, key):
    rc4 = RC4.RC4()
    rc4.set_key(key)
    return rc4.update(data) + rc4.final()

def rc4_decrypt(data, key):
    return rc4_encrypt(data, key) # second time encryption decrypts the data


def seal(string, pubkey):
    randomBytes = os.urandom(16)
    encryptedRC4Key = rsa_public2private_encrypt(randomBytes, pubkey)
    encryptedData =  rc4_encrypt(string, randomBytes)

    return base64.b64encode(encryptedData) + '@' + base64.b64encode(encryptedRC4Key)

def unseal(string, privateKey):
    randomBytes = os.urandom(16)

    (cipherText, cipherKey) = string.split('@')
    decryptedKey = rsa_public2private_decrypt(base64.b64decode(cipherKey), privateKey)
    decryptedData =  rc4_encrypt(base64.b64decode(cipherText), decryptedKey)

    return decryptedData