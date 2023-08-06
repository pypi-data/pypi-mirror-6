import hmac
import json
import struct
from datetime import datetime
from base64 import urlsafe_b64decode, urlsafe_b64encode


def json_decode(bs):
    return json.loads(bs.decode())


def json_encode(obj):
    return json.dumps(obj, separators=(',', ':')).encode()


def record_encode(record):
    return '\x1f'.join(record).encode()


def record_decode(bs):
    return bs.decode().split('\x1f')


def string_decode(bs):
    return bs.decode()


def string_encode(string):
    return string.encode()


def base64_encode(bs):
    return urlsafe_b64encode(bs).decode('ascii').strip('=')


def base64_decode(string):
    toomuch = len(string) % 4
    if toomuch:
        string = string + '=' * (4 - toomuch)
    return urlsafe_b64decode(string.encode('ascii'))


class Signer:

    def __init__(self, secret, method='sha256', digest_size=32,
                 epoch=1390000000):
        self.secret = secret
        self.method = method
        self.digest_size = digest_size
        self.epoch = epoch

    def get_signature(self, msg_bytes):
        return hmac.new(self.secret, msg_bytes, self.method).digest()

    def verify_signature(self, msg_bytes, signature):
        return hmac.compare_digest(signature, self.get_signature(msg_bytes))

    def sign(self, msg, expires=None, encoder=None):
        """returns base64 encoded string, '=' striped
        bytes structure before base64 encode
        - signature,
        - expiration, 4 bytes
        - message
        """
        if encoder:
            msg = encoder(msg)
        delta = b'\x00\x00\x00\x00'
        if expires is not None:
            delta = struct.pack('I', int(expires.timestamp() - self.epoch))
        signature = self.get_signature(delta + msg)
        return base64_encode(signature + delta + msg)

    def verify(self, raw, decoder=None):
        """loads from base64 encoded string,
        returns None if signature not valid or expired
        """
        bs = base64_decode(raw)
        signature = bs[:self.digest_size]
        delta = bs[self.digest_size: self.digest_size + 4]
        msg = bs[self.digest_size + 4:]
        if not self.verify_signature(delta + msg, signature):
            return None
        if delta != b'\x00\x00\x00\x00':
            expires = struct.unpack('I', delta)[0] + self.epoch
            if expires < datetime.utcnow().timestamp():
                return None
        return decoder(msg) if decoder else msg

    def verify_json(self, bs):
        return self.verify(bs, decoder=json_decode)

    def sign_json(self, obj, **kwargs):
        return self.sign(obj, encoder=json_encode, **kwargs)

    def verify_record(self, bs):
        return self.verify(bs, decoder=record_decode)

    def sign_record(self, obj, **kwargs):
        return self.sign(obj, encoder=record_encode, **kwargs)

    def verify_str(self, bs):
        return self.verify(bs, decoder=string_decode)

    def sign_str(self, obj, **kwargs):
        return self.sign(obj, encoder=string_encode, **kwargs)
