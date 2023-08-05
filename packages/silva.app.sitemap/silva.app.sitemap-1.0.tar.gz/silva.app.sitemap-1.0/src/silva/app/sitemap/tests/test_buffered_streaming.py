# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from random import randint
from ..views import BufferedGeneratorStream


class BufferedStreamingTest(unittest.TestCase):

    def test_data_smaller_than_buf_size(self):
        gen = iter(['abcd'])

        streamer = BufferedGeneratorStream(gen, size=100)
        self.assertEquals(['abcd'], list(streamer))

    def test_data_bigger_tan_buf_size(self):
        """ each item is bigger that buf size so each item is passed through.
        """
        gen = iter(['a'*20 for i in range(10)])
        streamer = BufferedGeneratorStream(gen, size=10)
        self.assertEquals(['a'*20 for i in range(10)], list(streamer))

    def test_big_stream(self):
        data = ['ab' * randint(100, 150) for i in range(1000)]
        gen = iter(data)
        streamer = BufferedGeneratorStream(gen, size=4*1024)
        self.assertEquals("".join(streamer),
                          "".join(data))

    def test_data_is_multiple_of_buf_size(self):
        data = ['ab' * 1024 for i in range(100)]
        gen = iter(data)
        streamer = BufferedGeneratorStream(gen, size=2048)
        chunks = list(streamer)
        self.assertEquals(100, len(chunks))
        self.assertEquals(data, chunks)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BufferedStreamingTest))
    return suite
