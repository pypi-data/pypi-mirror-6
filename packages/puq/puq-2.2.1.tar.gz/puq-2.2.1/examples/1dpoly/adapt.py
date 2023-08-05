from puq import *

def run():
    x = UniformParameter('x', 'x', min=0, max=10)
    host = InteractiveHost()
    uq = AdapStocColl([x], tol=.01)
    prog = TestProgram('./poly_prog.py', desc='1D Polynomial')
    return Sweep(uq, host, prog)
