from ClassСomplicatedConverter import СomplicatedConverter
from ClassDedicatedConverter import DedicatedConverter
from ClassDynamicSystem import DynamicSystem


# -- Инициализация --
m = 4
resourceTimeSeries = [
    [18, 10, 18, 10],
    [20, 45, 5, 55],
    [1, 1, 1, 1],
]
startLevel = 2

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

levels = dynamicSystem.determineLevels(startLevel, 3, resourceTimeSeries)
print(levels)

