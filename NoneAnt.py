
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

#Durchführung des Nicht-Antizipatorischen-Ansatzes

#Tourenplan der beiden Fahrzeuge zum Zeitpunkt 0
tourenplan = [[20],[21]]
#finaler Tourenplan der Endlösung
finalTourenplan = [[],[]]
#Zeitplan der beiden Fahrzeuge zum Zeitpunkt 0
zeitenplan = [[0],[0]]
#finaler Zeitplan der Endlösung
finalZeitenplan = [[],[]]
#Liste der während des Modelldurchlaufs abgelehnten Anfragen
abgelehnteAnfragen = []
#Liste der angenommenen Anfragen
angenommeneAnfragen = []
#for-Schleife, die bei jedem Eintreffen einer neuen Anfrage durchlaufen wird
for eintreffzeit in t_r:
    #Entfernen vergangener Ereignisse aus dem aktuellen Tourenplan
    zuEntfernen = [[],[]]
    for auto in tourenplan:
        for kunde in auto[:-1]:
            if zeitenplan[tourenplan.index(auto)][tourenplan[tourenplan.index(auto)].index(kunde)] < eintreffzeit:
                zuEntfernen[tourenplan.index(auto)].append(kunde)
    for auto in zuEntfernen:
        for kunde in auto:
            i = zuEntfernen.index(auto)
            index = tourenplan[i].index(kunde)
            finalZeitenplan[i].append(zeitenplan[i].pop(index))
            finalTourenplan[i].append(tourenplan[i].pop(index))
    #Ermittlung der neu eingetroffenen Anfrage
    aktuelleAnfrage = t_r.index(eintreffzeit)
    #Einfügen der neuen Anfrage in die Liste der aktuell nicht eingeplanten Anfragen
    ungeplanteAnfragen = [aktuelleAnfrage]
    #Festlegung der Anzahl an Iterationen der folgenden while-Schleife
    beta = 100
    #neu zu kreierender Tourenplan und Zeitenplan
    newTourenplan = copy.deepcopy(tourenplan)
    newZeitenplan = copy.deepcopy(zeitenplan)
    #while-Schleife für den Destroy- und Repair-Prozess
    while beta != 0 and ungeplanteAnfragen != []:
        #Destroy-Operator: Entfernen einer zufälligen Anfrage
        destroy = []
        for auto in newTourenplan:
            for kunde in auto[1:]:
                if kunde in auto and kunde+10 in auto:
                    destroy.append(kunde)
        if len(destroy) > 0:
            d = random.choice(destroy)
            for auto in newTourenplan:
                if d in auto:
                    autoIndex = newTourenplan.index(auto)
                    oriIndex = newTourenplan[autoIndex].index(d)
                    destiIndex = newTourenplan[autoIndex].index(d+10)
                    newTourenplan[autoIndex].remove(d)
                    newTourenplan[autoIndex].remove(d+10)
                    del newZeitenplan[autoIndex][destiIndex]
                    del newZeitenplan[autoIndex][oriIndex]
                    ungeplanteAnfragen.append(d)
                    break
        # Repair-Operator: Einfügen einer jeden ungeplanten Anfrage, die den Restriktionen entsprechend eingefügt werden kann
        random.shuffle(ungeplanteAnfragen)
        eingefügt = []
        for origin in ungeplanteAnfragen:
            destination = origin + 10
            einfügenZulässig = False
            zusatzkostenOpt = M
            for k in fahrzeuge:
                for m in range(1, len(newTourenplan[k])+1):
                    if m != len(newTourenplan[k]):
                        zusatzkosten = c_ij[newTourenplan[k][m-1],origin] + c_ij[origin,destination] + c_ij[destination,newTourenplan[k][m]] - c_ij[newTourenplan[k][m-1],newTourenplan[k][m]]
                    else:
                        zusatzkosten = c_ij[newTourenplan[k][m-1],origin] + c_ij[origin, destination]
                    if zusatzkosten < zusatzkostenOpt:
                        zulässig = []  
                        provisionsTourenplan = copy.deepcopy(newTourenplan[k])
                        provisionsTourenplan.insert(m,destination)
                        provisionsTourenplan.insert(m,origin)
                        provisionsZeitenplan = [copy.deepcopy(newZeitenplan[k][0])]
                        for haltestelle in provisionsTourenplan[1:]:
                            indexHaltestelle = provisionsTourenplan.index(haltestelle)
                            zeitVorgänger = max(provisionsZeitenplan[indexHaltestelle-1], eintreffzeit)
                            mindestZeit = zeitVorgänger + c_ij[provisionsTourenplan[indexHaltestelle-1], haltestelle]
                            provisionsZeitenplan.append(mindestZeit)
                        for haltestelle in provisionsTourenplan:                       
                            indexHaltestelle = provisionsTourenplan.index(haltestelle)
                            if frühest[haltestelle] <= provisionsZeitenplan[indexHaltestelle] <= spätest[haltestelle]:
                                zulässig.append(True)
                            else:
                                zulässig.append(False)
                        for ku in angenommeneAnfragen:
                            if ku in ungeplanteAnfragen:
                                if ku in provisionsTourenplan:
                                    zulässig.append(True)
                                else:
                                    zulässig.append(False)
                        #falls Einfügen der Anfrage zulässig, wird die ermittelte Einfügestelle als neue beste Lösung gespeichert
                        if not False in zulässig:
                            kOpt = k
                            mOpt = m
                            zusatzkostenOpt = zusatzkosten
                            einfügenZulässig = True
                            zeitenplanOpt = provisionsZeitenplan
            #falls eine zulässige Einfügestelle gefunden wurde, wird die Anfrage an der gespeicherten besten Einfügestelle in den Tourenplan integriert
            if einfügenZulässig:
                newTourenplan[kOpt].insert(mOpt,destination)
                newTourenplan[kOpt].insert(mOpt,origin)
                eingefügt.append(origin)
                newZeitenplan[kOpt].clear()
                for i in zeitenplanOpt:
                    newZeitenplan[kOpt].append(i)
        #eingefügte Anfragen werden aus der Menge der ungeplanten Anfragen wieder entfernt
        for eingefügteAnfrage in eingefügt:
            ungeplanteAnfragen.remove(eingefügteAnfrage)
        #Verringerung des Iterationszählers nach jedem vollständigen Iterationsablauf
        beta -= 1
    #falls Insertion nicht erfolgreich, wird die aktuelle Anfrage abgelehnt und der Tourenplan der letzten erfolgreichen Anfragenannahme weiterverwendet
    if ungeplanteAnfragen != []:
        abgelehnteAnfragen.append(aktuelleAnfrage)
    #falls Insertion erfolgreich, wird der in dieser Iteration neu generierte Tourenplan für die nächste Auftragsannahmeentscheidung weiterverwendet
    else:
        tourenplan = copy.deepcopy(newTourenplan)
        zeitenplan = copy.deepcopy(newZeitenplan)
        angenommeneAnfragen.append(aktuelleAnfrage)

#Fertigstellung des finalen Tourenplans
for auto in tourenplan:
    for ku in auto:
        i = tourenplan.index(auto)
        index = tourenplan[i].index(ku)
        finalZeitenplan[i].append(zeitenplan[i][index])
        finalTourenplan[i].append(ku)

#Print-Statements zur Abfrage der finalen Ergebnisse
print('Ergebnisse des Modelldurchlaufs des Nicht-Antizipatorischen Ansatzes:')
print()
print('Finaler Tourenplan: ', finalTourenplan)
print('Finaler Zeitenplan: ', finalZeitenplan)
print('Angenommene Anfragen: ', angenommeneAnfragen)
print('Abgelehnte Anfragen: ', abgelehnteAnfragen)
