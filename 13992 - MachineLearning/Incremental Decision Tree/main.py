from id5Classifier import Id5Classifier
from dataSet import Instance, DataSet
from validator import Validator

def main():
    #--------------------------------------------------------
    # Import DataSet:
    #--------------------------------------------------------
    fileName = input("Enter data file name:")
    sheetName = input("Enter data sheet name:")
    if fileName == "":
        fileName = "data.xls"
    if sheetName == "":
        sheetName = "student-mat"
    dataSet = DataSet.importXls(fileName, sheetName)
    print("-------------------------------------------------")
    
    #--------------------------------------------------------
    # Sample visual representation of the model (ID5 Tree):
    #--------------------------------------------------------
    model = Id5Classifier.train(dataSet = dataSet[:30])
    print("Sample visual representation of the model (ID5 Tree):")
    model.print()
    print("-------------------------------------------------")
    
    #--------------------------------------------------------
    # 5-fold cross validation of the model:
    #--------------------------------------------------------
    print("Accuracy of model by 5-fold cross validation:")
    accuracy = Validator.kFoldValidate(
        foldCount = 5,
        trainMethod = Id5Classifier.train,
        testMethod = Id5Classifier.test,
        dataSet = dataSet
        )
    print("Average:")
    print(accuracy)
    print("-------------------------------------------------")
  
    #--------------------------------------------------------
    # Training and testing on the whole dataset:
    #--------------------------------------------------------
    accuracy = Validator.validate(
        trainMethod = Id5Classifier.train,
        testMethod = Id5Classifier.test,
        trainDataSet = dataSet,
        testDataSet = dataSet
        )
    print("Accuracy of training and testing on the whole dataset:")
    print(accuracy)
    print("-------------------------------------------------")
    
    #--------------------------------------------------------
    #--------------------------------------------------------
    # Reduced Error Pruning:
    #--------------------------------------------------------
    #--------------------------------------------------------
    # Sample visual representation of the model after REP:
    #--------------------------------------------------------
    model = Id5Classifier.trainAndPrune(dataSet = dataSet[:30])
    print("Sample visual representation of the model (ID5 Tree),")
    print("after Reduced Error Pruning:")
    model.print()
    print("-------------------------------------------------")

    #--------------------------------------------------------
    # 5-fold cross validation of the model after REP:
    #--------------------------------------------------------
    print("Accuracy of model by 5-fold cross validation,")
    print("after Reduced Error Pruning:")
    accuracy = Validator.kFoldValidate(
        foldCount = 5,
        trainMethod = Id5Classifier.trainAndPrune,
        testMethod = Id5Classifier.test,
        dataSet = dataSet
        )
    print("Average:")
    print(accuracy)
    print("-------------------------------------------------")
  
    #--------------------------------------------------------
    # Training and testing on the whole dataset after REP:
    #--------------------------------------------------------
    accuracy = Validator.validate(
        trainMethod = Id5Classifier.trainAndPrune,
        testMethod = Id5Classifier.test,
        trainDataSet = dataSet,
        testDataSet = dataSet
        )
    print("Accuracy of training and testing on the whole dataset,")
    print("after Reduced Error Pruning:")
    print(accuracy)
    print("-------------------------------------------------")
    #--------------------------------------------------------
    
    input("Press enter to exit ... ")
if __name__ == "__main__":
    main()
