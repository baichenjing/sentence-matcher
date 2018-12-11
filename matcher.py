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
        if token in self.ac:
          self.ac.get(token)['entity'].add(entity)
        else:
          self.ac.add_word(token, {'type': 'entity', 'entity': {entity}, 'len': len(token)})

    self.__make_ac(self.root)
    self.ac.make_automaton()
  
  @staticmethod
  def __count_word(sent):
    return len(sent.strip())

  def __make_ac(self, node):
    if node.data['type'] == 'content':
      node.data['nullable'] = node.data['dropout'] != 0
      if not node.data['nullable']:
        node.data['min_node'] = 1
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
      count = 0
      for child in node:
        self.__make_ac(child)
        nullable &= child.data['nullable']
        if 'min_node' in child.data:
          count += child.data['min_node']
      node.data['nullable'] = nullable
      if 'dropout' in node.data:
        node.data['nullable'] |= (node.data['dropout'] != 0)
      if not node.data['nullable']:
        node.data['min_node'] = count
  
  def match(self, query):
    self.query = query
    self.query_len = len(query)
    for pair in self.ac.iter(self.query):
      if pair[1]['type'] == 'word':
        for node in self.index_node[pair[1]['index']]:
          node.data.setdefault('match', set())
          node.data['match'].add(((pair[0] + 1 - pair[1]['len'], pair[0]), 0, ((pair[0] + 1 - pair[1]['len'], pair[0]),), ()))
      else:
        for entity in pair[1]['entity']:
          for node in self.entity_node[entity]:
            node.data.setdefault('match', set())
            node.data['match'].add(((pair[0] + 1 - pair[1]['len'], pair[0]), 0, ((pair[0] + 1 - pair[1]['len'], pair[0]),), ()))

  def try_merge(self, prefix, suffix):
    if suffix[0][0] <= prefix[0][1]:
      return None
    count = prefix[1] + suffix[1] + self.__count_word(self.query[prefix[0][1] + 1:suffix[0][0]])
    return (prefix[0][0], suffix[0][1]), count, prefix[2] + suffix[2], prefix[3] + suffix[3]
  
  def gen_merge(self, node, deep, node_list, count, threshold, remove_list):
    '''
    node_list: [((st, ed), count, add_list, remove_list)]
    '''
    if deep == len(node):
      if len(node_list) == 0:
        return []
      if node.data['type'] == 'exchangeable':
        node_list = sorted(node_list, key=lambda x: x[0][0])
      result = node_list[0]
      for i in range(1, len(node_list)):
        result = self.try_merge(result, node_list[i])
        if result is None:
          break
      if result and result[1] + count <= threshold:
        return [(result[0], result[1] + count, result[2], result[3] + remove_list)]
      return []
    else:
      result = []
      if 'match' in node.children[deep].data:
        for match in node.children[deep].data['match']:
          result.extend(self.gen_merge(node, deep + 1, node_list + [match], count, threshold, remove_list))
      if node.children[deep].data['nullable']:
        result.extend(self.gen_merge(node, deep + 1, node_list, count, threshold, remove_list))
      else:
        result.extend(self.gen_merge(node, deep + 1, node_list, count + node.children[deep].data['min_node'], threshold, remove_list + (node.children[deep].index,)))
      return result

  def __classify(self, node, threshold):
    for child in node:
      self.__classify(child, threshold)
    if node.data['type'] in ('pickone', 'intent'):
      node.data.setdefault('match', set())
      for child in node:
        if 'match' in child.data:
          node.data['match'].update(child.data['match'])
      if node.data['type'] == 'intent':
        for match in node.data['match']:
          count = match[1] + match[0][0] + self.query_len - 1 - match[0][1]
          if count <= threshold:
            self.result.append((count, node.data['intent'], match[2], match[3]))
    elif node.data['type'] in ('order', 'exchangeable'):
      match = self.gen_merge(node, 0, [], 0, threshold, ())
      if match:
        node.data['match'] = match

  def classify(self, threshold=0):
    self.result = []
    self.__classify(self.root, threshold)
    self.result = sorted(self.result, key=lambda x: x[0])
    # print(self.result)
    if self.result:
      return self.result[0]
    else:
      return None

  def print_match(self, result):
    query = []
    front = 0
    for seg in result[2]:
      query.append(self.query[front:seg[0]])
      query.append('(%s)' % self.query[seg[0]:seg[1]+1])
      front = seg[1]+1
    query.append(self.query[front:])
    print('intent: %s' % result[1])
    print('delta: %d' % result[0])
    print('query: %s' % self.query)
    print('match query: %s' % ''.join(query))
    print('remove node index: %s' % str(result[3]))
