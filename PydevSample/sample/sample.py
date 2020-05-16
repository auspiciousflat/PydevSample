import re

path = '../resource/sample.txt'

with open(path, encoding='utf-8') as f:
    print(type(f))
    s = f.read()
    print(s)
    
    repatter = re.compile('a+')
    result = repatter.match(s)
    print(result.group())