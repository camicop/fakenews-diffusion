# coding=utf-8
import networkx as nx
import matplotlib.pyplot as plt7

import numpy as np
import matplotlib.pyplot as plt

import random

#constants
USERS = 1899
INFECT_PROB = 0.05 #probability of infection


def final_infected(user):
    infected = np.zeros((USERS, 1), dtype=bool)
    infected[user] = True
    
    for line in lines:
        res = line.split() #divido parole della riga del file

        if infected[int(res[0]) - 1]: 
            rand_num = random.random()
            if rand_num < INFECT_PROB: #con probabilità INFECT_PERC infetto il nodo di arrivo
                infected[int(res[1]) - 1] = True

    cont = 0

    for i in infected:
        if i: cont += 1

    return cont


f = open('CollegeMsg.txt', 'r')
lines = f.readlines()
f.close()

f = open('infected_by_each.txt', 'w')



for i in range(USERS):
    infect = str(i+1) + ": " + str(final_infected(i)) +"\n"
    f.write(infect)
    #print(infect)


f.write("ciao")



