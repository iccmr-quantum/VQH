import json
import csv
import numpy as np
from collections import OrderedDict
import time


json_file_path = 'midi/qubo_control.json'
csv_file_path = 'output.csv'

def json_to_csv(json_fp, csv_fp):
    with open(json_fp, 'r') as file:
        data = json.load(file)

    mapping_dict = {True: '', False: ' '}
    #main_order = ['c', 'e', 'g', 'b']
    main_order = ['s1', 's2', 's3', 's4']
    key_names = {'s1': 'c', 's2': 'e', 's3': 'g', 's4': 'b'}
    sub_order = main_order
    ordered_data = {key_names[k]: {key_names[sk]: data[k][sk] for sk in sub_order} for k in main_order}

    data = ordered_data

    with open(csv_fp, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        # Write the header
        headers = ['h1'] + list(data[next(iter(data))].keys())  # Extract keys from the first item
        csv_writer.writerow(headers)

        # Write the data
        for key, values in data.items():
            row = list(values.values())
            #print(row)
            test = np.array(row) < 0
            #print(test)
            row = [mapping_dict[value]+f'{float(row[i]):.2f}' for i, value in enumerate(test)]
            row = [key] + row
            csv_writer.writerow(row)
while True:
    try:
        json_to_csv(json_file_path, csv_file_path)
        time.sleep(0.1)  # Sleep for 0.1 seconds
    except Exception:
        continue
