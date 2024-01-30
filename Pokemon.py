# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 15:28:06 2024

@author: kirra
"""
import csv
import ast
import random


class Pokemon:
    
    def __init__(self, name, typeOfPokemon, hp, attack, defense, moves, height, weight):
        self.name = name
        self.typeOfPokemon = typeOfPokemon
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.moves = moves or []  # Tricky but since the pokemon has several moves instead of just one, we need to add it to an empty list so that the CSV file can fill in
        self.height = height
        self.weight = weight
        self.usedMoves = [] #empty list to track the used moves

    def isKnockedOut(self):
        #so like edge case
        return self.hp <= 0

    def performAttack(self, other, move, matchUpTable, movesInformation):
            if self.isKnockedOut():
                print( self.name,"can't attack because it's knocked out!")
                return
    
            moveName, movePower = move # touple that holds the name and power of move
            print(self.name+"s " + moveName,"cast to",other.name+":")
            stab = 1
            #print(movesInformation[moveName])
            if movesInformation[moveName].moveType == self.typeOfPokemon:
                stab = 1.5
            typeMatchUp = matchUpTable[self.typeOfPokemon][other.typeOfPokemon] #used to calculate the attacks effectiveness based on the type listed in the dicts in the colosseum class 
        
            # updated damage calculation using attack
            damage = movePower * (self.attack / other.defense) * stab * random.uniform(.5, 1)* typeMatchUp
            damage = round(max(damage, 0))
    
            other.hp -= damage
            other.hp = max(other.hp, 0)
    
            print("Damage to",other.name,"is",str(damage),"points\n")
            print("Now", self.name,"has",str(self.hp),"HP and", other.name,"has",str(other.hp),"HP\n")
            #print("\n----\n")
    
            if other.isKnockedOut():
                print("Now", other.name,"faints back to poke ball!\n")
                
    def displayMove(self):
        # Assuming self.moves is a list of tuples (moveName, power)
        return ', '.join(f"{move[0]} (Power: {move[1]})" for move in self.moves)
   
    # Function to read Pokemon data from CSV file straight from the canvas page.
    @staticmethod
    def readPokemonData(pokemonName):
        pokemonFileName = 'pokemon-data.csv'
        header = []
        pokemonMoves = {}

        with open(pokemonFileName) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = next(reader)
            for row in reader:
                moves = ''
                endOfMoves = False
                for s in row:
                    if s[0] == '[':
                        endOfMoves = True
                        moves = s
                    elif endOfMoves == True:
                        moves += ',' + s
                        if s[-1] == ']':
                            endOfMoves = False
                pokemonMoves[row[0]] = ast.literal_eval(moves)
                
                # testing for name 
        if pokemonName in pokemonMoves:
            print(f"{pokemonName}'s moves: {', '.join(pokemonMoves[pokemonName])}")
        else:
            print(pokemonName,"not found in the dataset.")

    def moveIsUsed(self,moveName):
        return moveName in self.usedMoves #checks to see if the move has already been used 
    
    def useMove(self,moveName):
        self.usedMoves.append(moveName) #moves the move to the usedMove list yasss
        
    def __str__(self):
        return self.name + " HP: " + str(self.hp) # gets ride of the dumb object address prints also help show its HP