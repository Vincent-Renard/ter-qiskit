#! /usr/bin/env python3
# coding: utf-8
import random
import time
import math
from fractions import Fraction

from qiskit import QuantumCircuit, Aer, execute
from qiskit import QuantumRegister, ClassicalRegister
from qiskit.tools.visualization import circuit_drawer

##############################################################################"
#Partie pb de la multiplication modulaire
def dectobin(n,nbits):
    nbin2=str(bin(n)[2:])
    nbin=""
    for i in range(0, len(nbin2)):
        nbin=nbin2[i]+nbin
    while len(nbin)<nbits:
        nbin=nbin+"0"
    return nbin

def inverse(n):
    n1=""
    for i in range(0, len(n)):
        if n[i]=='0':
            n1=n1+"1"
        else:
            n1=n1+"0"
    return n1

def test(swaps,a,N,nbits):
    for i in range(1,N):
        mulb=dectobin(i,nbits)
        if math.log2(a)-int(math.log2(a))!=0:
            mulb=inverse(mulb)
        resb=dectobin((a*i)%N,nbits)
        for swap in range (0,len(swaps)):
            i0 = swaps[swap][0]
            i1 = swaps[swap][1]
            c0 = mulb[i0]
            c1 = mulb[i1]
            mulb=mulb[:i0] + c1 + mulb[i0 + 1:]
            mulb=mulb[:i1] + c0 + mulb[i1 + 1:]
            mulb = mulb[:i1] + c0 + mulb[i1 + 1:]
        if mulb!=resb:
            return False
    return True

def generateListe(swaps,listeswaps):
    listeswaps2 = []
    for m in range(0, len(listeswaps)):
        temp = listeswaps[m].copy()
        for n in range(0, len(swaps)):
            temp2 = temp.copy()
            temp2.append(swaps[n])
            listeswaps2.append(temp2)
    return listeswaps2

def quelsSWAP(a,N,bits):
    swaps = []
    #generation des différents swap possibles
    for c in range(0, bits):
        for b in range(c+1, bits):
            swaps.append([c,b])

    #possibilités pour 1 swap
    listeswapsSave = []
    nbSwap = 1
    for h in range(0,len(swaps)):
        listeswapsSave.append([swaps[h]])
    listeswaps = listeswapsSave.copy()

    while nbSwap!=bits+1:
        #tests de la liste
        for i in range(len(listeswaps)-1,-1,-1):
            if len(listeswaps)!=0:
                #si la combinaison a échoué on l enleve
                if not test(listeswaps[i],a,N,bits):
                    listeswaps.pop(i)
        #si apres tous les tests la liste est pas vide on prend la 1ere combinaison a etre valide
        if len(listeswaps) != 0:
            return listeswaps[0]
        #sinon on génère la liste des combinaisons avec +1 swap
        nbSwap = nbSwap + 1
        listeswapsSave=generateListe(swaps,listeswapsSave)
        listeswaps=listeswapsSave.copy()
    return False
#######################################################################################################

def howManyBits(N):
    return math.floor(math.log2(N)+1)

def hadamardX(qc, q, nb):
    for i in range(0, nb):
        qc.h(q[i])

def cmulti(qc, q, c, i, sizeCircuitPower, a, swaps):
    if math.log2(a) - int(math.log2(a)) != 0:
        for z in range(0,sizeCircuitPower):
            qc.cx(c, q[z + i])
    for s in range(0,len(swaps)):
        if swaps[s][0]>swaps[s][1]:
            s1=swaps[s][0]
            s0=swaps[s][1]
        else:
            s1=swaps[s][1]
            s0=swaps[s][0]
        qc.ccx(c, q[s1 + i], q[s0 + i])
        qc.ccx(c, q[s0 + i], q[s1 + i])
        qc.ccx(c, q[s1 + i], q[s0 + i])

#Création d'un circuit controllé en fct de a qui fait 1*a puis on fait l'exponentiation
def createPowerCircuit(N,QuantumCircuit, QuantumRegister, i=0, nbInputQbit=3,sizeCircuitPower=4, a=7):
    listeSwap=quelsSWAP(a,N,sizeCircuitPower)
    if len(listeSwap)==0:
        return
    for i in range(nbInputQbit - 1, -1, -1):
        power = 2 ** (nbInputQbit - i - 1)
        for j in range(1, power + 1):
            cmulti(QuantumCircuit, QuantumRegister, QuantumRegister[i], nbInputQbit,sizeCircuitPower,a ,listeSwap)
            QuantumCircuit.barrier()

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
    sizeCircuitPower = howManyBits(N)
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
    createPowerCircuit(N,qc, q, 0, nbInputQbit,sizeCircuitPower, a)
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
def cleanSequence(sequence,N):
    sequence = []
    for i in range(2, N - 1):
        if math.gcd(N, i) == 1:
            sequence.append(i)
    return sequence


def fctShor(N,sequence):
    #On choisi le a de facon random
    a = random.choice(sequence)
    sequence.remove(a)

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
sequence = cleanSequence(sequence,N)
fctShor(N,sequence)

