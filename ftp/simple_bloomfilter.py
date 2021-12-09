import mmh3
import redis


class BloomFilter(object):
    def __init__(self, bf_key, bit_size=2000000, hash_count=4, start_seed=41, **redis_kwargs):
        self.bit_size = bit_size
        self.hash_count = hash_count
        self.start_seed = start_seed
        self.client = redis.Redis(**redis_kwargs)
        self.bf_key = bf_key

    def add(self, data):
        bit_points = self._get_hash_points(data)
        for index in bit_points:
            self.client.setbit(self.bf_key, index, 1)

    def madd(self, m_data):
        if isinstance(m_data, list):
            for data in m_data:
                self.add(data)
        else:
            self.add(m_data)

    def exists(self, data):
        bit_points = self._get_hash_points(data)
        result = [
            self.client.getbit(self.bf_key, index) for index in bit_points
        ]
        return all(result)

    def mexists(self, m_data):
        result = {}
        if isinstance(m_data, list):
            for data in m_data:
                result[data] = self.exists(data)
        else:
            result[m_data] = self.exists[m_data]
        return result

    def _get_hash_points(self, data):
        return [
            mmh3.hash(data, index) % self.bit_size
            for index in range(self.start_seed, self.start_seed +
                               self.hash_count)
        ]
