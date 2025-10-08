from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import json
import csv
import numpy as np
from .base import QUBOController


class OSCQUBOController(QUBOController):
    def __init__(self, problem_instance=None, ip="127.0.0.1", port=1451, vqh_controller=None):
        self.problem = problem_instance
        self.ip = ip
        self.port = port
        self.server = None
        self.server_thread = None
        self.current_matrix = {}
        self.matrix_size = 4  # Default size
        self.parent_controller = vqh_controller
        
    def start(self):
        """Start the OSC server in a separate thread"""
        dispatcher = Dispatcher()
        
        # Register OSC handlers
        dispatcher.map("/vqh/qubo/size", self.handle_size)
        dispatcher.map("/vqh/qubo/entry", self.handle_entry)
        dispatcher.map("/vqh/qubo/row", self.handle_row)
        dispatcher.map("/vqh/qubo/matrix", self.handle_matrix)
        dispatcher.map("/vqh/qubo/save", self.handle_save)
        dispatcher.map("/vqh/qubo/load", self.handle_load)
        dispatcher.map("/vqh/qubo/clear", self.handle_clear)
        
        self.server = BlockingOSCUDPServer((self.ip, self.port), dispatcher)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"OSC QUBO Controller listening on {self.ip}:{self.port}")
    
    def stop(self):
        """Stop the OSC server"""
        if self.server:
            self.server.shutdown()
            if self.server_thread:
                self.server_thread.join()
            print("OSC QUBO Controller stopped")
    
    def handle_size(self, address, *args):
        """Set the size of the QUBO matrix"""
        if len(args) > 0:
            self.matrix_size = int(args[0])
            self.clear_matrix()
            print(f"QUBO matrix size set to {self.matrix_size}x{self.matrix_size}")
    
    def handle_entry(self, address, *args):
        """Update a single entry in the QUBO matrix"""
        if len(args) >= 3:
            i, j, value = int(args[0]), int(args[1]), float(args[2])
            label_i = f"s{i}"
            label_j = f"s{j}"
            
            if (label_i, label_j) not in self.current_matrix:
                self.current_matrix = self.init_matrix()
            
            self.current_matrix[(label_i, label_j)] = value
            
            # Update the problem instance if connected
            if self.problem:
                self.problem.update_from_osc({
                    'entries': [{'i': i, 'j': j, 'value': value}]
                })
            
            print(f"Updated QUBO[{label_i},{label_j}] = {value}")
    
    def handle_row(self, address, *args):
        """Update an entire row of the QUBO matrix"""
        if len(args) > 1:
            row_index = int(args[0])
            values = [float(v) for v in args[1:]]
            
            label_i = f"s{row_index}"
            for j, value in enumerate(values[:self.matrix_size]):
                label_j = f"s{j}"
                self.current_matrix[(label_i, label_j)] = value
            
            if self.problem:
                entries = [{'i': row_index, 'j': j, 'value': v} 
                          for j, v in enumerate(values[:self.matrix_size])]
                self.problem.update_from_osc({'entries': entries})
            
            print(f"Updated QUBO row {row_index}")
    
    def handle_matrix(self, address, *args):
        """Update the entire QUBO matrix"""
        if len(args) >= self.matrix_size * self.matrix_size:
            matrix = np.array(args[:self.matrix_size * self.matrix_size])
            matrix = matrix.reshape(self.matrix_size, self.matrix_size)
            
            self.current_matrix = {}
            for i in range(self.matrix_size):
                for j in range(self.matrix_size):
                    label_i = f"s{i}"
                    label_j = f"s{j}"
                    self.current_matrix[(label_i, label_j)] = float(matrix[i, j])
            
            if self.problem:
                self.problem.update_from_osc({'matrix': matrix.tolist()})
            
            print(f"Updated entire QUBO matrix")
    
    def handle_save(self, address, *args):
        """Save current matrix to CSV file"""
        filename = ""
        if len(args) > 0 and isinstance(args[0], str):
            filename = args[0]
        else:
            raise ValueError("Filename must be provided to save QUBO matrix")
        
        self.parent_controller.source.strategy.problem.save_current_to_csv(filename)
        #self.save_to_csv(filename)
        print(f"Saved QUBO matrix to {filename}")
    
    def handle_load(self, address, *args):
        """Load matrix from CSV file"""
        filename = ""
        if len(args) > 0 and isinstance(args[0], str):
            filename = args[0]
        else:
            raise ValueError("Filename must be provided to load QUBO matrix")
        
        self.parent_controller.source.strategy.problem.load_from_csv(filename)
        print(f"Loaded QUBO matrix from {filename}")
    
    def handle_clear(self, address, *args):
        """Clear the QUBO matrix"""
        self.clear_matrix()
        print("Cleared QUBO matrix")
    
    def init_matrix(self):
        """Initialize an empty matrix"""
        matrix = {}
        for i in range(self.matrix_size):
            for j in range(self.matrix_size):
                label_i = f"s{i}"
                label_j = f"s{j}"
                matrix[(label_i, label_j)] = 0.0
        return matrix
    
    def clear_matrix(self):
        """Clear the current matrix"""
        self.current_matrix = self.init_matrix()
        if self.problem:
            matrix = [[0.0] * self.matrix_size for _ in range(self.matrix_size)]
            self.problem.update_from_osc({'matrix': matrix})
    
    def save_to_csv(self, filename):
        """Save the current matrix to a CSV file"""
        labels = [f"s{i}" for i in range(self.matrix_size)]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['h1'] + labels)
            
            for i, label_i in enumerate(labels):
                row = [label_i]
                for label_j in labels:
                    value = self.current_matrix.get((label_i, label_j), 0.0)
                    row.append(f"{value:.1f}")
                writer.writerow(row)
    
    def load_from_csv(self, filename):
        """Load a matrix from a CSV file"""
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
        
        header = rows[0]
        labels = header[1:]
        self.matrix_size = len(labels)
        
        self.current_matrix = {}
        for i, row in enumerate(rows[1:self.matrix_size+1]):
            label_i = row[0]
            for j, value in enumerate(row[1:self.matrix_size+1]):
                label_j = labels[j]
                self.current_matrix[(label_i, label_j)] = float(value)
        
        if self.problem:
            matrix = [[0.0] * self.matrix_size for _ in range(self.matrix_size)]
            for i in range(self.matrix_size):
                for j in range(self.matrix_size):
                    label_i = labels[i]
                    label_j = labels[j]
                    matrix[i][j] = self.current_matrix.get((label_i, label_j), 0.0)
            self.problem.update_from_osc({'matrix': matrix})
