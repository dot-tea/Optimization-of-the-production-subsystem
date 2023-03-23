from ClassProductionSubsystem import ProductionSubsystem
from math import fabs
from scipy.optimize import OptimizeResult
from typing import Callable


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
        self.productionSubsystem.Resource = resources
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
        stepCount = len(resourceTimeSeries) - 1
        for t in range(stepCount):
            optimizeResult = self.getOptimizeResult(currentLevel, resourceTimeSeries[t])
            sum += self.addedCostCoefficient \
                * optimizeResult.fun \
                - self.stuctureChangeCostFunction(fabs(controlTimeSeries[t])) \
                - self.getControlCost(optimizeResult)
            currentLevel += controlTimeSeries[t]
        optimizeResult = self.getOptimizeResult(currentLevel, resourceTimeSeries[stepCount])
        sum += self.addedCostCoefficient \
            * optimizeResult.fun \
            - self.getControlCost(optimizeResult)
        return sum
    
    
    


    
    

    