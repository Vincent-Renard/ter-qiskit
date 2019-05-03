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



#Not used
def cswap(qc,c,a,b):
    qc.ccx(c,a, b)
    qc.ccx(c,b, a)
    qc.ccx(c,a, b)



#Not used
def createMult2(qc,q,control,cin,n):
     cswap(qc,control,cin,q[0])
     for i in range(1,n):
         cswap(qc,control,cin,q[i])






'''
def multAmodC(qc,a,b,c,vA,vC,control,cin,cout,n):

    if (vA%2==1) and vA >1:
        print(vA)
        print("+x")
        vA-=1
        multAmodC(qc, a, b, c, vA, vC, control, cin, cout, n)
        createAddModulo(qc,cin,a,b,c,cout,n,control)

    elif  vA>1 :
        print(vA)
        print("*2")
        vA= int(vA/2)
        multAmodC(qc, a, b, c, vA, vC, control, cin, cout, n)
        createMult2(qc,b,control,cin[0],n)
        createModulo(qc,cin,b,c,cout,n,control)

'''

#Calcule control * vA % vC
def newmultAmodC(qc,a,b,c,vA,vC,control,cin,cout,n,inp):

    set(qc,c,vC)
    val =vA

    for i in range(0,2):
        set(qc,a,val)
        print(val)
        createAddModulo(qc, cin, a, b, c, cout, n, control[i])
        set(qc,a,val)
        val= (val*2)%vC


n = 4

#taille du registre de controle
inp=3

a = QuantumRegister(n, "a")
b = QuantumRegister(n, "b")
c = QuantumRegister(n,"c")

# swap c avec d


cin = QuantumRegister(1, "cin")
cout = QuantumRegister(2, "cout")
control = QuantumRegister(inp, "control")





ans = ClassicalRegister(n + 2, "ans")
qc = QuantumCircuit(a, b,c, cin, cout, ans,control ,name="rippleadd")



subcircuit = QuantumCircuit(cin, a, b,c, cout, control)




'''
set(qc, a, 5)
set(qc, b, 4)
set(qc,c,7)

'''
'''
set(qc,a,4)

set(qc,c,6)
'''




set(qc,control,3)

qc.barrier()



#createMult2(qc,b,control[0],cin[0],n)
#createControlSubCirc(subcircuit, cin, a, b, cout, n, control[0])
#createControlAddCirc(subcircuit,cin,a,b,cout[0],n,control[0]) ->OK
#createAddModulo(subcircuit,cin,a,b,c,cout,n,control[0])
#createAddModulo(subcircuit,cin,a,b,c,cout,n,control[0])
#createComparator(subcircuit,cin,c,b,cout[1],n,control[0])
#createControlSubCirc(subcircuit,cin,a,b,cout[1],n,control[0])
#createModulo(subcircuit,cin,b,c,cout,n,control[0])
#createControlSub2Circ(subcircuit, cin, c, b, cout[0], n, control[0])
#qc += subcircuit


vA=3
vC=6

#Calcule 3 * control %vC et stock le resultat dans b
newmultAmodC(qc,a,b,c,vA,vC,control,cin,cout,n,inp)






for j in range(n):
    qc.measure(b[j], ans[j])

qc.measure(cout[0],ans[n])
qc.measure(cout[1], ans[n+1])



print("Run")

backend = Aer.get_backend('qasm_simulator')
job_sim = execute(qc, backend)
print(job_sim.result().get_counts(qc))