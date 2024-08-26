import tkinter as tk
from tkinter import ttk

#bordello, guarda https://stackoverflow.com/questions/11536764/how-to-fix-attempted-relative-import-in-non-package-even-with-init-py
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from modules.simulation import simulation

bot_seed_size = 1
numberOfWindows = 1  
numberOfSimulations = 1 

bot_probability = 0.01
factChecker_probability = 0.01  # Nuova variabile per il factCheck probability

dataset_descriptions = {
    "CollegeMsg": 
    """This directed network contains sent messages between the users of an online community
of students from the University of California, Irvine. A node represents a user.
A directed edge represents a sent message. Multiple edges denote multiple messages.
                    
Nodes: 1,899
Edges/interactions: 59,835
Unique direct edges: 20,296
Unique indirect edges: 13,838""",
    
    "Democratic National Committee": 
    """This is the directed network of emails in the 2016 Democratic National Committee email leak.
The Democratic National Committee (DNC) is the formal governing body for the United States Democratic Party.
A dump of emails of the DNC was leaked in 2016. Nodes in the network correspond to persons in the dataset.

Nodes: 1,891
Edges/interactions: 39,264
Unique direct edges: 5,598
Unique indirect edges: 4,465""",
    
    "email-Eu-core": 
    """The network was generated using email data from a large European research institution.
We have anonymized information about all incoming and outgoing email
between members of the research institution.

Nodes: 816
Edges/interactions: 83,083
Unique direct edges: 11,685
Unique indirect edges: 7,754"""
}
method_descriptions = {
    "1": "All'inizio vengono selezionati un nodo bot e un nodo factChecker",
    "2": "All'inizio vengono infettati k nodi bot e k nodi factChecker",
    "3": "(RND) Scelgliamo i k nodi in modo aleatorio",
    "4": "(SN) Scelgliamo i k nodi che nel turno precedente erano bot/factchecker",
    "5": "(DGR) Scelgliamo come k nodi i nodi con highest degree",
    "6": "(CNT) Scelgliamo i k nodi con la maggiore closeness centrality  ",
    "7": "Scelgliamo i k nodi con la maggiore betweenness centrality",
    "8": "(RIC) Scelgliamo nodi che hanno vicini infetti influenti",
    "9": "(VI) Scelgliamo i k nodi con più vicini infetti",
    "10": "(RC) Scelgliamo nodi centrali lontani dagli altri infetti"
}

different_methods_ita = """    1: All'inizio vengono selezionati un nodo bot e un nodo factChecker
    2: All'inizio vengono infettati k nodi bot e k nodi factChecker
    3: (RND) Scelgliamo i k nodi in modo aleatorio
    4: (SN) Scelgliamo i k nodi che nel turno precedente erano bot/factchecker
    5: (DGR) Scelgliamo come k nodi i nodi con highest degree
    6: (CNT) Scelgliamo i k nodi con la maggiore closeness centrality
    7: Scelgliamo i k nodi con la maggiore betweenness centrality
    8: (RIC) Scelgliamo nodi che hanno vicini infetti influenti
    9: (VI) Scelgliamo i k nodi con più vicini infetti
    10: (RC) Scelgliamo nodi centrali lontani dagli altri infetti    """

different_methods = """    1: At the beginning, one bot node and one factChecker node are selected.
    2: At the beginning, k bot nodes and k factChecker nodes are infected.
    3: (RND) We randomly select the k nodes.
    4: (SN) We select the k nodes that were bots/factCheckers in the previous round.
    5: (DGR) We select the k nodes with the highest degree.
    6: (CNT) We select the k nodes with the highest closeness centrality.
    7: We select the k nodes with the highest betweenness centrality.
    8: (RIC) We select nodes that have influential infected neighbors.
    9: (VI) We select the k nodes with the most infected neighbors.
    10: (RC) We select central nodes that are far from other infected nodes.   """

# Prendere le chiavi da dataset_descriptions per options_dataset
options_dataset = list(dataset_descriptions.keys())
# Prendere le chiavi da method_descriptions per options_method
selected_dataset = options_dataset[0]
# Prendere le chiavi da method_descriptions per options_method
options_method = list(method_descriptions.keys())
# Impostare selected_method come il primo valore di method_descriptions
selected_FactMethod = options_method[0]
# Impostare selected_method come il primo valore di method_descriptions
selected_BotMethod = options_method[0]

def on_bot_seedSize_change(value):
    global bot_seed_size
    bot_seed_size = value
    label_seed_size.config(text=f"  Seed set size: {bot_seed_size}")

def on_factChecker_seedSize_change(value):
    global numberOfWindows
    numberOfWindows = value
    label_fact_seed_size.config(text=f"  Number of windows: {numberOfWindows}")

def on_bot_prob_change(value):
    global bot_probability 
    bot_probability = value
    label_value.config(text=f"Bot probability: {value}")

def on_factChecker_prob_change(value):
    global factChecker_probability 
    factChecker_probability = value
    label_factChecker_value.config(text=f"FactChecker probability: {value}")

def on_dataset_select(event):
    global selected_dataset
    selected_dataset = combobox_dataset.get()
    dataset_description_label.config(text=dataset_descriptions[selected_dataset])

def on_FactMethod_select(event):
    global selected_FactMethod
    selected_FactMethod = combobox_FactMethod.get()

def on_BotMethod_select(event):
    global selected_BotMethod
    selected_BotMethod = combobox_BotMethod.get()

