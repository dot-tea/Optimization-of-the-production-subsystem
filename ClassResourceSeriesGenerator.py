from ast import literal_eval
from math import sin
import numpy as np


class ResourceSeriesGenerator:
    @staticmethod
    def appendAsColumn(list2d: list[list], column: list) -> list[list]:
        if len(list2d) != len(column):
            if len(list2d) == 0:
                for index in range(len(column)):
                    list2d.append([column[index]])
                return list2d
            else:
                raise Exception('Column must have the same amount of elements as the number of rows in a 2D list.')
        for index in range(len(list2d)):
            list2d[index].append(column[index])
        return list2d
    
    @staticmethod
    def trend(
            length: int,
            step: float = 1,
            slope: float = 1,
            height: float = 0,
            noise: float = 0,
    ) -> list[float]:
        result = []
        x = 0
        for i in range(length):
            result.append(slope * x + height)
            x += step
        result = np.random.normal(result, noise)
        return result

    @staticmethod
    def season(
            length: int,
            step: float = 1,
            amplitude: float = 1,
            period: float = 1,
            shift: float = 0,
            height: float = 0,
            noise: float = 0,
    ) -> list[float]:
        result = []
        x = 0
        for i in range(length):
            result.append(amplitude * sin(period * x + shift) + height)
            x += step
        result = np.random.normal(result, noise)
        return result
    
    @staticmethod
    def trendAndSeason(
            length: int,
            step: float = 1,
            amplitude: float = 1,
            period: float = 1,
            shift: float = 0,
            slope: float = 1,
            height: float = 0,
            noise: float = 0,
    ) -> list[float]:
        result = []
        x = 0
        for i in range(length):
            result.append(amplitude * sin(period * x + shift) + slope * x + height)
            x += step
        result = np.random.normal(result, noise)
        return result

    @staticmethod
    def random(
            length: int,
            height: float = 0,
            range: float = 100,
    ) -> list[float]:
        return np.random.rand(length) * height + range

    @staticmethod
    def exportFile(list2d: list[list], fileName: str) -> None:
        file = open(fileName, 'w')
        for row in list2d:
            file.writelines(str(row) + "\n")
        file.close()
    
    @staticmethod
    def importFile(fileName: str) -> list[list]:
        file = open(fileName, 'r')
        list2d = []
        for row in file:
            print(row)
            list2d.append(literal_eval(row))
        file.close()
        return list2d
    
