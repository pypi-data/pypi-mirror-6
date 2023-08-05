# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>


# <codecell>

from iminuit import Minuit
import iminuit
def f(x,y,z):
    print "CALL", x, y, z
    return (x-2.)**2 + (y-3.)**2 + (z-4.)**2
print iminuit.__version__
m = Minuit(f, x=0.5, limit_x=(1,None ))
m.migrad()

# <codecell>


# <codecell>


# <codecell>


