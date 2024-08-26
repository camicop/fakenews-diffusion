import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
import math

# PARAMETERS
K_BOTS = 10 # seed size di bot e factChecker
PROB_BOT = 1 # probabilità di diffusione dell'infezione
PROB_FACTCHECKER = 0.29 # probabilità di diffusione del debunking
DATASET = "CollegeMsg" # dataset scelto
CHOOSING_METHOD = "3" # metodo di scelta nodi
BOT_METHOD = "3"

NUM_SIMULATIONS = 1

DATASET_OPTIONS = {
    "CollegeMsg": {"USERS": 1899, "IN_FILE": "CollegeMsg.txt"}, # college dataset # 59835 edges
    "Democratic National Committee": {"USERS": 1891, "IN_FILE": "dnc-temporalGraph.txt"}, # democratic dataset # 39264 edges
    "email-Eu-core": {"USERS": 816, "IN_FILE": "email-Eu-core-temporal.txt"} # email dataset # 332334 edges
}
USERS = DATASET_OPTIONS[DATASET]["USERS"] # numero di nodi
IN_FILE = DATASET_OPTIONS[DATASET]["IN_FILE"] # file del dataset

NUM_WINDOWS = 10 # numero di finestre in cui dividere il grafo temporale
time_windows = [] # Lista per memorizzare i margini delle finestre temporali

aggregation_method = "edges" ## "time" or "edges" # metodo di divisione finestre temporali

# strutture dati utili
social_network = nx.Graph() ### scegliere tra grafo diretto e non diretto
graphs = [nx.DiGraph() for _ in range(NUM_WINDOWS)] # lista di grafi per ogni finestra temporale
pos = {} # Layout per posizionare i nodi nel grafo
all_interactions = [] #nodo partenza, nodo arrivo, timestamp
state = [] ## SUS, INF, REC, SEED_INF, SEED_REC # vettore degli infetti // gli infetti vengono salvati con etichetta che parte da 1 (non 0)
sus_nodes = list(range(0, USERS)) # nodi che sono in stato SUS e quindi disponibili a diventare nodi BOT/FACTCHECKER
k_nodes = [-1] * K_BOTS # sono i k nodi che ad ogni turno diventano bot o factchecker


all_sorted_nodes_by_closeness = [None] * NUM_WINDOWS  # Inizializza con la dimensione delle finestre temporali
all_sorted_nodes_by_betweenness = [None] * NUM_WINDOWS  # Inizializza con la dimensione delle finestre temporali
tot_infetti = 0

num_inf_in_diretta = 0
num_rec_in_diretta = 0
inf_in_diretta = [] # andamento infetti
rec_in_diretta = [] # andamento factcheckers

tot_infetti_in_simulations = 0
final_infects_in_simulations = 0
final_factCheckers_in_simulations = 0

tot_infetti_in_simulations_list = []
final_infects_in_simulations_list = []
final_factCheckers_in_simulations_list = []

create_graph = True
calculate_closeness = [True] * NUM_WINDOWS
calculate_betweenness = [True] * NUM_WINDOWS


def draw_graph():
    # Definisci i colori dei nodi
    node_colors = []
    for node in social_network.nodes():
        if state[node] == "INF":
            node_colors.append('red')
        elif state[node] == "REC":
            node_colors.append('green')
        else:
            node_colors.append('blue')  # Puoi scegliere un altro colore di default se preferisci

    nx.draw(social_network, pos, node_color=node_colors, node_size=4)
    plt.show()

def reset_all():
    global state, tot_infetti, num_inf_in_diretta, num_rec_in_diretta, sus_nodes, k_nodes
    state = ["SUS" for _ in range(USERS)]
    tot_infetti = 0
    num_inf_in_diretta = 0
    num_rec_in_diretta = 0
    sus_nodes = list(range(0, USERS))
    k_nodes = [-1] * K_BOTS
    
def get_variables(bot_seed_size, num_windows, bot_probability, factChecker_probability, chosen_dataset, factMethod, botMethod, num_simulations):
    global K_BOTS
    K_BOTS = int(bot_seed_size)

    global NUM_WINDOWS
    NUM_WINDOWS = int(num_windows)

    global PROB_BOT, PROB_FACTCHECKER
    PROB_BOT = float(bot_probability)
    PROB_FACTCHECKER = float(factChecker_probability)

    global DATASET, USERS, IN_FILE
    DATASET = chosen_dataset
    USERS = DATASET_OPTIONS[DATASET]["USERS"]
    IN_FILE = DATASET_OPTIONS[DATASET]["IN_FILE"]

    global CHOOSING_METHOD, BOT_METHOD
    CHOOSING_METHOD = factMethod
    BOT_METHOD = botMethod

    global NUM_SIMULATIONS
    NUM_SIMULATIONS = num_simulations

    global state, sus_nodes, k_nodes
    state = ["SUS" for _ in range(USERS)] 
    sus_nodes = list(range(0, USERS)) 
    k_nodes = [-1] * K_BOTS 

    print("\n-----------PARAMETRI SIMULAZIONE-----------")
    print(f"\n\tBot seed size: {K_BOTS}")
    print(f"\n\tBot probability: {PROB_BOT}")
    print(f"\tFact-checkers probability: {PROB_FACTCHECKER}")
    print(f"\n\tDataset: {DATASET}\n")
    print(f"\tFactCheckers Choosing method: {CHOOSING_METHOD}")
    print(f"\tBot Choosing method: {BOT_METHOD}\n")

