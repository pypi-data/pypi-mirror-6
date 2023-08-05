import _hydra
from helpers import KeyGenerator

def test__hydra():
    # This test will probably fail on big-endian machines
    h1 = _hydra.hash('foo')
    h2 = _hydra.hash('foo', h1)
    3630293751, 986047357 == h1, h2

def test_collisions():
    keygen = KeyGenerator()
    hashes = {}
    for i, key in enumerate(keygen.randomKeys()):
        hcode = _hydra.hash(key)
        if hcode not in hashes:
            hashes[hcode] = key
        else:
            raise RuntimeError, "Hash collision!: %s %s" % (key, hashes[hcode])
