# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 13:43:52 2024

@author: kirra
"""
import pandas as pd



class Moves:
    
    # dict will store all moves from the CSV
    movesDict = {}
    
    # class will consist of all names from the moves-data row from the 
    def __init__ (self,name, moveType, category, contest, pp, power, accuracy):
        self.name = name
        self.moveType = moveType
        self.category = category
        self.contest = contest
        self.pp = pp
        self.power = power
        self.accuracy = accuracy
        
# File I/O for moves csv? not sure 
    def readMoveData():
        moveFileName = 'moves-data.csv'
        df = pd.read_csv(moveFileName)
        avg = int(df['Accuracy'].dropna().astype(int).mean()) # finding all avgs for none's listed in the accuracy column
        df['Accuracy'] = df['Accuracy'].fillna(avg).astype(int) # if found (none) cast to integer value
        for index,row in df.iterrows():
            pp = int(row['PP'])
            power = int(row['Power'])
            accuracy = int(row['Accuracy'])
            move = Moves(row['Name'],row['Type'], row['Category'],
            row['Contest'], row['PP'], row['Power'], row['Accuracy']) # long vari but move now holds all values in the csv moves.name will provide the name of the move so on and so forth
            Moves.movesDict[move.name] = move # stores all moves in the moves dict the key insex is moves.name
        return Moves.movesDict
    
    # testing for the moves to work properly 
# if __name__ == "__main__":
#     Moves.readMoveData()
#     if'Tackle' in Moves.movesDict:
#        print("Tackle Power: ", Moves.movesDict['Tackle'].power)
#     else:
#         print("Tackle not found in dataset")