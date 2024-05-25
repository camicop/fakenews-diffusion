import tkinter as tk
from tkinter import ttk

#bordello, guarda https://stackoverflow.com/questions/11536764/how-to-fix-attempted-relative-import-in-non-package-even-with-init-py
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from modules.node_ranking import simulation

seed_size = 1
probability = 0.05

selected_dataset = "CollegeMsg"
selected_method = "OutExp"

dataset_descriptions = {
    "CollegeMsg": "This directed network contains sent messages between the users of an online community\nof students from the University of California, Irvine. A node represents a user.\nA directed edge represents a sent message. Multiple edges denote multiple messages.\n\nNodes: 1,899\nEdges: 59,835\nUnique edges: 20,296",
    "Democratic National Committee": "This is the directed network of emails in the 2016 Democratic National Committee email leak.\nThe Democratic National Committee (DNC) is the formal governing body for the United States Democratic Party.\nA dump of emails of the DNC was leaked in 2016. Nodes in the network correspond to persons in the dataset.\n\nNodes: 1,891\nEdges: 39,264\nUnique edges: 5,598",
    "email-Eu-core": "The network was generated using email data from a large European research institution.\nWe have anonymized information about all incoming and outgoing email\nbetween members of the research institution.\n\nNodes: 986\nEdges: 332334\nUnique edges: 24929"
}
method_descriptions = {
    "OutExp": "Out-Degree with exponential forgetting",
    "Random": "Random seeds",
    "RandomBest": "Random best seeds",
    "Degree": "Nodes with higher degree"
}

def on_prob_change(value):
    global probability 
    probability = value
    label_value.config(text=f"Diffusion probability: {value}")

def on_seedsize_change(value):
    global seed_size
    seed_size = value
    label_seed_size.config(text=f"Seed size: {seed_size}")

def on_combobox_select_dataset(event):
    global selected_dataset
    selected_dataset = combobox_dataset.get()
    update_dataset_description()

def on_combobox_select_method(event):
    global selected_method
    selected_method = combobox_method.get()
    update_method_description()

def update_dataset_description():
    description_label.config(text=dataset_descriptions[selected_dataset])

def update_method_description():
    method_description_label.config(text=method_descriptions[selected_method])


def activate_simulation():
    selected_dataset = combobox_dataset.get()
    window.destroy()
    simulation(seed_size, probability, selected_dataset, selected_method)

window = tk.Tk()
window.geometry("720x500")
window.title("Fake News Simulation")
window.configure(background="lightblue")

label_seed_size = tk.Label(window, text=f"Seed size: {seed_size}")
label_seed_size.grid(row=0, column=0, padx=10, pady=10, sticky="e")

scale_seed_size = tk.Scale(window, from_=1, to=20, orient="horizontal", command=on_seedsize_change, length=300, showvalue=1)
scale_seed_size.grid(row=0, column=1, padx=10, pady=10, sticky="w")

label_value = tk.Label(window, text=f"Diffusion probability: {probability}")
label_value.grid(row=1, column=0, padx=10, pady=10)

scale = tk.Scale(window, from_=0.05, to=1.00, resolution=0.05, orient="horizontal", command=on_prob_change, length=300, showvalue=1)
scale.grid(row=1, column=1, padx=10, pady=10, sticky="w")

label_dataset = tk.Label(window, text="Dataset:")
label_dataset.grid(row=2, column=0, padx=10, pady=10, sticky="e")

options_dataset = ["CollegeMsg", "Democratic National Committee", "email-Eu-core"]
max_option_length_dataset = max(len(option) for option in options_dataset)
combobox_dataset = ttk.Combobox(window, values=options_dataset, state="readonly", width=max_option_length_dataset + 5)
combobox_dataset.current(0)
combobox_dataset.grid(row=2, column=1, padx=10, pady=10, sticky="w")
combobox_dataset.bind("<<ComboboxSelected>>", on_combobox_select_dataset)

description_label = tk.Label(window, text="", justify="left", wraplength=500)
description_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")

label_method = tk.Label(window, text="Method:")
label_method.grid(row=4, column=0, padx=10, pady=10, sticky="e")

options_method = ["OutExp", "Random", "RandomBest", "Degree"]
max_option_length_method = max(len(option) for option in options_method)
combobox_method = ttk.Combobox(window, values=options_method, state="readonly", width=max_option_length_method + 5)
combobox_method.current(0)
combobox_method.grid(row=4, column=1, padx=10, pady=10, sticky="w")
combobox_method.bind("<<ComboboxSelected>>", on_combobox_select_method)

method_description_label = tk.Label(window, text="", justify="left", wraplength=500)
method_description_label.grid(row=5, column=1, padx=10, pady=10, sticky="w")

update_dataset_description()  # Aggiorna la descrizione iniziale
update_method_description()  # Aggiorna la descrizione del metodo iniziale

start_button = tk.Button(window, text="Start simulation!", command=activate_simulation, width=50)
start_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="w")

def main():
    # Interfaccia utente per chiedere informazioni all'utente 
    window.mainloop()

if __name__ == "__main__":
    main()

