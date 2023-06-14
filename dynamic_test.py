from ClassСomplicatedConverter import СomplicatedConverter
from ClassDedicatedConverter import DedicatedConverter
from ClassDynamicSystem import DynamicSystem
from matplotlib.pyplot import show, step, xlabel, ylabel
from time import time
import os
import sys


# -- Инициализация --

resourceTimeSeries = [
    [38, 350, 57, 30],
    [0.1, 100, 180, 100],
    [20, 500, 0.01, 550],
    [1, 10, 100, 10],
    [0.55, 8, 500, 75],
    [45, 350, 55, 50],
    [38, 350, 57, 30],
    [0.1, 100, 180, 100],
]
startLevel = 2

for j in range(len(resourceTimeSeries[0])):
    y = []
    T = range(len(resourceTimeSeries))
    for i in T:
        y.append(resourceTimeSeries[i][j])
    #step(T, y)
    #xlabel('Шаг, t')
    #ylabel('Ресурс, R')
    #show()
    

m = len(resourceTimeSeries[0])
# инициализация n не играет особой роли
productionSubsystem = СomplicatedConverter(m, 1) 
# productionSubsystem = DedicatedConverter(m, 1)

def controlCost(simpleConverterCount: int, nonEmptyResourceStreamCount: int, beta: float) -> float:
    return beta * (simpleConverterCount + nonEmptyResourceStreamCount)

def structureChangeCost(levelDifference: int, alpha: float) -> float:
    return alpha * levelDifference * levelDifference

addedCostCoefficient = 1

dynamicSystem = DynamicSystem(productionSubsystem, controlCost, structureChangeCost, addedCostCoefficient, 0, 0)

elapsed_time = []
for i in range(1):
    origOut = sys.stdout
    origErr = sys.stderr
    nothing = open(os.devnull, 'w')
    sys.stdout = nothing
    sys.stderr = nothing
    start = time()
    levels = dynamicSystem.determineLevels(startLevel, 3, resourceTimeSeries)
    end = time()
    sys.stdout = origOut
    sys.stderr = origErr
    elapsed_time.append(end - start)
print(levels)
print(DynamicSystem.averageComplexity(levels), DynamicSystem.averageVariation(levels))
print(dynamicSystem.functional(levels[0], dynamicSystem.toControlSeries(levels), resourceTimeSeries))
print(sum(elapsed_time) / len(elapsed_time))
step(range(len(levels)), levels)
xlabel('Шаг, t')
ylabel('Уровень, n')
show()