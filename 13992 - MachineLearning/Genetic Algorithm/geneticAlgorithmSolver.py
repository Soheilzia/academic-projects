import random
class GeneticAlgorithmSolver:
    def __init__(self,
                 function,
                 variableCount,
                 findMinimum = True,
                 binaryVariableLength = 8,
                 chromosomeCount = 10,
                 populationCount = 30,
                 crossOverProbability = 0.8,
                 geneMutationProbability = 0.1,
                 compareAfterCrossOver = False,
                 compareAfterMutation = False,
                 compareCandidatePopulations = False,
                 candidatePopulationCount = 5
                 ):
        if variableCount <= 0:
            raise Exception("variableCount should be > 0")
        if binaryVariableLength <= 0:
            raise Exception("binaryVariableLength should be > 0")
        if chromosomeCount <= 0:
            raise Exception("chromosomeCount should be > 0")
        if chromosomeCount % 2 == 1:
            raise Exception("chromosomeCount should be even")
        if populationCount <= 0:
            raise Exception("populationCount should be > 0")
        if crossOverProbability < 0 or crossOverProbability > 1:
            raise Exception("crossOverProbability should be between 0 and 1")
        if geneMutationProbability < 0 or geneMutationProbability > 1:
            raise Exception("geneMutationProbability should be between 0 and 1")
        if candidatePopulationCount <= 0:
            raise Exception("candidatePopulationCount should be > 0")
        self.__function = function
        self.__variableCount = int(variableCount)
        self.__findMinimum = bool(findMinimum)
        self.__binaryVariableLength = int(binaryVariableLength)
        self.__chromosomeCount = int(chromosomeCount)
        self.__populationCount = int(populationCount)
        self.__crossOverProbability = float(crossOverProbability)
        self.__geneMutationProbability = float(geneMutationProbability)
        self.__compareAfterCrossOver = bool(compareAfterCrossOver)
        self.__compareAfterMutation = bool(compareAfterMutation)
        self.__compareCandidatePopulations = bool(compareCandidatePopulations)
        self.__candidatePopulationCount = int(candidatePopulationCount)
        self.__solved = False
        self.__populationErrorList = []
        self.__optimumVariableList = []
        self.__optimumResult = 0.0
    def solve(self):
        def convertChromosomeToVariableList(chromosome):
            variableList = []
            for v in range(0, self.__variableCount):
                binaryVariable = chromosome[v * self.__binaryVariableLength :
                                            (v + 1) * self.__binaryVariableLength]
                variable = (int(binaryVariable, 2) *
                            (self.__function.getMaxRangeOfVariables()
                             - self.__function.getMinRangeOfVariables())
                            / (2**self.__binaryVariableLength - 1)
                            + self.__function.getMinRangeOfVariables())
                variableList.append(variable)
            return variableList
        def calcualteValue(chromosome):
            variableList = convertChromosomeToVariableList(chromosome)
            value = self.__function.calculate(variableList)
            return value
        def generateFirstPopulation():
            firstPopulation = []
            for c in range(0, self.__chromosomeCount):
                newChromosome = ''
                for v in range(0, self.__variableCount):
                    newRandom = random.randint(0,
                                               2**self.__binaryVariableLength - 1)
                    newBinaryVariable = format(newRandom, '0'
                                  + str(self.__binaryVariableLength)
                                  + 'b')
                    newChromosome += newBinaryVariable
                firstPopulation.append(newChromosome)
            return firstPopulation
        def calculateFitness(population):
            valueList = []
            for c in range(0, len(population)):
                chromosome = population[c]
                value = calcualteValue(chromosome)
                valueList.append(value)
            sumValue = sum(valueList)
            fitnessList = []
            if self.__findMinimum:
                maxValue = max(valueList)
                for c in range(0, len(population)):
                    fitness = ((- valueList[c] + maxValue + 1)
                               /(- sumValue + (maxValue + 1)
                                 * len(population)))
                    fitnessList.append(fitness)
            else:
                minVlaue = min(valueList)
                for c in range(0, len(population)):
                    fitness = ((valueList[c] - minValue + 1)
                               /(sumValue + (- minValue + 1)
                                 * len(population)))
                    fitnessList.append(fitness)
            return fitnessList
        def selectRandomChromosome(population, fitnessList):
            newRandom = random.uniform(0,1)
            boundry = 0
            for c in range(0, len(population)):
                chromosome = population[c]
                boundry += fitnessList[c]
                if boundry > newRandom:
                    return chromosome
        def selectBestChromosome(population, fitnessList):
            maxFitness = max(fitnessList)
            indexOfMaxFitness = fitnessList.index(maxFitness)
            return population[indexOfMaxFitness]
        def crossOver(parentChromosome1, parentChromosome2):
            newRandom = random.uniform(0,1)
            if self.__crossOverProbability > newRandom:
                onePoint = random.randint(1,
                                          (self.__binaryVariableLength
                                           * self.__variableCount -1))
                childChromosome1 = (parentChromosome1[:onePoint]
                                    + parentChromosome2[onePoint:])
                childChromosome2 = (parentChromosome2[:onePoint]
                                    + parentChromosome1[onePoint:])
            else:
                childChromosome1 = parentChromosome1
                childChromosome2 = parentChromosome2
            return childChromosome1, childChromosome2
        def crossOverAndCompare(parentChromosome1, parentChromosome2):
            childChromosome1, childChromosome2 = (
                crossOver(parentChromosome1, parentChromosome2)
                )
            if self.__findMinimum:
                if (calcualteValue(parentChromosome1)
                    < calcualteValue(childChromosome1)):
                    childChromosome1 = parentChromosome1
                if (calcualteValue(parentChromosome2)
                    < calcualteValue(childChromosome2)):
                    childChromosome2 = parentChromosome2
            else:
                if (calcualteValue(parentChromosome1)
                    > calcualteValue(childChromosome1)):
                    childChromosome1 = parentChromosome1
                if (calcualteValue(parentChromosome2)
                    > calcualteValue(childChromosome2)):
                    childChromosome2 = parentChromosome2
            return childChromosome1, childChromosome2
        def mutate(chromosome):
            newChromosome = ''
            for g in range(0, len(chromosome)):
                newRandom = random.uniform(0,1)
                if self.__geneMutationProbability > newRandom:
                    newChromosome += str(1 - int(chromosome[g]))
                else:
                    newChromosome += chromosome[g]
            return newChromosome
        def mutateAndCompare(chromosome):
            newChromosome = mutate(chromosome)
            if self.__findMinimum:
                if (calcualteValue(newChromosome)
                    < calcualteValue(chromosome)):
                    return newChromosome
                else:
                    return chromosome
            else:
                if (calcualteValue(newChromosome)
                    > calcualteValue(chromosome)):
                    return newChromosome
                else:
                    return chromosome
        def getChromosomeError(chromosome):
            value = calcualteValue(chromosome)
            if self.__findMinimum:
                return (value
                        - self.__function.getGlobalMinimum()
                        ) ** 2
            else:
                return (value
                        - self.__function.getGlobalMaximum()
                        ) ** 2
        def getPopulationError(population, fitnessList):
            bestChromosome = selectBestChromosome(population, fitnessList)
            return getChromosomeError(bestChromosome)
        def findOptimum():
            self.__solved = False
            self.__populationErrorList = []
            self.__optimumVariableList = []
            self.__optimumResult = []
            currentPopulation = generateFirstPopulation()
            currentFitnessList = calculateFitness(currentPopulation)
            self.__populationErrorList.append(
                getPopulationError(currentPopulation, currentFitnessList))
            for p in range(1, self.__populationCount):
                if not self.__compareCandidatePopulations:
                    self.__candidatePopulationCount = 1
                else:
                    currentBestValue = calcualteValue(currentPopulation[0])
                    for c in range(1, self.__chromosomeCount):
                        tempValue = calcualteValue(currentPopulation[c])
                        if self.__findMinimum:
                            if tempValue < currentBestValue:
                                currentBestValue = tempValue
                        else:
                            if tempValue > currentBestValue:
                                currentBestValue = tempValue
                newPopulation = currentPopulation
                for cp in range(0, self.__candidatePopulationCount):
                    candidatePopulation = []
                    for c in range(0, int(self.__chromosomeCount / 2)):
                        chromosome1 = selectRandomChromosome(currentPopulation,
                                                             currentFitnessList)
                        chromosome2 = selectRandomChromosome(currentPopulation,
                                                             currentFitnessList)
                        if self.__compareAfterCrossOver:
                            child1, child2 = crossOverAndCompare(chromosome1,
                                                                 chromosome2)
                        else:
                            child1, child2 = crossOver(chromosome1,
                                                       chromosome2)
                        if self.__compareAfterMutation:
                            mutated1 = mutateAndCompare(child1)
                            mutated2 = mutateAndCompare(child2)
                        else:
                            mutated1 = mutate(child1)
                            mutated2 = mutate(child2)
                        candidatePopulation.append(mutated1)
                        candidatePopulation.append(mutated2)
                    if self.__compareCandidatePopulations:
                        candidateBestValue = calcualteValue(
                            candidatePopulation[0])
                        for c in range(1, self.__chromosomeCount):
                            tempValue = calcualteValue(candidatePopulation[c])
                            if self.__findMinimum:
                                if tempValue < candidateBestValue:
                                    candidateBestValue = tempValue
                            else:
                                if tempValue > candidateBestValue:
                                    candidateBestValue = tempValue
                        if self.__findMinimum:
                            if candidateBestValue < currentBestValue:
                                currentBestValue = candidateBestValue
                                newPopulation = candidatePopulation
                        else:
                            if candidateBestValue > currentBestValue:
                                currentBestValue = candidateBestValue
                                newPopulation = candidatePopulation
                    else:
                        newPopulation = candidatePopulation
                currentPopulation = newPopulation
                currentFitnessList = calculateFitness(currentPopulation)
                self.__populationErrorList.append(
                    getPopulationError(currentPopulation, currentFitnessList))
                self.__solved = True
                optimumChromosome = selectBestChromosome(currentPopulation,
                                                         currentFitnessList)
                self.__optimumVariableList = (
                    convertChromosomeToVariableList(optimumChromosome))
                self.__optimumResult = (
                    self.__function.calculate(self.__optimumVariableList))
            return self.getFinalError()
        return findOptimum()
    def getOptimumVariableList(self):
        if not self.__solved:
            return 'not solved'
        return self.__optimumVariableList
    def getOptimumResult(self):
        if not self.__solved:
            return 'not solved'
        return self.__optimumResult
    def getPopulationErrorList(self):
        if not self.__solved:
            return 'not solved'
        else:
            return self.__populationErrorList
    def getFinalError(self):
        if not self.__solved:
            return 'not solved'
        if self.__findMinimum:
            return (self.__optimumResult
                    - self.__function.getGlobalMinimum()
                    ) ** 2
        else:
            return (self.__optimumResult
                    - self.__function.getGlobalMaximum()
                    ) ** 2
    def printSolution(self):
        if not self.__solved:
            print('not solved')
            return
        printString='f('
        for v in range(0, self.__variableCount):
            if v != 0:
                printString += ','
            printString += str(self.__optimumVariableList[v])
        printString += ')=' + str(self.getOptimumResult())
        printString += ' Error=' + str(self.getFinalError())
        print(printString)
        return


        
