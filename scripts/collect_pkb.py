#! /usr/bin/python3

# Script for collecting results from PerfKitBenchmarker
import os
import json

results = []

if __name__ == '__main__':
    for root, dirs, files in os.walk("../perfkitbenchmarker", topdown=False):
        for name in files:
            if '.json' in name:
                filename = os.path.join(root, name)
                #print filename
                with open(filename, 'r') as fh:
                    for line in fh:    
                        r = json.loads(line)
                        #print r
                        results.append(r)

    print(json.dumps(results))
    json.dump(results, open('pkb_results.json', 'w'))

    import pandas as pd
    pd.DataFrame(results).to_csv('pkb_results.csv', index=False, encoding='utf-8')
