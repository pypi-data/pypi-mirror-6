# basic_crypto

Wrapper around PyCrypto providing basic symmetric key encryption with AES in CFB mode.

Plaintext is raw bytes(str in python 2.X or bytes in python 3.X). If it's actual text you're transmitting, ensure you encode/decode as necessary.

Includes four functions:

`generate_salt()`

Generates random data for use as salt.

`derive_key(password, salt)`

Returns the encryption/decryption key for the given password and salt, using the standard Password-Based Key Derivation Function 2.
The password should be secret and preshared, the salt should be preshared too but need not be secret, and can be transmitted for example insecurely at the beginning of communication.

`encrypt(plaintext, key)`

Encrypts plaintext using the Advanced Encryption Standard in cipher feedback mode (AES CFB). Uses a random initialisation vector each time it is called, which is prepended to the ciphertext.


`decrypt(ciphertext, key)`

Decrypts the ciphertext using the Advanced Encryption Standard in cipher feedback mode (AES CFB), using a key as returned by derive_key. Uses the initialisation vector prepended to the ciphertext by `encrypt()`. 

( 
[view on pypi](https://pypi.python.org/pypi/basic_crypto/);
[view on Bitbucket](https://bitbucket.org/cbillington/basic_crypto)
)

   * Install `python setup.py install`.

