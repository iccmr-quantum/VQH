from core.vqh_interfaces import MappingInterface
import asyncio
import numpy as np
import time
import requests
import json
import os
import xml.etree.ElementTree as ET


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
        self.scale = None

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
        #data_dict['values'] = data[1]

        data_msg = {
            "content": data_dict,
            "password": self.pwd
        }

        #print(data_dict)
        #self.current_data = data
        response = requests.post(self._page_url, data=json.dumps(data_msg), headers=self._headers)
        print(f"We have composed page {response.json()['id']} of the Circular Book.")

    #TODO: Migrate to new API
    def post_book(self, data, **kwargs):
        raise ValueError('This method is now deprecated')
        """Post a book to the database"""
        bookid = self.get_last_book_id()
        #bookid = "book_6"
        if bookid.startswith('book_'):
            bookid = int(bookid[5:])
        
        else:
            raise ValueError('Book id does not start with "book_"')
        
        newid = f'book_{bookid+1}'

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

        #print(data_dict)
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
        
        newid = f'book_{bookid+1}'

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




