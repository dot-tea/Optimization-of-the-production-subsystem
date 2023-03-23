from abc import ABC, abstractmethod
import numpy as np
from scipy.optimize import linprog
from scipy.optimize import OptimizeResult
from typing import Union

class ProductionSubsystem (ABC):
    
    m = 0
    '''
    Количество разных типов ресурсов (факторов производства)
    '''
    n = 0
    '''
    Количество итераций преобразователя (уровней)
    '''
    Resource = 0
    '''
    Количество имеющихся ресурсов в начале процесса
    '''
    # A = 0 
    def __init__(self, m: int, n: int):
        self.m = m
        self.n = n
        # Почему выбраны такие начальные значения?
        self.Resource = np.array([0.1, 100, 100, 100, 100])   
        #self.A = np.zeros((n+1, m), dtype=float) 
        
    @abstractmethod        
    def u (self):
        '''
        Возвращает суммарное количество ограничений в задаче линейного программирования

        Как правило, это сумма кол-ва ограничений на входные ресурсы 
        и кол-ва ограничений на распределение промежуточных ресурсов внутри структуры
        '''
        pass
    
    @abstractmethod
    def p (self):
        '''
        Возвращает размерность вектора факторных потоков, т.е. количество входных переменных в ЗЛП
        '''
        pass
    
    @abstractmethod
    def N(self):
        '''
        Возвращает индекс компонента фактороного вектора, 
        соответствующего кол-ву передаваемых начальных 
        ресурсов из процесса i-го уровня на процесс j-го
        уровня
        '''
        pass
    
    @abstractmethod
    def R(self):
        '''
        Возвращает индекс компонента фактороного вектора,
        соответствующего кол-ву передаваемых вспомогательных
        ресурсов из процесса i-го уровня на процесс j-го уровня
        '''
        pass
    
    @abstractmethod
    def N_F(self):
        '''
        Возвращает индекс компонента факторного вектора,
        соответствующего кол-ву передаваемых начальных
        ресурсов из процесса i-го уровня на конечный процесс
        F
        '''
        pass
    
    def formB (self):
        '''
        Возвращает вектор ограничений в задаче ЗЛП
        '''
        b=np.zeros(self.u(), dtype=float)
        for i in np.arange(0,self.u()):
            if i<self.m:
                b[i]=self.Resource[i];
        return b
    
    @abstractmethod    
    def formC (self):
        '''
        Возвращает вектор размерности p() коэффициентов при
        целевой функции, которая оптимизируется в рамках ЗЛП
        '''
        pass
    
    @abstractmethod
    def formA (self):
        '''
        Возвращает матрицу коэффициентов при ограничениях
        задачи ЗЛП. Это технологические коэффициенты при
        ПФ Леонтьева
        '''
        pass

    def OptimalF(self) -> OptimizeResult:
        '''
        Возвращает значение целевой функции при оптимальном
        векторе факторных потоков, т.е. при решении ЗЛП
        '''
        solution = linprog(self.formC(), A_ub=self.formA(), b_ub=self.formB(), method='revised simplex')
        return solution

    @abstractmethod
    def getSimpleConverterCount(self) -> int:
        pass

    def getNonEmptyResourceStreamCount(self, result: OptimizeResult) -> Union[int, None]:
        return np.count_nonzero(result.x)
