from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, Aer, execute
from qiskit.tools.visualization import circuit_drawer

import math


def maj(p, a, b, c):
    """Majority gate."""
    p.cx(c, b)
    p.cx(c, a)
    p.ccx(a, b, c)


def umaj(p, a, b, c):
    p.ccx(a, b, c)
    p.cx(c, a)
    p.cx(c, b)


def cmaj(p, a, b, c, control):
    p.ccx(c, control, b)
    p.cx(c, a)
    p.ccx(a, b, c)

def cumaj(p,a,b,c,control):
    p.ccx(a, b, c)
    p.cx(c, a)
    p.cx(c, b)


def cums(p, a, b, c, control):
    p.ccx(a, b, c)
    p.cx(c, a)
    p.ccx(a, control, b)

def ums(p, a, b, c):
    """Unmajority gate. and Sum"""
    p.ccx(a, b, c)
    p.cx(c, a)
    p.cx(a, b)

def set(qc, a, N):
    i = 0
    while (N != 0):
        if (N % 2 == 1):
            N -= 1
            qc.x(a[i])
        i += 1
        N /= 2


def findInverse(vA,N):
    for i in range(0,N):
        if((vA*i)%N==1):
            return i



def swap(qc,a,b):
    qc.cx(a, b)
    qc.cx(b, a)
    qc.cx(a, b)



def createAddCirc(adder_subcircuit, cin, a, b, cout, n):
    maj(adder_subcircuit, cin[0], b[0], a[0])

    for j in range(n - 1):
        maj(adder_subcircuit, a[j], b[j + 1], a[j + 1])

    adder_subcircuit.cx(a[n - 1], cout)

    for j in reversed(range(n - 1)):
        ums(adder_subcircuit, a[j], b[j + 1], a[j + 1])

    ums(adder_subcircuit, cin[0], b[0], a[0])


def createControlAddCirc(adder_subcircuit, cin, a, b, cout, n, control):
    cmaj(adder_subcircuit, cin[0], b[0], a[0], control)

    for j in range(n - 1):
        cmaj(adder_subcircuit, a[j], b[j + 1], a[j + 1], control)

    adder_subcircuit.ccx(a[n - 1], control, cout)

    for j in reversed(range(n - 1)):
        cums(adder_subcircuit, a[j], b[j + 1], a[j + 1], control)

    cums(adder_subcircuit, cin[0], b[0], a[0], control)

#b = a-b
def createControlSubCirc(sub_circ, cin, a, b, cout, n, control):
    for i in range(n):
        sub_circ.x(a[i])

    createControlAddCirc(sub_circ, cin, a, b, cout, n, control)

    for i in range(n):
        sub_circ.x(a[i])
        sub_circ.cx(control,b[i])

#b = b - a
def createControlSub2Circ(sub_circ, cin, a, b, cout, n, control):

    for i in range(n):
        sub_circ.cx(control,b[i])

    createControlAddCirc(sub_circ, cin, a, b, cout, n, control)

    for i in range(n):
        sub_circ.cx(control,b[i])

# Vrai si A < B
def createComparator(comp_circ, cin, a, b, cout, n, control):

    for i in range(n):
        comp_circ.x(a[i])

    maj(comp_circ, cin[0], b[0], a[0])

    for j in range(n - 1):
        maj(comp_circ, a[j], b[j + 1], a[j + 1])

    comp_circ.ccx(a[n - 1], control, cout)

    for j in reversed(range(n - 1)):
        umaj(comp_circ, a[j], b[j + 1], a[j + 1])

    umaj(comp_circ, cin[0], b[0], a[0])


    for i in range(n):
        comp_circ.x(a[i])




#b = b %c avec b< 2 c
def createModulo(mod_circ,cin,b,c,cout,n,control):

    # B > C ?
    createComparator(mod_circ, cin, c, b, cout[1], n, control)

    createControlSub2Circ(mod_circ, cin, c, b, cout[0], n, cout[1])



# b= b+a % c
def createAddModulo(add_circ,cin,a,b,c,cout,n,control):
    # b = a+b
  createControlAddCirc(add_circ,cin,a,b,cout[0],n,control)

  # c - b < 0 ?
  createComparator(add_circ,cin,c,b,cout[1],n,control)
 # add_circ.x(cout[1])
   #  b = b-c

  createControlSub2Circ(add_circ,cin,c,b,cout[0],n,cout[1])

  # Il faut reintialiser cout[1]
  createComparator(add_circ, cin, b, a, cout[1], n, control)



def hadamardX(qc, q, nb):
    for i in range(0, nb):
        qc.h(q[i])


#Calcule control * vA % vC et stock le resultat dans control
def newmultAmodC(qc,a,b,c,vA,vC,control,cin,cout,n,inp):

    set(qc,c,vC)
    val =vA


    for i in range(0,inp):
        set(qc,a,val)
        print(val)
        createAddModulo(qc, cin, a, b, c, cout, n, control[i])
        set(qc,a,val)
        val= (val*2)%vC

    # on swap b et control
    for i in range(0,inp):
        swap(qc,b[i],control[i])

    val=findInverse(vA, vC)
    print("Inverse==")
    print(val)


    #on multiplie b par l'inverse de a pour pouvoir le reintialiser à 0
    for i in range(0,inp):
        set(qc,a,val)
        createAddModulo(qc, cin, a, b, c, cout, n, control[i])
        set(qc, a, val)
        print(val)
        val = (val * 2) % vC

    qc.x(b[0])


n = 5
#taille du registre de controle

inp= 5

a = QuantumRegister(n, "a")
b = QuantumRegister(n, "b")
c = QuantumRegister(n,"c")

cin = QuantumRegister(1, "cin")
cout = QuantumRegister(2, "cout")
control = QuantumRegister(inp, "control")

ans = ClassicalRegister(n + 2, "ans")
qc = QuantumCircuit(a, b,c, cin, cout, ans,control ,name="rippleadd")


#hadamardX(qc,control,inp)


set(qc,control,5)

qc.barrier()

#vA et control  doivent être inférieur à vC

#Calcule 3 * control %vC et stock le resultat dans b

vA=7
vC=9




#stock le resultat dans control et remet bien b à 0
newmultAmodC(qc,a,b,c,vA,vC,control,cin,cout,n,inp)

for j in range(n):
    qc.measure(control[j], ans[j])

qc.measure(cout[0],ans[n])
qc.measure(cout[1], ans[n+1])


print("Run")

backend = Aer.get_backend('qasm_simulator')
job_sim = execute(qc, backend,shots=1)
print(job_sim.result().get_counts(qc))
