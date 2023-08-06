"""
Simplified Python interface for Hom4PS-3,
a numerical solver for systems of polynomial equations
based on homotopy continuation methods.
"""

import hom4ps

def _do_solve (system, solver, acc):
    if isinstance(system,list) or isinstance(system,tuple):
	polys  = map (lambda x: str(x) + ';', system)
        system = "{\n" + "\n".join(polys) + "\n}"
    hom = solver()
    hom.solve_string (system)
    var = list (hom.variables)
    soln = []
    for k in range(hom.get_total_solutions()):
	soln.append (dict (zip (var,acc(hom,k))))
    del hom
    return soln
    
def solve_with (system, solver):
    return _do_solve (system, solver, hom4ps.Hom4PS.get_solution_cd)

def solve_with_r (system, solver):
    return _do_solve (system, solver, hom4ps.Hom4PS.get_solution_rd)

def solve_fast (system):
    """
    Solves a system of polynomial equations using the 'fast' solver of Hom4PS-3.
    It is best used with medium to large sized polynomial systems as it delivers
    superior speed for such systems. However, the optimization for speed comes
    at a price: for certain systems, this solver may produces solutions with
    lower numerical accuracy.

    Args:

	system: a list of polynomials or a single string that represents the
		entire polynomial system.
		
		*   If it is a list, then each element should be a string or 
		    an object which can be turned into a string representing 
		    a polynomial (with no equal sign).
		    
		*   If it is a single string, then it should contain a list 
		    of semicolon-separated polynomials (with no equal signs)
		    enclosed in curly braces.

    Returns:

	A list of dictionaries representing the isolated (complex) solutions.

    Examples:

	>>> f = "x^2 - 3*x + 2"
	>>> g = "y^2 - 4*y + 3"
	>>> hom4pspy.solve_fast ( [f,g] )
	[
	    {'y': (3+0j), 'x': (2+0j)}, 
	    {'y': (3+0j), 'x': (1+0j)}, 
	    {'y': (1+0j), 'x': (2+0j)}, 
	    {'y': (1+0j), 'x': (1+0j)}
	]

	Alternatively, one could use a single string to represent the system.
	Note that in this case a semi-colon (rather than comma) is used to
	separate polynomials and equal signs never appear.

	>>> hom4pspy.solve_fast ( "{ x^2 - 3*x + 2; y^2 - 4*y + 3 }" )
	[
	    {'y': (3+0j), 'x': (2+0j)}, 
	    {'y': (3+0j), 'x': (1+0j)}, 
	    {'y': (1+0j), 'x': (2+0j)}, 
	    {'y': (1+0j), 'x': (1+0j)}
	]
    """
    return solve_with (system, hom4ps.Hom4PSFast)

def solve_small (system):
    """
    Solves a system of polynomial equations using the 'small' solver of Hom4PS-3.
    This solver is optimized for small systems.

    Args:

	system: a list of polynomials or a single string that represents the
		entire polynomial system.
		
		*   If it is a list, then each element should be a string or 
		    an object which can be turned into a string representing 
		    a polynomial (with no equal sign).
		    
		*   If it is a single string, then it should contain a list 
		    of semicolon-separated polynomials (with no equal signs)
		    enclosed in curly braces.

    Returns:

	A list of dictionaries representing the isolated (complex) solutions.

    Example:
	>>> f = "x^2 - 3*x + 2"
	>>> g = "y^2 - 4*y + 3"
	>>> hom4pspy.solve_small ( [f,g] )
	[
	    {'y': (3+0j), 'x': (2+0j)}, 
	    {'y': (3+0j), 'x': (1+0j)}, 
	    {'y': (1+0j), 'x': (2+0j)}, 
	    {'y': (1+0j), 'x': (1+0j)}
	]

	Alternatively, one could use a single string to represent the system.
	Note that in this case a semi-colon (rather than comma) is used to
	separate polynomials and equal signs never appear.

	>>> hom4pspy.solve_small ( "{ x^2 - 3*x + 2; y^2 - 4*y + 3 }" )
	[
	    {'y': (3+0j), 'x': (2+0j)}, 
	    {'y': (3+0j), 'x': (1+0j)}, 
	    {'y': (1+0j), 'x': (2+0j)}, 
	    {'y': (1+0j), 'x': (1+0j)}
	]
    """
    return solve_with (system, hom4ps.Hom4PSSmall)

