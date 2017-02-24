import hashlib
import string
import random


class PasswordEncryption:

    ALGORITHM_MD5 = "md5"
    ALGORITHM_SHA1 = "sha1"
    ALGORITHM_SHA256 = "sha256"
    ALGORITHM_SHA512 = "sha512"
    ALGORITHM_CRYPT = "crypt"
    DEFAULT_VALIDATOR = r'[A-Za-z0-9]'    # letters and digits
    DOLLAR = "$"

    def __init__(self, min_length=6,  max_length=None, salt=None,
                 algorithm=ALGORITHM_SHA1, regex=DEFAULT_VALIDATOR, **kwargs):
        self.max_length = max_length
        self.min_length = min_length
        self.algorithm = algorithm.lower()
        self.salt = salt or self.__random_password()

    def __random_password(self, nchars=6):
        chars   = string.printable
        hash    = ''
        for char in range(nchars):
            rand_char = random.randrange(0, len(chars))
            hash += chars[rand_char]
        return hash

    def hexdigest(self, password):
        if self.algorithm == PasswordEncryption.ALGORITHM_CRYPT:
            try:
                import crypt
            except ImportError:
                self.error("crypt module not found in this system. Please use md5 or sha* algorithm")
            return crypt.crypt(password, self.salt)
        encoded_str = (self.salt + password).encode('utf-8')
        if self.algorithm == PasswordEncryption.ALGORITHM_SHA1:
            return hashlib.sha1(encoded_str).hexdigest()
        elif self.algorithm == PasswordEncryption.ALGORITHM_MD5:
            return hashlib.md5(encoded_str).hexdigest()
        elif self.algorithm == PasswordEncryption.ALGORITHM_SHA256:
            return hashlib.sha256(encoded_str).hexdigest()
        elif self.algorithm == PasswordEncryption.ALGORITHM_SHA512:
            return hashlib.sha512(encoded_str).hexdigest()
        raise ValueError('Unsupported hash type %s' % self.algorithm)

    def get_password(self, password):
        encoded_password =  self.hexdigest(password)
        return '%s$%s$%s' % (self.algorithm, self.salt, encoded_password)

    def validate(self, password, password_str):
        try:
            (self.algorithm, self.salt, encoded_password) = password_str.split(PasswordEncryption.DOLLAR)
            return encoded_password == self.hexdigest(password)
        except ValueError:
            return False

