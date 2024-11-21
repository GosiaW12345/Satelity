import requests
import plotly.graph_objects as go
import ephem
import time


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



def mapa_swiata():
    fig = go.Figure(data=go.Scattergeo())

    fig.update_geos(projection_type="orthographic",
        showland=True,
        landcolor="lightgreen",
        showocean=True,
        oceancolor="lightblue")

    fig.show()


#==========================================


print("\nDostępne kalsy satelitów:\n  1) Satelity Amatorskie\n  2) Satelity NOAA\n")
n = input('Podaj klasę satelitów (numer), lub podaj adres do pliku z danymi TLE: ')

if n == '1':
    S = satelity('http://www.amsat.org/tle/dailytle.txt')
elif n == '2':
    S = satelity('http://celestrak.org/NORAD/elements/gp.php?GROUP=noaa&FORMAT=tle')

S.pobierz_dane(),
S.satelity_lista(),
print("lista satelitów amatorskich:"),
S.wypisz()

mapa_swiata()

