import requests
import ephem
import time

# Nazwy zmiennych są po polsku.
class satelity:
    def __init__(self, adres):
        self.adres = adres
        
    def pobierz_dane(self):
        self.dane = requests.get(self.adres)
        self.dane = self.dane.text

    def satelity_lista(self):
        self.sat_list = []
        n = 0
        for line in self.dane.splitlines():
            if line[0].isalpha():
                self.sat_list.append({})
                self.sat_list[n]['nazwa'] = line

            if line[0] == '1':
                self.sat_list[n]['dane1'] = line

            if line[0] == '2':
                self.sat_list[n]['dane2'] = line
                n += 1

    def wypisz(self):
        for self.i in range(len(self.sat_list)):
            print(f"{self.i}: {self.sat_list[self.i]['nazwa']}")

#==========================================

AmSat = satelity('http://www.amsat.org/tle/dailytle.txt')
AmSat.pobierz_dane()
AmSat.satelity_lista()
AmSat.wypisz()



