import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
import math

#constants

k_bot = 10 # bot seed size
k_factCheckers = 10 # debunk seed size
prob_bot = 0.2 # probabilità di diffusione dell'infezione
prob_factCheckers = 0.1 # probabilità di diffusione del debunking
dataset = "CollegeMsg" # dataset scelto
choosing_method = "1" # metodo di scelta nodi

dataset_options = {
    "CollegeMsg": {"USERS": 1899, "IN_FILE": "CollegeMsg.txt"}, # college dataset # 59835 edges
    "Democratic National Committee": {"USERS": 1891, "IN_FILE": "dnc-temporalGraph.txt"}, # democratic dataset # 39264 edges
    "email-Eu-core": {"USERS": 986, "IN_FILE": "email-Eu-core-temporal.txt"} # email dataset # 332334 edges
}
USERS = dataset_options[dataset]["USERS"] # numero di nodi
IN_FILE = dataset_options[dataset]["IN_FILE"] # file del dataset

num_windows = 10 # numero di finestre in cui dividere il grafo temporale

aggregation_method = "time" ## "time" or "edges" # metodo di divisione finestre temporali

# strutture dati utili
social_network = nx.Graph() ### scegliere tra grafo diretto e non diretto
all_interactions = []
state = ["SUS" for _ in range(USERS)] ## SUS, INF, REC # vettore degli infetti // gli infetti vengono salvati con etichetta che parte da 1 (non 0)





def get_variables(bot_seed_size, bot_probability, chosen_dataset, method):
    global k_bot
    k_bot = int(bot_seed_size)

    global prob_bot
    prob_bot = float(bot_probability)

    global dataset, USERS, IN_FILE
    dataset = chosen_dataset
    USERS = dataset_options[dataset]["USERS"]
    IN_FILE = dataset_options[dataset]["IN_FILE"]

    global choosing_method
    choosing_method = method

    print(f"La bot seed size è {k_bot}")
    print(f"La probabilità di diffusione bot è {prob_bot}")
    print(f"Il dataset scelto è {dataset}")
    print(f"Il metodo di scelta nodi è {choosing_method}")

# funzione che crea grafi statici aggregati
def aggregate():
    global social_network, all_interactions

    # Lettura del file
    with open(IN_FILE, 'r') as f:
        lines = f.readlines()

    # Processamento delle linee e creazione della lista delle interazioni
    for line in lines:
        res = line.split()
        all_interactions.append((int(res[0])-1, int(res[1])-1, float(res[2]))) # i nodi vengono salvati col valore precedente (ad esempio il nome di nome 1 occupa la posizione 0)

    print(f"numero linee: {len(lines)}")

    # Creazione di un singolo grafo statico aggregato
    for u, v, timestamp in all_interactions:
        social_network.add_edge(u, v)

    print(f"numero nodi nel grafo statico aggregato: {social_network.number_of_nodes()}")
    print(f"numero archi nel grafo statico aggregato: {social_network.number_of_edges()}")

    

# funzione per calcolare i punteggi dei nodi
def seed_choosing():
    if(choosing_method == "1"):
        a = 0
    elif(choosing_method == "2"):
        a = 0
    elif(choosing_method == "3"):
        a = 0
    elif(choosing_method == "4"):
        a = 0
    else:
        print("metodo non ancora sviluppato")



# funzione che simula l'infezione con i k nodi più in alto nel ranking
def infection():  
    tot = 0
    return tot
    

def simulation(bot_seed_size, bot_probability, chosen_dataset, method):

    # salviamo i valori dei parametri passati 
    get_variables(bot_seed_size, bot_probability, chosen_dataset, method)

    # aggreghiamo il grafo temporale in tot grafi statici
    aggregate()
    





if __name__ == "__main__":
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from modules.seed_selection import outExp
        from modules.seed_selection import rand
        from modules.seed_selection import randBest
        from modules.seed_selection import degree
    simulation(k_bot, prob_bot, dataset, choosing_method)
else: 
    from .seed_selection import outExp
    from .seed_selection import rand
    from .seed_selection import randBest
    from .seed_selection import degree
