from ClassСomplicatedConverter import СomplicatedConverter
from ClassDedicatedConverter import DedicatedConverter
from ClassDynamicSystem import DynamicSystem
from matplotlib.pyplot import scatter, show, xlabel, ylabel, pcolor, colorbar
from time import time
import numpy as np
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
maxLevel = 10
    

m = len(resourceTimeSeries[0])
productionSubsystem = СomplicatedConverter(m, 1) 

def controlCost(simpleConverterCount: int, nonEmptyResourceStreamCount: int, beta: float) -> float:
    return beta * (simpleConverterCount + nonEmptyResourceStreamCount)

def structureChangeCost(levelDifference: int, alpha: float) -> float:
    return alpha * levelDifference * levelDifference

addedCostCoefficient = 1
controlCostCoefficient = 0
structureChangeCostCoefficient = 0

dynamicSystem = DynamicSystem(
        productionSubsystem, 
        controlCost, 
        structureChangeCost, 
        addedCostCoefficient, 
        controlCostCoefficient, 
        structureChangeCostCoefficient
)

markerMap = [None, 'o', '^', 's', 'P', 's']
pointMap = [None, {'x': [], 'y': []}, {'x': [], 'y': []}, {'x': [], 'y': []}, {'x': [], 'y': []}, {'x': [], 'y': []}]

normalizedControlCosts = np.linspace(0, 50, 10)
normalizedStructureChangeCosts = np.linspace(0, 50, 10)
values = np.zeros((10, 10))
degenerateSeries = dynamicSystem.getDegenerateLevelSeries(startLevel, maxLevel, resourceTimeSeries)
for i, x in enumerate(normalizedControlCosts):
    for j, y in enumerate(normalizedStructureChangeCosts):
        dynamicSystem.controlCostCoefficient = x * addedCostCoefficient
        dynamicSystem.structureChangeCostCoefficient = y * addedCostCoefficient
        series, value = dynamicSystem.determineLevels(startLevel, maxLevel, resourceTimeSeries, returnFunctionalValue = True)
        numericMode = dynamicSystem.getOperatingMode(series, degenerateSeries).value
        pointMap[numericMode]['x'].append(x)
        pointMap[numericMode]['y'].append(y)
        values[i][j] = value
        
for mode, points in enumerate(pointMap):
    if markerMap[mode] == None:
        continue
    scatter(points['x'], points['y'], marker = markerMap[mode])

show()
plot = pcolor(normalizedControlCosts, normalizedStructureChangeCosts, values)
colorbar(plot)
show()
        