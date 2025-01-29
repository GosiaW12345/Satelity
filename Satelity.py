from typing import List
import requests
import plotly.graph_objects as go
import ephem
from datetime import datetime, timedelta, timezone
import pytz

class satellites:

    '''
    klasa jako argument przyjmuje adres url do danych TLE
    metody:
        - download_TLE:
            metoda czyta plik txt z podanego adresu i zapisuje tekst w zmiennej dane
        - list:
            metoda na podstawie zmiennej dane tworzy listę (sat_list) zawierającą tuple: (nazwa, TLE wiersz1, TLE wiersz2)
        - print_satellite_names:
            metoda wypisuje nazwy satelitów
    '''

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

    def print_satellite_names (self):
        for i in range(len(self.sat_list)):
            print(f"{i}: {self.sat_list[i]['nazwa']}")



def world_map(LAT, LON, set_lat, set_lon, nazwa, set_time, rise_time):
    '''

    :param LAT: lista (szerokości) na której podstawie jest rysowana trajektoria satelity
    :param LON: lista (długości) na której podstawie jest rysowana trajektoria satelity
    :param set_lat: punkt (szerokość) w którym satelita przestaje być widaczny
    :param set_lon: punkt (długość) w którym satelita przestaje być widaczny
    :param nazwa: nazwa satelity
    :param set_time: czas pojawienia się satelity nad horyzontem
    :param rise_time: czas pzniknięcia satelity za horyzont
    :return: None

    Funkcja rysuje fragment trajektori satelity (wtedy kiedy będzie ona widoczna) na mapie, oraz
    zazmnacza punkt w którym datelita zniknie z horyzontu optycznego
    '''
    # utworzenie obiektu przy pomocy biblioteki plotly, który jest wykresem przedstawiającym mapę ziemi
    fig = go.Figure(go.Scattergeo())

    # ustawienie tytułu wykresu
    fig.update_layout(title=f"{nazwa} {set_time} - {rise_time}")

    # ustawienia wyglądu mapy
    fig.update_geos(
        projection_type="orthographic",
        showland=True,
        landcolor="lightgreen",
        showocean=True,
        oceancolor="lightblue")

    # punkt przedstawiający położenie obserwatora
    fig.add_trace(go.Scattergeo(
        name = "twoja lokalizacja",
        lat = [50.45],
        lon = [18.8667],
        mode = 'markers',
        marker = dict(symbol='x', size=5, color='black') ))

    # punkt w którym satelita znika z horyzontu
    fig.add_trace(go.Scattergeo(
        name = "punkt zniknięcia satelity z horyzontu",
        lat = [set_lat],
        lon = [set_lon],
        mode = 'markers',
        marker = dict(symbol='star-diamond-dot', size=7, color='red')))

    # trajektoria
    fig.add_trace(go.Scattergeo(
        name = "trajektoria",
        lat = LAT,
        lon = LON,
        mode = 'lines',
        line = dict(color='red', width=2)))

    fig.show()


def prediction(Sat):
    '''

    :param Sat:
    :return: [visible_points_lat, visible_points_lon, satelite_rise_time, satelite_set_time, satelite_set_lat, satelite_set_lon]

    funkcja zwraca kolejno:
        - listę szerokości geograficznych punktów w których satelita będzie widoczny
        - listę długości geograficznych punktów w których satelita będzie widoczny
        - czas pojawienia się satelity nad horyzonrem
        - czas zniknięcia satelity za horyzont
        - punkt (szerokość) w którym satelita przestaje być widaczny
        - punkt (długość) w którym satelita przestaje być widaczny
    jeżeli satelita wogule nie będzie widoczny w przeciągu 4h to zwracana jest wartość [0,0,0,0,0,0]

    Zasada działania funkcji jest następująca:
        dla kolejnych czasów z krokiem 8 minut (zaczynając od bierzącego czasu kończąc na 4h później)
        liczona jest wysokość satelity nad hooryzontem (wyrażana w stopniach), jeżeli w którymś momencie
        jest ona większa od zera (satelita jest nad horyzontem) to przerywana jest pętla i utworzony zostaje
        punkt referencyjny. Następnie zaczynając od czasu referencyjnego sprawdzane są kolejne czas 0,5 min w dół i w górę
        jeżeli dla tych czasów satelita jest widoczny, wspułżędne geograficzne odpowiadające tym czasom dodawane są
        do odpoweidniech list, skrajne czasy zapisywanę są w zmiennych satelite_rise_time i satelite_set_time
        oznaczają czas pojawienie się satelity i jego zniknięcia
    '''
    o = ephem.Observer()
    o.lat = "50.45"
    o.lon = "18.8667"
    o.elevation = 274

    visible_points_lat = list()
    visible_points_lon = list()
    times = list()

    start_time = datetime.now(timezone.utc)
    alt = -1
    for n in range(120):
        time = start_time + timedelta(minutes = n)
        o.date = ephem.date(time)
        Sat.compute(o)
        if (Sat.alt) > 0:
            visible_points_lat.append(Sat.sublat / ephem.degree)
            visible_points_lon.append(Sat.sublong / ephem.degree)
            times.append(time)
        else:
            if alt>0:   # ten warunek powosuje przerwanie pętli gdy satelita przestaje być widoczny
                break
        alt = Sat.alt

    if len(visible_points_lat) == 0:
        return [0,0,0,0,0,0]
    else:
        return visible_points_lat, visible_points_lon, times[0], times[-1], visible_points_lat[-1], visible_points_lon[-1]


