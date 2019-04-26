#! /usr/bin/env python3
# coding: utf-8
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

size = 4

q = QuantumRegister(size)
c = ClassicalRegister(1)
circ = QuantumCircuit(q, c)

for i in range(1,size):
    circ.x(q[i])
for i in range(size):
    circ.x(q[i])

for i in range(size):
    i=i-((size-1)%size)
    circ.cx(q[(i-1)%size], q[i%size])
    circ.cx(q[i % size],q[(i-1)%size])
    circ.cx(q[(i-1)%size], q[i%size])

for i in range(size):
    circ.measure(q[i], c[0])
print(circ.draw())


