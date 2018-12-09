import ahocorasick

class Matcher(object):
  def __init__(self, root, entities):
    self.root = root
    self.ac = ahocorasick.Automaton()
    self.token_index = {}
    self.index_node = {}
    self.entity_node = {}
    for entity in entities:
      for token in entities[entity]:
        self.ac.add_word(token, {'type': 'entity', 'entity': entity, 'len': len(token)})
    self.__make_ac(self.root)
    self.ac.make_automaton()
  
  def __make_ac(self, node):
    if node.data['type'] == 'content':
      if node.data['isEntity']:
        self.entity_node.setdefault(node.data['entity'], set())
        self.entity_node[node.data['entity']].add(node)
      else:
        for token in node.data['content']:
          if token not in self.token_index:
            index = len(self.token_index)
            self.token_index[token] = index
            self.ac.add_word(token, {'type': 'word', 'index': index, 'len': len(token)})
            self.index_node[index] = set()
          index = self.token_index[token]
          self.index_node[index].add(node)
    else:
      for child in node:
        self.__make_ac(child)
  
  def match(self, query):
    for pair in self.ac.iter(query):
      if pair[1]['type'] == 'word':
        for node in self.index_node[pair[1]['index']]:
          node.data.setdefault('match', set())
          node.data['match'].add((pair[0] + 1 - pair[1]['len'], pair[0]))
      else:
        for node in self.entity_node[pair[1]['entity']]:
          node.data.setdefault('match', set())
          node.data['match'].add((pair[0] + 1 - pair[1]['len'], pair[0]))

  def print_match(self, node):
    if 'match' in node.data:
      if (node.data['isEntity']):
        print(node.data['entity'], ':', list(node.data['match']))
      else:
        print(node.data['content'][0], ':', list(node.data['match']))
    for child in node:
      self.print_match(child)
