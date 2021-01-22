from string import whitespace

class Term:
    '''
    Term:
    - Variable
    - Constant
    - Function (not yet implemented)
    '''
    def __init__(self, string = ""):

        brk = string.find("(")
        if brk != -1:
            self.name = string[:brk]
            self.args = string[brk+1:-1].split(",")
            self.args = [Term(x) for x in self.args]
        else:
            self.name = string
            self.args = None


    def __eq__(self, other):
        if type(other) != Term:
            return False
        return self.name == other.name and self.args == other.args


    @property
    def type_t(self):
        if self.name[0] == "_" or self.name[0].isupper():
            return "variable"
        else:
            return "constant"

    
    def sub(self, theta):
        if self.type_t == "variable" and self.name in theta:
            res = theta[self.name]
            while not res.sub(theta) == res:
                res = res.sub(theta)
            return res
        else:
            return self


    @property
    def var_list(self):
        if self.type_t == "variable":
            return [self.name]
        else:
            return []


    def __repr__(self):
        res = self.name
        if self.args is not None:
            res = res + "(" + ", ".join([repr(x) for x in self.args]) + ")"
        return res



class Predicate(Term):
    '''
    Predicate type. Predicate can be either one of these forms:
    -   Relate: name  or  name(term, term,...)
    -   Negate: not(name(...))
    -   Unify:  term = term or term \\= term
    '''
    def __init__(self, string = ""):    
        #Parse not
        if string.startswith("not("):
            string = string[4:-1]   #Strip not(...)
            self.truth = False
        else:
            self.truth = True

        # Parse = and \=
        if "\\=" in string:
            string = string.replace('\\', '')
            self.truth = False
        elif "=" in string:
            self.truth = True

        # Predicate is just a function return truth instead of obj
        # So parse the rest just like a term
        super().__init__(string)
    

    def __eq__(self, other):
        if type(other) != Predicate:
            return False
        return self.name == other.name and self.args == other.args and self.truth == other.truth


    @property
    def type_t(self):
        return "predicate"


    def sub(self, theta):
        res = Predicate()
        res.truth = self.truth
        res.name = self.name
        res.args = [t.sub(theta) for t in self.args]
        return res

    def neg(self):
        res = Predicate()
        res.truth = not self.truth
        res.name = self.name
        res.args = self.args
        return res


    @property
    def var_list(self):
        res = []
        for t in self.args:
            res += t.var_list
        res = list(set(res))  #Remove duplicate variable
        return res


    def standardize(self, args):
        if type(args) != set:
            raise TypeError("standardize only accept set of strings.")
        trans = {}
        # Create a substitution for every identical variable in 2 sentences
        for var in self.var_list:
            if var in args:
                new_var = var
                while new_var in args:
                    new_var = new_var + "%"
                trans[var] = Term(new_var)
        return self.sub(trans)



class Sentence:
    '''
    Sentence type. Sentence can be either one of these forms:
    -   Fact:   Predicate :- None
    -   Rule:   Predicate :- Predicate
    -   Query:  None :- Predicate
    '''

    def __init__(self, string = None, is_query = False):
        if string is None:
            self.inference = []
            self.premise = []
        else:
            # Remove every whitespace from string
            string = string.replace(' ', '').replace('\n', '').replace('.', '')

            # Break down a string into 2 parts: inference and premise
            string = string.split(":-")

            # If this string is a query then add predicate to premise
            if is_query:
                query = string[0].replace('),', ')|||').split('|||')
                self.premise = [Predicate(q) for q in query]
                self.inference = []
                return  # query does not accept sentence contain inferred symbol ":-" !!!

            # Parse inference part
            self.inference = [Predicate(string[0])]

            # Parse premise part
            if len(string) > 1:
                preds = string[1].replace('),', ')|||').split('|||')
                self.premise = [Predicate(p) for p in preds]
            else:
                self.premise = []


    def __eq__(self, other):
        if type(other) != Sentence:
            return False
        return self.premise == other.premise and self.inference == other.inference



    def __add__(self, other):
        res = Sentence()
        res.inference = self.inference + other.inference
        res.premise = self.premise + other.premise
        return res


    @property
    def type_t(self):        
        if len(self.premise) == 0:  return "fact"
        elif len(self.inference) == 0:  return "query"
        else: return "rule"


    def inferred(self, predicates):
        if type(predicates) != list:
            tmp = [predicates]
        else:
            tmp = predicates

        for p1 in tmp:
            found = False
            for p2 in self.inference:
                if p1.name == p2.name:
                    found = True
                    break
            if not found: return False
        
        return True


    def sub(self, theta):
        res = Sentence()
        res.inference = [p.sub(theta) for p in self.inference]
        res.premise = [p.sub(theta) for p in self.premise]
        return res

    
    @property
    def var_list(self):
        res = []
        for p in self.premise:
            res += p.var_list
        res = list(set(res))  #Remove duplicate variable
        return res

    def standardize(self, args):
        if type(args) != set:
            raise TypeError("standardize only accept set of strings.")
        trans = {}
        # Create a substitution for every identical variable in 2 sentences
        for var in self.var_list:
            if var in args:
                new_var = var
                while new_var in args:
                    new_var = new_var + "%"
                trans[var] = Term(new_var)
        return self.sub(trans)


    def __repr__(self):
        if self.type_t == "query":
            res = ", ".join([repr(x) for x in self.premise])
        else:
            res = ", ".join([repr(x) for x in self.inference]) + ":-" + ", ".join([repr(x) for x in self.premise])
        return res





def clean_sub(theta, var_list, prior_theta = {}):
    return {**prior_theta, **{x:theta[x] for x in var_list}}