def solve_easy (system):
    """
    Solves a system of polynomial equations using the 'easy' solver of Hom4PS-3.
    This solver automatically determines the best strategy for solving the given
    system of equations. However, note that this feature is still experimental.

    Args:

	system: a list of polynomials or a single string that represents the
		entire polynomial system.
		
		*   If it is a list, then each element should be a string or 
		    an object which can be turned into a string representing 
		    a polynomial (with no equal sign).
		    
		*   If it is a single string, then it should contain a list 
		    of semicolon-separated polynomials (with no equal signs)
		    enclosed in curly braces.

    Returns:

	A list of dictionaries representing the isolated (complex) solutions.

    Example:

	>>> f = "x^2 - 3*x + 2"
	>>> g = "y^2 - 4*y + 3"
	>>> hom4pspy.solve_easy ( [f,g] )
	[
	    {'y': (3+0j), 'x': (2+0j)}, 
	    {'y': (3+0j), 'x': (1+0j)}, 
	    {'y': (1+0j), 'x': (2+0j)}, 
	    {'y': (1+0j), 'x': (1+0j)}
	]

	Alternatively, one could use a single string to represent the system.
	Note that in this case a semi-colon (rather than comma) is used to
	separate polynomials and equal signs never appear.

	>>> hom4pspy.solve_easy ( "{ x^2 - 3*x + 2; y^2 - 4*y + 3 }" )
	[
	    {'y': (3+0j), 'x': (2+0j)}, 
	    {'y': (3+0j), 'x': (1+0j)}, 
	    {'y': (1+0j), 'x': (2+0j)}, 
	    {'y': (1+0j), 'x': (1+0j)}
	]
    """
    return solve_with (system, hom4ps.Hom4PSEasy)

def solve_real (system):
    """
    Finds the real solutions of a system of polynomial equations using Hom4PS-3.
    Note that this solver simply finds all the isolated complex solutions to the
    given system and discard those with sufficiently large imaginary components.

    Args:

	system: a list of polynomials or a single string that represents the
		entire polynomial system.
		
		*   If it is a list, then each element should be a string or 
		    an object which can be turned into a string representing 
		    a polynomial (with no equal sign).
		    
		*   If it is a single string, then it should contain a list 
		    of semicolon-separated polynomials (with no equal signs)
		    enclosed in curly braces.

    Returns:

	A list of dictionaries representing the isolated (real) solutions.

    Examples:

	>>> f = "x^2 - 3*x + 2"
	>>> g = "y^2 - 4*y + 3"
	>>> hom4pspy.solve_real ( [f,g] )
	[
	    {'y': 3.0, 'x': 2.0}, 
	    {'y': 3.0, 'x': 1.0}, 
	    {'y': 1.0, 'x': 2.0}, 
	    {'y': 1.0, 'x': 1.0}
	]

	Alternatively, one could use a single string to represent the system.
	Note that in this case a semi-colon (rather than comma) is used to
	separate polynomials and equal signs never appear.

	>>> hom4pspy.solve_real ( "{ x^2 - 3*x + 2; y^2 - 4*y + 3 }" )
	[
	    {'y': 3.0, 'x': 2.0}, 
	    {'y': 3.0, 'x': 1.0}, 
	    {'y': 1.0, 'x': 2.0}, 
	    {'y': 1.0, 'x': 1.0}
	]
    """
    return solve_with_r (system, hom4ps.Hom4PSReal)

