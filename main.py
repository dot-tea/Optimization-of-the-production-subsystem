from ClassDedicatedConverter import DedicatedConverter
from ClassСomplicatedConverter import СomplicatedConverter
import numpy as np


SPIII=DedicatedConverter(5, 5)
SPIII.Resource = np.array([0.1, 100, 100, 100, 100])
p=SPIII.p()
u=SPIII.u()
print(u)
print(p)

A=SPIII.OptimalF()
print(A)