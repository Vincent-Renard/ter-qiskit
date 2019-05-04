#! /usr/bin/env python3
# coding: utf-8


from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, Aer, execute

q = QuantumRegister(3,'q')
c = ClassicalRegister(3,'c')
qc = QuantumCircuit(q, c)


qc.ct(q[0], q[1],q[3])
qc.measure(q, c)

print(qc.draw())

backend = Aer.get_backend('qasm_simulator')
job_sim = execute(qc, backend)
sim_result = job_sim.result()

print(sim_result.get_counts(qc))
print(qc.draw())
