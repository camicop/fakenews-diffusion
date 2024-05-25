import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
import math

#constants

k = 1 # seed size

dataset = "CollegeMsg" # dataset scelto
ranking_method = "OutExp" # metodo di scelta nodi
prob = 0.2 # probabilità di diffusione dell'infezione

dataset_options = {
    "CollegeMsg": {"USERS": 1899, "IN_FILE": "CollegeMsg.txt"}, # college dataset # 59835 edges
    "Democratic National Committee": {"USERS": 1891, "IN_FILE": "dnc-temporalGraph.txt"}, # democratic dataset # 39264 edges
    "email-Eu-core": {"USERS": 986, "IN_FILE": "email-Eu-core-temporal.txt"} # email dataset # 332334 edges
}
USERS = dataset_options[dataset]["USERS"] # numero di nodi
IN_FILE = dataset_options[dataset]["IN_FILE"] # file del dataset


num_windows = 30 # numero di finestre in cui dividere il grafo temporale
num_wind_ranking = 10 # numero di finestre in cui attuo il ranking dei nodi prima di infettarli

aggregation_method = "time" ## "time" or "edges" # metodo di divisione finestre temporali

num_simulations = 10


# strutture dati utili
aggregated_graphs = {} # libreria dei grafi statici aggregati
state = ["SUS" for _ in range(USERS)] ## SUS, INF, REC # vettore degli infetti // gli infetti vengono salvati con etichetta che parte da 1 (non 0)
rankings = np.zeros(USERS) # vettore dei punteggi dei nodi, in base ai quali vengono scelti i top k nodi


# funzione che crea grafi statici aggregati
def aggregate():
    global aggregated_graphs
    temporal_graph = nx.MultiGraph()

    f = open(IN_FILE, 'r')
    lines = f.readlines()
    f.close()

    numero_linee = 0
    for line in lines:
        numero_linee+=1
        res = line.split() #divido parole della riga del file
        temporal_graph.add_edge(res[0], res[1], timestamp=res[2]) # i nodi sono memorizzati partendo da 1 (il primo nodo ha valore 1, non 0)

    print(f"numero edges grafo temporale: {temporal_graph.number_of_edges()}")
    print(f"numero linee: {numero_linee}")
    
    """
    nx.draw_spring(temporal_graph) #with_labels = True
    plt.show()
    """

    if(aggregation_method=="time"):

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

    else:
        total_edges = 0
        # Lista degli edge ordinati per timestamp
        edges_sorted_by_timestamp = sorted(temporal_graph.edges(data=True), key=lambda x: x[2]['timestamp'])
        
        # Numero di edge per finestra
        num_edges_per_window = len(edges_sorted_by_timestamp) // num_windows
        extra_edges = len(edges_sorted_by_timestamp) % num_windows

        start_index = 0
        for i in range(1, num_windows + 1):
            aggregated_graph = nx.DiGraph() 
            
            # Determina l'intervallo di edge per questa finestra
            end_index = start_index + num_edges_per_window + (1 if i <= extra_edges else 0)
            window_edges = edges_sorted_by_timestamp[start_index:end_index]
            
            # Aggiunge gli edge al grafo aggregato
            for u, v, attrib in window_edges:
                aggregated_graph.add_edge(u, v)
            
            aggregated_graphs[i] = aggregated_graph
            
            print(f"{i}: {aggregated_graph.number_of_nodes()} nodes, {aggregated_graph.number_of_edges()} edges, {len(window_edges)} edges from temporal graph")
            
            start_index = end_index

            total_edges += len(window_edges)
        # print(f"il numero totale di edges è {total_edges}")
    

# funzione per calcolare i punteggi dei nodi
def ranking():
    global rankings
    if(ranking_method == "OutExp"):
        rankings = outExp(aggregated_graphs, num_wind_ranking, USERS)
    elif(ranking_method == "Random"):
        rankings = rand(USERS)
    elif(ranking_method == "RandomBest"):
        rankings = randBest(aggregated_graphs, num_wind_ranking, USERS, k)
    elif(ranking_method == "Degree"):
        rankings = degree(aggregated_graphs, num_wind_ranking, USERS)
    else:
        print("metodo non ancora sviluppato")




# funzione che simula l'infezione con i k nodi più in alto nel ranking
def infection():
    global state
    global rankings
    state = ["SUS" for _ in range(USERS)]

    #CHATGPT // come trovare i top 5 elementi in una lista, conoscendone anche la posizione
    # Utilizza enumerate per ottenere sia il valore che la posizione
    valori_posizioni = list(enumerate(rankings))
    # Ordina la lista in base ai valori (dal più alto al più basso)
    valori_posizioni_ordinati = sorted(valori_posizioni, key=lambda x: x[1], reverse=True)
    # Prendi i primi 5 valori con le loro posizioni
    valori_piu_alti = valori_posizioni_ordinati[:k] #vettore con i k top nodi


    
    for posizione, valore in valori_piu_alti:
        state[int(posizione)] = "INF"
        print(f"Valore: {valore}, Posizione: {posizione}") #posizione parte da 0
    
    
    counter = 1
    for window in aggregated_graphs.values():
        if counter > num_wind_ranking:
            new_infected = set() # salvo i nodi appena infettati in un set, e alla fine li aggiorno sul vettore di infetti "state"
            for u, v in window.edges():
                if state[int(u)-1] == "INF":
                    rand_num = random.random()
                    if rand_num < prob: #con probabilità INFECT_PERC infetto il nodo di arrivo
                        new_infected.add(int(v))

            for i in new_infected:
                state[i-1] = "INF"
        
        counter = counter + 1

    tot = 0
    for i in state:
        if i == "INF":
            tot += 1
    
    return tot
    

    
 
def simulation(seed_size, probability, data, method):

    global k
    k = int(seed_size)

    global prob
    prob = float(probability)

    global dataset, USERS, IN_FILE
    dataset = data
    USERS = dataset_options[dataset]["USERS"]
    IN_FILE = dataset_options[dataset]["IN_FILE"]

    global ranking_method
    ranking_method = method

    print(f"La seed size è {k}")
    print(f"La probabilità di diffusione è {prob}")
    print(f"Il dataset scelto è {dataset}")
    print(f"Il metodo scelto è {ranking_method}")

    # aggreghiamo il grafo temporale in tot grafi statici
    aggregate()
    
    ranking()

    # diffusione dell'infezione
    tot = 0
    for i in range(1, num_simulations+1):
        if ranking_method == "Random" or ranking_method == "RandomBest":
            ranking() # algoritmo per classificare i migliori nodi da usare come seed
        infetti = infection()
        print (f"sim {i}: gli infetti finali sono {infetti} su {USERS}")
        tot += infetti
    print (f"In media sono stati infettati {tot/num_simulations} su {USERS}")




if __name__ == "__main__":
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from ranking import outExp
        from ranking import rand
        from ranking import randBest
        from ranking import degree
    simulation(k, prob, dataset, ranking_method)
else: 
    from .ranking import outExp
    from .ranking import rand
    from .ranking import randBest
    from .ranking import degree
