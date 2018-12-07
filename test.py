import json
import codecs
from matcher.match_ner import MatchNER

with codecs.open('data/demo1.json', 'r', encoding='utf-8') as fin:
  result = json.load(fin)
  matcher = MatchNER()
  matcher.construct(result[result["lang"]])
  print(result["query"])
  matcher.match_ner("检索一组与机器学习相关的期刊")