print("\nDostępne grupy satelitów:\n  1) Satelity Amatorskie\n  2) Satelity NOAA\n  3) Międzynarodowa stacja kosmiczna")
n = input('Podaj grupę satelitów (numer), lub podaj adres do pliku z danymi TLE: ')

if n == '1':
    sat_group = satellites('http://www.amsat.org/tle/dailytle.txt')
elif n == '2':
    sat_group = satellites('http://celestrak.org/NORAD/elements/gp.php?GROUP=noaa&FORMAT=tle')
elif n=='3':
    sat_group = satellites('https://live.ariss.org/iss.txt')

else:
    sat_group = satellites(n)

sat_group.download_TLE()
sat_group.list()

print("Satelity znajdujące się w wybranej grupie:")
sat_group.print_satellite_names()

N = input("\nWybierz numery interesujących Cię satelitów (numery odziel przecinkiem) lub wybierz x aby zaznaczyć wszystkie: ")

local_tz = pytz.timezone('Europe/Warsaw')

if N == 'x':
    longest_visible: list[tuple[List, List, datetime, datetime, float, float, int]] = []
    for i in range(len(sat_group.sat_list)):
        traced_sat = ephem.readtle(sat_group.sat_list[i]['nazwa'], sat_group.sat_list[i]['dane1'],
                                   sat_group.sat_list[i]['dane2'])

        LAT, LON, Rise_time, Set_time, set_lat, set_lon = prediction(traced_sat)
        if Rise_time != 0:
            longest_visible.append((LAT, LON, Rise_time, Set_time, set_lat, set_lon, i))

    longest_visible = sorted(longest_visible, key=lambda x: x[3] - x[2], reverse=True)[:5]

    if longest_visible == []:
        print("Rzaden z wybranych satelitów nie będzie widoczny")
    else:
        print("\nZe wszystkich satelitów w wybranej grupie w ciągu najbliższych 4h najdłużej widoczen będą:")
        for sat in longest_visible:
            Rise_time = sat[2].astimezone(local_tz).strftime('%Y-%m-%d %H:%M')
            Set_time = sat[3].astimezone(local_tz).strftime('%Y-%m-%d %H:%M')
            print(f"{sat_group.sat_list[sat[6]]['nazwa']}: {Rise_time} - {Set_time}")
            world_map(sat[0], sat[1], sat[4], sat[5], sat_group.sat_list[sat[6]]['nazwa'], Set_time, Rise_time)




else:
    N = N.split(",")
    print("\n Z wybranych satelitów: ")
    for i in N:
        i = int(i)
        #na podstawie nazwy satelity oraz dwuwiersza TLE, tworzymy obiekt typu "ephem.EarthSatelite"
        traced_sat = ephem.readtle(sat_group.sat_list[i]['nazwa'], sat_group.sat_list[i]['dane1'], sat_group.sat_list[i]['dane2'])

        LAT, LON, Rise_time, Set_time, set_lat, set_lon = prediction(traced_sat)

        if Rise_time != 0:
            Rise_time = Rise_time.astimezone(local_tz).strftime('%Y-%m-%d %H:%M')
            Set_time = Set_time.astimezone(local_tz).strftime('%Y-%m-%d %H:%M')
            print(f"{sat_group.sat_list[i]['nazwa']}: {Rise_time} - {Set_time}")
            world_map(LAT, LON, set_lat, set_lon, sat_group.sat_list[i]['nazwa'], Set_time, Rise_time)
        else:
            print(f"{sat_group.sat_list[i]['nazwa']} nie będzie widoczny w ciągu najbliższych 4h")