def on_simulation_count_select(event):
    global numberOfSimulations
    numberOfSimulations = int(combobox_simulation_count.get())

def activate_simulation():
    selected_dataset = combobox_dataset.get()
    window.destroy()
    print(f"passiamo factmethod: {selected_FactMethod} e bot method: {selected_BotMethod}")
    simulation(bot_seed_size, numberOfWindows, bot_probability, factChecker_probability, selected_dataset, selected_FactMethod, selected_BotMethod, numberOfSimulations)

window = tk.Tk()
window.geometry("1200x550")
window.title("Fake News Simulation")
window.configure(background="lightblue")

label_seed_size = tk.Label(window, text=f"  Seed set size: {bot_seed_size}", width=14, anchor="w")
label_seed_size.grid(row=0, column=0, padx=10, pady=10, sticky="e")

scale_seed_size = tk.Scale(window, from_=1, to=20, orient="horizontal", command=on_bot_seedSize_change, length=300, showvalue=1)
scale_seed_size.grid(row=0, column=1, padx=10, pady=10, sticky="w")

label_fact_seed_size = tk.Label(window, text=f"  Number of windows: {numberOfWindows}", width=20, anchor="w")
label_fact_seed_size.grid(row=0, column=2, padx=10, pady=10, sticky="e")

scale_fact_seed_size = tk.Scale(window, from_=1, to=20, orient="horizontal", command=on_factChecker_seedSize_change, length=300, showvalue=1)
scale_fact_seed_size.grid(row=0, column=3, padx=10, pady=10, sticky="w")


label_value = tk.Label(window, text=f"Bot probability: {bot_probability}", width=18)
label_value.grid(row=1, column=0, padx=10, pady=10)

scale = tk.Scale(window, from_=0.01, to=1.00, resolution=0.01, orient="horizontal", command=on_bot_prob_change, length=300, showvalue=1)
scale.grid(row=1, column=1, padx=10, pady=10, sticky="w")

label_factChecker_value = tk.Label(window, text=f"FactChecker probability: {factChecker_probability}", width=24)
label_factChecker_value.grid(row=1, column=2, padx=10, pady=10)

scale_factCheck = tk.Scale(window, from_=0.01, to=1.00, resolution=0.01, orient="horizontal", command=on_factChecker_prob_change, length=300, showvalue=1)
scale_factCheck.grid(row=1, column=3, padx=10, pady=10, sticky="w")

label_dataset = tk.Label(window, text="Dataset:")
label_dataset.grid(row=2, column=0, padx=10, pady=10, sticky="e")

options_dataset = list(dataset_descriptions.keys())
max_option_length_dataset = max(len(option) for option in options_dataset)
combobox_dataset = ttk.Combobox(window, values=options_dataset, state="readonly", width=max_option_length_dataset + 5)
combobox_dataset.current(0)
combobox_dataset.grid(row=2, column=1, padx=10, pady=10, sticky="w")
combobox_dataset.bind("<<ComboboxSelected>>", on_dataset_select)

label_methods = tk.Label(window, text="SEED SET CHOOSING METHODS:", width=30)
label_methods.grid(row=2, column=3, padx=10, pady=10, sticky="w")

dataset_description_label = tk.Label(window, text="", justify="left", wraplength=300)
dataset_description_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")
dataset_description_label.config(text=dataset_descriptions[selected_dataset]) # Aggiorna la descrizione iniziale

label_methods_list = tk.Label(window, text=different_methods, justify="left", wraplength=1300)
label_methods_list.grid(row=3, column=3, padx=10, pady=10)

label_simulations = tk.Label(window, text="Number of simulations:")
label_simulations.grid(row=4, column=0, padx=10, pady=10, sticky="e")

options_simulation_count = ["1", "10", "100", "500", "1000"]
combobox_simulation_count = ttk.Combobox(window, values=options_simulation_count, state="readonly", width=10)
combobox_simulation_count.current(0)
combobox_simulation_count.grid(row=4, column=1, padx=10, pady=10, sticky="w")
combobox_simulation_count.bind("<<ComboboxSelected>>", on_simulation_count_select)


label_FactMethod = tk.Label(window, text="FactCheckers method:")
label_FactMethod.grid(row=4, column=2, padx=10, pady=10, sticky="e")

options_method = list(method_descriptions.keys())
max_option_length_method = max(len(option) for option in options_method)
combobox_FactMethod = ttk.Combobox(window, values=options_method, state="readonly", width=max_option_length_method + 5)
combobox_FactMethod.current(0)
combobox_FactMethod.grid(row=4, column=3, padx=10, pady=10, sticky="w")
combobox_FactMethod.bind("<<ComboboxSelected>>", on_FactMethod_select)


label_BotMethod = tk.Label(window, text="Bots method:")
label_BotMethod.grid(row=5, column=2, padx=10, pady=10, sticky="e")

max_option_length_method = max(len(option) for option in options_method)
combobox_BotMethod = ttk.Combobox(window, values=options_method, state="readonly", width=max_option_length_method + 5)
combobox_BotMethod.current(0)
combobox_BotMethod.grid(row=5, column=3, padx=10, pady=10, sticky="w")
combobox_BotMethod.bind("<<ComboboxSelected>>", on_BotMethod_select)



start_button = tk.Button(window, text="Start simulation!", command=activate_simulation, width=50)
start_button.grid(row=6, column=0, columnspan=4, padx=10, pady=(30, 10))

def main():
    # Interfaccia utente per chiedere informazioni all'utente 
    window.mainloop()

if __name__ == "__main__":
    main()

