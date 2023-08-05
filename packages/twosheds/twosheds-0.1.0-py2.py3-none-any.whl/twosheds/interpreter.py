

class Interpreter(object):
    def __init__(self, grammar, semantics):
        self.grammar = grammar
        self.semantics = semantics

    def run(self, source_text):
        self.semantics.eval(self.grammar.parse(source_text))