# funzione che crea grafi statici aggregati
def aggregate():
    global social_network, all_interactions, pos, time_windows, create_graph, inf_in_diretta, rec_in_diretta, graphs

    if create_graph:
        # Lettura del file
        with open(IN_FILE, 'r') as f:
            lines = f.readlines()

        # Processamento delle linee e creazione della lista delle interazioni
        for line in lines:
            res = line.split()
            all_interactions.append((int(res[0])-1, int(res[1])-1, float(res[2]))) # i nodi vengono salvati col valore precedente (ad esempio il nodo di nome 1 occupa la posizione 0)

        # Creazione di un singolo grafo statico aggregato
        for u, v, timestamp in all_interactions:
            social_network.add_edge(u, v)

        inf_in_diretta = [0] * len(all_interactions)
        rec_in_diretta = [0] * len(all_interactions)

        print("\n------SOCIAL NETWORK/AGGREGATED GRAPH------")
        print(f"\n\tNumber lines/interactions: {len(lines)}")
        print(f"\tNodes in social network: {social_network.number_of_nodes()}")
        print(f"\tEdges in social network (friendship status): {social_network.number_of_edges()}\n")
        print(f"\n\tNumber of temporal windows: {NUM_WINDOWS}")
        print(f"\tAggregation method: {aggregation_method}\n")
        print(f"\tNumber of simulations: {NUM_SIMULATIONS}\n")

        create_graph = False

        # graph drawing
        
        pos = nx.spring_layout(social_network, k=0.3, iterations=50)  # Layout per posizionare i nodi nel grafo
        draw_graph()
        
        

    time_windows = []
    if(aggregation_method == "time"):
        # Calcolo del timestamp minimo e massimo
        min_timestamp = min(interaction[2] for interaction in all_interactions)
        max_timestamp = max(interaction[2] for interaction in all_interactions)

        # Calcolo della durata di ogni finestra temporale
        WINDOW_DURATION = (max_timestamp - min_timestamp) / NUM_WINDOWS

        for i in range(NUM_WINDOWS):
            start_time = min_timestamp + i * WINDOW_DURATION
            end_time = start_time + WINDOW_DURATION
            time_windows.append((start_time, end_time))
            # print(f"Window {i+1}: {start_time} to {end_time}")
    else:
        # Calcolo del numero di interazioni per finestra temporale
        num_interactions_per_window = len(all_interactions) // NUM_WINDOWS
        current_start = 0
        for i in range(NUM_WINDOWS):
            current_end = current_start + num_interactions_per_window
            
            if i == NUM_WINDOWS - 1:  # Assicurati di includere tutte le interazioni nell'ultima finestra
                current_end = len(all_interactions)
            
            start_time = all_interactions[current_start][2]
            end_time = all_interactions[current_end - 1][2]

            time_windows.append((start_time, end_time))
            # print(f"Window {i+1}: {start_time} to {end_time}")

            current_start = current_end
        # print(f"Prima e ultima interazione: {all_interactions[0][2]} {all_interactions[len(all_interactions)-1][2]}")

        #creiamo grafi statici
        indice_interazione = 0 # indice dell'interazione che stiamo valutando
        window_i = 0
        # finestre temporali
        for start_window, end_window in time_windows:

            while(indice_interazione < len(all_interactions) and all_interactions[indice_interazione][2] <= end_window):     
                # controlliamo interazione per vedere se avviene l'infezione
                nodo_partenza = all_interactions[indice_interazione][0]
                nodo_arrivo = all_interactions[indice_interazione][1]
                graphs[window_i].add_edge(nodo_partenza, nodo_arrivo)
                indice_interazione += 1
            window_i += 1

        # print(f"Interazioni per finestra: {num_interactions_per_window}")
        
        # Visualizzazione dei grafi
        '''
        for i, graph in enumerate(graphs):
            print(f"Graph for window {time_windows[i][0]} to {time_windows[i][1]}")
            print(graph.edges())
            nx.draw(graph, with_labels=True)
            plt.show() '''



