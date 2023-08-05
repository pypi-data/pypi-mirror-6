from _hydra import *
from hydra import WritingBloomFilter, ReadingBloomFilter, murmur_hash
import linecache
from os.path import join, dirname
from helpers import KeyGenerator

BENCH_SPEC = BloomCalculations.computeBloomSpec2(15, 0.1)

def test_compute_spec():
    bs1 = BloomCalculations.computeBloomSpec1(12)
    bs2 = BloomCalculations.computeBloomSpec2(12, 0.0032)
    bs3 = BloomCalculations.computeBloomSpec1(10)

    assert bs1 == bs2
    assert bs1 <> bs3
    assert bs2 <> bs3



class TestFilter:
    def testManyRandom(self):
        keygen = KeyGenerator()
        MAX_HASH_COUNT = 128
        bloom = WritingBloomFilter(15, 0.0009)
        hashes = set()
        collisions = 0
        for key in keygen.randomKeys():
            for i, hashIndex in enumerate(bloom.getHashBuckets(key, MAX_HASH_COUNT, 1024 * 1024)):
                hashes.add(hashIndex)
            collisions += MAX_HASH_COUNT - len(hashes)
            hashes.clear()
        assert collisions <= 100, "Got %d collisions." % collisions


class TestBloomFilter(object):
    ELEMENTS = 10000
    MAX_FAILURE_RATE = 0.1

    def setup(self):
        self.bf = WritingBloomFilter(self.ELEMENTS, self.MAX_FAILURE_RATE)

    def _testFalsePositives(self, filter, keys, otherkeys):
        fp = 0

        assert len(keys) == len(otherkeys)

        for key in keys:
            filter.add(key)

        for key in otherkeys:
            if filter.contains(key):
                fp += 1 

        bucketsPerElement = BloomFilter._maxBucketsPerElement(self.ELEMENTS)
        spec = BloomCalculations.computeBloomSpec2(bucketsPerElement, self.MAX_FAILURE_RATE)

        fp_ratio = fp / (len(keys) * BloomCalculations.PROBS[spec.bucketsPerElement][spec.K]) * 100
        assert fp_ratio < 103, "Over 103% of the maximum expected false positives found. %0.3f%%" % fp_ratoi
        print "OK: Got %0.3f%% of the expected false positives " % fp_ratio

        # False negatives never occur - this should always work
        for k in keys:
            assert filter.contains(k)


    def testBloomLimits1(slef):
        maxBuckets = len(BloomCalculations.PROBS) - 1
        maxK = len(BloomCalculations.PROBS[maxBuckets]) - 1

        # possible
        BloomCalculations.computeBloomSpec2(maxBuckets, BloomCalculations.PROBS[maxBuckets][maxK])

        # impossible, throws
        try:
            BloomCalculations.computeBloomSpec2(maxBuckets, BloomCalculations.PROBS[maxBuckets][maxK] / 2)
            raise RuntimeError
        except UnsupportedOperationException, ue:
            pass

    def test_one(self):
        self.bf.add("a")
        self.bf.contains("a")
        assert not self.bf.contains("b")

    def testFalsePositivesInt(self):
        keygen = KeyGenerator()
        self._testFalsePositives(self.bf, [str(x) for x in xrange(10000)], keygen.randomKeys(10000))

    def testFalsePositivesRandom(self):
        keygen1 = KeyGenerator(314159)
        self._testFalsePositives(self.bf, 
                [keygen1.random_string() for i in range(10000)],
                [keygen1.random_string() for i in range(10000)],)

    def testWords(self):
        keygen1 = KeyGenerator()
        bf = WritingBloomFilter(len(keygen1)/2, self.MAX_FAILURE_RATE, ignore_case=False)

        even_keys = keygen1[::2]
        odd_keys = keygen1[1::2]
        self._testFalsePositives(bf, even_keys, odd_keys)

class TestHugeBloom():
    ELEMENTS = 250000000
    MAX_FAILURE_RATE = 0.001

    def setup(self):
        self.bf = WritingBloomFilter(self.ELEMENTS, self.MAX_FAILURE_RATE)

    def test_one(self):
        self.bf.add("a")
        assert self.bf.contains("a")
        assert not self.bf.contains("b")

def test_murmur():
    # Just make sure we can run the hash function from pure python
    print murmur_hash('food')

def test_unicrap():
    filter = WritingBloomFilter(100000, 0.1)
    assert not u'\u2019' in filter
    assert not u'\u2018' in filter

    filter.add(u'\u2018')
    filter.add(u'\u2019')

    filter.add('just a plain string')

    assert u'\u2019' in filter
    assert u'\u2018' in filter
    assert 'just a plain string' in filter
