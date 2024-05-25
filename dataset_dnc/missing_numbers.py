import re
import os

# Otteniamo il percorso assoluto della directory in cui si trova questo script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Costruiamo il percorso completo del file
file_path = os.path.join(script_dir, "originale.txt") # prova con new_dataset.py


def check_numbers_in_file(file_path):
    # Leggere il contenuto del file
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Estrarre tutti i numeri presenti nel file
    numbers_in_file = set(map(int, re.findall(r'\b\d+\b', content)))
    
    # Definire l'insieme dei numeri da 1 a 2029
    required_numbers = set(range(1, 2030))
    
    # Verificare se tutti i numeri da 1 a 2029 sono presenti
    missing_numbers = required_numbers - numbers_in_file
    
    if not missing_numbers:
        print("Il file contiene tutti i numeri da 1 a 2029 almeno una volta.")
    else:
        print(f"Mancano i seguenti numeri: {sorted(missing_numbers)}")


# Eseguire il controllo
check_numbers_in_file(file_path)
