from anytree import Node, RenderTree
import copy
import math

class Id5Classifier:
    @classmethod
    def train(cls, dataSet):
        def getEntropy(instances):
            positiveCount = 0
            negativeCount = 0
            for i in instances:
                if i.label == "yes":
                    positiveCount += 1
                elif i.label == "no":
                    negativeCount += 1
            if positiveCount == 0 or negativeCount == 0:
                return 0
            positiveProportion = positiveCount / (positiveCount + negativeCount)
            negativeProportion = 1 - positiveProportion
            return (
                - positiveProportion * math.log2(positiveProportion)
                - negativeProportion * math.log2(negativeProportion)
                )
        def getFeatureDistinctValues(feature, instances):
            featureDistinctValues = []
            for i in instances:
                if i.featureValues[feature] not in featureDistinctValues:
                    featureDistinctValues.append(i.featureValues[feature])
            return featureDistinctValues
        def getInformationGain(feature, instances):
            featureDistinctValues = getFeatureDistinctValues(feature, instances)
            totalCount = len(instances)
            informationGain = getEntropy(instances)
            for fv in featureDistinctValues:
                subSetInstances = []
                for i in instances:
                    if i.featureValues[feature] == fv:
                        subSetInstances.append(i)
                subSetCount = len(subSetInstances)
                informationGain -= subSetCount / totalCount * getEntropy(subSetInstances)
            return informationGain
        def insertInstance(treeNode, instance):
            if treeNode == None:
                print("[!error] Empty node")
                return
            if treeNode.isLeaf:
                treeNode.leafSavedInstances.append(instance)
                if getEntropy(treeNode.leafSavedInstances) == 0:
                    return
                else:
                    potentialFeatures = treeNode.getPotentialFeatures(dataSet)
                    maxInformationGain = 0
                    selectedFeature = ""
                    for f in potentialFeatures:
                        informationGain = getInformationGain(f, treeNode.leafSavedInstances)
                        if informationGain > maxInformationGain:
                            maxInformationGain = informationGain
                            selectedFeature = f
                    if selectedFeature != "":
                        treeNode.expandLeafNode(selectedFeature)
            else:
                foundWhereToInsert = False
                for b in treeNode.childBranches:
                    if instance.featureValues[treeNode.decisionFeature] == b.featureValue:
                        foundWhereToInsert = True
                        insertInstance(b.childNode, instance)
                if not foundWhereToInsert:
                    newBranch = TreeBranch(
                        parentNode = treeNode,
                        featureValue = instance.featureValues[treeNode.decisionFeature],
                        childNode = None
                        )
                    treeNode.childBranches.append(newBranch)
                    newLeafNode = TreeNode(
                        parentBranch = newBranch,
                        isLeaf = True,
                        leafSavedInstances = [],
                        decisionFeature = None,
                        childBranches = None
                        )
                    newBranch.childNode = newLeafNode
                    insertInstance(newLeafNode, instance)
        def updateTree(treeNode):
            def pullUp(feature, treeNode):
                if treeNode.isLeaf:
                    treeNode.expandLeafNode(feature)
                elif treeNode.decisionFeature == feature:
                    return
                else:
                    for b in treeNode.childBranches:
                        pullUp(feature, b.childNode)
                    swapWithChilds(treeNode)
            def swapWithChilds(treeNode):
                decisionFeature1 = treeNode.decisionFeature
                featureValues1 = []
                decisionFeature2 = treeNode.childBranches[0].childNode.decisionFeature
                featureValues2 = []
                childsOfChilds = {}
                for b1 in treeNode.childBranches:
                    if not b1.featureValue in featureValues1:
                        featureValues1.append(b1.featureValue)
                    for b2 in b1.childNode.childBranches:
                        if not b2.featureValue in featureValues2:
                            featureValues2.append(b2.featureValue)
                        key = (b1.featureValue, b2.featureValue)
                        childsOfChilds[key] = b2.childNode
                for b1 in treeNode.childBranches:
                    for b2 in b1.childNode.childBranches:
                        del b2
                    del b1.childNode
                    del b1
                treeNode.decisionFeature = decisionFeature2
                treeNode.childBranches = []
                for fv2 in featureValues2:
                    newBranch2 = TreeBranch(
                        parentNode = treeNode,
                        featureValue = fv2,
                        childNode = None
                        )
                    treeNode.childBranches.append(newBranch2)
                    newDecisionNode1 = TreeNode(
                        parentBranch = newBranch2,
                        isLeaf = False,
                        leafSavedInstances = [],
                        decisionFeature = decisionFeature1,
                        childBranches = []
                        )
                    newBranch2.childNode = newDecisionNode1
                    for fv1 in featureValues1:
                        if (fv1, fv2) in list(childsOfChilds.keys()):
                            newBranch1 = TreeBranch(
                                parentNode = newDecisionNode1,
                                featureValue = fv1,
                                childNode = childsOfChilds[(fv1, fv2)]
                                )
                            newDecisionNode1.childBranches.append(newBranch1)
                            childsOfChilds[(fv1, fv2)].parentBranch = newBranch1
            if treeNode.isLeaf:
                return
            else:
                savedInstances = treeNode.getSavedInstances()
                currentInformationGain = getInformationGain(treeNode.decisionFeature, savedInstances)
                potentialFeatures = treeNode.getPotentialFeatures(dataSet)
                maxInformationGain = 0
                selectedFeature = ""
                for f in potentialFeatures:
                    informationGain = getInformationGain(f, savedInstances)
                    if informationGain > maxInformationGain:
                        maxInformationGain = informationGain
                        selectedFeature = f
                if maxInformationGain > currentInformationGain:
                    pullUp(selectedFeature, treeNode)
                for b in treeNode.childBranches:
                    updateTree(b.childNode)
        def shrinkTree(treeNode):
            if treeNode.isLeaf:
                return
            else:
                for b in treeNode.childBranches:
                    shrinkTree(b.childNode)
                savedInstances = treeNode.getSavedInstances()
                if getEntropy(savedInstances) == 0:
                    for b in treeNode.childBranches:
                        if b.childNode.isLeaf:
                            del b.childNode
                            del b
                    treeNode.isLeaf = True
                    treeNode.leafSavedInstances = savedInstances
                    treeNode.decisionFeature = None
                    treeNode.childBranches = []
        id5Tree = SubTree(rootNode = TreeNode())
        for i in dataSet:
            insertInstance(id5Tree.rootNode, i)
            updateTree(id5Tree.rootNode)
            shrinkTree(id5Tree.rootNode)
        return id5Tree
    @classmethod
    def test(cls, subTree, dataSet):
        trueCount = 0
        for i in dataSet:
            if subTree.rootNode.predict(i) == i.label:
                trueCount +=1
        accuracy = float(trueCount / len(dataSet))        
        return accuracy
    @classmethod
    def trainAndPrune(cls, dataSet):
        validationCount = int(len(dataSet) * 0.25)
        validationDataSet = dataSet[:validationCount]
        trainDataSet = dataSet[validationCount:]
        id5Tree = cls.train(trainDataSet)
        trainAccuracy = cls.test(id5Tree, validationDataSet)
        while True:
            prunedTree = copy.deepcopy(id5Tree)
            prunedTree.rootNode.pruneOnce()
            prunedAccuracy = cls.test(prunedTree, validationDataSet)
            if (prunedAccuracy < trainAccuracy
                or len(prunedTree.rootNode.getAllLeafNodes())
                == len(id5Tree.rootNode.getAllLeafNodes())):
                break
            else:
                id5Tree = prunedTree
                trainAccuracy = prunedAccuracy
        return id5Tree            
        
