import xlrd

class Instance:
    def __init__(self, featureValues = [], label = None):
        self.featureValues = featureValues
        self.label = label
class DataSet:
    @classmethod
    def importXls(cls, fileName, sheetName):
        workBook = xlrd.open_workbook(fileName)
        inputSheet =  workBook.sheet_by_name(sheetName)
        rowCount = inputSheet.nrows
        colCount = inputSheet.ncols
        features = []
        for col in range(0, colCount-1):
            features.append(inputSheet.cell(0, col).value)
        instances = []
        for row in range(1, rowCount):
            values = []
            for col in range(0, colCount-1):
                values.append(inputSheet.cell(row, col).value)
            label = inputSheet.cell(row, colCount-1).value
            featureValues = {}
            for i in range(len(features)):
                featureValues[features[i]] = values[i]
            instances.append(Instance(featureValues, label))
        return instances
