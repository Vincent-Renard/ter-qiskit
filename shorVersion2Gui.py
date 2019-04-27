#! /usr/bin/env python3
# coding: utf-8
import random
import time
import math
from fractions import Fraction

from qiskit import QuantumCircuit, Aer, execute
from qiskit import QuantumRegister, ClassicalRegister
from qiskit.tools.visualization import circuit_drawer


def hadamardX(qc, q, nb):
    for i in range(0, nb):
        qc.h(q[i])

# Controlled Circuit for 7*input with c control qbit
def cmulti7mod15(qc, q, c, i=0):
    qc.cx(c, q[0 + i])
    qc.cx(c, q[1 + i])
    qc.cx(c, q[2 + i])
    qc.cx(c, q[3 + i])

    qc.ccx(c, q[2 + i], q[1 + i])
    qc.ccx(c, q[1 + i], q[2 + i])
    qc.ccx(c, q[2 + i], q[1 + i])

    qc.ccx(c, q[1 + i], q[0 + i])
    qc.ccx(c, q[0 + i], q[1 + i])
    qc.ccx(c, q[1 + i], q[0 + i])

    qc.ccx(c, q[3 + i], q[0 + i])
    qc.ccx(c, q[0 + i], q[3 + i])
    qc.ccx(c, q[3 + i], q[0 + i])


# Controlled Circuit for 11*input with c control qbit
def cmulti11mod15(qc, q, c, i=0):
    qc.cx(c, q[0 + i])
    qc.cx(c, q[1 + i])
    qc.cx(c, q[2 + i])
    qc.cx(c, q[3 + i])

    qc.ccx(c, q[2 + i], q[0 + i])
    qc.ccx(c, q[0 + i], q[2 + i])
    qc.ccx(c, q[2 + i], q[0 + i])

    qc.ccx(c, q[3 + i], q[1 + i])
    qc.ccx(c, q[1 + i], q[3 + i])
    qc.ccx(c, q[3 + i], q[1 + i])

# Controlled Circuit for 7^power with c control qbit
def cpower7mod15(qc, q, c, power, i=0):
    for j in range(1, power + 1):
        cmulti7mod15(qc, q, c, i)
        qc.barrier()

# Controlled Circuit for 11^power with c control qbit
def cpower11mod15(qc, q, c, power, i=0):
    for j in range(1, power + 1):
        cmulti11mod15(qc, q, c, i)
        qc.barrier()

def createPowerCircuit(QuantumCircuit, QuantumRegister, i=0, nbInputQbit=3, a=7):
    for i in range(nbInputQbit - 1, -1, -1):
        power = 2 ** (nbInputQbit - i - 1)
        if a==7:
            cpower7mod15(QuantumCircuit, QuantumRegister, QuantumRegister[i], power, nbInputQbit)
        elif a==11:
            cpower11mod15(QuantumCircuit, QuantumRegister, QuantumRegister[i], power, nbInputQbit)

def qft(circ, q, n):
    """n-qubit QFT on q in circ."""
    for j in range(n):
        for k in range(j):
            circ.cu1(math.pi / float(2 ** (j - k)), q[j], q[k])
        circ.h(q[j])

# Mesure les qbit des registre deb à fin exclus
def measureX(qc, q, c, deb, fin):
    for i in range(deb, fin):
        qc.measure(q[i], c[i])

def sampled_freq_to_period(sampled_freq, num_freqs, max_period):
    f = Fraction(sampled_freq, num_freqs)
    r = f.limit_denominator(max_period)
    return r.denominator

def calculPeriod(counts, deb, nbInputQbit):
    maxPeriodFind = 0

    for a in counts:
        b = 0
        mul = 2 ** (nbInputQbit - 1)
        valMax = 2 ** nbInputQbit

        for i in range(deb, deb + nbInputQbit):
            b += int(int(a[i]) * mul)
            mul /= 2
        if b != 0:
            freq = sampled_freq_to_period(b, valMax, 15)
            maxPeriodFind = max(freq, maxPeriodFind)
            print(str(a) + "=>" + str(b) + "/" + str(valMax) + ("=>") + str(freq))

    return maxPeriodFind

