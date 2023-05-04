from ClassDedicatedConverter import DedicatedConverter
from ClassСomplicatedConverter import СomplicatedConverter


SPIII=СomplicatedConverter(5,5)
p=SPIII.p()
u=SPIII.u()
print(u)
print(p)

A=SPIII.OptimalF()
print(A.fun)