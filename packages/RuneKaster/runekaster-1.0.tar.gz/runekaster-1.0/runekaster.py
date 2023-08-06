#!/usr/bin/env python3
 
# Title: RuneKaster
# Summary: A simple program that gives the user a three-rune answer to a question
# Copyright (c) 2014 Michael Thomas
# See the file license.txt for copying permission
# Released under the MIT license

import random
import time
import os

os.system('clear')

# Intro
print('Runes, those mysterious symbols of northern Europe.')
time.sleep(2)
print('Some say that if you truly believe, you can ask a question, and three runes will be shown you.')
time.sleep(3)
print('The first illuminates your Past.')
time.sleep(2)
print('The second illuminates your Present.')
time.sleep(2)
print('The third illuminates your possible Future.')
time.sleep(2)
print('Some say that it is all nonsense.')
time.sleep(2)
print('What do you say?')
input( '\nPlease press <Enter> to ask your question.' )
print('Please type in your question.')
myQuestion = input()
time.sleep(1)
print('The answer to your question, '+ myQuestion +' , is:')
time.sleep(2)

def main():
    rune = random.randint(1,28)
    print('')
    if rune == 1:
        print('FEOH - Wealth is a comfort to all men. Give it freely if you wish to gain honor.')
    if rune == 2:
        print('UR - The aurochs is proud and has great horns; a savage beast, a creature of mettle.')
    if rune == 3:
        print('THORN - The thorn is exceedingly sharp and cuts those who sit among them.')
    if rune == 4:
        print('OS - The mouth is the source of all language, wisdom, comfort, blessing and joy.')
    if rune == 5: 
        print('RAD - Riding seems easy to those indoors or on a sturdy horse.')
    if rune == 6: 
        print('CEN - The torch is known to all and burns when princes sit within.')
    if rune == 7:
        print('GYFU - Generosity brings credit and honour, and help and subsistence.')
    if rune == 8: 
        print('WYNN - Bliss is enjoyed by those not suffering, and who have a good house.')
    if rune == 9: 
        print('NYD - Trouble is oppressive but can be a help to those who heed it.')
    if rune == 10:  
        print ('IS or ISA - Ice is cold and slippery, wrought by the frost and fair to look upon.')
    if rune == 11: 
        print ('GER - Summer is a joy, when the earth bears fruit for rich and poor alike.')
    if rune == 12:  
        print ('EOH -The yew is a mighty tree, guardian of the flame and a joy upon an estate.')
    if rune == 13:  
        print ('PEORTH - A source of amusement where warriors sit blithely in their hall.')
    if rune == 14:  
        print ('EOHL - The eohl-sedge grows in a marsh and covers those who touch it with blood.')
    if rune == 15:  
        print ('SIGEL - The sun is a joy to sailors until the sea bears them home.')
    if rune == 16:  
        print ('TIR - Tir is a guiding star, constant and ever on its course.')
    if rune == 17:  
        print ('BEORC - The poplar bears no fruit, is without seed, and reaches to the sky.')
    if rune == 18:  
        print ('EH - The horse is a joy, a source of comfort to the restless.')
    if rune == 19:  
        print ('MANN - The joyous man is dear to his kinsmen, but every man will fail his fellow.')
    if rune == 20:  
        print ('LAGU - The ocean is a mighty thing, terrifying and unbridled.')
    if rune == 21:  
        print ('ING - Ing was first seen by men among the East-Danes. until he departed eastward.')
    if rune == 22:  
        print ('ETHEL - An estate is dear, to be enjoyed if right and proper.')
    if rune == 23:  
        print ('DAEG - Day is a source of hope to rich and poor and of service to all.')
    if rune == 24:  
        print ('AC - The oak fatttens pigs and the ocean proves if it keeps faith honorably.')
    if rune == 25: 
        print ('AESC - The ash is high and precious and resists the attack of many a man.')
    if rune == 26:  
        print ('YR - Yr is a source of joy and honor and is reliable equipment on a journey.')
    if rune == 27: 
        print ('IAR - Iar is a river fish but feeds on land, with a fair abode, living in happiness.')
    if rune == 28:  
        print ('EAR - The grave is horrible, prosperity dims, happiness passes, covenants are broken.')
main()

main()
main()

print('')
print('Thank you for using RuneKaster.')
print('Do not make life decisions based on these results.')
print('Remember, IT IS ONLY A GAME!')
print('FOR ENTERTAINMENT PURPOSES ONLY!')
print('Goodbye.')

