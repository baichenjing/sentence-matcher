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
        # TODO: multi-entity
        self.ac.add_word(token, {'type': 'entity', 'entity': entity, 'len': len(token)})
    self.__make_ac(self.root)
    self.ac.make_automaton()
  
  def __make_ac(self, node):
    if node.data['type'] == 'content':
      node.data['nullable'] = node.data['dropout'] != 0
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
      nullable = True
      for child in node:
        self.__make_ac(child)
        nullable &= child.data['nullable']
      node.data['nullable'] = nullable
      if 'dropout' in node.data:
        node.data['nullable'] |= (node.data['dropout'] != 0)
  
  def match(self, query):
    self.query = query
    for pair in self.ac.iter(self.query):
      if pair[1]['type'] == 'word':
        for node in self.index_node[pair[1]['index']]:
          node.data.setdefault('match', set())
          node.data['match'].add((pair[0] + 1 - pair[1]['len'], pair[0]))
      else:
        for node in self.entity_node[pair[1]['entity']]:
          node.data.setdefault('match', set())
          node.data['match'].add((pair[0] + 1 - pair[1]['len'], pair[0]))

  def try_merge(self, prefix, suffix):
    if suffix[0] <= prefix[1]:
      return None
    if self.query[prefix[1] + 1:suffix[0]].strip() == '':
      return (prefix[0], suffix[1])
    return None

  @staticmethod
  def __lcs(a, b):
    if len(a) == 0 or len(b) == 0:
      return 0
    f = [0 for _ in range(len(b) + 1)]
    for i in range(1, len(a) + 1):
      left_up = 0
      f[0] = 0
      for j in range(1, len(b) + 1):
        left = f[j-1]
        up = f[j]
        if a[i-1] == b[j-1]:
          f[j] = left_up + 1
        else:
          f[j] = max([left, up])
        left_up = up
    return f[len(b)]

  def classify(self, node):
    for child in node:
      result = self.classify(child)
      if result:
        return result
    if node.data['type'] in ('pickone', 'intent'):
      node.data.setdefault('match', set())
      for child in node:
        if 'match' in child.data:
          node.data['match'].update(child.data['match'])
      if node.data['type'] == 'intent' and (0, len(self.query) - 1) in node.data['match']:
        return node.data['intent']
    elif node.data['type'] in ('order', 'exchangeable'):
      contains = []
      match_list = []
      for child in node:
        if 'match' in child.data:
          for suffix in child.data['match']:
            match_list.append((suffix, (child, )))
        if not child.data['nullable']:
          contains.append(child)
      # Start Merge
      changed = True
      while changed:
        changed = False
        match_list = sorted(match_list, key=lambda x: x[0][0])
        new_match_list = set(match_list)
        for i in range(len(match_list)):
          for j in range(i + 1, len(match_list)):
            if set(match_list[i][1]) & set(match_list[j][1]) == set():
              result = self.try_merge(match_list[i][0], match_list[j][0])
              if result:
                item = (result, match_list[i][1] + match_list[j][1])
                if item not in new_match_list:
                  changed = True
                  new_match_list.add(item)
        match_list = list(new_match_list)
      if node.data['type'] == 'order':
        new_match_list = []
        child_list = [x for x in node]
        for item in match_list:
          if self.__lcs(child_list, item[1]) == len(item[1]):
            new_match_list.append(item)
        match_list = new_match_list
      match = []
      for x in match_list:
        all_match = True
        for y in contains:
          if y not in x[1]:
            all_match = False
            break
        if all_match:
          match.append(x[0])
      if match:
        node.data['match'] = match
          

  def print_match(self, node):
    if 'match' in node.data:
      print(list(node.data['match']))
    for child in node:
      self.print_match(child)
