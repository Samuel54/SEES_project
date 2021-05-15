#!/usr/bin/env python
import random
import hashlib
import sys
import os
import os.path
import pyaes
import chilkat
import binascii
import hmac


def unlock():
    """(CkPython) Global Unlock -> https://www.example-code.com/python/global_unlock.asp"""
    glob = chilkat.CkGlobal()
    success = glob.UnlockBundle("Anything for 30-day trial")
    if (success != True):
        print(glob.lastErrorText())
        sys.exit()

    status = glob.get_UnlockStatus()
    if (status == 2):
        print("\nUnlocked using purchased unlock code.")
    else:
        print("\nUnlocked in trial mode.")
    # The LastErrorText can be examined in the success case to see if it was unlocked in
    # trial more, or with a purchased unlock code.
    # print(glob.lastErrorText())


def get_rsa_public_key(cert_file_name):
    """Lê a chave pública RSA a partir de um certificado x509
    Mostra também os campos de interesse do certificado"""
    cert = chilkat.CkCert()
    success = cert.LoadFromFile(cert_file_name)
    if (success != True):
        print(cert.lastErrorText())
        sys.exit()

    print("SubjectDN:" + cert.subjectDN())
    print("\nCommon Name:" + cert.subjectCN())
    print("\nIssuer Common Name:" + cert.issuerCN())
    print("\nSerial Number:" + cert.serialNumber())

    public_key = cert.ExportPublicKey()
    return public_key


def send_message(self, message, count):
    """Envia uma mensagem através do socket"""
    self.sendall(message)
    count += 1
    return count


def receive_message(self, count):
    """Recebe uma mensagem através do socket"""
    message = self.recv(2048)
    count += 1
    return (message, count)


def key_derivation(num, master_key):
    """Deriva chaves a partir de uma chave mestra"""
    master_key = str(master_key)
    count = str(num)
    key = master_key + count
    key = hashlib.sha256(key.encode('latin-1')).hexdigest()
    return key


def loaddsaparameters(file_name):
    """Importa os paramtros DSA a partir de um ficheiro .txt ou .pem"""
    from asn1crypto.keys import DSAParams
    os.system("openssl dsaparam -outform DER -in" + " " + file_name + " " + " -out parameters.der")

    with open("parameters.der", "rb") as f:
        certs = f.read()
    params = DSAParams.load(certs)
    p = params['p']
    g = params['g']
    q = params['q']
    return (p, q, g)


def DH_public_param():
    """Gera o parâmetro público DH a enviar à outra parte na 'troca de chaves'."""
    p, q, g = loaddsaparameters('DSA_params.txt')
    x = random.randint(10, int(q))
    Y = pow(int(g), x, int(p))
    return Y, x


def DH_simetric_key_gen(x, other_part_public_param):
    """Calcula uma chave simetrica com base no parametro DH público da outra parte"""
    p, q, g = loaddsaparameters('DSA_params.txt')
    key = pow(other_part_public_param, x, int(p))
    key = hashlib.sha256(str(key).encode('latin-1')).hexdigest()
    return key


def encrypt_message(key, iv, message):
    """Cifra uma mensagem com o AES"""
    aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
    ciphertext = aes.encrypt(message)
    return ciphertext


def decrypt_message(key, iv, message):
    """Decifra uma mensagem com o AES"""
    aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
    plaintext = aes.decrypt(message)
    return plaintext


def create_sha256_signature(key, message):
    """Retorna um MAC da mensagem recebida"""
    byte_key = binascii.unhexlify(key)
    message = message
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()


def sign_rsa_priv_key(fileName, message):
    """Produz uma assinatura RSA utilizado a chave privada lida a partir de um ficheiro .pem"""
    unlock()  # Desbloqueia alguns modulos do módulo CkPython

    pkey = chilkat.CkPrivateKey()
    # Load the private key from an RSA PEM file:
    pkey.LoadPemFile(fileName)

    # Get the private key in XML format:
    pkeyXml = pkey.getXml()

    rsa = chilkat.CkRsa()

    # Import the private key into the RSA component:
    success = rsa.ImportPrivateKey(pkeyXml)
    if (success != True):
        print(rsa.lastErrorText())
        sys.exit()

    rsa.put_EncodingMode("hex")
    rsa.put_LittleEndian(False)

    strData = message
    hexSignature = rsa.signStringENC(strData, "sha-1")

    return hexSignature


def verify_rsa_siganture(fileName, signature, test_message):
    """Verifica a assinatura RSA"""
    unlock()  # Desbloqueia alguns modulos do módulo CkPython
    cert = chilkat.CkCert()  # Carrega um certificadao digital x509 de um ficheiro .cer
    success = cert.LoadFromFile(fileName)
    if (success != True):
        print(cert.lastErrorText())
        sys.exit()

    public_key = cert.ExportPublicKey()

    # Now verify using a separate instance of the RSA object:
    rsa2 = chilkat.CkRsa()

    # Import the public key into the RSA object:
    success = rsa2.ImportPublicKey(public_key.getXml())
    if (success != True):
        print(rsa2.lastErrorText())
        sys.exit()

    rsa2.put_EncodingMode("hex")  # Encoding mode == hex

    # Verify the signature:
    strData = test_message
    hex_Signature = signature
    success = rsa2.VerifyStringENC(strData, "sha-1", hex_Signature)
    if (success != True):
        print(rsa2.lastErrorText())
        sys.exit()

    print("Success! The RSA signature is valid!!!")