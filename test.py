import jieba
import codecs

with codecs.open('data/demo1.txt', 'r', encoding='utf-8') as fin:
  for line in fin:
    line = line.split()
    t = line[0]
    c = line[1:]
    print(t, c)
