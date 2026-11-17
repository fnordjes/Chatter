#!/usr/bin/env python3

import json, sys

file_name = sys.argv[1]
with open(file_name, encoding='utf-8') as fp:
    data = json.load(fp)
print(json.dumps(data, indent=4, ensure_ascii=False))
