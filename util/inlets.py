from threading import Lock

class VQHOutlet:
    def __init__(self):
        self.inlets = {}
        self.lock = Lock()

    def bang(self, message_dict):
        with self.lock:
            for attribute, msg in message_dict.items():
                if attribute in self.inlets:
                    #print(f"Updating attribute {attribute} in inlet {self.inlets[attribute].target_instance}")
                    self.inlets[attribute].update(msg)
                else:
                    print(f"Warning: no inlet for attribute {attribute}")


    def close(self):
        self.bang(None) 

    def connect(self, inlet):
        self.inlets[inlet.target_attribute] = inlet

    def disconnect(self, inlet):
        self.inlets.pop(inlet.target_attribute)

    def reset(self):
        self.inlets = {}



class VQHInlet:
    def __init__(self, target_instance, target_attribute):
        self.target_instance = target_instance
        self.target_attribute = target_attribute
        self.name = f'{target_attribute}'

    def update(self, message):
        setattr(self.target_instance, self.target_attribute, message)


class InletLinkedAttribute:
    def __init__(self, setter_method):
        self.setter_method = setter_method
        self.lock = Lock()

    def __get__(self, instance, owner): 
        return self.getter(instance)

    def __set__(self, instance, value):
        with self.lock:
            self.setter_method(value)