# funzione per calcolare i punteggi dei nodi
def seed_choosing(window_i): 
    global tot_infetti, sus_nodes, k_nodes, calculate_closeness, all_sorted_nodes_by_closeness, calculate_betweenness, all_sorted_nodes_by_betweenness
    
    etichetta = "SEED_INF" if window_i % 2 == 0 else "SEED_REC"


    if(CHOOSING_METHOD == "1"): # PER ORA SOLTANTO UN BOT E UN FACT-CHECKER
        if window_i == 0: 
            next_bot = random.randint(0, USERS - 1)
            while(state[next_bot] != "SUS"):
                next_bot = random.randint(0, USERS - 1)
            state[next_bot] = "INF"
            tot_infetti += 1

            next_factChecker = random.randint(0, USERS - 1)
            while(state[next_factChecker] != "SUS"):
                next_factChecker = random.randint(0, USERS - 1)
            state[next_factChecker] = "REC"          
    elif(CHOOSING_METHOD == "2"): # infettiamo k bot e k factcheckers all'inizio e basta
        if window_i == 0:
            for i in range(0, K_BOTS):
                next_bot = random.randint(0, USERS - 1)
                while(state[next_bot] != "SUS"):
                    next_bot = random.randint(0, USERS - 1)
                state[next_bot] = "INF"
                tot_infetti += 1

            for i in range(0, K_BOTS):
                next_factChecker = random.randint(0, USERS - 1)
                while(state[next_factChecker] != "SUS"):
                    next_factChecker = random.randint(0, USERS - 1)
                state[next_factChecker] = "REC"
    elif((CHOOSING_METHOD == "3" and window_i % 2 != 0) or (BOT_METHOD == "3" and window_i % 2 == 0)): # scelgo i k nodi a random
        # libero i nodi del turno precedente
        for i in k_nodes:
            if i != -1:
                sus_nodes.append(i)
                state[i] = "SUS"
        nodi_casuali = random.sample(sus_nodes, K_BOTS) # selezioni k nodi casuali tra i nodi ancora sus
        for i in range(0, len(nodi_casuali)):
            k_nodes[i] = nodi_casuali[i]
            sus_nodes.remove(nodi_casuali[i])
            state[nodi_casuali[i]] = etichetta

    elif((CHOOSING_METHOD == "4" and window_i % 2 != 0) or (BOT_METHOD == "4" and window_i % 2 == 0)): # scelgo come k nodi i nodi che nel turno precedente erano bot/factchecker
        # libero i nodi del turno precedente
        for i in k_nodes:
            if i != -1:
                sus_nodes.append(i)
                state[i] = "SUS"
        if window_i == 0: # se siamo nella prima finestra, non ci sono k nodi scelti nel turno prima, perché non c'è un turno prima
            for i in range(0, K_BOTS): # scegliamo i primi k bot
                k_nodes[i] = i
                sus_nodes.remove(i)
                state[i] = "SEED_INF"   
        else:
            for i in k_nodes:
                sus_nodes.remove(i)
                state[i] = etichetta           
    elif((CHOOSING_METHOD == "5" and window_i % 2 != 0) or (BOT_METHOD == "5" and window_i % 2 == 0)): # scelgo come k nodi i nodi con highest degree
        # libero i nodi del turno precedente
        for i in k_nodes:
            if i != -1:
                sus_nodes.append(i)
                state[i] = "SUS"        

        # Calcolo dei gradi dei nodi
        degree_dict = dict(graphs[window_i].degree())
        # Ordinamento dei nodi per grado in ordine decrescente
        sorted_nodes_by_degree = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)

        nodi_presi = 0
        ind = 0
        while nodi_presi < K_BOTS:
            next_node, _ = sorted_nodes_by_degree[ind]
            if state[next_node] == "SUS": # se nodo è sus, possiamo sceglierlo come seed
                k_nodes[nodi_presi] = next_node
                sus_nodes.remove(next_node)
                state[next_node] = etichetta
                nodi_presi += 1
            ind += 1         

    elif((CHOOSING_METHOD == "6" and window_i % 2 != 0) or (BOT_METHOD == "6" and window_i % 2 == 0)): # scelgo i k nodi in base alla closeness centrality    
        # libero i nodi del turno precedente
        for i in k_nodes:
            if i != -1:
                sus_nodes.append(i)
                state[i] = "SUS"

        if(calculate_closeness[window_i]): #calcoliamo la closeness centrality solo una volta
            calculate_closeness[window_i] = False
            # Calcolo della closeness centrality per tutti i nodi del grafo corrente
            closeness_dict = nx.closeness_centrality(graphs[window_i])
            # Ordinamento dei nodi per closeness centrality in ordine decrescente
            sorted_nodes_by_closeness = sorted(closeness_dict.items(), key=lambda x: x[1], reverse=True)
            # Assegna la lista ordinata all'indice corretto
            all_sorted_nodes_by_closeness[window_i] = sorted_nodes_by_closeness
        
        nodi_presi = 0
        ind = 0
        while nodi_presi < K_BOTS:
            next_node, _ = all_sorted_nodes_by_closeness[window_i][ind]  
            if state[next_node] == "SUS": # se nodo è sus, possiamo sceglierlo come seed
                k_nodes[nodi_presi] = next_node
                sus_nodes.remove(next_node)
                state[next_node] = etichetta
                nodi_presi += 1
            ind += 1
    elif((CHOOSING_METHOD == "7" and window_i % 2 != 0) or (BOT_METHOD == "7" and window_i % 2 == 0)): # scelgo i k nodi in base alla betweenness centrality
        # libero i nodi del turno precedente
        for i in k_nodes:
            if i != -1:
                sus_nodes.append(i)
                state[i] = "SUS"        

        if(calculate_betweenness[window_i]): #calcoliamo la closeness centrality solo una volta
            calculate_betweenness[window_i] = False
            print(f"Calcoliamo betweenness per finestra {window_i}")
            # Calcolo della closeness centrality per tutti i nodi del grafo corrente
            betweenness_dict = nx.betweenness_centrality(graphs[window_i])
            # Ordinamento dei nodi per closeness centrality in ordine decrescente
            sorted_nodes_by_betweenness = sorted(betweenness_dict.items(), key=lambda x: x[1], reverse=True)
            # Assegna la lista ordinata all'indice corretto
            all_sorted_nodes_by_betweenness[window_i] = sorted_nodes_by_betweenness
        
        nodi_presi = 0
        ind = 0
        while nodi_presi < K_BOTS:
            next_node, _ = all_sorted_nodes_by_betweenness[window_i][ind]  
            if state[next_node] == "SUS": # se nodo è sus, possiamo sceglierlo come seed
                k_nodes[nodi_presi] = next_node
                sus_nodes.remove(next_node)
                state[next_node] = etichetta
                nodi_presi += 1
            ind += 1
            
    elif((CHOOSING_METHOD == "8" and window_i % 2 != 0) or (BOT_METHOD == "8" and window_i % 2 == 0)): # (RIC) scegliamo nodi che hanno vicini infetti influenti
        # libero i nodi del turno precedente
        for i in k_nodes:
            if i != -1:
                sus_nodes.append(i)
                state[i] = "SUS"        

        punteggio = [0] * USERS
        for i in range(0, USERS):
            if state[i] == "SUS":
                punteggio[i] += 1 # per fare in modo di scegliere sempre nodi SUS
            if state[i] == "SUS" and i in graphs[window_i]:
                vicini = list(graphs[window_i].successors(i))
                for j in vicini:
                    if(state[j] == "INF"): # per ogni vicino infetto, ne sommiamo il degree
                        punteggio[i] += graphs[window_i].degree(j)
        # Creazione di un dizionario con indici e punteggi
        punteggi_dict = {i: punteggio[i] for i in range(USERS)}
        # Ordinamento del dizionario per valori di punteggio (dal più alto al più basso)
        sorted_punteggi = sorted(punteggi_dict.items(), key=lambda x: x[1], reverse=True)
        # Selezione dei primi 5 indici con i punteggi più alti
        top_k = sorted_punteggi[:K_BOTS]

        nodi_presi = 0
        for idx, score in top_k:
            # print(f"Indice: {idx}, Punteggio: {score}")
            k_nodes[nodi_presi] = idx
            sus_nodes.remove(idx)
            state[idx] = etichetta
            nodi_presi += 1 

    elif((CHOOSING_METHOD == "9" and window_i % 2 != 0) or (BOT_METHOD == "9" and window_i % 2 == 0)): # scelgo i k nodi con più vicini infetti
        # libero i nodi del turno precedente
        for i in k_nodes:
            if i != -1:
                sus_nodes.append(i)
                state[i] = "SUS"        

        punteggio = [0] * USERS
        for i in range(0, USERS):
            if state[i] == "SUS":
                punteggio[i] += 1 # per fare in modo di scegliere sempre nodi SUS
            if state[i] == "SUS" and i in graphs[window_i]:
                vicini = list(graphs[window_i].successors(i))
                for j in vicini:
                    if(state[j] == "INF"): # per ogni vicino infetto, ne sommiamo il degree
                        punteggio[i] += 1

        # Creazione di un dizionario con indici e punteggi
        punteggi_dict = {i: punteggio[i] for i in range(USERS)}
        # Ordinamento del dizionario per valori di punteggio (dal più alto al più basso)
        sorted_punteggi = sorted(punteggi_dict.items(), key=lambda x: x[1], reverse=True)
        # Selezione dei primi 5 indici con i punteggi più alti
        top_k = sorted_punteggi[:K_BOTS]
        nodi_presi = 0
        for idx, score in top_k:
            # print(f"Indice: {idx}, Punteggio: {score}")
            k_nodes[nodi_presi] = idx
            sus_nodes.remove(idx)
            state[idx] = etichetta
            nodi_presi += 1 

    elif((CHOOSING_METHOD == "10" and window_i % 2 != 0) or (BOT_METHOD == "10" and window_i % 2 == 0)): # scelgo nodi centrali lontani dagli altri infetti
        # libero i nodi del turno precedente
        for i in k_nodes:
            if i != -1:
                sus_nodes.append(i)
                state[i] = "SUS"        

        distances = {node: float('inf') for node in range(USERS)}
        for i in range(USERS):
            if(state[i] == "INF" and i in graphs[window_i]):
                for node, length in nx.single_source_shortest_path_length(graphs[window_i], i).items():
                    if length < distances[node]:
                        distances[node] = length
        for i in range(len(distances)): # faccio così per evitare di scegliere nodi che non possono mai raggiungerne altri
            if distances[i] == float('inf'):
                distances[i] = 0

        # Calcola la centralità dei nodi (ad esempio, centralità di grado)
        centrality = {node: 0 for node in range(USERS)}
        degree_centrality = nx.degree_centrality(graphs[window_i])
        for node in degree_centrality:
            centrality[node] = degree_centrality[node]

        # Normalizza le distanze e le centralità
        normalized_distances = normalize(list(distances.values()))
        normalized_centrality = normalize(list(centrality.values()))

        # Combina la distanza e la centralità con una somma ponderata
        alpha = 0.5 # Se alpha è vicino a 1, la distanza è più importante; se alpha è vicino a 0, la centralità è più importante.
        combined_scores = {}
        for i in range(USERS):
            combined_scores[i] = alpha * normalized_distances[i] + (1 - alpha) * normalized_centrality[i]
            if state[i] == "SUS":
                combined_scores[i] += 2 # per scegliere nodi sempre in stato sus

        # Ordina i nodi in base ai punteggi combinati
        sorted_nodes = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Seleziona i nodi migliori
        top_k = sorted_nodes[:K_BOTS]

        nodi_presi = 0
        for idx, score in top_k:
            # print(f"Indice: {idx}, Punteggio: {score}")
            k_nodes[nodi_presi] = idx
            sus_nodes.remove(idx)
            state[idx] = etichetta
            nodi_presi += 1 
           
    else:
        print("metodo non ancora sviluppato")

