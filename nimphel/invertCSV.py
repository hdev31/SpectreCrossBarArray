import csv
import numpy as np
import argparse

def invert_csv(input_filepath, output_filepath):
    # Lire le fichier CSV
    with open(input_filepath, 'r', newline='') as infile:
        reader = csv.reader(infile)
        data = list(reader)
    
    # Convertir les données en un tableau numpy et le transposer
    data_array = np.array(data)
    transposed_data = data_array.T
    
    # Écrire les données transposées dans un nouveau fichier CSV
    with open(output_filepath, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(transposed_data)

def main():
    # Créer un analyseur d'arguments
    parser = argparse.ArgumentParser(description='Inverser les lignes et les colonnes d\'un fichier CSV.')
    
    # Ajouter des arguments pour les chemins des fichiers d'entrée et de sortie
    parser.add_argument('input_filepath', type=str, help='Le chemin du fichier CSV d\'entrée.')
    parser.add_argument('output_filepath', type=str, help='Le chemin du fichier CSV de sortie.')

    # Analyser les arguments
    args = parser.parse_args()
    
    # Inverser les lignes et colonnes du fichier CSV
    invert_csv(args.input_filepath, args.output_filepath)

if __name__ == '__main__':
    main()
