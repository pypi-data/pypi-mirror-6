# -*- coding: utf8 -*-

import hashlib

from .base58 import b58encode


def decode(asm_hash):

    if len(asm_hash.split()) == 1:
        key = asm_hash[len(asm_hash) - 66:]
    else:
        key = asm_hash.split()[1]

    sha = hashlib.sha256(key.decode("hex")).digest()
    ripe160 = hashlib.new('ripemd160')
    ripe160.update(sha)

    d = ripe160.digest()
    address = ('\x32' + d)
    checksum = hashlib.sha256(hashlib.sha256(address).digest()).digest()[:4]
    address += checksum
    encoded_address = b58encode(address)

    return encoded_address