def normalize(values):
    min_val = min(values)
    max_val = max(values)
    return [(val - min_val) / (max_val - min_val) if max_val > min_val else 0 for val in values]

            
# funzione che simula l'infezione con i k nodi più in alto nel ranking
def infection():  
    global all_interactions, tot_infetti, num_inf_in_diretta, num_rec_in_diretta, state, inf_in_diretta, rec_in_diretta

    reset_all()

    indice_interazione = 0 # indice dell'interazione che stiamo valutando

    window_i = 0
    # finestre temporali
    for start_window, end_window in time_windows:
        # print(f"-- FINESTRA {i} --")
        interaction_in_window = 0

        # scelta nodi bot/debunk
        seed_choosing(window_i)

        while(indice_interazione < len(all_interactions) and all_interactions[indice_interazione][2] <= end_window):
            interaction_in_window += 1
            
            # controlliamo interazione per vedere se avviene l'infezione
            nodo_partenza = all_interactions[indice_interazione][0]
            nodo_arrivo = all_interactions[indice_interazione][1]

            if((state[nodo_partenza] == "INF" or state[nodo_partenza] == "SEED_INF") and state[nodo_arrivo] == "SUS"):
                # il nodo di partenza prova a infettare il nodo di arrivo
                rand_num = random.random()
                if rand_num < PROB_BOT: #con probabilità prob_bot infetto il nodo di arrivo
                    state[nodo_arrivo] = "INF"
                    tot_infetti += 1
                    num_inf_in_diretta += 1
                    sus_nodes.remove(nodo_arrivo) # il nodo non è più disponibile per diventare un seed node
            elif((state[nodo_partenza] == "REC" or state[nodo_partenza] == "SEED_REC") and (state[nodo_arrivo] == "SUS" or state[nodo_arrivo] == "INF")):
                # il nodo di partenza prova a debunkare il nodo di arrivo
                rand_num = random.random()
                if rand_num < PROB_FACTCHECKER: #con probabilità prob_factChecker infetto il nodo di arrivo
                    num_rec_in_diretta += 1
                    if state[nodo_arrivo] == "SUS": # il nodo non è più disponibile per diventare un seed node
                       sus_nodes.remove(nodo_arrivo)
                    else: #ho riconvertito un inf, perciò lo rimuovo dagli infetti in diretta
                        num_inf_in_diretta -= 1
                    state[nodo_arrivo] = "REC"
            inf_in_diretta[indice_interazione] += num_inf_in_diretta
            rec_in_diretta[indice_interazione] += num_rec_in_diretta
            indice_interazione += 1
        # print(f"\t {interaction_in_window} interactions")

        draw_graph()
        window_i += 1

