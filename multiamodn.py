from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, Aer, execute
from qiskit.tools.visualization import circuit_drawer

import math

#For modular multiplication#

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

def cset(qc,control,a,N):
    i = 0
    while (N != 0):
        if (N % 2 == 1):
            N -= 1
            qc.cx(control,a[i])
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

def cswap(qc,c,a,b):
    qc.ccx(c,a, b)
    qc.ccx(c,b, a)
    qc.ccx(c,a, b)


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


def createComparator2(comp_circ, cin, a, b, vA,cout, n, control):

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


def createAddModuloConst(add_circ,cin,a,b,vA,vC,cout,n,control):
    # b = a+b

  set(add_circ,a,vA)
  createControlAddCirc(add_circ, cin, a, b, cout[0], n, control)
  set(add_circ, a, vA)

    # c - b < 0 ?
  set(add_circ,a,vC)
  createComparator(add_circ,cin,a,b,cout[1],n,control)
 # add_circ.x(cout[1])
   #  b = b-c
  createControlSub2Circ(add_circ,cin,a,b,cout[0],n,cout[1])
  set(add_circ, a, vC)

  set(add_circ,a,vA)
  # Il faut reintialiser cout[1]
  createComparator(add_circ, cin, b, a, cout[1], n, control)
  set(add_circ, a, vA)



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


#Calcule c * vA % vC et stock le resultat dans c
def multAmodC(qc,a,b,vA,vC,c,cin,cout,n,inp):

    val =vA

    for i in range(0,inp):
        print(val)
        createAddModuloConst(qc, cin, a, b, val, vC, cout, n, c[i])
        val= (val*2)%vC

    # on swap b et c
    for i in range(0,inp):
        swap(qc,b[i],c[i])

    set(qc,a,vC)
    set(qc,cout[1],1)
    createControlSubCirc(qc, cin, a, b, cout[0], n, cout[1])
    set(qc, cout[1], 1)
    set(qc,a,vC)

    val = findInverse(vA, vC)
    print("Inverse==")
    #on multiplie b par l'inverse de a pour pouvoir le reintialiser à 0
    for i in range(0,inp):

        createAddModuloConst(qc, cin, a, b, val, vC, cout, n, c[i])
        print(val)
        val = (val * 2) % vC

    set(qc,b,vC)


#taille de registre
n = 5
inp= n

#total = n*3+3

a = QuantumRegister(n, "a")
b = QuantumRegister(n, "b")

cin = QuantumRegister(1, "cin")
cout = QuantumRegister(2, "cout")
c = QuantumRegister(inp, "c")

ans = ClassicalRegister(n + 3, "ans")
qc = QuantumCircuit(a, b,c , cin, cout, ans,name="rippleadd")

set(qc,c,2)

qc.barrier()
#vA et c  doivent être inférieur à vC
vA=7
vC=15

#Calcule c * vA %vC et stock le resultat dans c
#et remet bien a et b à 0

multAmodC(qc,a,b,vA,vC,c,cin,cout,n,inp)

for j in range(n):
    qc.measure(c[j], ans[j])


#Mesure pour vérifier absence erreur
#normalement tous égale a 0
qc.measure(cout[0],ans[n])
qc.measure(cout[1], ans[n+1])
qc.measure(cin[0],ans[n+2])

print("Run")

backend = Aer.get_backend('qasm_simulator')
job_sim = execute(qc, backend,shots=100)
print(job_sim.result().get_counts(qc))
