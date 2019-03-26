from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, Aer, execute
from qiskit.tools.visualization import circuit_drawer
from qiskit.tools.visualization import plot_histogram

import math

from fractions import Fraction


def sampled_freq_to_period(sampled_freq, num_freqs, max_period):
    f = Fraction(sampled_freq, num_freqs)
    r = f.limit_denominator(max_period)
    return r.denominator


def qft(circ, q, n):
    """n-qubit QFT on q in circ."""
    for j in range(n):
        for k in range(j):
            circ.cu1(math.pi/float(2**(j-k)), q[j], q[k])
        circ.h(q[j])


def qftN(circ, q, deb,fin):
    """n-qubit QFT on q in circ."""
    for j in range(deb,fin):
        for k in range(deb,j):
            circ.cu1(math.pi/float(2**(j-k)), q[j], q[k])
    circ.h(q[j])



#Circuit for 7*input
def multi7mod15(qc,q,i=0):


    qc.x(q[0+i])
    qc.x(q[1+i])
    qc.x(q[2+i])
    qc.x(q[3+i])

    qc.cx(q[2+i],q[1+i])
    qc.cx(q[1+i],q[2+i])
    qc.cx(q[2+i], q[1+i])

    qc.cx(q[1+i],q[0+i])
    qc.cx(q[0+i], q[1+i])
    qc.cx(q[1+i], q[0+i])

    qc.cx(q[3+i],q[0+i])
    qc.cx(q[0+i], q[3+i])
    qc.cx(q[3+i], q[0+i])

#Controlled Circuit for 7*input with c control qbit
def cmulti7mod15(qc,q,c,i=0):


    qc.cx(c,q[0+i])
    qc.cx(c,q[1+i])
    qc.cx(c,q[2+i])
    qc.cx(c,q[3+i])

    qc.ccx(c,q[2+i],q[1+i])
    qc.ccx(c,q[1+i],q[2+i])
    qc.ccx(c,q[2+i], q[1+i])

    qc.ccx(c,q[1+i],q[0+i])
    qc.ccx(c,q[0+i], q[1+i])
    qc.ccx(c,q[1+i], q[0+i])

    qc.ccx(c,q[3+i],q[0+i])
    qc.ccx(c,q[0+i], q[3+i])
    qc.ccx(c,q[3+i], q[0+i])




#Controlled Circuit for 7^power with c control qbit
def cpower7mod15(qc,q,c,power,i=0):
    for j in range(1,power+1):

        cmulti7mod15(qc, q, c, i)
        qc.barrier()



def createPowerCircuit7mod15(qc,q,i=0,nbInputQbit=3):

    for i in range(nbInputQbit-1,-1,-1):
        power=2**(nbInputQbit-i-1)
        cpower7mod15(qc,q,q[i],power,nbInputQbit)



def hadamardX(qc ,q,nb):
  for i in range(0 ,nb):
      qc.h(q[i])



#Mesure les qbit des registre deb à fin exclus
def measureX(qc,q,c,deb,fin):
    for i in range(deb,fin):
        qc.measure(q[i],c[i])


def calculPeriod(counts,deb,nbInputQbit):

    maxPeriodFind=0

    for a in counts:
        b = 0
        mul = 2**(nbInputQbit-1)
        valMax= 2**nbInputQbit

        for i in range(deb, deb+nbInputQbit):
            b += int(int(a[i]) * mul)
            mul /= 2
        if b != 0:
            freq = sampled_freq_to_period(b, valMax, 15)
            maxPeriodFind=max(freq,maxPeriodFind)
            print(str(a)+"=>"+str(b)+"/"+str(valMax) + ("=>") + str(freq))

    return maxPeriodFind



#Decompose N si possible et affiche le resultat
def decompose(a,periode,N):
    if(period%2==1):
        print("Période non pair, il faut recommencer avec un autre A\n")
    else :
       r=period/2
       if((int(a**r)+1)%N==0):
           print("N:"+str(N)+" divise (A**R)+1 , il faut recommencer avec un autre A\n")

       else:

           p1= math.gcd(N,int(a**r)-1)
           p2= math.gcd(N,int(a**r)+1)
           print(str(N)+"="+str(p1)+"*"+str(p2))



 #On recherche la periode de 7**x mod 15




#On peut changer le nombre de bit d'entrée pour voir que tout fonctionne
#Valeur 3 par defaut pour respecter la contrainte des 7 qbits du circuit.
nbInputQbit = 3
sizeCircuitPower=4
size = nbInputQbit+sizeCircuitPower

q = QuantumRegister(size)
c = ClassicalRegister(size)
qc = QuantumCircuit(q, c)



#On met en superposition total le registre d'entrée
hadamardX(qc,q,nbInputQbit)

#1 element neutre de la multiplication
qc.x(q[size-1])
qc.barrier()

#On crée le circuit 7^x avec x valeur pris dans le registre d'entrée
createPowerCircuit7mod15(qc,q,0,nbInputQbit)
qc.barrier()

#Transformation de Fourier Quantique
qft(qc,q,nbInputQbit)

#On mesure les Qbit d'entrée
measureX(qc,q,c,0,nbInputQbit)


#Lance la simulation
backend = Aer.get_backend('qasm_simulator')
job_sim = execute(qc, backend)
sim_result = job_sim.result()


#On affiche le circuit(opt)
t = circuit_drawer(qc,0.7,None,None,"text")
print(t)

#On affiche les resultat
# Si fonctionne le nombre de pic doit être egal à la période càd ici 4
print(sim_result.get_counts(qc))



counts = sim_result.get_counts(qc)
period=calculPeriod(counts,sizeCircuitPower,nbInputQbit)

if(period==0):
    print("Erreur dans la recherche de période\n")
else:
    print("La période vaut "+str(period)+"\n")
    decompose(7,period,15)






