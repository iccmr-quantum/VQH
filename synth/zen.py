from core.vqh_interfaces import MappingInterface
import asyncio
import numpy as np
import time
import requests
import json
import os
import xml.etree.ElementTree as ET
from queue import Queue, Empty
from pythonosc.udp_client import SimpleUDPClient


class ZenMapping(MappingInterface):
    def __init__(self):
    
        if os.path.exists('synth/credentials_zen_local.json'):
            print('Local Credentials file exists')
            self._path = 'synth/credentials_zen_local.json'
        else:
            print('Using public credentials file')
            self._path = 'synth/credentials_zen.json'
        with open(self._path) as f:
            cred = json.load(f)

        self._data_url = cred['url'] 
        self._headers = cred['headers']
        self.pwd = cred['password']
        self.num_pages = cred['num_pages']  
        self.current_data = None
        self.circular_book_id = cred['circular_id']
        self._page_url = f'{self._data_url}/{self.circular_book_id}/page'
        self._book_url = f'{self._data_url}/{self.circular_book_id}'
        self.scale = None
        self.hwQueue = Queue()

        self.qbicon = True

        if self.qbicon:
            self.client = SimpleUDPClient("172.23.37.209", 8070)
            #self.client = SimpleUDPClient("127.0.0.1", 1450)
        else:
            self.client = None

        #self.make_circular_book()

    def post_page(self, data, **kwargs):
        """Post a book to the database"""
        bookid = self.circular_book_id
        
        #print(f'Posting new page in Circular book with id: {bookid}')
        #print(self._page_url)
        #print(self._headers)

        data_dict = {}
        #data_dict['states'] = [[int(x) for x in state] for state in data[2]]
        data_dict['amps'] = [x for x in data[0][0].values()]
        data_dict['value'] = data[1]
        data_dict['state'] = "0000"

        data_msg = {
            "content": data_dict,
            "password": self.pwd
        }

        #print(data_dict)
        #self.current_data = data
        response = requests.post(self._page_url, data=json.dumps(data_msg), headers=self._headers)
        try:
            print(f"We have composed page {response.json()['id']} of the Circular Book.")
        except:
            print(f"We _may_ have composed a page of the Circular Book.")

    #make sure to switch the credentials between HC and HW
    def post_param_page(self, data, **kwargs):
        """Post a parameter page to the infitine book"""
        bookid = self.circular_book_id
        
        #print(f'Posting new page in Circular book with id: {bookid}')
        #print(self._page_url)
        #print(self._headers)

        #print(f'Data list: {data}')
        try:
            params = self.hwQueue.get(timeout=0.05)
            self.hwQueue.put({'params': data[0]})
        except Empty:
            params = {'params': data[0]}

        data_msg = {
            "content": params,
            "password": self.pwd
        }

        self.current_data = data
        response = requests.post(self._page_url, data=json.dumps(data_msg), headers=self._headers)
        try:
            print(f"We have composed page {response.json()['id']} of the Book of Sand.")
        except Exception as e:
            print(f".")

    def post_param_page_qbicon(self, data, **kwargs):
        """Post a parameter page to the infitine book"""
        bookid = self.circular_book_id
        
        #print(f'Posting new page in Circular book with id: {bookid}')
        #print(self._page_url)
        #print(self._headers)

        #print(f'Data list: {data}')
        try:
            params = self.hwQueue.get(timeout=0.05)
            self.hwQueue.put({'params': data[0]})
        except Empty:
            params = {'params': data[0]}

        data_msg = {
            "content": params,
            "password": self.pwd
        }

        self.current_data = data
        response = requests.post(self._page_url, data=json.dumps(data_msg), headers=self._headers)
        try:
            print(f"..")
        except Exception as e:
            print(f".")


        qbicon_energy = data[1]
        
        qbicon_params = ','.join([f"{x:.3f}" for x in params['params']])
        
        qbicon_params = qbicon_params + f",{qbicon_energy:.3f}"

        self.client.send_message("/writ/post", qbicon_params)

    #TODO: Migrate to new API
    #def post_book(self, data, **kwargs):

    #    print(f"DATA: {data}")

    def post_book(self, data, **kwargs):
        #raise ValueError('This method is now deprecated')
        """Post a book to the database"""
        #bookid = self.get_last_book_id()
        bookid = "book_6"
        #if bookid.startswith('book_'):
        #    bookid = int(bookid[5:])
        
        #else:
        #    raise ValueError('Book id does not start with "book_"')
        
        newid = 'book_6'

        print(f'Posting new book with id: {newid}')
        print(self._data_url)
        print(self._headers)

        data_dict = {}
        states = []
        amps = []
        values = []
        for iteration in data:
            if iteration != None:
                states.append([int(x) for x in iteration[2]])
                amps.append([x for x in iteration[0][0].values()])
                values.append(iteration[1])
        data_dict['states'] = states
        data_dict['amps'] = amps
        data_dict['values'] = values
        #data_dict['states'] = [[int(x) for x in iteration[2]] for iteration in data]
        #data_dict['amps'] = [[x for x in iteration[0].values()] for iteration in data]
        #data_dict['values'] = [x for x in iteration[1] for iteration in data]

        data_msg = {
            "key": newid,
            "data": data_dict,
            "password": self.pwd
        }

        print(data_dict)
        self.current_data = data
        response = requests.post(self._data_url, data=json.dumps(data_msg), headers=self._headers)

    #TODO: Migrate to new API
    def post_book_and_update_display(self, data, **kwargs):
        raise ValueError('This method is now deprecated')
        """Post a book to the database"""
        bookid = self.get_last_book_id()
        #bookid = "book_6"
        if bookid.startswith('book_'):
            bookid = int(bookid[5:])
        
        else:
            raise ValueError('Book id does not start with "book_"')
        
        #newid = f'book_{bookid+1}'
        newid = "book_6"

        print(f'Posting new book with id: {newid}')
        print(self._data_url)
        print(self._headers)

        data_dict = {}
        data_dict['states'] = [[int(x) for x in state] for state in data[2]]
        data_dict['amps'] = [[x for x in dist.values()] for dist in data[0]]
        data_dict['values'] = data[1]

        data_msg = {
            "key": newid,
            "data": data_dict,
            "password": self.pwd
        }
        
        #Convert data_dict['states'] to Processing format in xml
        book = ET.Element("book")
        for k, current_state in enumerate(data_dict['states']):
            iteration = ET.SubElement(book, "iteration", id=str(k))
            state = ET.SubElement(iteration, "state")
            amps = ET.SubElement(iteration, "amps")
            #exp = ET.SubElement(iteration, "values")
            for l, stream in enumerate(current_state):
                ET.SubElement(state, "qubit", id=f's{str(l)}').text = str(stream)
                ET.SubElement(amps, "amp", id=f's{str(l)}').text = str(data_dict['amps'][k][l])
            ET.SubElement(iteration, "value", id=f'{str(k)}').text = str(data_dict['values'][k])

        tree = ET.ElementTree(book)
        tree.write("display_hexagonal_chambers/data/processing_data.xml")
        tree.write("java_hexagonal_chambers/data/processing_data.xml")
        #tree.write("synth/processing_data.xml")


        #print(data_dict)
        self.current_data = data
        response = requests.post(self._data_url, data=json.dumps(data_msg), headers=self._headers)

    def get_book(self, **kwargs):
        """Get a book from the database"""
        book = requests.get(self._data_url, headers=self._headers)
        return book.json()
    

    def get_last_book_id(self):
        """Get the id of the last book in the database"""
        book = self.get_book()
        return book['key']


    def make_circular_book(self):

        circular_request = {"password": self.pwd, "num_pages": self.num_pages}
        response = requests.post(self._data_url, data=json.dumps(circular_request), headers=self._headers)
        print(response.json())
        self.circular_book_id = response.json()['id']
        print(f'Created circular book with ID: {self.circular_book_id}')




