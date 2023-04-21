#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import io
import json
import pickle

import rdbtools
import tnetstring


def read_rdb(rdbfile, key):
    """Returns the DB content for the key."""
    output = io.BytesIO()
    callback = rdbtools.JSONCallback(output, string_escape='raw')
    parser = rdbtools.RdbParser(callback, filters={'keys': '^' + key + '$'})
    parser.parse(rdbfile)
    return json.loads(output.getvalue())


def handle(x):
    """Convert to something that json can dump."""
    if isinstance(x, (bool, int, float, str)) or x is None:
        return x
    elif isinstance(x, bytes):
        return x.decode('latin-1')
    elif isinstance(x, list):
        return [handle(y) for y in x]
    elif isinstance(x, dict):
        return {handle(k): handle(v) for (k, v) in x.items()}
    raise ValueError('Unknown type: {}'.format(type(x)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('key')
    parser.add_argument('rdbfile')
    parser.add_argument('outfile')
    parser.add_argument('-t', '--tnetstring', action='store_true')
    args = parser.parse_args()

    data = read_rdb(args.rdbfile, args.key)
    assert set(data[0].keys()) == {args.key}
    data = data[0][args.key]
    print(f'Found {len(data)} records for key {args.key}')

    parsed = {}
    for key, value in data.items():
        value = pickle.loads(bytes(value, 'latin-1'))
        if args.tnetstring:
            parsed[key] = handle(tnetstring.loads(value))
        else:
            parsed[key] = handle(value)
    
    with open(args.outfile, 'w') as fout:
        json.dump(parsed, fout, indent=1)


if __name__ == '__main__':
    main()