def infection_stats():
    global state, tot_infetti, tot_infetti_in_simulations, final_infects_in_simulations, final_factCheckers_in_simulations
    global tot_infetti_in_simulations_list, final_infects_in_simulations_list, final_infects_in_simulations_list
    # infetti totali nel corso delle simulazioni
    tot_infetti_in_simulations += tot_infetti
    tot_infetti_in_simulations_list.append(tot_infetti)
    
    # nodi infetti alla fine delle simulazioni
    final_infects = 0
    for i in state:
        if i == "INF":
            final_infects += 1
    final_infects_in_simulations += final_infects
    final_infects_in_simulations_list.append(final_infects)

    # nodi ricoverati alla fine delle simulazioni
    final_factCheckers = 0
    for i in state:
        if i == "REC":
            final_factCheckers += 1
    final_factCheckers_in_simulations += final_factCheckers
    final_factCheckers_in_simulations_list.append(final_factCheckers)
    
    '''
    print(f"\nINFETTI TOTALI: {tot_infetti}")    
    print(f"INFETTI FINALI: {final_infects}")
    print(f"FACT-CHECKERS FINALI: {final_factCheckers}\n")
    
    print(f"INFETTI FINALI in diretta: {infetti_in_diretta}")
    print(in_diretta[len(in_diretta) - 1])
    '''
    
