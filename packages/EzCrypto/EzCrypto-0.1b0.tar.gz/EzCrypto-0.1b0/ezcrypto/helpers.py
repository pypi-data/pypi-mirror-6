"""
EZCrypto CipherText module
"""

import json
import base64
from itertools import izip_longest

class ChunkSet(object):

    def __init__(self):
        self.__chunks = []

    def __len__(self):
        return self.chunk_count()

    def __str__(self):
        return self.join()

    def get_chunks(self):
        return self.__chunks

    def get_chunks_as_base64(self):
        return [base64.encodestring(chunk) for chunk in self.get_chunks()]

    def encode_as_base64(self):
        return base64.encodestring(json.dumps(self.get_chunks_as_base64()))

    def chunk_count(self):
        return len(self.__chunks)

    def set_chunks(self, iterable):
        self.__chunks = [element for element in iterable]

    def set_chunks_from_base64(self, iterable):
        chunks = [base64.decodestring(element) for element in iterable]
        self.set_chunks(chunks)

    def decode_from_base64(self, text):
        base64_chunks = json.loads(base64.decodestring(text))
        self.set_chunks_from_base64(base64_chunks)

    def add_chunk(self, chunk):
        self.__chunks.append(chunk)

    def join(self, padvalue=''):
        return padvalue.join(self.get_chunks())

    def clear(self):
        self.__chunks = [] 



class FixedSizeChunkSet(ChunkSet):

    def __init__(self, text='', size=128):
        self.size = size
        super(FixedSizeChunkSet, self).__init__()
        if len(text)>0:
            chunks = FixedSizeChunkSet.grouper(self.size, text)
            self.set_chunks(chunks)

    @staticmethod
    def grouper(n, iterable, padvalue=''):
        groups = izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)
        return [''.join(g) for g in groups]


class PlainText(FixedSizeChunkSet):
    
    def encrypt(self, encryption_callable):
        result = CipherText()
        for chunk in self.get_chunks():
            result.add_chunk(encryption_callable(chunk))
        return result


class CipherText(ChunkSet):

    def decrypt(self, decryption_callable, join=True):
        result = ChunkSet()
        for chunk in self.get_chunks():
            result.add_chunk(decryption_callable(chunk))
        if join:
            return result.join()
        else:
            return result
