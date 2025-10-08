from core.vqh_interfaces import QuantumHardwareInterface
from qiskit_aer import AerProvider
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer.primitives import Sampler, Estimator


class LocalSimulatorTemplate(QuantumHardwareInterface):
    def __init__(self):
        self.provider = None
        self.backend = None
        self.name = 'template'

    def connect(self):
        self.provider = AerProvider()

    def get_backend(self, backend_name="aer_simulator"):
        self.backend = self.provider.get_backend(backend_name)

    def run_sampler(self, qcirc, **options):
        #TODO: Implement the run_sampler method
        pass

    def run_estimator(self, qcirc, **options):
        #TODO: Implement the run_estimator method
        pass

