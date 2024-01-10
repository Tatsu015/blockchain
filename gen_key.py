from ecdsa import SigningKey, SECP256k1, VerifyingKey

secret_key = SigningKey.generate(curve=SECP256k1)
print("secret key:", secret_key.to_string().hex())
public_key = secret_key.verifying_key
print("public key:", public_key.to_string().hex())
