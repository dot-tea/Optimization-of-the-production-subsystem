from ClassProductionSubsystem import ProductionSubsystem
from math import fabs
from scipy.optimize import OptimizeResult
from typing import Callable
import numpy as np


class DynamicSystem:
    productionSubsystem = None
    '''
    Производственная система.
    '''
    controlCostFunction = None
    '''
    Функция затрат на управление текущей иерархической структурой ПС.
    '''
    stuctureChangeCostFunction = None
    '''
    Функция затрат на изменение иерархической структуры ПС.
    '''
    addedCostCoefficient = 1
    '''
    Коэффициент надбавленной стоимости.
    '''
    def __init__(
            self, 
            productionSubsystem: ProductionSubsystem,
            controlCostFunction: Callable[[int, int], float],
            structureChangeCostFunction: Callable[[int], float],
            addedCostCoefficient: float = 1

        ):
        self.productionSubsystem = productionSubsystem
        self.controlCostFunction = controlCostFunction
        self.stuctureChangeCostFunction = structureChangeCostFunction
        self.addedCostCoefficient = addedCostCoefficient
    
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
        return self.productionSubsystem.OptimalF()

    def getControlCost(self, solution: OptimizeResult) -> float:
        '''
        Возвращает значение стоимости затрат на управление структурой ПФ в зависимости
        от числа слоёв в преобразователе.
        '''
        return self.controlCostFunction(self.productionSubsystem.getSimpleConverterCount(), self.productionSubsystem.getNonEmptyResourceStreamCount(solution))

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
                - self.stuctureChangeCostFunction(fabs(controlTimeSeries[t])) \
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
                - self.stuctureChangeCostFunction(fabs(nextLevel - level))
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
                        print('Structure change cost: ', self.stuctureChangeCostFunction(fabs(nextLevel - startLevel)))
                        print('Bonus functional value for following the optimal path: ', sumValues[step + 1][nextLevel]['value'])
                    value = partialValue - self.stuctureChangeCostFunction(fabs(nextLevel - startLevel)) + sumValues[step + 1][nextLevel]['value']
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
                        print('Structure change cost: ', self.stuctureChangeCostFunction(fabs(nextLevel - startLevel)))
                        print('Bonus functional value for following the optimal path: ', sumValues[step + 1][nextLevel]['value'])
                    value = partialValue - self.stuctureChangeCostFunction(fabs(nextLevel - level)) + sumValues[step + 1][nextLevel]['value']
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
        controlSeries = []
        for i in range(len(levelSeries) - 1):
            controlSeries.append(levelSeries[i + 1] - levelSeries[i])
        return controlSeries
    
    @staticmethod
    def averageComplexity(levelSeries: list[int]) -> float:
        return np.sum(levelSeries) / len(levelSeries)
    
    @staticmethod
    def averageVariation(levelSeries: list[int]) -> float:
        sum = 0
        for i in range(len(levelSeries) - 1):
            sum += fabs(levelSeries[i + 1] - levelSeries[i])
        return sum / len(levelSeries)

    