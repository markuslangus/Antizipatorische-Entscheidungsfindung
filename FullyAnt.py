
#Import-Befehle
import random
import numpy as np
import math
import copy

#Inputdaten der Beispielinstanz

#Gewährleistung der gleichen Zufallszahlenabfolge
random.seed(26)
#Liste der Knoten des Modells
knoten = list(range(22))
#Liste der Koordinaten der Knoten
locations = [(-8, 4), (-7, 7), (-6, 2), (-4, 6), (-3, 7), (9, 3), (6, 3), (5, 0), (7, -5), (8, -4),
             (-7, 6), (-5, 5), (-2, 3), (-4, 9), (-3, 8), (9, -2), (5, 1), (6, -2), (7, -6), (8, -8),
             (-8, 3), (8, 4)]
#Anzahl der Elemente der Koordinatenliste
anzLocations = len(locations)
#Funktion zur Distanzberechnung zwischen den einzelnen Knoten
def distanzberechnung(a,b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (math.sqrt(dx*dx + dy*dy))
#Erstellung und anschließende Berechnung der Distanz- bzw. Kostenmatrix c_ij
c_ij = np.zeros((anzLocations, anzLocations), dtype=float)
for i in range(anzLocations):
    for j in range(anzLocations):
        c_ij[i,j] = distanzberechnung(locations[i], locations[j])
#Big-M
M = 1_000_000
#Liste der Kundenanfragen des Modells
anfragen = list(range(10))
#Liste der eingesetzten Fahrzeuge
fahrzeuge = list(range(2))
#Eintreffzeitpunkte der Anfragen
t_r = [2, 4, 8, 9, 10, 11, 13, 15, 18, 22]
#Parameter für die tolerierte maximale Verspätung in Zeiteinheiten
alpha = 6
#Liste der frühesten Bedienzeiten der Kundenanfragen
frühest = t_r
frühest = frühest + frühest + [0, 0]
#Liste der spätesten Bedienzeiten der Kundenanfragen
spätest = []
for kunde in anfragen:
    spätest_berechnen = frühest[kunde]+c_ij[kunde,(kunde+10)]+alpha
    spätest.append(spätest_berechnen)
spätest = spätest + spätest + [M, M]

#Durchführung des Vollkommen-Antizipatorischen-Ansatzes

#initiale Touren- und Zeitenpläne der beiden Fahrzeuge
tourenplan = [[20],[21]]
tourenplanBest = copy.deepcopy(tourenplan)
zeitenplan = [[0],[0]]
zeitenplanBest = copy.deepcopy(zeitenplan)
#beste gefundene Lösung hinsichtlich der Anzahl insgesamt angenommener Anfragen
insgesamtAngenommenBest = 0
#beste gefundene Lösung hinsichtlich der Gesamdauer der Tour
gesamtdauerBest = 0
#Menge der nicht eingeplanten Anfragen
ungeplanteAnfragen = copy.deepcopy(anfragen)
#Iterationszähler
beta = 100
#while-Schleife für den Destroy- und Repair-Prozess
while beta != 0:
    #Destroy
    destroy = []
    for auto in tourenplan:
        for kunde in auto[1:]:
            if kunde < 10:
                destroy.append(kunde)
    if len(destroy) > 0:
        d = random.choice(destroy)
        for auto in tourenplan:
            if d in auto:
                autoIndex = tourenplan.index(auto)
                oriIndex = tourenplan[autoIndex].index(d)
                destiIndex = tourenplan[autoIndex].index(d+10)
                tourenplan[autoIndex].remove(d)
                tourenplan[autoIndex].remove(d+10)
                del zeitenplan[autoIndex][destiIndex]
                del zeitenplan[autoIndex][oriIndex]
                ungeplanteAnfragen.append(d)
                break
    #Repair
    random.shuffle(ungeplanteAnfragen)
    eingefügt = []
    for origin in ungeplanteAnfragen:
        destination = origin + 10
        einfügenZulässig = False
        zusatzkostenOpt = M
        for k in fahrzeuge:
            for m in range(1, len(tourenplan[k])+1):
                if m != len(tourenplan[k]):
                    zusatzkosten = c_ij[tourenplan[k][m-1],origin] + c_ij[origin,destination] + c_ij[destination,tourenplan[k][m]] - c_ij[tourenplan[k][m-1],tourenplan[k][m]]
                else:
                    zusatzkosten = c_ij[tourenplan[k][m-1],origin] + c_ij[origin, destination]
                if zusatzkosten < zusatzkostenOpt:
                    zulässig = []  
                    provisionsTourenplan = copy.deepcopy(tourenplan[k])
                    provisionsTourenplan.insert(m,destination)
                    provisionsTourenplan.insert(m,origin)
                    provisionsZeitenplan = [copy.deepcopy(zeitenplan[k][0])]
                    for haltestelle in provisionsTourenplan[1:]:
                        indexHaltestelle = provisionsTourenplan.index(haltestelle)
                        zeitVorgänger = provisionsZeitenplan[indexHaltestelle-1]
                        mindestZeit = zeitVorgänger + c_ij[provisionsTourenplan[indexHaltestelle-1], haltestelle]
                        if haltestelle < 10:
                            mindestZeit = max(mindestZeit, frühest[haltestelle])
                        provisionsZeitenplan.append(mindestZeit)
                    for haltestelle in provisionsTourenplan:                       
                        indexHaltestelle = provisionsTourenplan.index(haltestelle)
                        if frühest[haltestelle] <= provisionsZeitenplan[indexHaltestelle] <= spätest[haltestelle]:
                            zulässig.append(True)
                        else:
                            zulässig.append(False)
                    if not False in zulässig:
                        kOpt = k
                        mOpt = m
                        zusatzkostenOpt = zusatzkosten
                        einfügenZulässig = True
                        zeitenplanOpt = provisionsZeitenplan
        if einfügenZulässig:
            tourenplan[kOpt].insert(mOpt,destination)
            tourenplan[kOpt].insert(mOpt,origin)
            eingefügt.append(origin)
            zeitenplan[kOpt].clear()
            for i in zeitenplanOpt:
                zeitenplan[kOpt].append(i)                
    for eingefügteAnfrage in eingefügt:
        ungeplanteAnfragen.remove(eingefügteAnfrage)
    #Ermittlung der in dieser Iteration insgesamt angenommener Anfragen
    insgesamtAngenommen = 0
    for auto in tourenplan:
        for kunde in auto:
            if kunde < 10:
                insgesamtAngenommen += 1
    #Ermittlung der gesamten Reisezeit
    gesamtdauer = 0
    for auto in zeitenplan:
        gesamtdauer += auto[-1]
    #neue beste Lösung, falls mehr Anfragen angenommen
    if insgesamtAngenommen > insgesamtAngenommenBest:
        tourenplanBest = copy.deepcopy(tourenplan)
        zeitenplanBest = copy.deepcopy(zeitenplan)
        insgesamtAngenommenBest = copy.deepcopy(insgesamtAngenommen)
        gesamtdauerBest = copy.deepcopy(gesamtdauer)
    #neue beste Lösung, falls Anzahl angenommener Anfragen gleich hoch bei kürzerer Gesamtdauer
    if insgesamtAngenommen == insgesamtAngenommenBest:
        if gesamtdauer < gesamtdauerBest:
            tourenplanBest = copy.deepcopy(tourenplan)
            zeitenplanBest = copy.deepcopy(zeitenplan)
            insgesamtAngenommenBest = copy.deepcopy(insgesamtAngenommen)
            gesamtdauerBest = copy.deepcopy(gesamtdauer)
    #Verringerung des Iterationszählers
    beta -= 1

#Ermittlung, welche Anfragen angenommen wurden
angenommeneAnfragen = []
for kunde in anfragen:
    if kunde in tourenplanBest[0] or kunde in tourenplanBest[1]:
        angenommeneAnfragen.append(kunde)
abgelehnteAnfragen = []
for kunde in anfragen:
    if kunde not in angenommeneAnfragen:
        abgelehnteAnfragen.append(kunde)

#Print-Statements zur Abfrage der finalen Ergebnisse
print('Ergebnisse des Modelldurchlaufs des Vollkommen-Antizipatorischen-Ansatzes:')
print()
print('Finaler Tourenplan: ', tourenplanBest)
print('Finaler Zeitenplan: ', zeitenplanBest)
print('Angenommene Anfragen: ', angenommeneAnfragen)
print('Abgelehnte Anfragen: ', abgelehnteAnfragen)
