import csv
from util.inlets import VQHInlet
from threading import Lock, RLock
import json
import numpy as np
from datetime import datetime
import os


class QUBOProblem:
    def __init__(self, filename, source_type='csv', rt_mode=0):
        
        self._qubos = []
        self.lock = RLock()

        self.source_type = source_type
        self.filename = filename
        self.size = 0


        self.rt_mode = rt_mode
        self._updates_locked = False

        self.pending_updates = []
        self.update_lock = Lock()

        self._has_updates = False
        self.update_count = 0
        self.last_update_time = None
        
        print(f"[QUBOProblem] Initializing with:")
        print(f"  Source type: {self.source_type}")
        print(f"  Filename: {self.filename}")
        print(f"  Real-time mode: {self.rt_mode}")


        self.init_data()

    @property
    def qubos(self):
        with self.lock:
            return self._qubos

    def load_data(self, filename):

        print(f"[QUBOProblem] Loading data with source type '{self.source_type}' from '{filename}'")

        if self.source_type == 'osc':
            #self.init_empty_qubo()
            if os.path.exists(filename):
                self.load_from_csv(filename)
            else:
                print(f"[QUBOProblem] OSC source selected but file '{filename}' not found. Initializing empty 4x4 QUBO.")
                self.init_empty_qubo(4)
            
        elif self.source_type == 'json':
            self.load_from_json(filename)
        else:
            self.load_from_csv(filename)

        self.size = len(self._qubos)

        print(f"[QUBOProblem] Loaded {self.size} QUBO(s).")

    def load_initial_for_osc(self, filename):
        print(f"[QUBOProblem] Loading initial QUBO from '{filename}' for OSC source.")

        if os.path.exists(filename):
            try:
                self.load_from_csv(filename)
                print(f"[QUBOProblem] Successfully loaded!")
            except Exception as e:
                print(f"[QUBOProblem] Error loading {filename}: {e}")
                print(f"[QUBOProblem] Initializing empty 4x4 QUBO instead.")
                self.init_empty_qubo(4)
        else:
            print(f"[QUBOProblem] File {filename} not found. Initializing empty 4x4 QUBO.")
            self.init_empty_qubo(4)



    def init_empty_qubo(self, size=4):
        labels = [f"s{i}" for i in range(size)]
        qubo = {}

        for i in range(size):
            for j in range(size):
                qubo[(labels[i], labels[j])] = 0.0 if i != j else 1.0

        with self.lock:
            self._qubos = [qubo]

    def load_from_csv(self, filename):

        '''Builds a list of qubos from a csv file. 
        The csv file must be in the same folder as this script and must be named 
        "h_setup.csv". The csv file must have the following format:
        
        h1,label1,label2,label3,...,labeln
        label1,c11,c12,c13,...,c1n
        label2,c21,c22,c23,...,c2n
        label3,c31,c32,c33,...,c3n
        ...
        labeln,cn1,cn2,cn3,...,cnn
        h2,label1,label2,label3,...,labeln
        label1,c11,c12,c13,...,c1n
        ...
        
        where h1, h2, ... are the QUBO matrices names and label1, label2, ... are the
        note labels used by the sonification.

        The function returns a list of qubos of the form:
        [{(note_1, note_2): coupling, ...}, ...]
        where note_1 and note_2 are the note labels with its corresponding coupling
        coefficients.
        '''

        print('Loading from CSV')

        try:
            with open(filename, 'r') as hcsv:
                hsetup = list(csv.reader(hcsv, delimiter=','))
        except FileNotFoundError:
            print(f"File {filename} not found. Initializing empty QUBO.")
            self.init_empty_qubo()
            return
        except Exception as e:
            print(f"Error: {e}. Exiting.")
            return

        #header = hsetup.pop(0)
        #n_of_ham = int(header[1])
        #n_of_ham = 1
        #n_of_notes = 6
        qubos_aux = []
        #n_of_notes = int(header[2])

        current_row = 0

        while current_row < len(hsetup):
            if not hsetup[current_row][0].startswith('h'):
                current_row += 1
                continue
            notes = hsetup[current_row][1:]
            n_of_notes = len(notes)
            current_row += 1

            qubo = {}

            for i in range(n_of_notes):
                if current_row >= len(hsetup):
                    break
                row = hsetup[current_row+i]
                row_label = row[0]

                for j, value in enumerate(row[1:n_of_notes+1]):
                    if j < len(notes):
                        qubo[(row_label, notes[j])] = float(value)

            qubos_aux.append(qubo)
            current_row += n_of_notes

            if qubo:
                sample_keys = list(qubo.keys())[:5]
                sample = {k: qubo[k] for k in sample_keys}
                print(f"[QUBOProblem] Sample entries: {sample}")

        
        with self.lock:
            self._qubos = qubos_aux

    def load_from_json(self, json_filename):
        print(f'Loading from JSON: {json_filename}')

        json_path = json_filename if json_filename.endswith('.json') else 'midi/qubo_control.json'


        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON file {json_path}: {e}. Quitting...")
            raise



        qubo = {}
        for key1, row in data.items():
            if isinstance(row, dict):
                for key2, value in row.items():
                    qubo[(key1, key2)] = float(value) 
    
        with self.lock:
            self._qubos = [qubo]

        print(f"[QUBOProblem] Loaded QUBO from JSON with {len(qubo)} entries.")

    
    def lock_updates(self, locked:bool):
        
        self._updates_locked = locked
        if locked:
            print("QUBO Updates locked.")

        else:
            print("QUBO Updates unlocked.")


    def has_updates(self) -> bool:
        return self._has_updates

    def clear_update_flag(self):
        self._has_updates = False

    def update_from_osc(self, osc_data):

        if self._updates_locked:
            print("FIXED MODE: OSC Updates are rejected. Ignoring incoming data.")
            return

        if self.rt_mode == 0: 
            return

        elif self.rt_mode == 1:

            with self.update_lock:
                self.pending_updates.append({'data': osc_data, 'timestamp': datetime.now()})
            print(f"Buffered QUBO update. Pending updates: {len(self.pending_updates)}")

        elif self.rt_mode == 2:

            with self.lock:
                self._apply_osc_update(osc_data)
                self._has_updates = True
                self.update_count += 1
                self.last_update_time = datetime.now()
            print(f"Applied QUBO update #{self._update_count}. RT")

    def apply_pending_updates(self):
        with self.update_lock:
            if not self.pending_updates:
                return

            print(f"Applying {len(self.pending_updates)} pending QUBO updates.")
            for update in self.pending_updates:
                with self.lock:
                    self._apply_osc_update(update['data'])

            self.pending_updates = []

    def _apply_osc_update(self, osc_data):

        if 'matrix' in osc_data:

            matrix = osc_data['matrix']
            size = len(matrix)
            labels = [f"s{i}" for i in range(size)]

            qubo = {}

            for i in range(size):
                for j in range(size):
                    qubo[(labels[i], labels[j])] = float(matrix[i][j])

            self._qubos = [qubo]
            self.size = 1

        elif 'entries' in osc_data:

            if len(self._qubos) == 0:
                size = osc_data.get('size', 4)
                self.init_empty_qubo(size)

            for entry in osc_data['entries']:

                i, j, value = entry['i'], entry['j'], entry['value']
                label_i = f"s{i}"
                label_j = f"s{j}"

                if self._qubos:
                    self._qubos[0][(label_i, label_j)] = float(value)


    def save_current_to_csv(self, filename):
        """Save current QUBO state to CSV file"""
        if not self._qubos:
            print(f"[QUBOProblem] No QUBO to save")
            return
            
        print(f"[QUBOProblem] Saving current QUBO to {filename}")
        
        # Get labels from the first QUBO
        qubo = self._qubos[0]
        labels = sorted(set([key[0] for key in qubo.keys()]))
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['h1'] + labels)
            
            for i, label_i in enumerate(labels):
                row = [label_i]
                for label_j in labels:
                    value = qubo.get((label_i, label_j), 0.0)
                    row.append(f"{value:.2f}")
                writer.writerow(row)
        
        print(f"[QUBOProblem] Saved to {filename}")


    @qubos.setter
    def qubos(self,value):
        if value is None:
            with self.lock:
                self._qubos = None
        self.load_data(value)


    def init_data(self):
        self.load_data(self.filename)




    def get_info(self):
        """Get current QUBO information for debugging"""
        with self.lock:
            if self._qubos:
                qubo = self._qubos[0]
                labels = sorted(set([key[0] for key in qubo.keys()]))
                size = len(labels)
                non_zero = sum(1 for v in qubo.values() if v != 0.0)
                return {
                    'size': f"{size}x{size}",
                    'labels': labels,
                    'non_zero_entries': non_zero,
                    'total_entries': len(qubo),
                    'source': self.source_type,
                    'file': self.filename,
                    'rt_mode': ['fixed', 'segmented', 'realtime'][self.rt_mode],
                    'pending_updates': len(self.pending_updates)
                }
            else:
                return {'status': 'No QUBO loaded'}
