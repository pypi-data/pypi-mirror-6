# signer

```python
from signer import Signer
from datetime import datetime, timedelta

signer = Signer(b'secret key')

tomorrow = datetime.utcnow() + timedelta(days=1)
signed_message = signer.sign(b'message', expires=tomorrow)

signer.verify(signed_message)
```

* signed message is not encrypted
* if the signature failed the verification, verify() returns `None`
* if expired, verfiy() returns `None`

signing as json and tuple

```python
signer.sign_json(dict(key="value"))

signer.sign_record(['some', b'msg'], expires=tomorrow)

signer.sign(obj, encoder=encode_fn)
signer.verify(signed_bytes, decoder=decode_fn)
```

specify hash method

```python
Signer(method='sha1', digest_size=20)
```
