from spambase import *
import random

random.seed(21619)

x = toolbox.individual()
string = str(x)

print(string)

ind = creator.Individual.from_string(string, pset)
print(ind.to_string())
print(x == ind)
print(ind[-1].value)
print(x[-1].value)