def plot_andamento():
    global inf_in_diretta, rec_in_diretta, DATASET, PROB_BOT, PROB_FACTCHECKER, CHOOSING_METHOD

    # Crea una lista di numeri di interazioni (0, 1, 2, ..., len(in_diretta)-1)
    interazioni = list(range(len(inf_in_diretta)))

    # Crea il grafico
    plt.figure(figsize=(10, 6))
    plt.plot(interazioni, inf_in_diretta, marker='o', linestyle='-', color='r', label='Infetti')
    plt.plot(interazioni, rec_in_diretta, marker='o', linestyle='-', color='g', label='FactChecker')

    # Aggiungi titoli e etichette agli assi
    titolo = f"Numero di infetti nel tempo"
    plt.title(titolo)
    plt.xlabel('Numero di interazioni')
    plt.ylabel('Numero di nodi colpiti')

    # Aggiungi una leggenda
    plt.legend()

    # Mostra il grafico
    plt.grid(True)

    # Salva il grafico come immagine
    plt.savefig('andamento.png')

    plt.show()

    # Salva i dati in un file di testo
    with open('dati_andamento.txt', 'w') as file:
        file.write(f"DATASET: {DATASET}\n")
        file.write(f"P_BOT: {PROB_BOT}\n")
        file.write(f"P_FACT: {PROB_FACTCHECKER}\n")
        file.write(f"METHOD: {CHOOSING_METHOD}\n")
         
        file.write("Valori del vettore in_diretta:\n")
        file.write(f"INFETTI\t RECOVERED\n")
        for index in range(len(inf_in_diretta)):
            file.write(f"{inf_in_diretta[index]}\t {rec_in_diretta[index]}\n")

def simulation(bot_seed_size, num_windows, bot_probability, factChecker_probability, chosen_dataset, factMethod, botMethod, num_simulations):

    global inf_in_diretta, rec_in_diretta

    # salviamo i valori dei parametri passati 
    get_variables(bot_seed_size, num_windows, bot_probability, factChecker_probability, chosen_dataset, factMethod, botMethod, num_simulations)

    # aggreghiamo il grafo temporale in tot grafi statici
    aggregate()
    
    for _ in range(0, NUM_SIMULATIONS):
        #print(i)
        global sus_nodes
        # avviamo simulazione
        infection()
        # stampa statistiche finali
        infection_stats()
    
    global tot_infetti, final_infects_in_simulations, final_factCheckers_in_simulations
    print("------ STAT FINALI ------")
    print(f"\n\tMedia totale infetti: {tot_infetti_in_simulations/NUM_SIMULATIONS}")
    print(f"\tMedia totale infetti finali: {final_infects_in_simulations/NUM_SIMULATIONS}")
    print(f"\tMedia totale factCheckers finali: {final_factCheckers_in_simulations/NUM_SIMULATIONS}")



    for index in range(len(inf_in_diretta)):
        inf_in_diretta[index] /= NUM_SIMULATIONS
        rec_in_diretta[index] /= NUM_SIMULATIONS

    # print(f"rec finali medi: {final_factCheckers_in_simulations/NUM_SIMULATIONS} rec finali secondo 'in_diretta': {rec_in_diretta[len(rec_in_diretta) - 1]}")
    plot_andamento()

