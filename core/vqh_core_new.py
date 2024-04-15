from vqh_source import VQHSource, VQHSourceStrategy, VQHFileReader, VQHProblem, VQHProtocol, VQHProcess
from vqh_mapper import VQHMapper, VQHMappingStrategy
from vqh_process_test import ProcessTest, ProblemTest, ProtocolTest, MappingTest
from time import sleep
from threading import Thread
import numpy as np


PROCESS_LIBRARY = {
        "test": (ProcessTest, ProblemTest, ProtocolTest)
}


def init_vqh_process(name, filename) -> VQHProcess:
    
    process, problem, protocol = PROCESS_LIBRARY[name]
    return process(problem(filename), protocol())



def init_vqh_source(process: VQHProcess) -> VQHSource:

    source = VQHSource(process)
    source.thread.start()
    return source

def wait_for_source_and_mapper(source: VQHSource, mapper: VQHMapper):

    source_finished = False
    mapper_finished = False

    while True:
        sleep(1)
        if source.is_done and not source_finished:
            source.stop()
            source_finished = True
        
        if mapper.is_done and not mapper_finished:
            mapper.stop()
            mapper_finished = True

        if source_finished and mapper_finished:
            break


if __name__ == '__main__':
    process = init_vqh_process("test", "test.json")

    source = VQHSource(process)

    mapping_strategy = MappingTest()
    mapper = VQHMapper(mapping_strategy, source.queue)

    source.thread.start()
    mapper.thread.start()
    
    Thread(target=wait_for_source_and_mapper, args=(source, mapper)).start()

    sleep(5)
    mapper.update_clock_speed(0.2)

