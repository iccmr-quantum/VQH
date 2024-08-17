from core.vqh_interfaces import QuantumHardwareInterface
from qiskit_aer import AerProvider
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager


class LocalSimulatorInterface1(QuantumHardwareInterface):
    def __init__(self):
        self.provider = None
        self.backend = None
        self.name = 'local'

    def connect(self):
        self.provider = AerProvider()

    def get_backend(self, backend_name="aer_simulator"):
        self.backend = self.provider.get_backend(backend_name)

    def execute(self, qcirc, shots=1024):
        pass_manager = generate_preset_pass_manager(backend=self.backend, optimization_level=1)
        qcirc_pass = pass_manager.run(qcirc)

        job = self.backend.run(qcirc_pass, shots=shots, memory=True)
        return job
    
    def optimize(self, qcirc):
        pass

# class LocalSimulatorInterface1(QuantumHardwareInterface):
#     def __init__(self):
#         self.name = 'local'

#     def connect(self):
#         pass

#     def get_backend(self, backend_name="aer_simulator"):
#         pass

#     def execute(self, qcirc, shots=1024):
#         pass
    
#     def optimize(self, qcirc):
#         pass
