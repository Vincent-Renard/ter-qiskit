#! /usr/bin/env python3
# coding: utf-8


from qiskit import QuantumCircuit, QuantumRegister

q = QuantumRegister(3, 'q')

circ = QuantumCircuit(q)
circ.x(q[0])
circ.cx(q[0], q[1])
circ.cx(q[0], q[2])

print(circ.draw())
