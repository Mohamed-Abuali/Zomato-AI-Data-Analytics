"""
Generate an RSA key pair for Snowflake key-pair authentication.
Produces:
  - rsa_key.p8   (private key, PKCS8, unencrypted)
  - rsa_key.pub  (public key, PEM)
  - Prints the single-line public key to paste into Snowflake.
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Private key -> PKCS8 PEM (unencrypted)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
with open("rsa_key.p8", "wb") as f:
    f.write(private_pem)

# Public key -> PEM
public_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
with open("rsa_key.pub", "wb") as f:
    f.write(public_pem)

# Extract the single-line body for the Snowflake ALTER USER command
public_pem_str = public_pem.decode()
body = (
    public_pem_str
    .replace("-----BEGIN PUBLIC KEY-----", "")
    .replace("-----END PUBLIC KEY-----", "")
    .replace("\n", "")
    .strip()
)

print("Files created: rsa_key.p8, rsa_key.pub\n")
print("Run this SQL in Snowflake (replace <YOUR_USER>):\n")
print(f"ALTER USER <YOUR_USER> SET RSA_PUBLIC_KEY='{body}';")
