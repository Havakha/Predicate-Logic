from sentence import Sentence
from back_chaining import FOL_BC_ASK


class KB:
    '''
    Knowledge base type. Contain all read Sentences of either rules or facts.
    '''

    def __init__(self):
        self.rules = []
        self.facts = []

    def add(self, input_string):
        if ":-" in input_string:
            rule = Sentence(input_string)
            self.rules.append(rule)
        else:
            fact = Sentence(input_string)
            self.facts.append(fact)

    def query(self, s):
        if type(s) == str:
            q = Sentence(s, is_query=True)
        else:
            q = s
        return FOL_BC_ASK(self, q)
