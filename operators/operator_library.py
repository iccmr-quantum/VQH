from abstract_classes import VQHOperator
from operator.qubo import VQHOperatorQUBO

class OperatorLibrary():
    def __init__(self):
        self._operators = {
            "qubo": VQHOperatorQUBO, 
        }
    def get_protocol(self, operator_name: str='qubo') -> VQHOperator:
        """Returns:operator class associated with name.
        """
        operator = self._operators.get(operator_name)
        if not operator:
            raise ValueError(f'"{operator_name}" is not a valid name. Valid names are: {list(self._operators.keys())}')
        return operator(operator_name)


