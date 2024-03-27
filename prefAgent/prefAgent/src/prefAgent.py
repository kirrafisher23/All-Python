from pysat.solvers import Solver, Glucose4
from pysat.formula import CNF
from prettytable import PrettyTable  
import copy
import random
import os

# stream von dutch charli xcx

def readFile(filepath):
    with open(filepath,'r') as file:
        contents  = file.readlines() # gets list of lines
        return contents
    
def parseAttributes(rawData):
    #rawData will be used to call upon the .txt file in question
    attributes = {} #stores all of attrbutes once parsed into this dictionary
    i = 0
    orderOfAtt = {}
    
    for line in rawData:
        key, value  = line.strip().split(":") #this is assuming each line is a key value i beleive this is correct
        tempVal = value.split(",")
        value = []
        for val in tempVal:
            value.append(val.strip())
        attributes[key] = value
        orderOfAtt[i] = key
        i += 1 
        # need to throw exceptions for numbers to give errors 
    #print(attributes)
    return (attributes,orderOfAtt)

def parseConstraints(rawData):
    constraints = []
    for line in rawData:
        #this assumes at the moment the constraint is a space-separated list of literals (i think i am right since it is a single sentence)
        constraint = [ x for x in line.strip().split(" ")]
        constraints.append(constraint)
        # need to throw exceptions for numbers to give errors 
    #print (constraints)
    return constraints


