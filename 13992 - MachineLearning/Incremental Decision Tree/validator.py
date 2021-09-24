class Validator:
    @classmethod
    def kFoldValidate(cls, foldCount, trainMethod, testMethod, dataSet):
        sumAccuracy = 0
        foldLength = int(len(dataSet) / foldCount)
        print("Accuracy of each fold:")
        for f in range(0, foldCount):
            trainDataSet = dataSet[: f * foldLength] + dataSet[(f+1) * foldLength :]
            testDataSet = dataSet[f * foldLength : (f+1) * foldLength]
            accuracy = cls.validate(trainMethod, testMethod, trainDataSet, testDataSet)
            print(f+1, ',', accuracy)
            sumAccuracy += accuracy
        return float(sumAccuracy / foldCount)
    @classmethod
    def validate(cls, trainMethod, testMethod, trainDataSet, testDataSet):
        accuracy = 0
        model = trainMethod(trainDataSet)
        accuracy = testMethod(model, testDataSet)
        return accuracy
        
