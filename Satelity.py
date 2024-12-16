import requests
import plotly.graph_objects as go
import ephem
from datetime import datetime, timedelta


class satellites:
    def __init__(self, adres):
        self.adres = adres       # adres url do danych TLE
        
    def download_TLE(self):
        self.dane = requests.get(self.adres)
        self.dane = self.dane.text

    def list(self):
        # lista zawiera słowniki 3-elementowe, zawierające: nazwe satelity i dwie linijki danych TLE
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
        return self.sat_list

    # funkcja wypisująca nazwy satelitów
    def print_satellite_names (self):
        for self.i in range(len(self.sat_list)):
            print(f"{self.i}: {self.sat_list[self.i]['nazwa']}")



def world_map(LAT, LON):
    fig = go.Figure(go.Scattergeo())

    fig.update_geos(
        #projection_type="orthographic",
        showland=True,
        landcolor="lightgreen",
        showocean=True,
        oceancolor="lightblue")

    fig.add_trace(go.Scattergeo(
        lon = [18.8667],
        lat = [50.45],
        mode = 'markers',
        marker = dict(symbol='x', size=3, color='black') ))

    fig.add_trace(go.Scattergeo(
        lon=LON,
        lat=LAT,
        mode='lines',
        line = dict(color='red', width=2)))


    fig.show()

def predykcja(Sat):
    #Tworzymy obiekt typu ephem.Observer i efiniujemy jego:
    # wspułrzędne geograficzne, wysokość nad poziomem morza

    o = ephem.Observer()
    o.lat = "50.45"
    o.lon = "18.8667"
    o.elevation = 274

    start_time = datetime.now()

    # na obiekcie S typu ephem.satelte wywoujemy metodę compute, której parametrem jest wyżej zdefiniowany ephem.Observer
    # metoda compute oblicza m.in. wysokość satelity nad hotyzontem obserwatora w zadanym czasie
    for n in range(30):
        time = start_time + timedelta(minutes = n*8)
        o.date = ephem.date(time)
        Sat.compute(o)
        if (Sat.alt / ephem.degree) > 0:
            reference_point = (Sat.sublat/ephem.degree, Sat.sublong/ephem.degree, time)
            break

    visible_points_lat = []
    visible_points_lon = []

    visible_points_lat.append(reference_point[0])
    visible_points_lon.append(reference_point[1])

    start_time = reference_point[2]

    for n in range(10):
        time_up = start_time + timedelta(minutes=n+1)
        time_down = start_time - timedelta(minutes=n+1)

        o.date = ephem.date(time_up)
        Sat.compute(o)
        if (Sat.alt / ephem.degree) > 0:
            visible_points_lat.append(Sat.sublat / ephem.degree)
            visible_points_lon.append(Sat.sublong / ephem.degree)
            satelite_rise_point = (Sat.sublat / ephem.degree, Sat.sublong / ephem.degree, time_up)

        o.date = ephem.date(time_down)
        if (Sat.alt / ephem.degree) > 0:
            visible_points_lat.append(Sat.sublat / ephem.degree)
            visible_points_lon.append(Sat.sublong / ephem.degree)
            satelite_set_point = (Sat.sublat / ephem.degree, Sat.sublong / ephem.degree, time_down)

    return [visible_points_lat, visible_points_lon, satelite_rise_point[2], satelite_set_point[2]]
"""
def current_trajectory(Sat):
    #Tworzymy obiekt typu ephem.Observer i efiniujemy jego:
    # wspułrzędne geograficzne, wysokość nad poziomem morza

    o = ephem.Observer()
    o.lat = "50.45"
    o.lon = "18.8667"
    o.elevation = 274

    start_time = datetime.now()

    visible_points_lat = []
    visible_points_lon = []

    # na obiekcie S typu ephem.satelte wywoujemy metodę compute, której parametrem jest wyżej zdefiniowany ephem.Observer
    # metoda compute oblicza m.in. wysokość satelity nad hotyzontem obserwatora w zadanym czasie
    for n in range(30):
        time = start_time + timedelta(minutes = n)
        o.date = ephem.date(time)
        Sat.compute(o)
        visible_points_lat.append(Sat.sublat / ephem.degree)
        visible_points_lon.append(Sat.sublong / ephem.degree)
    return [visible_points_lat, visible_points_lon]
"""
"""
======================================================================================================
======================================================================================================
"""
"""
sat_group = satellites('http://www.amsat.org/tle/dailytle.txt')
n=11
sat_group.download_TLE()
sat_group.list()
"""

print("\nDostępne grupy satelitów:\n  1) Satelity Amatorskie\n  2) Satelity NOAA\n")
n = input('Podaj grupę satelitów (numer), lub podaj adres do pliku z danymi TLE: ')

if n == '1':
    sat_group = satellites('http://www.amsat.org/tle/dailytle.txt')
elif n == '2':
    sat_group = satellites('http://celestrak.org/NORAD/elements/gp.php?GROUP=noaa&FORMAT=tle')
else:
    sat_group = satellites(n)

sat_group.download_TLE()
sat_group.list()

print("Satelity znajdujące się w wybranej grupie:")
sat_group.print_satellite_names()

n = int(input("Wybierz numer interesującego Cię satelity: "))


#na podstawie nazwy satelity oraz dwuwiersza TLE, tworzymy obiekt typu "ephem.EarthSatelite"
traced_sat = ephem.readtle(sat_group.sat_list[n]['nazwa'], sat_group.sat_list[n]['dane1'], sat_group.sat_list[n]['dane2'])

#traced_sat.compute()
#world_map(lat = 50.45, lon = 18.8667)

LAT, LON, rise_time, set_time = predykcja(traced_sat)
print("Satelita będzie widoczny: ", rise_time)
print("Satelita będzie zniknie z horyzontu: ", set_time)
world_map(LAT, LON)

#sat.compute(o)
#mapa_swiata(k)

"""
o = ephem.Observer()
o.lat = "50.45"
o.lon = "18.8667"
o.elevation = 274
o.date = '2024/12/15 13:36:56'
traced_sat.compute(o)
print(traced_sat.alt / ephem.degree)

"""
