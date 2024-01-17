# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 20:32:00 2024

@author: kirra
"""

#lil surf conditions fun
#wave height, wind speed, tide 

def enterWaveHeight():
    waveheight = float(input("Enter the wave height in feet: "))
    
    if waveheight > 8:
        print("Bold of you to surf this big.")
    elif waveheight > 3:
        print("Yeah, this is more of your comfort zone. Enjoy yourself, and let's hope the wind isn't too bad.")
    elif waveheight <= 2: 
        print("Nah, this is ass. It's too flat.")
    else:
        print("either invaild or too flat your too depressed to enter the number");
    return waveheight

def enterWindSpeed():
    windSpeed = int(input("enter the wind speed in MPH: "))
    
    if windSpeed > 11:
        print("hmm you may want to sit this one out cause its blown out")
    else:
        print("WYA?!")
    
    return windSpeed


def enterTide():
    tide = input("enter the tide mid, high, low: ");
    
    if tide == "low" or tide =="LOW":
        print("hmm might be fun careful with the rocks/reef below");
    elif tide == "mid" or tide == "MID":
        print("every instance ive been out its been damn perfect");
    elif tide == "high" or tide == "HIGH":
        print("hmm might be fun if its a low tide spot enjoy the shorepound");
    else:
        print("invalid");
    return tide


def main():
    while True:
        print("Yeah, here's my small surf conditions code:")
        
        print(enterWaveHeight())
        print(enterWindSpeed())
        print(enterTide())
 
        quiter = input("would you like to go again? if not hit q or Q: ");
        if quiter == "Q" or quiter == "q":
            break;
if __name__ == "__main__":
    main()
 
    