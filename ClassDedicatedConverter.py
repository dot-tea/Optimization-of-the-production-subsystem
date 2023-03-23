import numpy as np


from ClassProductionSubsystem import ProductionSubsystem
# Структура специализированного преобразователя

class DedicatedConverter (ProductionSubsystem):
    
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
    A = 0 
    '''
    Матрица коэффициентов при задаче ЗЛП
    '''
    def __init__(self, m,n):
        ProductionSubsystem.__init__(self, m, n)
        self.A = np.ones((n+1, m), dtype=float) 
        
    def u (self):
        return int(self.m*(self.n+1))
    def p (self):
        return int(((self.n*(self.n+2*self.m+1))/2))

    def N(self,i, j):
        return int((self.n-1)*i-((i-1)*i)/2+j-1)

    def R(self, l,  i):
        return int(self.N(self.n-1,self.n)+(l-1)*self.n+i)
    
    

    def N_F(self, i):
        return int((self.p()-1-self.n+i))


    
    def formC (self):
        c=np.zeros(self.p(), dtype=float)
        for i in np.arange(0,self.p()):
            if (i>=self.p()-self.n) and (i<=self.p()-1):
                c[i]=-1.
        return c

    def formA (self):
        M=np.zeros((self.u(), self.p()), dtype=float)
        for i in np.arange(1,self.n+1):
            M[0][self.N(0,i)]=1.0
            for l in np.arange(1,self.m):
                M[l][self.N(self.n-1,self.n)+(l-1)*self.n+i]=1.0
        # for i in np.arange (1,self.n):
        #     for l in np.arange (0,i):
        #         M[self.m+self.m*(i-1)][self.N(l,i)]=-float(self.A.sum(axis=1)[i]/self.A[i][0])
        #     for j in np.arange (i+1,self.n+1):
        #         M[self.m+self.m*(i-1)][self.N(i,j)]=1.0
        #     M[self.m+self.m*(i-1)][self.N_F(i)]=1.0
        #     for k in np.arange (1,self.m):
        #         M[self.m+self.m*(i-1)+k][self.N(self.n-1,self.n)+(k-1)*self.n+i]=-float(self.A.sum(axis=1)[i]/self.A[i][0])
        #         for j in np.arange (i+1,self.n+1):
        #             M[self.m+self.m*(i-1)+k][self.N(i,j)]=1.0
        #         M[self.m+self.m*(i-1)+k][self.N_F(i)]=1.0
        
        # for l in np.arange (0,self.n):
        #     M[self.u()-self.m][self.N(l,self.n)]=-float(self.A.sum(axis=1)[self.n]/self.A[self.n][0])
        # M[self.u()-self.m][self.N_F(self.n)]=1.0
        # for k in np.arange (1,self.m):
        #     M[self.u()-self.m+k][self.N(self.n-1,self.n)+(k-1)*self.n+self.n]=-float(self.A.sum(axis=1)[self.n]/self.A[self.n][k])
        #     M[self.u()-self.m+k][self.N_F(self.n)]=1.0
        return M

    def getSimpleConverterCount(self) -> int:
        return self.n * (self.m + 1) + 2
    
