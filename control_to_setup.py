import json
import csv
import time
import numpy as np

json_file_path = 'midi/qubo_control.json'
csv_file_path = 'output.csv'

def json_to_csv(json_fp, csv_fp):
    with open(json_fp, 'r') as file:
        data = json.load(file)

    mapping_dict = {True: '', False: ' '}
    headers = data['h1']
    with open(csv_fp, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['h1'] + headers)
        for h in headers:
            print(data[h])
            test = np.array(data[h]) < 0
            print(test)
            spaced_data = [mapping_dict[value]+f'{data[h][i]:.1f}' for i, value in enumerate(test)]
            #spaced = [item for pair in zip(spacer, data[h]) for item in pair]
            print(spaced_data)
            csv_writer.writerow([h] + spaced_data)

while True:
    json_to_csv(json_file_path, csv_file_path)
    time.sleep(0.1)  # Sleep for 0.1 seconds

