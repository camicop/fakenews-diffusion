import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt


#constants
USERS = 1899 
IN_FILE = "CollegeMsg.txt"
num_windows = 50
prob = 0.1

# libreria dei grafi
aggregated_graphs = {}
infected = np.full(USERS, False)



#funzione che crea grafi statici aggregati
def aggregate(lines):
    temporal_graph = nx.MultiGraph()
    numero_linee = 0
    for line in lines:
        numero_linee+=1
        res = line.split() #divido parole della riga del file
        temporal_graph.add_edge(res[0], res[1], timestamp=res[2])
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
        global aggregated_graph
        aggregated_graph = nx.Graph() #l'ho messo multi per ora, ma sarebbe da cambiare
        for u, v, attrib in temporal_graph.edges(data=True):
            if float(attrib['timestamp']) >= window_start and float(attrib['timestamp']) < window_end:
                aggregated_graph.add_edge(u, v)
        aggregated_graphs[i] = aggregated_graph

        """
        nx.draw_spring(aggregated_graph) #with_labels = True
        plt.show()
        """
        
        print(f"{i}: {aggregated_graph.number_of_nodes()} nodes")
    


def infection(seed):
    global infected
    infected = np.full(USERS, False)
    infected[seed-1] = True
    
    for window in aggregated_graphs.values():
        new_infected = set()
        for u, v in window.edges():
            if infected[int(u)-1] == True:
                rand_num = random.random()
                if rand_num < prob: #con probabilità INFECT_PERC infetto il nodo di arrivo
                    new_infected.add(int(v))

        for i in new_infected:
            infected[i-1] = True


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

    # per ogni nodo simuliamo una diffusione
    for i in range(10):
        print(f"{i})")
        infection(i)
        print()


    

if __name__ == "__main__":
    simulation(prob)
