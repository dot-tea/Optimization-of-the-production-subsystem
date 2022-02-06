import numpy as np
from ClassProductionSubsystem import ProductionSubsystem
# Структура сложного преобразователя

class СomplicatedConverter (ProductionSubsystem):
    
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
        return int(self.m*(self.n+2))     

    def p (self):
        return int(((self.n+1)*(self.n+2*self.m)+2)/2)

    def N(self,i,j):
        return int((self.n-1)*i-((i-1)*i)/2+j-1)

    def R(self,l,i):
        return int(self.N(self.n-1,self.n)+(l-1)*self.n+i)

    def N_F(self,i):
        return int (self.p()-1-(self.m-1)-(self.n+1)+i)

    def R_F(self,i):
        '''
        Возвращает индекс компонента факторного вектора,
        соответствующего кол-ву передаваемых вспомогательных
        ресурсов из процесса i-го уровня на конечный процесс
        F
        '''
        return int (self.p()-1-(self.m-1)+i-1)
    
    # Стоп, почему тут нельзя присвоить напрямую c[p-1] = -1?
    def formC (self):
        c=np.zeros(self.p(), dtype=float)
        for i in np.arange(0,self.p()):
            if i == self.p()-1:
                c[i]=-1.
        return c

    def formA(self):
        M=np.zeros((self.u(), self.p()), dtype=float)
                
        for i in np.arange(1,self.n+1): 
            M[0][self.N(0,i)]=1.0
            M[0][self.N_F(0)]=1.0
            for l in np.arange(1,self.m):
                M[l][self.R(l,i)]=M[l][self.R_F(l)]=1.0
                
        for i in np.arange(1,self.n): 
            for l in np.arange(0,i):
                M[self.m+self.m*(i-1)][self.N(l,i)]=-float(self.A.sum(axis=1)[i]/self.A[i][0])
            for j in np.arange(i+1,self.n+1):
                M[self.m+self.m*(i-1)][self.N(i,j)]=1.0
            M[self.m+self.m*(i-1)][self.N_F(i)]=1.0#1 заменить на e_i
            for k in np.arange(1,self.m):
                M[self.m+self.m*(i-1)+k][self.R(k,i)]=-float(self.A.sum(axis=1)[i]/self.A[i][k])
                for j in np.arange(i+1,self.n+1):
                    M[self.m+self.m*(i-1)+k][self.N(i,j)]=1.0
                M[self.m+self.m*(i-1)+k][self.N_F(i)]=1.0
        
        for l in np.arange(0,self.n): 
            M[self.u()-2*self.m][self.N(l,self.n)]=-float(self.A.sum(axis=1)[self.n]/self.A[self.n][0])
        M[self.u()-2*self.m][self.N_F(self.n)]=1.0 
        for k in np.arange(1,self.m):
            M[self.u()-2*self.m+k][self.R(k,self.n)]=-float(self.A.sum(axis=1)[self.n]/self.A[self.n][k])
            M[self.u()-2*self.m+k][self.N_F(self.n)]=1.0
        
        for i in np.arange(0,self.n+1):
            M[self.u()-self.m][self.N_F(i)]=-float(self.A.sum(axis=1)[0]/self.A[0][0])
            M[self.u()-self.m][self.p()-1]=1.0;
        for k in np.arange(1,self.m):
            M[self.u()-self.m+k][self.R_F(k)]=-float(self.A.sum(axis=1)[0]/self.A[0][k])
            M[self.u()-self.m+k][self.p()-1]=1.0
        return M
            
        
            
            
        
            



