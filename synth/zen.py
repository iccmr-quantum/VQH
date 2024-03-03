from abstract_classes import SonificationInterface
import asyncio
import numpy as np
import time
import requests
import json
import os
import xml.etree.ElementTree as ET


class ZenMapping(SonificationInterface):
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
        self.current_data = None

    def post_book(self, data, **kwargs):
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

    def post_book_and_update_display(self, data, **kwargs):
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
