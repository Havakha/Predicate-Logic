from sentence import Sentence, clean_sub
from unify import unify


def FOL_BC_ASK(kb, query):
    '''
    Param:
    -   kb (KB): knowledge base.
    -   goal (Sentence).
    Return
    -   a generator of Substitutions actions (FOL_BC_AND for multiple queries on 1 line or FOL_BC_OR for single and simple query on 1 line)
    '''
    if len(query.premise) > 1:
        return FOL_BC_AND(kb, query.premise, {})
    else:
        return FOL_BC_OR(kb, query.premise[0], {})


def FOL_BC_OR(kb, goal, theta):
    '''
    find answer for a goal based on all rules in KB and return all substitution exist if no answer found return nothing.
    Param:
    -   kb (KB): knowledge base.
    -   goal (Predicate): only accept one predicate.
    -   theta (dict): substitution value.
    Return
    -   all substitution possible so that goal is correct (dict)
    '''
    
    #Return list of only goal variables
    goal_var_to_keep = goal.var_list

    #Special case: equal relation
    if goal.name == "=":
        theta_equal = unify(goal.args[0], goal.args[1], dict(theta))
        #If a substitution is found and goal is an equal relation => that substitution satisfy the goal query
        #or cannot found any substitution and this is not equal relation => the current substitution satisfy the goal query
        if theta_equal is not None and goal.truth:
            yield clean_sub(theta_equal, goal_var_to_keep, theta)
        elif theta_equal is None and not goal.truth:
            yield theta
    else:
        for rule in fetch_rule(kb, goal):
            rule_handle = rule.standardize(set(goal.var_list + list(theta.keys())))
            lhs, rhs = rule_handle.premise, rule_handle.inference
            if len(rhs) > 0:
                for predicate in rhs:
                    if predicate.name == goal.name:
                        rhs = predicate
                        break
            else:
                rhs = rhs[0]
            for theta1 in FOL_BC_AND(kb, lhs, unify(rhs, goal, dict(theta))):
                yield clean_sub(theta1, goal_var_to_keep, theta)


def FOL_BC_AND(kb, goal, theta):
    '''
    Param:
    -   kb (KB): knowledge base.
    -   goal (list of Predicate).
    -   theta (dict).
    Return
    -   call FOL_BC_OR for each goal query and return all substitution possible so that goal is correct (dict)
    '''
    if theta is None:
        return
    elif len(goal) == 0:
        yield theta
    else:
        first, rest = goal[0], goal[1:]
        for theta1 in FOL_BC_OR(kb, first.sub(theta), theta):
            for theta2 in FOL_BC_AND(kb, rest, theta1):
                yield theta2


def fetch_rule(kb, goal):
    '''
    Fetch all rules that inferred goal.
    Param:
    -   kb (KB): knowledge base
    -   goal (Predicate): rule found must inferred this.
    Return:
    -   (Sentence - generator) all rules inferred goal.
    '''
    #Finding unit clause first
    for fact in kb.facts:
        if fact.inferred(goal):
            yield fact

    for rule in kb.rules:
        if rule.inferred(goal):
            yield rule