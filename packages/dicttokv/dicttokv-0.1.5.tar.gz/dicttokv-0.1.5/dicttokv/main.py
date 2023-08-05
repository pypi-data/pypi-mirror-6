# coding: utf-8
from __future__ import unicode_literals, print_function
from itertools import izip


class DictToKeyValue(object):

    @classmethod
    def from_object(cls, target, prefixes=()):
        if isinstance(target, dict):
            for key, value in target.iteritems():
                for i in cls.from_object(value, prefixes + (key, )):
                    yield i

        elif isinstance(target, (list, tuple)):
            for index, value in enumerate(target):
                for i in cls.from_object(value, prefixes + (index, )):
                    yield i

        else:
            yield (prefixes, target)

    @classmethod
    def keys_to_keystr(cls, keys, delimiter='.', ignore_number=False):
        if ignore_number:
            keys = (unicode(key) for key in keys if not isinstance(key, int))
        else:
            keys = (unicode(key) for key in keys)
        return delimiter.join(keys)

    @classmethod
    def to_tsvlines(cls, target, delimiter='.', ignore_number=False):
        for keys, v in cls.from_object(target):
            yield '{}\t{}'.format(
                cls.keys_to_keystr(keys, delimiter, ignore_number), v)

    @classmethod
    def restore(cls, converted):
        def extend(target, key, value):
            if isinstance(target, dict):
                target[key] = value
            elif isinstance(target, list):
                target.insert(key, value)

        def create_path_setter(target_root, keys):
            s = target_root
            next_keys = keys[1:] + (None,)
            for key, next_key in izip(keys, next_keys):
                if next_key is None:
                    break
                if (
                    (isinstance(s, dict) and key not in s) or
                    (isinstance(s, list) and len(s) - 1 < key)
                ):
                    if isinstance(next_key, basestring):
                        extend(s, key, {})
                    else:
                        extend(s, key, [])
                s = s[key]
            return lambda v: extend(s, key, v)

        ret = []
        for keys, value in converted:
            keys_padded = (0,) + keys
            path_setter = create_path_setter(ret, keys_padded)
            path_setter(value)
        return ret[0]


if __name__ == '__main__':
    import sys
    import json
    obj = json.load(sys.stdin)
    for line in DictToKeyValue.to_tsvlines(obj):
        print(line)
