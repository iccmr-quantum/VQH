from core.vqh_interfaces import QuantumHardwareInterface
'''
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Options, Session, SamplerOptions
from qiskit_ibm_runtime import SamplerV2 as Sampler

class IBMQHardwareInterface(QuantumHardwareInterface):
    def __init__(self):
        self.provider = None
        self.backend = None
        self.name = 'ibm'
        self.options = None

    def connect(self):
        self.provider = QiskitRuntimeService()
        self.options = SamplerOptions()

    def get_backend(self, backend_name=None):
        print(f'Getting backend {backend_name}')
        self.backend = self.provider.get_backend(backend_name)
        print(f'Backend {self.backend.name} is ready')

    def execute(self, qcirc, shots=1024):
        pass_manager = generate_preset_pass_manager(backend=self.backend, optimization_level=3)
        qcirc_pass = pass_manager.run(qcirc)
        self.options.execution.init_qubits = True
        self.options.default_shots = shots

        print(f'Executing on {self.backend.name}')

        with Session(service=self.provider, backend=self.backend) as session:

            sampler = Sampler(self.backend, options=self.options)
            job = sampler.run(qcirc_pass)
            return job
    
    def optimize(self, qcirc):
        pass
'''

class IBMQHardwareInterface(QuantumHardwareInterface):
    def __init__(self):
        self.name = 'ibm'

    def connect(self):
        pass

    def get_backend(self, backend_name=None):
        pass

    def execute(self, qcirc, shots=1024):
        pass

    def optimize(self, qcirc):
        pass
