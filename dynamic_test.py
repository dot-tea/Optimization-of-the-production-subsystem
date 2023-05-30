from ClassСomplicatedConverter import СomplicatedConverter
from ClassDedicatedConverter import DedicatedConverter
from ClassDynamicSystem import DynamicSystem


# -- Инициализация --

resourceTimeSeries = [
    [18, 10, 18, 10],
    [20, 50, 5, 55],
    [1, 1, 1, 10],
    [55, 8, 50, 75],
    [45, 35, 55, 50],
    [38, 35, 57, 30],
    [80, 18, 58, 80],
    [1, 5, 1, 1],
    [80, 60, 75, 60],
    [80, 60, 75, 60],
    [78, 15, 35, 55],
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

dynamicSystem = DynamicSystem(productionSubsystem, controlCost, structureChangeCost, addedCostCoefficient)

levels = dynamicSystem.determineLevels(startLevel, 4, resourceTimeSeries)
print(levels)
print(DynamicSystem.averageComplexity(levels), DynamicSystem.averageVariation(levels))
