import json
import codecs
import argparse

from matcher.matcher import Matcher
from numpy import random

from utils.hierarchy import hierarchy, link_entity, str_stat

random.seed(0)

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', required=True, help='input file')
parser.add_argument('-q', '--query', required=True, help='query file')

args = parser.parse_args()

with codecs.open(args.file, 'r', encoding='utf-8') as fin:
  result = hierarchy(json.load(fin))
  if result[0]:
    root = result[1]
    with codecs.open(args.query, 'r', encoding='utf-8') as qin:
      query = json.load(qin)
      matcher = Matcher(root, query['entities'])
      matcher.match(query['query'])
      matcher.print_match(matcher.root)
