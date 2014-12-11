'''
Created on 10 Dec 2012

@author: Qasim

Score a DNA string.
Does not save anything.
'''

import atd_bot, dna

#This has not been updated in a while (no logging support)
if __name__ == '__main__':
    dna_s = input("Enter DNA string to use: ")
    the_dna = dna.DNA(dna_s)
    score = atd_bot.score_func(the_dna)
    
    print("DNA: ", str(the_dna))
    print("Score: ", score)
    print("End.")
