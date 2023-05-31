from time import time
from ClassСomplicatedConverter import СomplicatedConverter
from ClassDedicatedConverter import DedicatedConverter
from ClassDynamicSystem import DynamicSystem


# -- Инициализация --

resourceTimeSeries = [
    [0.1, 100, 180, 100],
    [20, 500, 5, 550],
    [1, 10, 100, 10],
    [55, 8, 500, 75],
    [45, 350, 55, 50],
    [38, 350, 57, 30],
    [80, 18, 58, 80],
    [1, 2000, 1, 1],
    [80, 60, 75, 60],
    [80, 60, 120, 60],
    [78, 1500, 35, 55],
]
startLevel = 2

m = len(resourceTimeSeries[0])
# инициализация n не играет особой роли
productionSubsystem = СomplicatedConverter(m, 1) 
# productionSubsystem = DedicatedConverter(m, 1)

def controlCost(simpleConverterCount: int, nonEmptyResourceStreamCount: int) -> float:
    beta = 0
    return beta * (simpleConverterCount + nonEmptyResourceStreamCount)

def structureChangeCost(levelDifference: int) -> float:
    alpha = 0
    return alpha * levelDifference * levelDifference

addedCostCoefficient = 1

dynamicSystem = DynamicSystem(productionSubsystem, controlCost, structureChangeCost, addedCostCoefficient, 'scipy_highs')

elapsed_time = []
for i in range(1000):
    start = time()
    levels = dynamicSystem.determineLevels(startLevel, 3, resourceTimeSeries)
    end = time()
    elapsed_time.append(end - start)
print(levels)
print(DynamicSystem.averageComplexity(levels), DynamicSystem.averageVariation(levels))
print(sum(elapsed_time) / len(elapsed_time))