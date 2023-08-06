"""Helper classes for handling X.509 certificate files."""

from binascii import a2b_base64
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import MD2, MD4, MD5, SHA, SHA256
from Crypto.PublicKey import RSA
from Crypto.Util import asn1, number

from pyasn1.codec.ber import encoder, decoder

_BEGIN_STR = '-----BEGIN '
_END_STR = '-----END '
_OID_RSA_MD2 = (1, 2, 840, 113549, 1, 1, 2)
_OID_RSA_MD4 = (1, 2, 840, 113549, 1, 1, 3)
_OID_RSA_MD5 = (1, 2, 840, 113549, 1, 1, 4)
_OID_RSA_SHA1 = (1, 2, 840, 113549, 1, 1, 5)
_OID_RSA_SHA256 = (1, 2, 840, 113549, 1, 1, 11)


class X509SignatureAlgorithmUnsupported(Exception):
    """Exception indicating that the requested X.509 signature algorithm
    isn't supported."""       


class Certificate:
    """Represents an X.509 certificate with all data."""

    def __init__(self, pubkey, certdata, signature, algo):
        """Initialize the certificate structure.

        Args:
        pubkey: RSA public key contained in the certificate.
        certdata:
        signature: Signature which was placed on the certificate.
        algo:
        """
        self._pubkey = pubkey
        self._certdata = certdata
        self._signature = signature
        self._algo = algo

    def get_pub_key(self):
        """Returns the public key of the certificate.

        Returns:
        RSA key object containing the private key.
        """
        return self._pubkey

    def check_signature(self, cacert):
        """Verifies that the certificate is signed by cacert.

        Args:
        cacert: Certificate object which is suspected to be the parent
        of this one in the trust chain.

        Returns:
        True if this certificate was signed by cacert, false
        otherwise.
        """

        cakey = cacert.get_pub_key()
        cahash = None

        if self._algo == _OID_RSA_SHA1:
            cahash = SHA.new(self._certdata)
        elif self._algo == _OID_RSA_MD4:
            cahash = MD4.new(self._certdata)
        elif self._algo == _OID_RSA_MD2:
            cahash = MD2.new(self._certdata)
        elif self._algo == _OID_RSA_MD5:
            cahash = MD5.new(self._certdata)
        elif self._algo == _OID_RSA_SHA256:
            cahash = SHA256.new(self._certdata)
        else:
            raise X509SignatureAlgorithmUnsupported(
                "No algorithm known for " + self._algo)

        verifier = PKCS1_v1_5.new(cakey)
        return verifier.verify(cahash, self._signature)


class FileFormatException(Exception):
    """There was a problem with the format of the file."""


def bitstring_to_bytes(bitstring):
    """Converts one of those ASN.1 bitstrings to bytes.

    Args:
    bitstring: ASN.1 bitstring encoded as a sequence of bits.

    Returns:
    Binary representation of the bitstring as bytes.
    """
    bits = list(bitstring) + [0] * ((8 - len(bitstring) % 8) % 8)
    bytes = []
    for i in range(0, len(bits), 8):
        bytes.append(chr(int(''.join(str(b) for b in bits[i:i + 8]), 2)))

    return ''.join(bytes)


def parse_certificate(indata):
    """Parse the PEM or DER encoded X.509 certificate in indata.

    Args:
    indata: a string you want to be parsed as a X.509 certificate.
    Can be PEM encoded or plain DER.

    Returns:
    Certificate class describing the actual contents of the
    certificate.
    """
    cert = None
    data = indata.splitlines()
    isbase64 = False

    for line in data:
        if line.startswith(_BEGIN_STR):
            isbase64 = True

    if isbase64:
        data = indata.splitlines()
        b64data = ''
        end = False

        while len(data) and not data[0].startswith(_BEGIN_STR):
            data = data[1:]

        if not data[0].startswith(_BEGIN_STR):
            raise FileFormatException('Unable to find ' + _BEGIN_STR)

        # Now skip the BEGIN CERTIFICATE line.
        # TODO(tonnerre): perhaps add a sanity check on what exactly
        # begins here.
        data = data[1:]

        for i in range(len(data)):
            if data[i].startswith(_END_STR):
                end = True
                break

            b64data += data[i]

        if not end:
            raise FileFormatException('Unable to find ' + _END_STR)

        der = a2b_base64(b64data)

        cert = decoder.decode(der)
    else:
        cert = decoder.decode(indata)

    # If we end up here, we managed to read the certificate.
    certdata = cert[0]

    keydata = bitstring_to_bytes(certdata[0][6][1])
    pubkey = RSA.importKey(keydata)

    sigalgo = certdata[1][0].asTuple()

    sigdata = bitstring_to_bytes(certdata[2])

    return Certificate(pubkey, encoder.encode(certdata[0]), sigdata, sigalgo)

def parse_certificate_file(path):
    """Parse the PEM or DER encoded X.509 certificate file "path".

    Args:
    path: path to a file containing the X.509 certificate.
    Can be PEM encoded or plain DER.

    Returns:
    Certificate class describing the actual contents of the
    certificate.
    """
    f = open(path, "r")
    ret = parse_certificate(f.read())
    f.close()
    return ret
