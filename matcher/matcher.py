def match(node, query):
  if node.data['type'] == 'content':
    if node.data['isEntity']:
      # Do entity match
      pass
    else:
      # Make AC Here
      # Match then
      pass
  else:
    for child in node:
      match(child, query)