def parsePenaltyLogic(filepath):
    penalties = []
    with open(filepath, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            rule = parts[0].strip()
            penalty_value = int(parts[1].strip())
            penalties.append((rule, penalty_value))
    #print("pen",penalties)
    return penalties

def parseQL(rawData):
    ql = []
    for line in rawData:
        ql.append(line.strip())
    return ql
        
       
def encoding(attributes, orderOfAtt):
    atributesEnc = {}
    countOfKey = len(attributes.keys())
    options = pow(2, countOfKey)
    for i in range(options): 
        temp = '{0:0'+str(countOfKey)+'b}'
        binRep = temp.format(i) # format i into a binary string with leading zeros
        storeEnc = []
        for j in range(countOfKey):
            partOfMeal = attributes.get(orderOfAtt[j])
            item = 1-int(binRep[j]) # determine which item (0 or 1) is represented by the j-th bit
            storeEnc.append(partOfMeal[item])
        atributesEnc[binRep] = storeEnc

    # Move this outside of the nested loop so it only prints once per unique encoding
    for binRep, attrs in atributesEnc.items():
        print(f"Encoding: o{binRep} - {', '.join(attrs)}")

    return atributesEnc

def varMapping(attributes):
    varMap = {}
    counter = 1
    for attr in attributes:
        values = attributes[attr]
        # Assign positive to the first value and negative to the second
        varMap[f"{attr}={values[0]}"] = counter
        varMap[f"{attr}={values[1]}"] = -counter
        counter += 1
    return varMap


def encodeConstraintsToCNF(attributes, constraints, varMap):
    clauses = []
    #print("var", varMap)
    for constraint in constraints:
        #print("Processing constraint:", constraint)
        currentClause = []
        for literal in constraint:
            #print("Current literal:", literal)
            if literal == "NOT":
                negationPend = True
            elif literal == "AND":
                clauses.append(currentClause)
                currentClause = []  # reset for new clause
                negationPend = False  # reset negation flag for new clause
            elif literal == "OR":
                continue  #  handled by appending literals to currentClause
            else:
                varKey =''
                #print("literal", literal)
                for i in attributes.keys():
                    #print("what i is",i)
                    if literal in attributes[i]:
                        #print("att of i", attributes[i])
                        attr = i
                        varKey = f"{attr}={literal}"
                        break
                    else:
                        continue
                varID = varMap[varKey]
                if negationPend:  # apply negation if pending
                    varID = -varID
                   # print("Appending literal to current clause:", varID)
                    currentClause.append(varID)
                    negationPend = False  # reset negation flag after use
        if len(currentClause) < len(attributes.keys()):
            tempSet = set(list(range(1,1+len(attributes.keys()))))
            #print("temp",tempSet)
            for c in currentClause:
                if c in tempSet:
                    tempSet.remove(c)
                if -c in tempSet:
                    tempSet.remove(-c)
            for t in tempSet:
                tempClause = copy.deepcopy(currentClause)
                tempClause.append(-t)
                currentClause.append(t)
                clauses.append(tempClause)
        clauses.append(currentClause)
        # append the last processed clause
    cnf = CNF(from_clauses=clauses)
    #print("Current clause to be appended:", currentClause)
    #print("CNF PRINT", cnf.clauses)
    return cnf


def feasCheck(cnf):
    # Initialize an empty list to store models if you want to enumerate all models
    allModels = []
    
    # initializes a context manager that creates an instance of a SAT solver
    with Solver(name="Glucose4", bootstrap_with=cnf) as solver:  # Ensure the solver is specified correctly
        isSatisfiable = solver.solve()
        
        # If you want to enumerate models, do it here and store them
        if isSatisfiable:
            for model in solver.enum_models():
                allModels.append(model)
                
        # Now, return the satisfiability result and the models
        return isSatisfiable, allModels  # Return all found models if that is the intent
    

def penTable(atributesEnc, penalties, model, varMap, orderOfAtt):
    table = PrettyTable()
    table.field_names = ["encoding"] + [f"{rule}" for rule, _ in penalties] + ["total penalty"]

    # iter over each attribute encoding
    for attr, attrs in atributesEnc.items():
        # checks if the attribute encoding matches any model; skips if not
        if not any(all(varMap[f"{orderOfAtt[i]}={attrs[i]}"] == m[i] for i in range(len(attrs))) for m in model):
            continue

        totalPenalty = 0  # the total penalty for the current attribute encoding
        row = [attr] #  new row with the attribute encoding
        
        # iter over each penalty rule
        for pen in penalties:
            penVal = pen[1]
            attrPen = pen[0].split()
            penAtt = [p for p in attrPen if p not in ['AND', 'OR', 'NOT']]

            #flags for logic operations 
            isOr = 'OR' in attrPen
            isAnd = 'AND' in attrPen
            isNot = 'NOT' in attrPen

            penalty = penVal  # start with the full penalty value

        ## apply pen from logic operators  
            if isOr:
                if any(p in attrs for p in penAtt):
                    penalty = 0  # reduce penalty to 0 if any attribute value is present
            elif isAnd:
                if all(p in attrs for p in penAtt):
                    penalty = 0  # reduce penalty to 0 if all attribute values are present
            else:
                if isNot:
                    if any(p in attrs for p in penAtt):
                        penalty = 0  # reduce penalty to 0 if any attribute value is present
                else:
                    if not all(p in attrs for p in penAtt):
                        penalty = 0  # reduce penalty to 0 if any attribute value is missing

            row.append(penalty) # adds the calculated penalty to the row
            totalPenalty += penalty # adds the penalty to the total penalty for the current encoding

        row.append(totalPenalty)  # adds the total penalty to the row
        table.add_row(row)

    print(table)
    
    
def exemplification(model, penalties, atributesEnc, varMap, orderOfAtt):
    if len(model) < 2:
        print("Not enough feasible objects for exemplification.") # base case if you will
        return

    obj1, obj2 = random.sample(model, 2)

    # calcs the penalties for the selected objects
    penalty1 = calcPen(obj1, penalties, atributesEnc, varMap, orderOfAtt)
    penalty2 = calcPen(obj2, penalties, atributesEnc, varMap, orderOfAtt)

    
    # gets the encoding numbers for the selected objects
    encoding1 = getEncodingNumber(obj1, atributesEnc)
    encoding2 = getEncodingNumber(obj2, atributesEnc)


    # determines the preference
    if penalty1 < penalty2:
        preference = f"o{encoding1} is strictly preferred over o{encoding2}"
    elif penalty1 > penalty2:
        preference = f"o{encoding2} is strictly preferred over o{encoding1}"
    elif penalty1 == penalty2:
        preference = f"o{encoding1} and o{encoding2} are equivalent"
    else:
        preference = f"o{encoding1} and o{encoding2} are incomparable"

    print(f"Two randomly selected feasible objects are: o{encoding1} and o{encoding2}")
    print(f"{preference}")

def getEncodingNumber(obj, atributesEnc):
    # used in the exemplification function for bin encoding retreiveal
    binRep = ''.join(['1' if x > 0 else '0' for x in obj])
    for encoding, attrs in atributesEnc.items():
        if attrs == atributesEnc[binRep]:
            return encoding
    return None

def calcPen(obj, penalties, atributesEnc, varMap, orderOfAtt):
    attrs = decodeBin(obj, atributesEnc, orderOfAtt)  # dec the bin rep of the object to get its attributes
    totalPenalty = 0 # inital of total penalites 

    # iter over each penalty rule
    for pen in penalties:
        penVal = pen[1] # extracts the penalty value
        attrPen = pen[0].split() # splits the penalty rule into components
        penAtt = [p for p in attrPen if p not in ['AND', 'OR', 'NOT']] # extracts the attr involved in the penalty


    # damn flags again
        isOr = 'OR' in attrPen
        isAnd = 'AND' in attrPen
        isNot = 'NOT' in attrPen

        penalty = penVal  # start with the full penalty value

        if isOr:
            if any(p in attrs for p in penAtt):
                penalty = 0  # reduce penalty to 0 if any attribute value is present
        elif isAnd:
            if all(p in attrs for p in penAtt):
                penalty = 0  # reduce penalty to 0 if all attribute values are present
        else:
            if isNot:
                if any(p in attrs for p in penAtt):
                    penalty = 0  #reduce penalty to 0 if any attribute value is present
            else:
                if not all(p in attrs for p in penAtt):
                    penalty = 0  # reduce penalty to 0 if any attribute value is missing

        totalPenalty += penalty

    return totalPenalty

def decodeBin(obj, atributesEnc, orderOfAtt):
    # for calcpen
    binRep = ''.join(['1' if x > 0 else '0' for x in obj])
    attrs = atributesEnc[binRep]
    return attrs
    

def optimization(model, penalties, atributesEnc, varMap, orderOfAtt):
    if len(model) == 0:
        print("No feasible objects found for omni-optimization.") # another base case of sorts 
        return

    optimalObjects = []  # int the list of optimal objects
    minPenalty = float('inf') # min pen is set to inf to compare

    # iterates over each object
    for obj in model:
        penalty = calcPen(obj, penalties, atributesEnc, varMap, orderOfAtt) # calc the penalty for the object
        if penalty < minPenalty:
            minPenalty = penalty # update the minimum penalty
            optimalObjects = [obj] # sets the current object as the only optimal object
        elif penalty == minPenalty:
            optimalObjects.append(obj) # adds the current object to the list of optimal objects if it shares the minimum penalty


    if len(optimalObjects) == 0:
        print("No optimal objects found.")
    else:
        #print(f"All optimal objects: ")
        for obj in optimalObjects:
            encoding = getEncodingNumber(obj, atributesEnc)
            print(f"All optimal objects: o{encoding}\n")
               

def qlTable(model, qlRules, atributesEnc, varMap, orderOfAtt, attributes):
    table = PrettyTable()
    tableDict ={}
    
    field_names = ["Objects"] + [rule.replace(' IF ', ' <- ').replace(' BT ', ' > ') for rule in qlRules]
    table.field_names = field_names

    # Sorts the model objects based on their bin encoding to ensure order like in pentable
    sortedModel = sorted(model, key=lambda x: ''.join(['1' if i > 0 else '0' for i in x]))

    # iterates over each object in the sorted model to evaluate
    for obj in sortedModel:
        encoding = getEncodingNumber(obj, atributesEnc)  # retrieves the encoding number of the object for identification
        row = [f"o{encoding}"]  # starts a new row for the table with the object's encoding number
        tableDict[f"o{encoding}"] = []
        # processes each qualitative rule to apply it to the current object
        for rule in qlRules:
            parts = rule.split('IF')  # splits the rule into the action part and the condition part
            #print("Parts", parts)
            condition = ""
            preference = ""
            for part in parts:
                if "BT" in part:
                    preference = part
                elif part != "":
                    condition = part
            preferred, other = preference.split('BT')  # ids the preferred and other in the rule
            preferred = preferred.strip()
            other = other.strip()
            condition = condition.strip()
            currentEnc = atributesEnc[encoding]
            if condition != "" and condition not in currentEnc:
                row.append("inf")
                tableDict[f"o{encoding}"].append("inf")
                #print("row", row)
                continue
            elif condition != "" and condition in currentEnc:
                if preferred in currentEnc:
                    row.append(1)
                    tableDict[f"o{encoding}"].append(1)
                    #print("row", row)
                else:
                    row.append(2)
                    tableDict[f"o{encoding}"].append(2)
                    #print("row", row)
                continue
            if preferred in currentEnc:
                row.append(1)
                tableDict[f"o{encoding}"].append(1)
                #print("row", row)
            else:
                row.append(2)
                tableDict[f"o{encoding}"].append(2)
                #print("row", row)
                    
        table.add_row(row)

    print(table)
    return tableDict
            
def exemplificationQL(model, penalties, atributesEnc, varMap, orderOfAtt,qalTable):
    if len(model) < 2:
        print("Not enough feasible objects for exemplification.") # base case if you will
        return

    obj1, obj2 = random.sample(model, 2)
    #print(qalTable)
    encoding1 = getEncodingNumber(obj1, atributesEnc)
    encoding2 = getEncodingNumber(obj2, atributesEnc)
    print(encoding1)
    print(encoding2)
    encodingComp1 = 0
    encodingComp2 = 0
    val1  = qalTable[f"o{encoding1}"]
    val2 = qalTable[f"o{encoding2}"]
    for i in range(len(val1)):
        if val1[i] == "inf" and val2[i] == "inf":
            continue
        if val1[i] == "inf":
            if val2[i] != "inf":
                print("encoding 1 is incompareable")
                return
        if val2[i] == "inf":
            if val1[i] != "inf":
                print("encoding 2 is incompareable")
                return
        else:
            encodingComp1 += val1[i]
            encodingComp2 += val2[i]
    if encodingComp1 < encodingComp2:
        print("encoding 1 is strictly prefered")
    elif encodingComp1 > encodingComp2:
        print("encoding 2 is strictly prefered")
    elif encodingComp1 == encodingComp2:
        print("encodings are equal")
    else:
        return
            
def optimizationQL(model, qlTable, atributesEnc):
    if len(model) == 0:
        print("No feasible objects found for omni-optimization.")
        return

    optimalObjects = []  # initialize the list of optimal objects

    # Iterate over each object in the model
    for obj1 in model:
        encoding1 = getEncodingNumber(obj1, atributesEnc)
        isOptimal = True

        # Compare the current object with every other object
        for obj2 in model:
            if obj1 == obj2:
                continue

            encoding2 = getEncodingNumber(obj2, atributesEnc)
            isDominated = True

            # Compare the satisfaction degrees for each rule
            for i in range(len(qlTable[f"o{encoding1}"])):
                if qlTable[f"o{encoding1}"][i] == "inf" and qlTable[f"o{encoding2}"][i] == "inf":
                    continue
                if qlTable[f"o{encoding1}"][i] == "inf" and qlTable[f"o{encoding2}"][i] != "inf":
                    isDominated = False
                    break
                if qlTable[f"o{encoding1}"][i] != "inf" and qlTable[f"o{encoding2}"][i] == "inf":
                    continue
                if qlTable[f"o{encoding1}"][i] < qlTable[f"o{encoding2}"][i]:
                    isDominated = False
                    break

            if isDominated:
                isOptimal = False
                break

        if isOptimal:
            optimalObjects.append(obj1)

    if len(optimalObjects) == 0:
        print("No optimal objects found.")
    else:
        print("All optimal objects:")
        for obj in optimalObjects:
            encoding = getEncodingNumber(obj, atributesEnc)
            print(f"o{encoding}")
            
   
def processTestCase(testCaseDirectory, attributeFilePath, constraintsFilePath, penaltyFilePath, qlFilePath, isPenaltyLogic, encodedObjects):
    rawAttributes = readFile(attributeFilePath)
    attributes, orderOfAtt = parseAttributes(rawAttributes)

    rawConstraints = readFile(constraintsFilePath)
    constraints = parseConstraints(rawConstraints)

    # parse the penalty logic file
    if isPenaltyLogic:
        penalties = parsePenaltyLogic(penaltyFilePath)
    else:
        penalties = None

    while True:
        print("\nChoose the reasoning task to perform:")
        print("1. Encoding")
        print("2. Feasibility Checking")
        print("3. Show the Table")
        print("4. Exemplification")
        print("5. Omni-optimization")
        print("6. Back to previous menu\n")
        choice = input("Your Choice: ")

        if choice == "1":
            encodedObjects = encoding(attributes, orderOfAtt)
        elif choice in ["2", "3", "4", "5"]:
            # variable mapping for CNF conversion
            varMap = varMapping(attributes)
            # encoding constraints to CNF
            cnfFormula = encodeConstraintsToCNF(attributes, constraints, varMap)
            # checking feasibility of the encoded CNF formula
            isFeasible, model = feasCheck(cnfFormula)

            if choice == "2":
                print(f"\nYes, there are {len(model)} feasible objects.\n")
            elif not isFeasible:
                print("\nFeasibility Check: Unsatisfiable. No feasible objects.")
                continue

            if choice == "3":
                if encodedObjects is None:
                    encodedObjects = encoding(attributes, orderOfAtt)
                if isPenaltyLogic:
                    testPenTab = penTable(encodedObjects, penalties, model, varMap, orderOfAtt)
                else:
                    qalTable = qlTable(model, parseQL(readFile(qlFilePath)), encodedObjects, varMap, orderOfAtt, attributes)
            elif choice == "4":
                if encodedObjects is None:
                    encodedObjects = encoding(attributes, orderOfAtt)
                if isPenaltyLogic:
                    exemplification(model, penalties, encodedObjects, varMap, orderOfAtt)
                else:
                    exemplificationQL(model, None, encodedObjects, varMap, orderOfAtt, qalTable)
            elif choice == "5":
                if encodedObjects is None:
                    encodedObjects = encoding(attributes, orderOfAtt)
                if isPenaltyLogic:
                    optimization(model, penalties, encodedObjects, varMap, orderOfAtt)
                else:
                    optimizationQL(model, qalTable, encodedObjects)
        elif choice == "6":
            break
        else:
            print("Wrong Choice! Enter your choice:")
            
    return encodedObjects
            
            
def main():
    print("Welcome to PrefAgent!")
    testCaseInput = input("Enter the file directory: ")
    testCaseDir = os.path.abspath(os.path.join(os.path.dirname(__file__),'../..',"prefAgent/"+ testCaseInput))
    #print("file",testCaseDir)

    testCaseDirectory = input("Enter attributes: ")
    attributeFilePath = os.path.join(testCaseDir,testCaseDirectory)
    #print("attr", attributeFilePath)
    testCaseDirectory = input("Enter hard constraints: ")
    constraintsFilePath = os.path.join(testCaseDir,testCaseDirectory)
    

    encodedObjects = None

    while True:
        print("\nChoose the preference logic to use:")
        print("1. Penalty Logic")
        print("2. Qualitative Choice Logic")
        print("3. Exit")
        choice = input("Your Choice: ")

        if choice == "1":
            print("\nYou picked Penalty Logic")
            penaltyFilePath = os.path.join(testCaseDir, "penaltylogic.txt")
            encodedObjects = processTestCase(testCaseDirectory, attributeFilePath, constraintsFilePath, penaltyFilePath, None, True, encodedObjects)
        elif choice == "2":
            print("\nYou picked Qualitative Choice Logic")
            qlFilePath = os.path.join(testCaseDir, "qualitativechoicelogic.txt")
            encodedObjects = processTestCase(testCaseDirectory, attributeFilePath, constraintsFilePath, None, qlFilePath, False, encodedObjects)
        elif choice == "3":
            print("Bye!")
            return
        else:
            print("Wrong Choice! Enter your choice:")
if __name__ == "__main__":
    main()