#!/usr/bin/env python3
# Standard Bitcoin Core rpcauth generator (used by exports.sh to mint the node's RPC
# password on first run). Prints the rpcauth line, then the generated password on the
# last line (exports.sh reads that with `tail -1`).
# Usage: rpcauth.py <username> [password]
import hmac
import os
import sys
from base64 import urlsafe_b64encode
from binascii import hexlify
from secrets import token_hex, token_urlsafe


def generate_salt(size):
    return token_hex(size)


def generate_password():
    return token_urlsafe(32)


def password_to_hmac(salt, password):
    m = hmac.new(salt.encode("utf-8"), password.encode("utf-8"), "SHA256")
    return m.hexdigest()


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Please include username as an argument.\n")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else generate_password()

    salt = generate_salt(16)
    password_hmac = password_to_hmac(salt, password)

    print(f"String to be appended to bitcoin.conf:")
    print(f"rpcauth={username}:{salt}${password_hmac}")
    print(f"Your password:\n{password}")


if __name__ == "__main__":
    main()
