import tkinter as tk
from tkinter import ttk
from modules.module1 import simulation

probability = 0.05

def on_scale_changed(value):
    # Modifica il valore della label
    global probability 
    probability = value
    label_value.config(text=f"Probabilità di diffusione: {value}")
    
def activate_simulation():
    window.destroy()
    simulation(probability)

# creazione finestra
window = tk.Tk()
window.geometry("600x400")
window.title("Simulazione Fake News")
window.configure(background="lightblue")

label_value = tk.Label(window, text=f"Probabilità di diffusione: {probability}")
label_value.grid(row=0, column=0, padx=10, pady=10)

scale = tk.Scale(window, from_=0.05, to=1.00, resolution=0.05, orient="horizontal", command=on_scale_changed, length=300, showvalue=1)
scale.grid(row=0, column=1, padx=10, pady=10)

start_button = tk.Button(text="Avvia simulazione!", command=activate_simulation)
start_button.grid(row=2, column=0)



def main():
    # Interfaccia utente per chiedere informazioni all'utente 
    window.mainloop()

if __name__ == "__main__":
    main()
