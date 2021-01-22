from sentence import Term, Predicate


def unify(x, y, theta={}):
    '''
	Take 2 compound expressions(predicate or sentence) and return a substitution if exist.
	Param: 
		x, y: variable, constant, list or compound expression.
		theta: the substitution built up so far.
	Return:
		Substitution found or None when not exist.
    '''

    # no substitution found
    if theta is None:
        return None

    # X and Y is identical -> this theta substitution is correct
    elif x == y:
        return theta

    # Do unification on variable if either x or y is variable
    elif is_variable(x):
        return unify_var(x, y, theta)
    elif is_variable(y):
        return unify_var(y, x, theta)


    # if both X and Y is in the form F(A, B) then unify the list of variables
    elif is_compound(x) and is_compound(y):
        return unify(x.args, y.args, unify(x.name, y.name, theta))


    # If both x and y is list of variables/constants/compound expressions
    # -> Find substitution of the first one and unify the rest with that
    elif type(x) is list and type(y) is list:
        return unify(x[1:], y[1:], unify(x[0], y[0], theta))

    # Usually this case is reached when compare the op of 2 compound expressions.
    else:
        return None


def unify_var(var, x, theta):
    '''
	Unify 1 variable with 1 expression, return a substitution if exist.
	'''

    if var.name in theta:  # There is a sub for var exist
        return unify(theta[var.name], x, theta)
    elif is_variable(x) and x.name in theta:  # There is a sub for x exist
        return unify(var, theta[x.name], theta)
    else:  # Add new record to theta
        theta[var.name] = x
        return theta


def is_variable(x):
    if type(x) != Term:
        return False
    if x.type_t == "variable":
        return True
    else:
        return False


def is_compound(x):
    if type(x) != Term and type(x) != Predicate:
        return False
    if x.type_t == "predicate":
        if x.args is not None:
            return True
    else:
        return False
