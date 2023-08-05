# import logging
import os
import sys
import time
import unittest

is_py3 = sys.version_info[0] > 2
# logging.basicConfig(level=logging.DEBUG)

if is_py3:
    from collections.abc import Iterable, MappingView
else:
    from collections import Iterable, MappingView

import ticktock


class TestDictMethods(unittest.TestCase):

    shelves = [{'maxsize': 4, 'timeout': None}, {'maxsize': None, 'timeout':
               1}, {'maxsize': 4, 'timeout': 1}]

    def delete_cache_files(self):
        if os.path.exists('test_cache'):
            os.remove('test_cache')
        if os.path.exists('test_cache.db'):
            os.remove('test_cache.db')

    tearDown = delete_cache_files

    def test_classes(self):
        for shelf in self.shelves:
            obj = ticktock.open('test_cache', maxsize=shelf['maxsize'],
                                timeout=shelf['timeout'])
            self.basic_access_methods(obj)
            obj.clear()
            obj.close()
            self.delete_cache_files()
            obj = ticktock.open('test_cache', maxsize=shelf['maxsize'],
                                timeout=shelf['timeout'])
            self.advanced_access_methods(obj)
            obj.clear()
            obj.close()
            self.delete_cache_files()
            obj = ticktock.open('test_cache', maxsize=shelf['maxsize'],
                                timeout=shelf['timeout'])
            self.iter_view_methods(obj)
            obj.clear()
            obj.close()
            self.delete_cache_files()
            if shelf['maxsize'] is not None:
                obj = ticktock.open('test_cache', maxsize=shelf['maxsize'],
                                    timeout=shelf['timeout'])
                self.lru_methods(obj)
                obj.clear()
                obj.close()
                self.delete_cache_files()
            if shelf['timeout'] is not None:
                obj = ticktock.open('test_cache', maxsize=shelf['maxsize'],
                                    timeout=shelf['timeout'])
                self.timeout_methods(obj)
                obj.clear()
                obj.close()
                self.delete_cache_files()
            if shelf['maxsize'] is not None and shelf['timeout'] is not None:
                obj = ticktock.open('test_cache', maxsize=shelf['maxsize'],
                                    timeout=shelf['timeout'])
                self.lru_timeout_methods(obj)
                obj.clear()
                obj.close()
                self.delete_cache_files()

    def basic_access_methods(self, obj):
        """Tests __setitem__, __getitem__, __delitem___, __contains__,
        and __len__.

        """
        obj['a'] = 1
        self.assertTrue('a' in obj)
        self.assertEqual(obj['a'], 1)
        self.assertEqual(len(obj), 1)
        del obj['a']
        self.assertFalse('a' in obj)
        self.assertRaises(KeyError, obj.__getitem__, 'a')
        self.assertEqual(len(obj), 0)

    def advanced_access_methods(self, obj):
        """Tests get(), setdefault(), update(), pop(), popitem(), and
        clear().

        """
        self.assertEqual(obj.get('a', 'blah'), 'blah')
        self.assertEqual(obj.setdefault('a', 'blah'), 'blah')
        obj.update({'b': 2, 'c': 3, 'd': 4})
        self.assertEqual(obj.get('b'), 2)
        self.assertEqual(len(obj), 4)
        self.assertEqual(obj.pop('a'), 'blah')
        self.assertRaises(KeyError, obj.pop, 'a')
        self.assertEqual(type(obj.popitem()), tuple)
        self.assertEqual(len(obj), 2)
        obj.clear()
        self.assertEqual(len(obj), 0)

    def iter_view_methods(self, obj):
        self.assertTrue(isinstance(obj.__iter__(), Iterable))
        self.assertTrue(isinstance(obj.items(),
                        MappingView if is_py3 else list))
        self.assertTrue(isinstance(obj.keys(),
                        MappingView if is_py3 else list))
        self.assertTrue(isinstance(obj.values(),
                        MappingView if is_py3 else list))
        if not is_py3:
            self.assertTrue(isinstance(obj.iteritems(), Iterable))
            self.assertTrue(isinstance(obj.iterkeys(), Iterable))
            self.assertTrue(isinstance(obj.itervalues(), Iterable))

    def lru_methods(self, obj):
        self.assertTrue(hasattr(obj, 'maxsize'))
        self.assertTrue(hasattr(obj, '_queue'))
        obj['a'] = 1
        obj['b'] = 2
        obj['c'] = 3
        self.assertEqual(list(obj._queue), ['a', 'b', 'c'])
        obj._remove_add_key('b')
        self.assertEqual(list(obj._queue), ['a', 'c', 'b'])
        obj._remove_add_key('a')
        self.assertEqual(list(obj._queue), ['c', 'b', 'a'])
        obj.clear()
        obj['a'] = 1
        obj['b'] = 2
        obj.maxsize = 3
        obj.update({'c': 3, 'd': 4})
        self.assertEqual(len(obj), 3)
        obj['a'] = 1
        self.assertEqual(len(obj), len(obj._queue))
        del obj['a']
        self.assertEqual(len(obj), len(obj._queue))

    def timeout_methods(self, obj):
        self.assertTrue(obj._INDEX not in obj)
        self.assertRaises(TypeError, obj.__setitem__, obj._INDEX, 'blah')
        self.assertRaises(KeyError, obj.__delitem__, obj._INDEX)
        self.assertTrue(obj._INDEX not in list(obj.keys()))
        self.assertTrue(obj._INDEX not in repr(obj))
        self.assertEqual(len(obj), 0)

        obj.set('bar', ord, 'c')
        self.assertEqual(obj['bar'], ord('c'))

        obj.settimeout('foo', 'value', 1)
        self.assertEqual(obj['foo'], 'value')
        time.sleep(1)
        self.assertRaises(KeyError, obj.__getitem__, 'foo')
        self.assertEqual(obj.get('foo', 'blah'), 'blah')
        obj.default_timeout = 1
        obj['foo'] = 'value'
        self.assertEqual(obj['foo'], 'value')
        time.sleep(1)
        self.assertRaises(KeyError, obj.__getitem__, 'foo')

    def lru_timeout_methods(self, obj):
        obj.maxsize = 3
        obj.default_timeout = 1
        obj['a'], obj['b'] = 1, 2
        self.assertEqual((obj['a'], obj['b']), (1, 2))
        time.sleep(1)
        self.assertRaises(KeyError, obj.__getitem__, 'b')
        obj.default_timeout = 0
        obj['a'], obj['b'], obj['c'] = 1, 2, 3
        self.assertEqual(len(obj), 3)
        obj['d'] = 4
        self.assertEqual(len(obj), 3)
        self.assertRaises(KeyError, obj.__getitem__, 'a')


if __name__ == '__main__':
    unittest.main()
