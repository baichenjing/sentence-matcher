import ahocorasick

class MatchNER(object):
  def __init__(self):
    self.ac = ahocorasick.Automaton(ahocorasick.STORE_ANY)

  def construct(self, ner_list):
    for ner_type in ner_list:
      if ner_type is not "O":
        for item in ner_list[ner_type]:
          self.ac.add_word(item, (ner_type, len(item)))
    self.ac.make_automaton()
  
  def match_ner(self, query):
    for item in self.ac.iter(query):
      print(item)
