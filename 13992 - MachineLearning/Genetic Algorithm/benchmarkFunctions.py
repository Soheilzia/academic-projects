import math
class IBenchmarkFunction:
    @classmethod
    def getMinRangeOfVariables(cls):
        pass
    @classmethod
    def getMaxRangeOfVariables(cls):
        pass
    @classmethod
    def getGlobalMinimum(cls):
        pass
    @classmethod
    def getGlobalMaximum(cls):
        pass
    @classmethod
    def calculate(cls, variables):
        pass
class SphereFunction(IBenchmarkFunction):
    @classmethod
    def getMinRangeOfVariables(cls):
        return -5.12
    @classmethod
    def getMaxRangeOfVariables(cls):
        return 5.12
    @classmethod
    def getGlobalMinimum(cls):
        return 0
    @classmethod
    def getGlobalMaximum(cls):
        raise Exception('This function has no global maximum')
        return
    @classmethod
    def calculate(cls, variables):
        result = 0.0
        for x in variables:
            result += x ** 2
        return result
class BentCigarFunction(IBenchmarkFunction):
    @classmethod
    def getMinRangeOfVariables(cls):
        return -5.12
    @classmethod
    def getMaxRangeOfVariables(cls):
        return 5.12
    @classmethod
    def getGlobalMinimum(cls):
        return 0
    @classmethod
    def getGlobalMaximum(cls):
        raise Exception('This function has no global maximum')
        return
    @classmethod
    def calculate(cls, variables):
        result = variables[0] ** 2
        for i in range(1, len(variables)):
            result += (10 ** 6) * (variables[i] ** 2)
        return result
class RastriginsFunction(IBenchmarkFunction):
    @classmethod
    def getMinRangeOfVariables(cls):
        return -5.12
    @classmethod
    def getMaxRangeOfVariables(cls):
        return 5.12
    @classmethod
    def getGlobalMinimum(cls):
        return 0
    @classmethod
    def getGlobalMaximum(cls):
        raise Exception('This function has no global maximum')
        return
    @classmethod
    def calculate(cls, variables):
        result = 10 * len(variables)
        for x in variables:
            result += x ** 2 - 10 * math.cos(2 * math.pi * x)
        return result
class AckleysFunction(IBenchmarkFunction):
    @classmethod
    def getMinRangeOfVariables(cls):
        return -5.12
    @classmethod
    def getMaxRangeOfVariables(cls):
        return 5.12
    @classmethod
    def getGlobalMinimum(cls):
        return 0
    @classmethod
    def getGlobalMaximum(cls):
        raise Exception('This function has no global maximum')
        return
    @classmethod
    def calculate(cls, variables):
        sumX2 = 0.0
        for x in variables:
            sumX2 += x ** 2
        sumCos2PiX = 0.0
        for x in variables:
            sumCos2PiX += math.cos(2 * math.pi * x)            
        result = (
            - 20 * math.exp(- 0.2 * math.sqrt(sumX2 / len(variables)))
            - math.exp(sumCos2PiX / len(variables))
            + 20 + math.exp(1)
            )
        return result

        