class SubTree:
    def __init__(self, parentBranch = None, rootNode = None):
        self.parentBranch = parentBranch
        self.rootNode = rootNode
    def print(self):
        if self == None or self.rootNode == None:
            visualTree = Node("Empty tree")
        else:
            visualTree = self.rootNode.getVisualNode()
        for pre, fill, node in RenderTree(visualTree):
            print("%s%s" % (pre, node.name))
class TreeNode:
    def __init__(self, parentBranch = None, isLeaf = True,
                 leafSavedInstances = [], # for leaf nodes
                 decisionFeature = None, childBranches = [] # for decision nodes
                 ):
        self.parentBranch = parentBranch
        self.isLeaf = isLeaf
        self.leafSavedInstances = leafSavedInstances
        self.decisionFeature = decisionFeature
        self.childBranches = childBranches
    def predict(self, instance):
        if self.isLeaf:
            return self.getLabel()
        else:
            for b in self.childBranches:
                if instance.featureValues[self.decisionFeature] == b.featureValue:
                    return b.childNode.predict(instance)
            return "not found"
    def expandLeafNode(self, feature):
        if not self.isLeaf:
            return self
        leafSavedInstances = copy.deepcopy(self.leafSavedInstances)
        featureDistinctValues = []
        for i in leafSavedInstances:
            if i.featureValues[feature] not in featureDistinctValues:
                featureDistinctValues.append(i.featureValues[feature])
        self.isLeaf = False
        self.leafSavedInstances = []
        self.decisionFeature = feature
        self.childBranches = []
        for fv in featureDistinctValues:
            newBranch = TreeBranch(
                parentNode = self,
                featureValue = fv,
                childNode = None
                )
            self.childBranches.append(newBranch)
            newLeafNode = TreeNode(
                parentBranch = newBranch,
                isLeaf = True,
                leafSavedInstances = [],
                decisionFeature = None,
                childBranches = None
                )
            newBranch.childNode = newLeafNode
            for i in leafSavedInstances:
                if i.featureValues[feature] == fv:
                    newLeafNode.leafSavedInstances.append(i)
    def shrinkDecisionNode(self):
        if self.isLeaf:
            return self
        savedInstances = self.getSavedInstances()
        for b in self.childBranches:
            b.childNode.shrinkDecisionNode()
            del b.childNode
            del b
        self.isLeaf = True
        self.leafSavedInstances = savedInstances
        self.decisionFeature = None
        self.childBranches = []
    def getPositiveCount(self, decisionFeature = None, featureValue = None):
        positiveCount = 0
        if self.isLeaf:
            for i in self.leafSavedInstances:
                if decisionFeature == None or featureValue == None:
                    if i.label == "yes":
                        positiveCount += 1
                elif i.featureValues[decisionFeature] == featureValue:
                    if i.label == "yes":
                        positiveCount += 1
        else:
            for b in self.childBranches:
                if self.decisionFeature == decisionFeature and b.featureValue == featureValue:
                    positiveCount += b.getPositiveCount()
                else:
                    positiveCount += b.getPositiveCount(decisionFeature, featureValue)
        return positiveCount           
    def getNegativeCount(self, decisionFeature = None, featureValue = None):
        negativeCount = 0
        if self.isLeaf:
            for i in self.leafSavedInstances:
                if decisionFeature == None or featureValue == None:
                    if i.label == "no":
                        negativeCount += 1
                elif i.featureValues[decisionFeature] == featureValue:
                    if i.label == "no":
                        negativeCount += 1
        else:
            for b in self.childBranches:
                if self.decisionFeature == decisionFeature and b.featureValue == featureValue:
                    negativeCount += b.getNegativeCount()
                else:
                    negativeCount += b.getNegativeCount(decisionFeature, featureValue)
        return negativeCount
    def getPotentialFeatures(self, dataSet):
        potentialFeatures = list(dataSet[0].featureValues.keys())
        treeNode = self
        while True:
            if not treeNode.isLeaf:
                potentialFeatures.remove(treeNode.decisionFeature)
            if treeNode.parentBranch == None:
                break
            treeNode = treeNode.parentBranch.parentNode
        return potentialFeatures
    def getLabel(self):
        if self.getPositiveCount() > self.getNegativeCount():
            return "yes"
        elif self.getPositiveCount() < self.getNegativeCount():
            return "no"
        else:
            return "unknown"
    def getSavedInstances(self):
        savedInstances = []
        if self.isLeaf:
            savedInstances.extend(self.leafSavedInstances)
        else:
            for b in self.childBranches:
                savedInstances.extend(b.childNode.getSavedInstances())
        return savedInstances
    def getAllLeafNodes(self):
        allLeafNodes = []
        if self.isLeaf:
            allLeafNodes.append(self)
        else:
            for b in self.childBranches:
                allLeafNodes.extend(b.childNode.getAllLeafNodes())
        return allLeafNodes
    def pruneOnce(self):
        allLeafNodes = self.getAllLeafNodes()
        parentOfLeafNodes = []
        for l in allLeafNodes:
            if (l.parentBranch != None
                and l.parentBranch.parentNode not in parentOfLeafNodes):
                parentOfLeafNodes.append(l.parentBranch.parentNode)
        maxProportion = 0
        selectedNode = None
        for p in parentOfLeafNodes:
            hasOnlyLeafNodes = True
            for b in p.childBranches:
                if not b.childNode.isLeaf:
                    hasOnlyLeafNodes = False
            if hasOnlyLeafNodes:
                positiveCount = p.getPositiveCount()
                negativeCount = p.getNegativeCount()
                proportion = (
                    abs(positiveCount - negativeCount)
                    / (positiveCount + negativeCount))
                if proportion > maxProportion:
                    maxProportion = proportion
                    selectedNode = p
        if selectedNode != None:
            selectedNode.shrinkDecisionNode()
        return
    def getVisualNode(self):
        if self == None:
            return Node("Empty node")
        elif self.isLeaf:
            return Node("<" + self.getLabel() + ">"
                        + "(y:" + str(self.getPositiveCount())
                        + ",n:" + str(self.getNegativeCount())
                        + ")"
                        )
        else:
            visualNode = Node(self.decisionFeature)
            for b in self.childBranches:
                visualBranch = b.getVisualNode()
                visualBranch.parent = visualNode
            return visualNode
class TreeBranch:
    def __init__(self, parentNode = None, featureValue = None, childNode = None):
        self.parentNode = parentNode
        self.featureValue = featureValue
        self.childNode = childNode
    def getPositiveCount(self, decisionFeature, featureValue):
        return self.childNode.getPositiveCount(decisionFeature, featureValue)           
    def getNegativeCount(self, decisionFeature, featureValue):
        return self.childNode.getNegativeCount(decisionFeature, featureValue)          
    def getVisualNode(self):
        if self == None:
            return Node("Empty branch")
        else:
            visualBranch = Node(str(self.featureValue))
            visualNode = self.childNode.getVisualNode()
            visualNode.parent = visualBranch
            return visualBranch
