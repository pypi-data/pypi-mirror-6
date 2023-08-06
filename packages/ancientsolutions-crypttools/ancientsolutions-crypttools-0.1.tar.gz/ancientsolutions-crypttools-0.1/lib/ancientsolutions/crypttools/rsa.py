"""Helper class for unwrapping PEM encoded DER RSA keys."""

from binascii import a2b_base64
from Crypto.Util.asn1 import DerSequence
from Crypto.PublicKey import RSA

from os.path import exists


class RSAKeyUnwrappingError(Exception):
    """Exception indicating an error with RSA key unwrapping."""

    def __init__(self, message="Unknown error"):
        """Creates a new exception with the given message."""
        self._message = message
        super(Exception).__init__(message)


class RSAKeyUnwrapper(object):
    """Unwrap a PEM encoded DER RSA key.

    Opens a file which contains a DER encoded RSA key in PEM format,
    parses the key and returns it as a Crypto.RSA key.
    """

    def __init__(self, path):
        """Reads the RSA key from the given path.

        The file must contain a PEM formatted DER encoded RSA key, the
        kind openssl rsa would produce.

        Args:
        path: Path to the file containing the RSA key.
        """
        if path is not None and exists(path):
            pemfile = open(path)
            if not pemfile:
                raise RSAKeyUnwrappingError("No such file: " + path)

            pem = pemfile.read()
            pemfile.close()
        else:
            pem = path

        lines = pem.replace(" ",'').split()

        if not lines:
            raise RSAKeyUnwrappingError("The file " + path + " was empty")

        der = a2b_base64(''.join(lines[1:-1]))

        # Extract subjectPublicKeyInfo field from X.509 certificate (see RFC3280)
        cert = DerSequence()
        cert.decode(der)
        tbsCertificate = DerSequence()
        tbsCertificate.decode(cert[0])
        subjectPublicKeyInfo = tbsCertificate[6]

        # Initialize RSA key
        self._rsa_key = RSA.importKey(subjectPublicKeyInfo)

    def rsa_key(self):
        """Return the extracted RSA private key."""
        return self._rsa_key


def UnwrapRSAKey(path):
    """Static function for unwrapping an RSA key in one go without an
    intermediate object.

    Args:
    path: path to a file containing the RSA private key.

    Returns:
    Crypto.RSA object containing the RSA key.
    """
    return RSAKeyUnwrapper(path).rsa_key()