#Fonction pour trouver la période de (a**k)%N VERSION QUANTIQUE
def fctPeriodeQuantique(N,a):
    nbInputQbit = 3
    sizeCircuitPower = 4
    size = nbInputQbit + sizeCircuitPower

    q = QuantumRegister(size)
    c = ClassicalRegister(size)
    qc = QuantumCircuit(q, c)

    # On met en superposition total le registre d'entrée
    hadamardX(qc, q, nbInputQbit)

    # On va faire la multiplication 1*a pour initialiser
    qc.x(q[size - 1])
    qc.barrier()

    # On crée le circuit a^x avec x valeur pris dans le registre d'entrée
    createPowerCircuit(qc, q, 0, nbInputQbit, a)
    qc.barrier()

    # Transformation de Fourier Quantique pour faire ressortir le résultat
    qft(qc, q, nbInputQbit)

    # On mesure les Qbit d'entrée
    measureX(qc, q, c, 0, nbInputQbit)

    # Lance la simulation
    backend = Aer.get_backend('qasm_simulator')
    job_sim = execute(qc, backend)
    sim_result = job_sim.result()

    # On affiche le circuit(opt)
    t = circuit_drawer(qc, 0.7, None, None, "text")
    print(t)

    # On affiche les resultat
    # Si fonctionne le nombre de pic doit être egal à la période càd ici 4
    print(sim_result.get_counts(qc))

    counts = sim_result.get_counts(qc)
    period = calculPeriod(counts, sizeCircuitPower, nbInputQbit)

    return period


#Fonction pour trouver la période de (a**k)%N
def fctPeriodeNormal(N,a):
    k=0
    while True:
        k+=1
        res=(a**k)%N
        if res==1:
            return k



# Enlever les nombres dont le pgcd(nombre,N)!=1 et donne direct la réponse (optionnel)
def cleanSequence(sequence):
    sequence = []
    for i in range(2, N - 1):
        if math.gcd(N, i) == 1:
            sequence.append(i)
    return sequence


def fctShor(N,sequence):
    #On choisi le a de facon random
    a = random.choice(sequence)
    sequence.remove(a)

    #########################ici on a mis a=11
    a=11
    print("Shor=========================\nN=" + str(N)+"\na=" + str(a))

    # Pgcd de N et de a
    pgcd = math.gcd(N, a)
    print("Pgcd: "+str(pgcd))

    # Si pgcd!=1 factorisation réussie
    if pgcd != 1:
        print("Factorisation directe de " + str(N) + " : " + str(pgcd) + " et " + str(int(N / pgcd)))
        return


    # utilisation du sous programme de recherche normal pour trouver la période
    periodeN = fctPeriodeNormal(N, a)

    # utilisation du sous programme de recherche quantique pour trouver la période
    periodeQ = fctPeriodeQuantique(N, a)

    if(periodeN!=periodeQ):
        print("Erreur periodes différentes")
        print("Periode Normal: " + str(periodeN))
        print("Periode Quantique: " + str(periodeQ))
        return
    periode=periodeQ
    print("Periode: " + str(periode))

    # Tests sur la période
    if periode%2!=1:
        temp=a**(int(periode/2))
        if temp%N!=1:
            #Calcul des 2 facteurs
            res1= math.gcd(N, temp + 1)
            res2= math.gcd(N, temp - 1)
            if res1*res2==N and res1!=1 and res2!=1:
                print("Factorisation de " + str(N) + " : " + str(res1) + " et " + str(res2))
                return
    return fctShor(N,sequence)




N=15
sequence = []
for i in range(2, N - 1):
    sequence.append(i)
# en option
sequence = cleanSequence(sequence)
fctShor(N,sequence)