def run_all_simulations():
    global NUM_WINDOWS, tot_infetti_in_simulations, final_infects_in_simulations, final_factCheckers_in_simulations, PROB_FACTCHECKER

    total_infected_results = []
    final_infected_results = []
    final_fact_checkers_results = []

    get_variables(K_BOTS, NUM_WINDOWS, PROB_BOT, PROB_FACTCHECKER, DATASET, CHOOSING_METHOD, BOT_METHOD, NUM_SIMULATIONS)

    # for num_of_windows in range(1, 101): # window
    for pf_value in np.arange(0.01, 1.01, 0.01): # p_fact_values
       
        # NUM_WINDOWS = num_of_windows # window
        PROB_FACTCHECKER = pf_value # p_fact_values
        print(f"pizza {PROB_FACTCHECKER}") # PROB_FACTCHECKER o NUM_WINDOWS

        # Reset statistiche
        tot_infetti_in_simulations = 0
        final_infects_in_simulations = 0
        final_factCheckers_in_simulations = 0

        # aggreghiamo il grafo temporale in tot grafi statici
        aggregate()

        # Esegui 100 simulazioni per il valore corrente di NUM_WINDOWS
        for i in range(0, NUM_SIMULATIONS):
            # avviamo simulazione
            infection()
            # segna statistiche finali
            infection_stats()
        # simulation(K_BOTS, NUM_WINDOWS, PROB_BOT, PROB_FACTCHECKER, DATASET, CHOOSING_METHOD)

        # Calcola i valori medi
        avg_total_infected = tot_infetti_in_simulations / NUM_SIMULATIONS
        avg_final_infected = final_infects_in_simulations / NUM_SIMULATIONS
        avg_final_fact_checkers = final_factCheckers_in_simulations / NUM_SIMULATIONS

        print(f" avg_total_infected: {avg_total_infected}")
        print(f" avg_final_infected: {avg_final_infected}")
        print(f" avg_final_fact_checkers: {avg_final_fact_checkers}")

        # Salva i risultati
        total_infected_results.append(avg_total_infected)
        final_infected_results.append(avg_final_infected)
        final_fact_checkers_results.append(avg_final_fact_checkers)

        print(f"Completed simulations for NUM_WINDOWS = ")
    # Salva i risultati su un file
    save_results_to_file(total_infected_results, final_infected_results, final_fact_checkers_results)

    # Mostra i risultati in un grafico
    plot_results(total_infected_results, final_infected_results, final_fact_checkers_results)

def save_results_to_file(total_infected, final_infected, final_fact_checkers):
    with open('risultati.txt', 'w') as file:
        file.write("NUM_WINDOWS\tTotal_Infected\tFinal_Infected\tFinal_Fact_Checkers\n")
        """
        for i, num_windows in enumerate(range(1,101)):
            file.write(f"{num_windows}\t{total_infected[i]}\t{final_infected[i]}\t{final_fact_checkers[i]}\n")
        """
        for i, p_val in enumerate(np.arange(0.01, 1.01, 0.01)):
            file.write(f"{p_val}\t{total_infected[i]}\t{final_infected[i]}\t{final_fact_checkers[i]}\n")

def plot_results(total_infected, final_infected, final_fact_checkers):
    # x = list(range(1,101)) # window
    x = list(np.arange(0.01, 1.01, 0.01)) # p_fact_values
    
    plt.figure(figsize=(12, 8))

    plt.plot(x, total_infected, color='red', label='Media totale infetti')
    plt.plot(x, final_infected, color='blue', label='Media totale infetti finali')
    plt.plot(x, final_fact_checkers, color='green', label='Media totale factCheckers finali')

    # plt.xlabel('NUM_WINDOWS') # window
    plt.xlabel('PROB_FACT') # p_fact_values
    plt.ylabel('Numero di nodi')
    plt.title('Risultati delle Simulazioni')
    plt.legend()

    plt.savefig('simulation_results.png', dpi=300, bbox_inches='tight')

    plt.show()

