# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 16:42:56 2024

@author: kirra
"""
import random
from Pokemon import Pokemon
from Moves import Moves
import pandas as pd
import ast

class PokemonColosseum:
    def __init__ (self,playerName,playerTeam,rocketTeam):
        self.playerName = playerName
        self.playerTeam = playerTeam
        self.rocketTeam = rocketTeam
        self.movesVari = Moves.readMoveData()
        self.matchUpTable = {}
        self.matchUpTable["Normal"] = {"Normal":1,"Fire":1,"Electric":1,"Grass":1,"Water":1,"Others":1} # dicts for effectiveness of power used against eachother  
        self.matchUpTable["Fire"] = {"Normal":1,"Fire":.5,"Electric":1,"Grass":.5,"Water":2,"Others":1}
        self.matchUpTable["Water"] = {"Normal":1,"Fire":.5,"Electric":2,"Grass":2,"Water":.5,"Others":1}
        self.matchUpTable["Electric"] = {"Normal":1,"Fire":1,"Electric":.5,"Grass":1,"Water":1,"Others":1}
        self.matchUpTable["Grass"] = {"Normal":1,"Fire":2,"Electric":.5,"Grass":.5,"Water":.5,"Others":1} 
        
    
    #@staticmethod      
    def coinToss(self):
        if random.choice([True,False]):
            rocketTeamName = ', '.join([pokemon.name for pokemon in self.rocketTeam]) #rocket goes first if true 
            return "Team Rocket "+ rocketTeamName
        else:
            return "Team "+self.playerName
        
    
    def playerMove(self,pokemon):
        edgeCaseForNum = len(pokemon.moves)
        while True:
            print("choose the move for", pokemon.name+":")
            for i in range(edgeCaseForNum):
                moveName = pokemon.moves[i][0]
                if not pokemon.moveIsUsed(moveName):
                    print(str(i+1) + ". " + moveName)
            choice = input("Team "+ self.playerName + "'s choice: ")
            # loop checks to make sure there is a vaild input all below is the response to the users choice
            if choice.isdigit():
                choiceNum = int(choice)
                if 1 <= choiceNum <= edgeCaseForNum:
                    moveName = pokemon.moves[choiceNum-1][0]
                    if not pokemon.moveIsUsed(moveName):
                        pokemon.useMove(moveName)  # Mark move as used
                        return pokemon.moves[choiceNum-1]
                    else:
                        print("Error: that move has already been used. Please choose another move.")
                else:
                    print("Error: invalid choice please enter a number between 1 and", edgeCaseForNum)
            else:
                print("Error: please enter a number.")
  

    def battle(self):
        print(f"Team Rocket enters with {', '.join([p.name for p in self.rocketTeam])}.")
        print(f"Team {self.playerName} enters with {', '.join([p.name for p in self.playerTeam])}.")
        print("--------------------------------")
        print("Let the battle begin!")
        
        turn = self.coinToss()
        print("Coin toss goes to -----", turn, "to start the attack!")

        while any(not p.isKnockedOut() for p in self.playerTeam) and any(not p.isKnockedOut() for p in self.rocketTeam):
            if turn == "Team "+self.playerName:
                # players turn
                pokemon = next(p for p in self.playerTeam if not p.isKnockedOut())
                move = self.playerMove(pokemon)
                opponent = next(p for p in self.rocketTeam if not p.isKnockedOut())
                pokemon.performAttack(opponent, move, self.matchUpTable,self.movesVari)
                
                print(opponent)
                print(pokemon)
                turn = "Team Rocket"
            else:
                # rockets turn
                opponent = next(p for p in self.playerTeam if not p.isKnockedOut())
                pokemon = next(p for p in self.rocketTeam if not p.isKnockedOut())
                move = random.choice(pokemon.moves)
                pokemon.performAttack(opponent, move, self.matchUpTable,self.movesVari)
                
                print(opponent)
                
                
                
                
                print(pokemon)
                turn = "Team " + self.playerName
                print("\n--------------------------\n")

        winner ="Team " + self.playerName if any(not p.isKnockedOut() for p in self.playerTeam) else "Team Rocket"
       
        loser = "Team Rocket" if winner == "Team " + self.playerName else "Team " + self.playerName
        
       
        print("All of", loser + "'s Pokemon fainted", winner ,"prevails!")

# Example usage
if __name__ == '__main__':
    print("Welcome to Pokemon Colosseum!")
    print("------------------------------")
    playerName = input("Enter Player Name: ")
    # defines pokemon for both teams
    Moves.readMoveData()

    # reads csv to create pokemon objects
    pokemonData = pd.read_csv('pokemon-data.csv')
    allPokemon = []
    
    for index, row in pokemonData.iterrows():
        # convert the string representation of moves into a list of move names
        moveNames = ast.literal_eval(row['Moves'])
        
        # get the move details for each move name
        moves = [(move_name, Moves.movesDict[move_name].power) for move_name in moveNames if move_name in Moves.movesDict]
        
        # create the Pokemon object with the move details
        pokemon = Pokemon(row['Name'], row['Type'], row['HP'], row['Attack'], row['Defense'], moves, row['height'], row['weight'])
        allPokemon.append(pokemon)
    

    randomPlayerIndex = []
    randomPlayerIndex = random.sample(range(0,len(allPokemon)),6)
        

    playerTeam = [allPokemon[randomPlayerIndex[0]], allPokemon[randomPlayerIndex[1]], allPokemon[randomPlayerIndex[3]]]
    rocketTeam = [allPokemon[randomPlayerIndex[2]], allPokemon[randomPlayerIndex[4]], allPokemon[randomPlayerIndex[5]]]

    game = PokemonColosseum(playerName, playerTeam, rocketTeam)
    game.movesVari = Moves.readMoveData()
    #print(game.movesVari)
    game.battle()
