from ClassСomplicatedConverter import СomplicatedConverter
from ClassDedicatedConverter import DedicatedConverter
from ClassDynamicSystem import DynamicSystem
from matplotlib.pyplot import scatter, show, xlabel, ylabel, pcolor, colorbar, subplots
from time import time
import numpy as np
import os
import sys
import matplotlib.colors as colors
from ClassResourceSeriesGenerator import ResourceSeriesGenerator as RSG


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
#resourceTimeSeries = RSG.importFile('output3_test.txt')
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
labelMap = [None, 'Д1', 'Д2', 'Д3', 'С1', 'С2']

normalizedControlCosts = np.linspace(0, 10, 20)
normalizedStructureChangeCosts = np.linspace(0, 50, 20)
values = np.zeros((20, 20))
maxValue = None
minValue = None
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
        if maxValue == None or value > maxValue: maxValue = value
        if minValue == None or value < minValue: minValue = value

fig, axs = subplots()
for mode, points in enumerate(pointMap):
    if markerMap[mode] == None:
        continue
    axs.scatter(points['x'], points['y'], marker = markerMap[mode], label = labelMap[mode])

axs.legend()
axs.set_xlabel('ξ')
axs.set_ylabel('η')
show()
plot = pcolor(normalizedControlCosts, normalizedStructureChangeCosts, values)
colorbar(plot)
xlabel('ξ')
ylabel('η')
show()
