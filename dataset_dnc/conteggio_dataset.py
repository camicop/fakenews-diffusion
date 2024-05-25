import pandas as pd
import os

#CHATGPT

# Otteniamo il percorso assoluto della directory in cui si trova questo script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Costruiamo il percorso completo del file
file_path = os.path.join(script_dir, "new_dataset.txt") # prova con new_dataset.py

# Verifichiamo che il file esista
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"Il file {file_path} non è stato trovato.")

# Leggiamo il file e carichiamo i dati in un DataFrame di pandas
df = pd.read_csv(file_path, sep="\s+", header=None, names=['start', 'end', 'timestamp'])

# Estraiamo i nodi unici
unique_nodes = pd.concat([df['start'], df['end']]).unique()

# Calcoliamo il nodo con il numero più piccolo
min_node = unique_nodes.min()

# Calcoliamo il nodo con il numero più grande
max_node = unique_nodes.max()

# Calcoliamo il numero di nodi unici
num_unique_nodes = len(unique_nodes)

# Stampiamo i risultati
print(f"Numero del nodo più piccolo: {min_node}")
print(f"Numero del nodo più grande: {max_node}")
print(f"Numero totale di nodi unici: {num_unique_nodes}")
