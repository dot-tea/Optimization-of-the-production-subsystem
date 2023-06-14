from ClassProductionSubsystem import ProductionSubsystem
from copy import deepcopy
from enum import Enum
from math import fabs
from scipy.optimize import OptimizeResult
from typing import Callable, Union
import numpy as np


class OperatingMode(Enum):
    DYNAMIC_OBSERVING = 1
    DYNAMIC_SIMPLIFIED = 2
    DYNAMIC_COMPLICATED = 3
    STATIONARY_BASIC = 4
    STATIONARY_STARTING = 5
class DynamicSystem:
    productionSubsystem = None
    '''
    Производственная система.
    '''
    controlCostFunction = None
    '''
    Функция затрат на управление текущей иерархической структурой ПС.
    '''
    structureChangeCostFunction = None
    '''
    Функция затрат на изменение иерархической структуры ПС.
    '''
    addedCostCoefficient = 1
    '''
    Коэффициент надбавленной стоимости.
    '''
    solver = 'scipy_revised_simplex'
    '''
    Метод решения задачи линейного программирования, принимаемый ProductionSubsystem.
    '''
    controlCostCoefficient = 0
    '''
    Коэффициент, используемый в определении функции затрат на текущее управление.
    '''
    structureChangeCostCoefficient = 0
    '''
    Коэффициент, используемый в определии функции затрат на изменение.
    '''
    def __init__(
            self, 
            productionSubsystem: ProductionSubsystem,
            controlCostFunction: Callable[[int, int], float],
            structureChangeCostFunction: Callable[[int], float],
            addedCostCoefficient: float = 1,
            controlCostCoefficient: float = 0,
            structureChangeCostCoefficient: float = 0,
            solver: str = 'scipy_revised_simplex',
        ):
        self.productionSubsystem = productionSubsystem
        self.controlCostFunction = controlCostFunction
        self.structureChangeCostFunction = structureChangeCostFunction
        self.addedCostCoefficient = addedCostCoefficient
        self.solver = solver
        self.controlCostCoefficient = controlCostCoefficient
        self.structureChangeCostCoefficient = structureChangeCostCoefficient
    
    def getOptimizeResult(self, levelCount: int, resources: list[float]) -> OptimizeResult:
        '''
        Возвращает решение ПФ при заданном числе уровней и распределении ресурсов.
        Размерность вектора ресурсов должна совпадать с количеством разных типов
        ресурсов.
        '''
        self.productionSubsystem.n = levelCount
        if (hasattr(self.productionSubsystem, 'A')):
            self.productionSubsystem.A = np.ones((levelCount + 1, self.productionSubsystem.m), dtype = float)
        self.productionSubsystem.Resource = np.array(resources)
        return self.productionSubsystem.OptimalF(self.solver)

    def getControlCost(self, solution: OptimizeResult) -> float:
        '''
        Возвращает значение стоимости затрат на управление структурой ПФ в зависимости
        от числа слоёв в преобразователе.
        '''
        return self.controlCostFunction(
                self.productionSubsystem.getSimpleConverterCount(), 
                self.productionSubsystem.getNonEmptyResourceStreamCount(solution), 
                self.controlCostCoefficient
        )

    def getStructureChangeCost(self, levelDifference: int) -> float:
        '''
        Возвращает значение стоимости затрат на изменение числа уровней преобразоветля 
        в зависимости от абсолютной величины этого изменения.
        '''
        return self.structureChangeCostFunction(levelDifference, self.structureChangeCostCoefficient)

    def functional(
            self,
            startLevel: int,
            controlTimeSeries: list[int],
            resourceTimeSeries: list[list[float]]
    ) -> float:
        '''
        Возвращает значение функционала, который необходимо
        максимизировать в рамках задачи управления.
        '''
        sum = 0
        currentLevel = startLevel
        stepCount = len(resourceTimeSeries)
        for t in range(stepCount - 1):
            optimizeResult = self.getOptimizeResult(currentLevel, resourceTimeSeries[t])
            sum += self.addedCostCoefficient \
                * optimizeResult.fun \
                - self.getStructureChangeCost(fabs(controlTimeSeries[t])) \
                - self.getControlCost(optimizeResult)
            currentLevel += controlTimeSeries[t]
        optimizeResult = self.getOptimizeResult(currentLevel, resourceTimeSeries[stepCount - 1])
        sum += self.addedCostCoefficient \
            * optimizeResult.fun \
            - self.getControlCost(optimizeResult)
        return sum
    
    def determineFinalStepLevel(
            self,
            maxLevel: int,
            resource: list[float],
    ) -> int:
        '''
        Возвращает оптимальное количество уровней на финальном состоянии.
        '''
        bestLevel = None
        bestValue = None
        for level in range(1, maxLevel + 1):
            optimizeResult = self.getOptimizeResult(level, resource)
            value = self.addedCostCoefficient * optimizeResult.fun - self.getControlCost(optimizeResult)
            if ((not value) or value > bestValue):
                bestLevel = level
                bestValue = value
        return bestLevel
    
    def determineStepLevel(
            self,
            maxLevel: int,
            resource: list[float],
            nextLevel: int,
    )-> int:
        '''
        Возвращает оптимальное количество уровней на промежуточном состоянии
        с учётом выбранного следующего уровня.
        '''
        bestLevel = None
        bestValue = None
        for level in range(1, maxLevel + 1):
            optimizeResult = self.getOptimizeResult(level, resource)
            value = self.addedCostCoefficient * optimizeResult.fun - self.getControlCost(optimizeResult) \
                - self.structureChangeCostFunction(fabs(nextLevel - level))
            if ((not value) or value > bestValue):
                bestLevel = level
                bestValue = value
        return bestLevel
    
    def determineLevels(
            self,
            startLevel: int,
            maxLevel: int,
            resourceTimeSeries: list[list[float]],
            verbose: bool = False,
    ) -> list[int]:
        '''
        Возвращает оптимальную траекторию уровней для динамического процесса.
        '''
        if verbose:
            print('Start level: ', startLevel)
            print('Max level: ', maxLevel)
            print('Added cost coefficient: ', self.addedCostCoefficient)
        sumValues = {}
        stepCount = len(resourceTimeSeries)
        if verbose: print('Step count: ', stepCount)
        # 1. Вычисляем функционал для последнего шага со всеми возможными уровнями.
        if verbose: 
            print('Step ', stepCount)
            print('Resources: ', resourceTimeSeries[stepCount - 1])
        sumValues[stepCount] = {}
        for level in range(1, maxLevel + 1):
            if verbose: print('Calculating for level ', level)
            optimizeResult = self.getOptimizeResult(level, resourceTimeSeries[stepCount - 1])
            if verbose: 
                print('Result: ', optimizeResult.fun, ' for X = ', optimizeResult.x)
                print('With coefficient: ', optimizeResult.fun * self.addedCostCoefficient)
                print('Control cost: ', self.getControlCost(optimizeResult))
            value = self.addedCostCoefficient * optimizeResult.fun - self.getControlCost(optimizeResult)
            if verbose: print('Functional value: ', value)
            sumValues[stepCount][level] = {'value': value, 'nextLevel': None}
        # 2. Для каждого предыдущего шага:
        for step in reversed(range(1, stepCount)):
            if verbose:
                print('Step ', step)
                print('Resources: ', resourceTimeSeries[step - 1])
            sumValues[step] = {}
            # 3. На первом шаге управление будет фиксированным, так как startLevel уже задан.
            if step == 1:
                if verbose: print('Reached fixed starting level ', startLevel)
                optimizeResult = self.getOptimizeResult(startLevel, resourceTimeSeries[step - 1])
                if verbose: 
                    print('Result: ', optimizeResult.fun, ' for X = ', optimizeResult.x)
                    print('With coefficient: ', optimizeResult.fun * self.addedCostCoefficient)
                    print('Control cost: ', self.getControlCost(optimizeResult))
                partialValue = self.addedCostCoefficient * optimizeResult.fun - self.getControlCost(optimizeResult)
                if verbose: print('Partial functional value: ', partialValue)
                optimalNextLevel = None
                optimalValue = None
                if verbose: print('Searching for optimal next level')
                for nextLevel in range(1, maxLevel + 1):
                    if verbose: 
                        print('Checking level ', nextLevel, ' as next level')
                        print('Absolute difference: ', fabs(nextLevel - startLevel))
                        print('Structure change cost: ', self.getStructureChangeCost(fabs(nextLevel - startLevel)))
                        print('Bonus functional value for following the optimal path: ', sumValues[step + 1][nextLevel]['value'])
                    value = partialValue - self.getStructureChangeCost(fabs(nextLevel - startLevel)) + sumValues[step + 1][nextLevel]['value']
                    if verbose: print('Total functional value: ', value)
                    if ((optimalValue == None) or (value > optimalValue)):
                        if verbose and optimalValue == None: print('Setting as optimal')
                        elif verbose and value > optimalValue: print('Found new optimal')
                        optimalNextLevel = nextLevel
                        optimalValue = value
                sumValues[step][startLevel] = {'value': optimalValue, 'nextLevel': optimalNextLevel}
                break
            # 2.1. Вычисляем функционал со всеми возможными уровнями и управлениями.
            for level in range(1, maxLevel + 1):
                if verbose: print('Checking level ', level)
                optimizeResult = self.getOptimizeResult(level, resourceTimeSeries[step - 1])
                if verbose: 
                    print('Result: ', optimizeResult.fun, ' for X = ', optimizeResult.x)
                    print('With coefficient: ', optimizeResult.fun * self.addedCostCoefficient)
                    print('Control cost: ', self.getControlCost(optimizeResult))
                partialValue = self.addedCostCoefficient * optimizeResult.fun - self.getControlCost(optimizeResult)
                if verbose: print('Partial functional value: ', partialValue)
                optimalNextLevel = None
                optimalValue = None
                # 2.2. Среди них выбираем с таким управлением, чтобы сумма этого функционала
                # и последующих была максимальной.
                for nextLevel in range(1, maxLevel + 1):
                    if verbose: 
                        print('Checking level ', nextLevel, ' as next level')
                        print('Absolute difference: ', fabs(nextLevel - startLevel))
                        print('Structure change cost: ', self.getStructureChangeCost(fabs(nextLevel - startLevel)))
                        print('Bonus functional value for following the optimal path: ', sumValues[step + 1][nextLevel]['value'])
                    value = partialValue - self.getStructureChangeCost(fabs(nextLevel - level)) + sumValues[step + 1][nextLevel]['value']
                    if verbose: print('Total functional value: ', value)
                    if ((optimalValue == None) or (value > optimalValue)):
                        if verbose and optimalValue == None: print('Setting as optimal')
                        elif verbose and value > optimalValue: print('Found new optimal')
                        optimalNextLevel = nextLevel
                        optimalValue = value
                sumValues[step][level] = {'value': optimalValue, 'nextLevel': optimalNextLevel}
        levelSeries = []
        selectedLevel = startLevel
        for step in range(1, stepCount + 1):
            levelSeries.append(selectedLevel)
            selectedLevel = sumValues[step][selectedLevel]['nextLevel']
        if verbose: print(sumValues)
        return levelSeries
    
    def toControlSeries(self, levelSeries: list[int]) -> list[int]:
        '''
        Преобразует последовательность уровней для динамической системы в
        последовательность управлений на каждом этапе системы.
        '''
        controlSeries = []
        for i in range(len(levelSeries) - 1):
            controlSeries.append(levelSeries[i + 1] - levelSeries[i])
        return controlSeries
    
    @staticmethod
    def averageComplexity(levelSeries: list[int]) -> float:
        '''
        Возвращает среднюю сложность ряда уровней для производственной системы.
        '''
        return np.sum(levelSeries) / len(levelSeries)
    
    @staticmethod
    def averageVariation(levelSeries: list[int]) -> float:
        '''
        Возвращает среднюю изменчивость ряда уровней для производственной системы.
        '''
        sum = 0
        for i in range(len(levelSeries) - 1):
            sum += fabs(levelSeries[i + 1] - levelSeries[i])
        return sum / len(levelSeries)

    def getDegenerateLevelSeries(
            self,
            startLevel: int,
            maxLevel: int,
            resourceTimeSeries: list[list[float]],
            verbose: bool = False,
    ) -> list[int]:
        '''
        Возвращает последовательность уровней при нулевых функциях затрат, что является
        случаем вырожденной динамической задачи оптимизации.
        '''
        originalControlCostCoefficient = self.controlCostCoefficient
        originalStructureChangeCostCoefficient = self.structureChangeCostCoefficient
        self.controlCostCoefficient = 0
        self.structureChangeCostCoefficient = 0
        levelSeries = self.determineLevels(startLevel, maxLevel, resourceTimeSeries, verbose)
        self.controlCostCoefficient = originalControlCostCoefficient
        self.structureChangeCostCoefficient = originalStructureChangeCostCoefficient
        return levelSeries

    def getOperatingMode(
            self,
            levelSeries: list[int],
            degenerateLevelSeries: list[int],
    ) -> OperatingMode:
        '''
        Возвращает режим работы динамической системы при данной последовательности
        уровней в динамической системе и "эталонной" последовательности уровней
        в вырожденной задаче (её можно получить через DynamicSystem::getDegenerateLevelSeries).
        '''
        averageVariation = DynamicSystem.averageVariation(levelSeries)
        if np.isclose(averageVariation, 0):
            return OperatingMode.STATIONARY_STARTING
        elif np.isclose(averageVariation, fabs(levelSeries[1] - levelSeries[0]) / len(levelSeries)):
            return OperatingMode.STATIONARY_BASIC
        else:
            degenerateAverageVariation = DynamicSystem.averageVariation(degenerateLevelSeries)
            if np.isclose(averageVariation, degenerateAverageVariation):
                return OperatingMode.DYNAMIC_OBSERVING
            elif averageVariation < degenerateAverageVariation:
                return OperatingMode.DYNAMIC_SIMPLIFIED
            else:
                return OperatingMode.DYNAMIC_COMPLICATED


    