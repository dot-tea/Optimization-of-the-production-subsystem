from ClassСomplicatedConverter import СomplicatedConverter
from ClassDedicatedConverter import DedicatedConverter
from ClassDynamicSystem import DynamicSystem


# -- Инициализация --

resourceTimeSeries = [
    [1, 250, 120, 100, 230],
    [50, 500, 300, 200, 100],   
    [0.1, 100, 100, 100, 100],
]
startLevel = 2

m = len(resourceTimeSeries[0])
# инициализация n не играет особой роли
productionSubsystem = СomplicatedConverter(m, 1) 
# productionSubsystem = DedicatedConverter(m, 1)

def controlCost(simpleConverterCount: int, nonEmptyResourceStreamCount: int) -> float:
    beta = 1
    return beta * (simpleConverterCount + nonEmptyResourceStreamCount)

def structureChangeCost(levelDifference: int) -> float:
    alpha = 1
    return alpha * levelDifference * levelDifference

addedCostCoefficient = 1

dynamicSystem = DynamicSystem(productionSubsystem, controlCost, structureChangeCost, addedCostCoefficient)

levels = dynamicSystem.determineLevels(startLevel, 3, resourceTimeSeries, True)
print(levels)