def critical_prob():
    global PROB_BOT, PROB_FACTCHECKER, DATASET, tot_infetti_in_simulations_list, final_infects_in_simulations_list, final_factCheckers_in_simulations_list

    P_bot = 0.25
    
    P_fact_values = np.arange(0.01, 0.26, 0.01) # Range di valori di P_fact
    best_ratio = 0
    critical_P_fact = 0

    # Array per memorizzare i risultati medi e le deviazioni standard
    mean_tot_infetti = []
    std_tot_infetti = []
    mean_final_infects = []
    mean_final_factCheckers = []
    std_mean_ratio = []

    get_variables(K_BOTS, NUM_WINDOWS, P_bot, PROB_FACTCHECKER, DATASET, CHOOSING_METHOD, BOT_METHOD, NUM_SIMULATIONS)
    aggregate()
    
    print(f"\nPROB_BOT: {PROB_BOT}")
    for P_fact in P_fact_values:
        
        PROB_FACTCHECKER = P_fact
        print(f"\nPROB_FACT: {PROB_FACTCHECKER}")

        tot_infetti_in_simulations_list = []
        final_infects_in_simulations_list = []
        final_factCheckers_in_simulations_list = []
        
        for i in range(0, NUM_SIMULATIONS):
            # avviamo simulazione
            infection()
            # segna statistiche finali
            infection_stats()


        # Calcolo delle medie e delle deviazioni standard
        mean_infected = np.mean(tot_infetti_in_simulations_list)
        std_infected = np.std(tot_infetti_in_simulations_list)
        mean_final_inf = np.mean(final_infects_in_simulations_list)
        mean_final_fact = np.mean(final_factCheckers_in_simulations_list)

        # Aggiungi i valori agli array
        mean_tot_infetti.append(mean_infected)
        std_tot_infetti.append(std_infected)
        mean_final_infects.append(mean_final_inf)
        mean_final_factCheckers.append(mean_final_fact)
        std_mean_ratio.append(std_infected / mean_infected if mean_infected != 0 else 0)
        # print(f"std_ratio_vettore: {std_mean_ratio}")

        
        ratio = std_infected / mean_infected if mean_infected != 0 else 0
        if ratio > best_ratio:
            best_ratio = ratio
            critical_P_fact = P_fact

        print(f"size= {len(tot_infetti_in_simulations_list)}   media:{mean_infected}  deviazione:{std_infected}  P_fact: {P_fact}  ratio:{ratio}")

    # Scrivere i risultati in un file di testo
    with open("risultati_deviazione.txt", "w") as f:
        f.write(f"PROB:  {PROB_BOT}  DATASET: \"{DATASET}\"\n")
        f.write("P_FACT\tTOT_INFETTI_MEDI\tFINAL_INFETTI_MEDI\tFINAL_FACTCHECKER_MEDI\tDEV_STD_TOT_INFETTI\n")
        for i in range(len(P_fact_values)):
            f.write(f"{P_fact_values[i]}\t\t{mean_tot_infetti[i]}\t\t{mean_final_infects[i]}\t\t{mean_final_factCheckers[i]}\t\t{std_tot_infetti[i]}\n")

    # Grafico dei valori medi
    plt.figure(figsize=(10, 5))
    plt.plot(P_fact_values, mean_tot_infetti, color="red", label='Totale Infetti Medi')
    plt.plot(P_fact_values, mean_final_infects, color="blue", label='Infetti Finali Medi')
    plt.plot(P_fact_values, mean_final_factCheckers, color="green", label='FactChecker Finali Medi')
    plt.xlabel('P_FACT')
    plt.ylabel('Valore Medio')
    titolo_1 = f"Valori Medi in Funzione di P_FACT (P_BOT = {PROB_BOT} DATASET: \"{DATASET}\")" 
    plt.title(titolo_1)
    plt.legend()
    plt.grid(True)
    plt.savefig('valori_medi.png')
    plt.show()

    
    
    # Grafico delle deviazioni standard e deviazioni standard/media
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.set_xlabel('P_FACT')
    ax1.set_ylabel('Deviazione Standard Totale Infetti', color='tab:blue')
    ax1.plot(P_fact_values, std_tot_infetti, label='Deviazione Standard Totale Infetti', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Deviazione Standard/Media Totale Infetti', color='tab:red')
    ax2.plot(P_fact_values, std_mean_ratio, label='Deviazione Standard/Media Totale Infetti', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    fig.tight_layout()
    plt.subplots_adjust(top=0.85)
    titolo_2 = f"Deviazioni Standard e Deviazioni Standard/Media in Funzione di P_FACT (P_BOT = {PROB_BOT} DATASET: \"{DATASET}\") "
    plt.title(titolo_2)
    plt.grid(True)
    plt.savefig('deviazioni_standard.png')
    plt.show()

if __name__ == "__main__":
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from modules.seed_selection import seed_choosing2
        from modules.seed_selection import rand
        from modules.seed_selection import randBest
        from modules.seed_selection import degree

    # run_all_simulations() # funzione per fare simulazioni con num_finestre che va da 1 a 100
    simulation(K_BOTS, NUM_WINDOWS, PROB_BOT, PROB_FACTCHECKER, DATASET, CHOOSING_METHOD, BOT_METHOD, NUM_SIMULATIONS)
    # critical_prob() # funzione per fare simulazioni per trovare deviazioni standard
else: 
    from .seed_selection import seed_choosing2
    from .seed_selection import rand
    from .seed_selection import randBest
    from .seed_selection import degree