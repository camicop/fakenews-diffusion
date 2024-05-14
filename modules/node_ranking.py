import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
import math


corrente = 0

#constants


k = 5 # seed size

# college dataset
USERS = 1899 
IN_FILE = "CollegeMsg.txt"

# democratic dataset
"""
USERS = 2029
IN_FILE = "dnc-temporalGraph.txt"
"""
# email dataset
"""
USERS = 986
IN_FILE = "email-Eu-core-temporal.txt"
"""

num_windows = 20 # numero di finestre in cui dividere il grafo temporale
num_wind_ranking = 2  #num_windows/2 # numero di finestre in cui attuo il ranking dei nodi prima di infettarli
prob = 0.2 # probabilità di diffusione dell'infezione


aggregated_graphs = {} # libreria dei grafi statici aggregati
infected = np.full(USERS, False) # vettore degli infetti // gli infetti vengono salvati con etichetta che parte da 1 (non 0)
rankings = np.zeros(USERS) # vettore dei punteggi dei nodi


# funzione che crea grafi statici aggregati
def aggregate(lines):
    global aggregated_graphs
    temporal_graph = nx.MultiGraph()
    numero_linee = 0
    for line in lines:
        numero_linee+=1
        res = line.split() #divido parole della riga del file
        temporal_graph.add_edge(res[0], res[1], timestamp=res[2]) # i nodi sono memorizzati partendo da 1 (il primo nodo ha valore 1, non 0)
        #print(f"{res[0]} {res[1]} : {res[2]}")

    print(f"numero edges grafo temporale: {temporal_graph.number_of_edges()}")
    print(f"numero linee: {numero_linee}")
    
    """
    nx.draw_spring(temporal_graph) #with_labels = True
    plt.show()
    """

    # Definizione delle finestre temporali
    start_time = float(min(nx.get_edge_attributes(temporal_graph, 'timestamp').values()))
    end_time = float(max(nx.get_edge_attributes(temporal_graph, 'timestamp').values()))

    window_size = (end_time - start_time) / num_windows

    for i in range(1, num_windows + 1):
        window_start = start_time + (i - 1) * window_size
        window_end = window_start + window_size
        aggregated_graph = nx.DiGraph() 
        for u, v, attrib in temporal_graph.edges(data=True):
            if float(attrib['timestamp']) >= window_start and float(attrib['timestamp']) < window_end:
                aggregated_graph.add_edge(u, v)
        aggregated_graphs[i] = aggregated_graph

        """
        nx.draw_spring(aggregated_graph) #with_labels = True
        plt.show()
        """
        
        print(f"{i}: {aggregated_graph.number_of_nodes()} nodes")
    

# funzione per calcolare il valore dei nodi
def ranking():
    global rankings
    counter = 1 # serve per fermarci a metà dei grafi aggregati
    for window in aggregated_graphs.values():
        if counter <= num_wind_ranking:                     
            for i in range(1, USERS+1):
                if str(i) in window:
                    rankings[i-1] += (1/math.exp(num_wind_ranking-counter+1)) * window.out_degree(str(i)) # exponential forgetting pag. 9
                    #print((1/math.exp(num_wind_ranking-counter+1)) * window.out_degree(i))
        counter = counter + 1
    lol = 0
    for i in rankings:
        print(f"{lol}: {i} \n")
        lol += 1
        if lol==20:
            break



# funzione che simula l'infezione con i k nodi più in alto nel ranking
def infection():
    global infected
    global rankings
    infected = np.full(USERS, False)

    #CHATGPT // come trovare i top 5 elementi in una lista, conoscendone anche la posizione
    # Utilizza enumerate per ottenere sia il valore che la posizione
    valori_posizioni = list(enumerate(rankings))
    # Ordina la lista in base ai valori (dal più alto al più basso)
    valori_posizioni_ordinati = sorted(valori_posizioni, key=lambda x: x[1], reverse=True)
    # Prendi i primi 5 valori con le loro posizioni
    valori_piu_alti = valori_posizioni_ordinati[:k] #vettore con i k top nodi


    
    for posizione, valore in valori_piu_alti:
        infected[int(posizione)] = True
        print(f"Valore: {valore}, Posizione: {posizione}") #posizione parte da 0
    
    #infected[corrente] = True 

    
    
    counter = 1
    for window in aggregated_graphs.values():
        if counter > num_wind_ranking:
            new_infected = set() # salvo i nodi appena infettati in un set, e alla fine li aggiorno sul vettore di infetti "infected"
            for u, v in window.edges():
                if infected[int(u)-1] == True:
                    rand_num = random.random()
                    if rand_num < prob: #con probabilità INFECT_PERC infetto il nodo di arrivo
                        new_infected.add(int(v))

            for i in new_infected:
                infected[i-1] = True
        
        counter = counter + 1


    tot = 0
    for i in infected:
        if i:
            tot += 1
    print (f"gli infetti finali sono {tot} su {USERS}")

    

 
def simulation(probability):
    global prob
    prob = float(probability)
    print(f"La probabilità di diffusione è {prob}")

    f = open(IN_FILE, 'r')
    lines = f.readlines()
    f.close()
    f = open('infected_by_each.txt', 'w')

    #aggreghiamo il grafo temporale in tot grafi statici
    aggregate(lines)

    ranking()
    infection()
    """
    for i in range(0, USERS):
        global corrente
        corrente = i
        print(i)
        infection()
    """



if __name__ == "__main__":
    simulation(prob)