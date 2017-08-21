#!/usr/bin/env python

import subprocess
import sys
import os

# OTS_PATH = '/Users/USER/Documents/ots/ots-sanitize'
# OTS_PATH = '/Users/USER/src/github.com/khaledhosny/ots/ots-sanitize'
OTS_PATH = '/usr/local/bin/ots-sanitize'

def main(gf_path):
    results = []
    for p, i, files in os.walk(gf_path):
        for f in files:
            if f.endswith('.ttf'):
                try:
                    result = subprocess.check_output([OTS_PATH, os.path.join(p,f)])
                    results.append('%s\t%s' % (f, result))
                except subprocess.CalledProcessError as e:
                    result = '%s\t%s' % (f, e.output)
                    results.append(result)

                print '%s\t%s' % (f, result)
    with open('ots_gf_results.txt', 'w') as doc:
        doc.write(''.join(results))
    print 'done!'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'ERROR: Include path to OFL dir'
    else:
        main(sys.argv[-1])
