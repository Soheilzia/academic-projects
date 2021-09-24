import random
import matplotlib.pyplot as plt
from benchmarkFunctions import SphereFunction
from benchmarkFunctions import BentCigarFunction
from benchmarkFunctions import RastriginsFunction
from benchmarkFunctions import AckleysFunction
from geneticAlgorithmSolver import GeneticAlgorithmSolver
def main():
    variableCount = 30
    functionList = [SphereFunction,
                    BentCigarFunction,
                    RastriginsFunction,
                    AckleysFunction]
    functionNameList = ['SphereFunction',
                        'BentCigarFunction',
                        'RastriginsFunction',
                        'AckleysFunction']
    #---------------------------------------------------------------------
    # Plot error of classic and 4 enhanced algorithms
    # in each population on 4 benchmark functions
    #---------------------------------------------------------------------
    populationCount = 40
    for function in functionList:
        populationErrorList = []
        #------------- Classic algorithm
        random.seed(1)
        solver = GeneticAlgorithmSolver(function = function,
                                        variableCount = variableCount,
                                        populationCount = populationCount)
        solver.solve()
        populationErrorList.append(solver.getPopulationErrorList())
        #------------- Enhanced algorithm 1 (compare after cross over)
        random.seed(1)
        solver = GeneticAlgorithmSolver(function = function,
                                        variableCount = variableCount,
                                        populationCount = populationCount,
                                        compareAfterCrossOver = True
                                        )
        solver.solve()
        populationErrorList.append(solver.getPopulationErrorList())
       #------------- Enhanced algorithm 2 (compare candidate populations)
        random.seed(1)
        solver = GeneticAlgorithmSolver(function = function,
                                        variableCount = variableCount,
                                        populationCount = populationCount,
                                        compareCandidatePopulations = True
                                        )
        solver.solve()
        populationErrorList.append(solver.getPopulationErrorList())
        #------------- Enhanced algorithm 3 (compare after mutation)
        random.seed(1)
        solver = GeneticAlgorithmSolver(function = function,
                                        variableCount = variableCount,
                                        populationCount = populationCount,
                                        compareAfterMutation = True
                                        )
        solver.solve()
        populationErrorList.append(solver.getPopulationErrorList())
        #------------- Enhanced algorithm 4 (all together)
        random.seed(1)
        solver = GeneticAlgorithmSolver(function = function,
                                        variableCount = variableCount,
                                        populationCount = populationCount,
                                        compareAfterCrossOver = True,
                                        compareCandidatePopulations = True,
                                        compareAfterMutation = True
                                        )
        solver.solve()
        populationErrorList.append(solver.getPopulationErrorList())
        #------------- Plot populationErrorList
        xpoints = range(0, populationCount)
        ypoints0 = populationErrorList[0]
        ypoints1 = populationErrorList[1]
        ypoints2 = populationErrorList[2]
        ypoints3 = populationErrorList[3]
        ypoints4 = populationErrorList[4]
        lineWidth = 0.4
        plt.rcParams['figure.figsize'] = (15,5)
        plt.plot(xpoints, ypoints0, color='black',
                 linewidth=lineWidth,
                 label='Classic algorithm')
        plt.plot(xpoints, ypoints1, color='red',
                 linewidth=lineWidth,
                 label='Enhanced algorithm 1')
        plt.plot(xpoints, ypoints2, color='orange',
                 linewidth=lineWidth,
                 label='Enhanced algorithm 2')
        plt.plot(xpoints, ypoints3, color='green',
                 linewidth=lineWidth,
                 label='Enhanced algorithm 3')
        plt.plot(xpoints, ypoints4, color='blue',
                 linewidth=lineWidth,
                 label='Enhanced algorithm 4')
        plt.xlabel('Population')
        plt.ylabel('Error')
        plt.title(functionNameList[functionList.index(function)])
        plt.legend()
        plt.show()
    #---------------------------------------------------------------------
    # Compare mean error of classic and 4 enhanced algorithms
    # on 4 benchmark functions
    #---------------------------------------------------------------------
    iterationCount = 51
    populationCount = 300
    for function in functionList:
        #------------- Classic algorithm
        sumError = 0.0
        meanError = 0.0
        random.seed(1)
        for i in range(0, iterationCount):
            solver = GeneticAlgorithmSolver(function = function,
                                            variableCount = variableCount,
                                            populationCount = populationCount
                                            )
            sumError += solver.solve()
        meanError = float(sumError / iterationCount)
        print("-----------------------------------------")
        print("Classic algorithm for "
              + functionNameList[functionList.index(function)] + ":")
        print(meanError)
        #------------- Enhanced algorithm 1 (compare after cross over)
        sumError = 0.0
        meanError = 0.0
        random.seed(1)
        for i in range(0, iterationCount):
            solver = GeneticAlgorithmSolver(function = function,
                                            variableCount = variableCount,
                                            populationCount = populationCount,
                                            compareAfterCrossOver = True
                                            )
            sumError += solver.solve()
        meanError = float(sumError / iterationCount)
        print("Enhanced algorithm 1 (compare after cross over):")
        print(meanError)
        #------------- Enhanced algorithm 2 (compare candidate populations)
        sumError = 0.0
        meanError = 0.0
        random.seed(1)
        for i in range(0, iterationCount):
            solver = GeneticAlgorithmSolver(function = function,
                                            variableCount = variableCount,
                                            populationCount = populationCount,
                                            compareCandidatePopulations = True
                                            )
            sumError += solver.solve()
        meanError = float(sumError / iterationCount)
        print("Enhanced algorithm 2 (compare candidate populations):")
        print(meanError)
        #------------- Enhanced algorithm 3 (compare after mutation)
        sumError = 0.0
        meanError = 0.0
        random.seed(1)
        for i in range(0, iterationCount):
            solver = GeneticAlgorithmSolver(function = function,
                                            variableCount = variableCount,
                                            populationCount = populationCount,
                                            compareAfterMutation = True
                                            )
            sumError += solver.solve()
        meanError = float(sumError / iterationCount)
        print("Enhanced algorithm 3 (compare after mutation):")
        print(meanError)
        #------------- Enhanced algorithm 4 (all together)
        sumError = 0.0
        meanError = 0.0
        random.seed(1)
        for i in range(0, iterationCount):
            solver = GeneticAlgorithmSolver(function = function,
                                            variableCount = variableCount,
                                            populationCount = populationCount,
                                            compareAfterCrossOver = True,
                                            compareCandidatePopulations = True,
                                            compareAfterMutation = True
                                            )
            sumError += solver.solve()
        meanError = float(sumError / iterationCount)
        print("Enhanced algorithm 4 (all together)")
        print(meanError)
    #---------------------------------------------------------------------
if __name__ == "__main__":
    main()
