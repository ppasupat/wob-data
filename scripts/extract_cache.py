#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import gzip
import io
import json
import os


def parse_header(x):
    return dict((k.lower(), v) for (k, v) in x)


def decompress(x):
    stream = io.BytesIO(x)
    with gzip.GzipFile(fileobj=stream) as fin:
        return fin.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('outdir')
    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    elif not os.path.isdir(args.outdir) or os.listdir(args.outdir):
        print('Error: {} exists and is not empty'.format(args.outdir))
        exit(1)

    opener = gzip.open if args.infile.endswith('.gz') else open
    with opener(args.infile) as fin:
        data = json.load(fin)
    print('Loaded {} entries'.format(len(data)))

    extracted = []
    for entry in data.values():
        if 'cert' in entry['server_conn']:
            del entry['server_conn']['cert']
        # Read request
        req = entry['request']
        url = req['scheme'] + '://' + req['host'] + req['path']
        method = req['method']
        # Read response
        res = entry['response']
        response_header = parse_header(res['headers'])
        content_type = response_header.get('content-type', 'None')
        response_content = res['content'].encode('latin-1')
        if response_header.get('content-encoding') == 'gzip':
            response_content = decompress(response_content)
        del res['content']
        extracted.append((
            (url, method, content_type),
            entry, response_content,
        ))
    extracted.sort(key=lambda x: x[0])

    with open(os.path.join(args.outdir, 'index.tsv'), 'w') as fout:
        for i, (metadata, entry, response_content) in enumerate(extracted):
            filename = '{:04d}'.format(i)
            print('{}\t{}\t{}'.format(
                filename, '\t'.join(metadata), len(response_content)),
                file=fout)
            print('Writing {}: {}'.format(filename, metadata))
            with open(os.path.join(args.outdir, filename + '.entry'), 'w') as fent:
                print(json.dumps(entry, indent=1), file=fent)
            with open(os.path.join(args.outdir, filename + '.response'), 'wb') as fres:
                fres.write(response_content)


if __name__ == '__main__':
    main()

