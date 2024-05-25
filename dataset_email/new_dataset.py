import pandas as pd
import os

# CHATGPT

# Otteniamo il percorso assoluto della directory in cui si trova questo script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Costruiamo il percorso completo del file pippo.txt
input_file_path = os.path.join(script_dir, "originale.txt")

# Verifichiamo che il file esista
if not os.path.isfile(input_file_path):
    raise FileNotFoundError(f"Il file {input_file_path} non è stato trovato.")

# Leggiamo il file e carichiamo i dati in un DataFrame di pandas
df = pd.read_csv(input_file_path, sep="\s+", header=None, names=['start', 'end', 'timestamp'])

# Estraiamo i nodi unici
unique_nodes = pd.concat([df['start'], df['end']]).unique()

# Creiamo una mappatura dai nodi originali ai nuovi nodi numerati da 1 al numero totale di nodi
node_mapping = {node: i+1 for i, node in enumerate(unique_nodes)}

# Applichiamo la mappatura ai dati
df['start'] = df['start'].map(node_mapping)
df['end'] = df['end'].map(node_mapping)

# Costruiamo il percorso completo del file new_dataset.txt
output_file_path = os.path.join(script_dir, "new_dataset.txt")

# Scriviamo il DataFrame trasformato nel nuovo file new_dataset.txt
df.to_csv(output_file_path, sep=' ', header=False, index=False)

print(f"Il nuovo file è stato generato con successo: {output_file_path}")
