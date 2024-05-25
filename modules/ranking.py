import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
import math

def stampa():
    print("\nPiZzA\n")

def outExp(aggregated_graphs, num_wind_ranking, users):
    print("\n OUTEXP \n")
    rankings = np.zeros(users)
    counter = 1
    for window in aggregated_graphs.values():
        if counter <= num_wind_ranking:                     
            for i in range(1, users+1):
                if str(i) in window:
                    rankings[i-1] += (1/math.exp(num_wind_ranking-counter+1)) * window.out_degree(str(i)) # out-degree exponential forgetting pag. 9
                    # rankings[i-1] += (1/math.exp(num_wind_ranking-counter+1)) * window.in_degree(str(i)) # in-degree exponential forgetting pag. 9
                    ### divisione per 0 ?? rankings[i-1] += math.log(window.degree(str(i))) / math.log(counter) # tot-degree logaritmic forgetting
            # print(math.log(counter))
        counter = counter + 1
    return rankings

def rand(users):
    print("\n RANDOM \n")
    rankings = np.zeros(users)
    for i in range(users):
        rankings[i] = random.random()
    return rankings
    
def randBest(aggregated_graphs, num_wind_ranking, users, k):
    print("\n RANDOM BEST \n")
    pool = np.zeros(users)

    # sommo il numero di edges in entrata e uscita per ogni nodo nelle finestre di ranking (num_wind_ranking)
    counter = 1
    for window in aggregated_graphs.values():
        if counter <= num_wind_ranking:                     
            for i in range(1, users+1):
                if str(i) in window:
                    pool[i-1] += window.out_degree(str(i)) + window.in_degree(str(i))
        counter = counter + 1

    """
    print(f"ARRAY DEGREE NODI: \n {pool}")
    for i in pool:
        if i>10:
            print(i)
    """
    
    # Normalizza i valori del pool in modo che abbiano una somma totale di 1
    normalized_weights = np.array(pool) / np.sum(pool)
    
    # Seleziona casualmente gli elementi con pesi ponderati
    selected_indices = np.random.choice(len(pool), size=k, p=normalized_weights)
    print("Selected elements:")
    print(selected_indices)
    
    # estraggo i primi k elementi, che saranno il seed iniziale
    selected_elements = np.zeros(users)
    for i in selected_indices:
        selected_elements[i] = 1

    return selected_elements
    
def degree(aggregated_graphs, num_wind_ranking, users):
    print("\n NODE DEGREE \n")
    rankings = np.zeros(users)

    # sommo il numero di edges in entrata e uscita per ogni nodo nelle finestre di ranking (num_wind_ranking)
    counter = 1
    for window in aggregated_graphs.values():
        if counter <= num_wind_ranking:                     
            for i in range(1, users+1):
                if str(i) in window:
                    rankings[i-1] += window.out_degree(str(i)) + window.in_degree(str(i))
        counter = counter + 1

    """
    print(f"ARRAY DEGREE NODI: \n {rankings}")
    for i in rankings:
        if i>10:
            print(i)
    """
    return rankings
    

