from puq import *

def run(num=20):
    # Declare our parameters here. Both are uniform on [-2, 2]
    p1 = UniformParameter('x', 'x', min=-2, max=2)
    p2 = UniformParameter('y', 'y', min=-2, max=2)

    # Create a host
    host = InteractiveHost()

    # Declare a UQ method.
    uq = LHS([p1, p2], num=num, ds=True)

    # Our test program
    prog = TestProgram(exe='./rosen_prog.py --x=$x --y=$y',
        desc='Rosenbrock Function')

    return Sweep(uq, host, prog)
