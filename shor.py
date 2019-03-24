#! /usr/bin/env python3
# coding: utf-8
import random
import time

#Fonction PGDC
def fctPgcd(N, a):
    if a == 0:
        return abs(N)
    else:
        r = abs(N) % abs(a)
        return fctPgcd(abs(a), r)

#Fonction pour trouver la période de (a**k)%N
def fctPeriode(N,a):
    k=0
    while True:
        k+=1
        res=(a**k)%N
        if res==1:
            return k

#Fonction pour trouver la période de (a**k)%N VERSION QUANTIQUE
def fctPeriodeQuantique(a,N):
    return 0

#Fonction algo de shor
def fctshor(N,mode):
    start_time = time.time()
    # Choix de a aléatoire 0<a<N
    a = random.choice(sequence)
    print("Shor=========================\nN=" + str(N)+"\na=" + str(a))

    # Pgcd de N et de a
    pgcd = fctPgcd(a, N)
    print("Pgcd: "+str(pgcd))

    # Si pgcd!=1 facto réussie
    if pgcd != 1:
        return pgcd, int(N / pgcd),time.time()-start_time

    if(mode=="quantique"):
        # utilisation du sous programme de recherche quantique pour trouver la période
        periode = fctPeriodeQuantique(N, a)
    else:
        # utilisation du sous programme de recherche quantique pour trouver la période
        periode = fctPeriode(N, a)
    print("Periode: " + str(periode))

    # Tests sur la période
    if periode%2!=1:
        temp=a**(int(periode/2))
        if temp%N!=1:
            #Calcul des 2 facteurs
            res1=fctPgcd(N,temp+1)
            res2=fctPgcd(N,temp-1)
            print("Res1: " + str(res1))
            print("Res2: " + str(res2))
            if res1*res2==N and res1!=1 and res2!=1:
                return res1,res2,time.time()-start_time
    return fctshor(N,"normal")





# Choix de N
N = 15

# Enlever les nombres dont le pgcd(nombre,N)!=1 et donne direct la réponse (optionnel)
sequence=[]
for i in range(2,N-1) :
    if fctPgcd(N,i)==1:
        sequence.append(i)

#Algo normal
resNormal = fctshor(N,"normal")
print("Factorisation normal de " + str(N) + " : " + str(resNormal[0]) + " et " + str(resNormal[1]) +" en "+str(resNormal[2]) +" secondes")

#Algo quantique
#resQuantique = fctshor(N,"quantique")
#print("Factorisation avec recherche période quantique de " + str(N) + " : " + str(resQuantique[0]) + " et " + str(resQuantique[1]) +" en "+str(resQuantique[2]) +" secondes")