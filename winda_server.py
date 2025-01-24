from flask import Flask, jsonify, render_template, request
import random
import json
import threading
import time
import tkinter as tk
from tkinter import messagebox
import random
import sqlite3
import json
import os
import requests
from flask_cors import CORS

kolejkaPasażerów = []
wielkośćSzybu = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
pietraIPasazerowie = [(pietro, 0) for pietro in wielkośćSzybu]
ruchWindy = False
pracaDrzwiWindy = False
wydarzenieStatusSymulacji = False
wydarzenieZapisywaniaStatystyk = False
wydarzenieJazda = threading.Event() # Event do zarządzania aktywnością wątku jazdaWindy
wydarzeniePracaDrzwi = threading.Event() # Event do zarządzania aktywnością wątku pracaDrzwi
wydarzenieSymulacjaPodaży = threading.Event() # Event do zarządzania aktywnością wątku symulacji podaży
zapisywanieStatystyk = threading.Event() # Event do zarządzania aktywnością wątku zapisywania statystyk


jsonFilePath = '/data/statystyki_windy.json'


app = Flask(__name__)
CORS(app)

wlasciwosci_windy = {
    'wielkośćSzybu': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}


wlasciwosci_drzwi = {
    'poleceniaDrzwi': [],
    'statusPracyDrzwi': 2
}

windy_data = {
    'status': 'OK',
    'polecenia': [],
    'kierunekJazdy': 0,
    'lokalizacjaWindy': 0
}


wybrane_przyciski = {
    'słownik': {}
}


dane_symulacji = {
    'statusSymulacji': 0,
    'zmiennaCzęstotliwościGenerowaniaPasażerów': 5
}


@app.route("/")
def home():
    return "Witam w aplikacji Flask dla serwera Windy!"

@app.route('/get_winda_status')
def get_winda_status():
    combined_data = {
        'windy_data': {
            'lokalizacjaWindy': windy_data.get('lokalizacjaWindy'),
            'kierunekJazdy': windy_data.get('kierunekJazdy'),
            'polecenia': windy_data.get('polecenia')
        },
        'wybrane_przyciski': wybrane_przyciski,
        'dane_symulacji': { 
            'status_symulacji': dane_symulacji.get('statusSymulacji'),
            'zmienna_częstotliwości_generowania_pasażerów': dane_symulacji.get('zmiennaCzęstotliwościGenerowaniaPasażerów')
        }
    }
    return jsonify(combined_data)


@app.route('/get_wielkosc_szybu')
def get_wielkosc_szybu():
    return jsonify(wlasciwosci_windy['wielkośćSzybu'])


@app.route('/get_polecenia_drzwi')
def get_polecenia_drzwi():
    return jsonify({
        'poleceniaDrzwi': wlasciwosci_drzwi['poleceniaDrzwi'],
        'statusPracyDrzwi': wlasciwosci_drzwi['statusPracyDrzwi']
    })


@app.route('/get_statystyki')
def get_statystyki():
    return jsonify(statystyki)


@app.route('/get_status_symulacji')
def get_status_symulacji():
    return jsonify(dane_symulacji)


@app.route('/wlacz_wylacz_symulacje', methods=['POST'])
def wlacz_wylacz_symulacje():
    dane_symulacji['statusSymulacji'] = request.json.get('statusSymulacji')
    włączWyłączSymulacje()
    return jsonify({'statusSymulacji': dane_symulacji['statusSymulacji']})
if __name__ == '__main__':
    app.run(debug=True)


@app.route('/zmien_czestotliwosc', methods=['POST'])
def zmien_czestotliwosc():
    dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów'] = request.json.get('zmiennaCzęstotliwościGenerowaniaPasażerów')
    return jsonify({'zmiennaCzęstotliwościGenerowaniaPasażerów': dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów']})


def odczytajStatystykiJSON():
    try:
        with open(jsonFilePath, 'r') as json_file:
            print("Plik istnieje przy wczytania")
            return json.load(json_file)
    except FileNotFoundError:
        print("Plik nie istnieje do wczytania. Zwracam pusty słownik.")
        return {
                "przebyta_odleglosc": 0,
                "zaliczone_przystanki": 0,
                "pokonane_pietra": 0,
                "przewiezieni_pasazerowie": {
                    "typ1": 0,
                    "typ2": 0,
                    "typ3": 0
                },
                "liczba_otworzen_drzwi": 0,
                "liczba_oczekujacych_pasazerow": 0
        }


def zapiszStatystykiJSON(statystyki):
    try:
        with open(jsonFilePath, 'w') as json_file:
            print("Plik istnieje przy zapisywaniu")
            json.dump(statystyki, json_file)
    except FileNotFoundError:
        print("Plik nie istnieje do zapisu. Zwracam pusty słownik.")
        return
        

def zapiszStatystykiOkresowo():
    while wydarzenieZapisywaniaStatystyk == True:
        time.sleep(5)
        zapiszStatystykiJSON(statystyki)


def zapiszStatystykiPrzyZamykaniu():
    zapiszStatystykiJSON(statystyki)


def zaktualizujPolecenia():
    if windy_data['kierunekJazdy'] == 2: #jazda do góry
        windy_data['polecenia'] = sorted([p for p in windy_data['polecenia'] if p >= windy_data['lokalizacjaWindy']]) + sorted([p for p in windy_data['polecenia'] if p < windy_data['lokalizacjaWindy']], reverse=True)
    if windy_data['kierunekJazdy'] == 1: #jazda w dół
        windy_data['polecenia'] = sorted([p for p in windy_data['polecenia'] if p < windy_data['lokalizacjaWindy']], reverse=True) + sorted([p for p in windy_data['polecenia'] if p >= windy_data['lokalizacjaWindy']])
    zmianaKierunkuJazdy()


def wskażPiętro(nowePolecenie, źródłoPolecenia, typUsera=1):
    global ruchWindy
    if sprawdźCzyDubel(nowePolecenie, źródłoPolecenia) == False:
        windy_data['polecenia'].append(nowePolecenie)
        zaktualizujPolecenia()
        #zapiszLog(1, źródłoPolecenia, None, nowePolecenie, polecenia, None, typUsera)
        #wyświetlLogWWidżecie()
        zapiszWybranePiętro(nowePolecenie, źródłoPolecenia)
        if ruchWindy is False and wlasciwosci_drzwi['statusPracyDrzwi'] == 2:
            ruchWindy = True
            threading.Thread(target=jazdaWindy, daemon=True).start()
            wydarzenieJazda.set()
        else:
            return 
    else:
        return


def zapiszWybranePiętro(nowePolecenie, źródłoPolecenia):
    if 'słownik' not in wybrane_przyciski:
        wybrane_przyciski['słownik'] = {}
    if not isinstance(wybrane_przyciski.get('słownik'), dict):
        wybrane_przyciski['słownik'] = {}
    klucz = int(nowePolecenie)
    wybrane_przyciski['słownik'].update({klucz: źródłoPolecenia})


def usunPiętroZListyWybranychPięter(lokalizacja):
    if lokalizacja in wybrane_przyciski['słownik']:
        wybrane_przyciski['słownik'].pop(lokalizacja, None)


def sprawdźCzyDubel(nowePolecenie, źródłoPolecenia):
    if nowePolecenie == windy_data['lokalizacjaWindy']:
        return True
    else:
        for x in windy_data['polecenia']:
            if x == nowePolecenie or nowePolecenie == windy_data['lokalizacjaWindy']:
                #aktualizujStanPrzyciskówDodawaniaPoleceń(nowePolecenie, 1, źródłoPolecenia) - do zmiany
                return True
            else:
                pass
        return False 


def jazdaWindy():
    global ruchWindy, liczbaPrzystanków
    while ruchWindy:
        time.sleep(2) 
        zmianaLokalizacjiWindy()
        zmianaKierunkuJazdy()
        if windy_data['polecenia']:
            if windy_data['lokalizacjaWindy'] == windy_data['polecenia'][0]:
                windy_data['polecenia'].pop(0)
                liczbaPrzystanków += 1
                statystyki['zaliczone_przystanki'] = liczbaPrzystanków
                symulujWybórPięter()
                usunPiętroZListyWybranychPięter(windy_data['lokalizacjaWindy'])
                zmianaKierunkuJazdy()
                dodajPolecenieDrzwi(1)
                if not windy_data['polecenia']:
                    wydarzenieJazda.clear()
                    ruchWindy = False
        else:
            wydarzenieJazda.clear()
            ruchWindy = False


def zmianaLokalizacjiWindy():    
    global liczbaPokonanychPięter, przebytaOdległość
    if windy_data['kierunekJazdy'] == 2:
        windy_data['lokalizacjaWindy'] += 1
    elif windy_data['kierunekJazdy'] == 1:
        windy_data['lokalizacjaWindy'] -= 1
    liczbaPokonanychPięter += 1
    przebytaOdległość = (int(liczbaPokonanychPięter) * 2.35) / 1000
    statystyki["pokonane_pietra"] = liczbaPokonanychPięter
    statystyki["przebyta_odleglosc"] = przebytaOdległość


def zmianaKierunkuJazdy():
    target = windy_data['polecenia'][0] if windy_data['polecenia'] else None
    if windy_data['polecenia']:
        if windy_data['polecenia'][0] > windy_data['lokalizacjaWindy'] and windy_data['kierunekJazdy'] != 2:
            windy_data['kierunekJazdy'] = 2
            #zapiszLog(3, None, kierunekJazdy, target, polecenia, None)
            #wyświetlLogWWidżecie()     
        if windy_data['polecenia'][0] < windy_data['lokalizacjaWindy'] and windy_data['kierunekJazdy'] != 1:
            windy_data['kierunekJazdy'] = 1
            #zapiszLog(3, None, kierunekJazdy, target, polecenia, None)
            #wyświetlLogWWidżecie()
        else:
            pass
    else:
        if target == None and windy_data['kierunekJazdy'] != 0:
            windy_data['kierunekJazdy'] = 0
            #zapiszLog(4, None, kierunekJazdy, lokalizacjaWindy, polecenia, None)
            #wyświetlLogWWidżecie()


def dodajPolecenieDrzwi(rodzajPracy): # 0 - zamknij, 1 - otwórz
    global pracaDrzwiWindy
    global ruchWindy
    if ruchWindy == False:
        wlasciwosci_drzwi['poleceniaDrzwi'].append(rodzajPracy)
        pracaDrzwiWindy = True
        threading.Thread(target=uruchomPracęDrzwi, daemon=True).start()
        wydarzeniePracaDrzwi.set()
    if ruchWindy == True:
        wydarzenieJazda.clear()
        ruchWindy = False
        wlasciwosci_drzwi['poleceniaDrzwi'].append(rodzajPracy)
        pracaDrzwiWindy = True
        threading.Thread(target=uruchomPracęDrzwi, daemon=True).start()
        wydarzeniePracaDrzwi.set()


def uruchomPracęDrzwi():
    global pracaDrzwiWindy
    global ruchWindy
    #zapiszLog(4, None, kierunekJazdy, lokalizacjaWindy, polecenia, None)
    #wyświetlLogWWidżecie()
    if wlasciwosci_drzwi['poleceniaDrzwi'][0] == 1 and wlasciwosci_drzwi['statusPracyDrzwi'] == 0 or wlasciwosci_drzwi['statusPracyDrzwi'] == 2:
        otwórzDrzwi()
        time.sleep(1)
        zamknijDrzwi()
        wlasciwosci_drzwi['poleceniaDrzwi'].pop(0)
    elif wlasciwosci_drzwi['statusPracyDrzwi'] == 1 or wlasciwosci_drzwi['statusPracyDrzwi'] == 3:
        zamknijDrzwi()
        wlasciwosci_drzwi['statusPracyDrzwi'] = 2
        time.sleep(1)
        otwórzDrzwi()
        wlasciwosci_drzwi['poleceniaDrzwi'].pop(0)
    wydarzeniePracaDrzwi.clear() 
    pracaDrzwiWindy = False
    #if polecenia:
        #zapiszLog(3, None, kierunekJazdy, polecenia[0], polecenia, None)
        #wyświetlLogWWidżecie()
    #else:
        #pass
    ruchWindy = True
    threading.Thread(target=jazdaWindy, daemon=True).start()
    wydarzenieJazda.set()


def otwórzDrzwi(): # 0 - zamykanie, 1 - otwieranie, 2 - zamknięte, 3 - otwarte
    wlasciwosci_drzwi['statusPracyDrzwi'] = 1
    time.sleep(2)
    wlasciwosci_drzwi['statusPracyDrzwi'] = 3
    
    
def zamknijDrzwi(): # 0 - zamykanie, 1 - otwieranie, 2 - zamknięte, 3 - otwarte
    wlasciwosci_drzwi['statusPracyDrzwi'] = 0
    time.sleep(1)
    wlasciwosci_drzwi['statusPracyDrzwi'] = 2


def włączWyłączSymulacje(): # poprawić statusy symulacji@@@@@@@@@@@@@@@@@@@@@@@@
    global wydarzenieStatusSymulacji
    if dane_symulacji['statusSymulacji'] == 1:
        odczytajStatystykiJSON()
        wydarzenieStatusSymulacji = True
        threading.Thread(target=generujPodażPasażerów, daemon=True).start()
        wydarzenieSymulacjaPodaży.set()
        #zapiszLog(6, None, None, None, None, None, 2)
        wydarzenieZapisywaniaStatystyk = True
        threading.Thread(target=zapiszStatystykiOkresowo, daemon=True).start()
        zapisywanieStatystyk.set()
    else:
        wydarzenieSymulacjaPodaży.clear()
        wydarzenieStatusSymulacji = False
        #zapiszLog(7, None, None, None, None, None, 2)
    #wyświetlLogWWidżecie()


def generujPodażPasażerów():
    dostępnaLiczbaPasażerów = [1, 2, 3, 4]
    while wydarzenieStatusSymulacji == True:
        time.sleep(definiujCzasZwłokiGenerowaniaPasażerów(dane_symulacji.get('zmiennaCzęstotliwościGenerowaniaPasażerów')))
        losowaLokalizacjaPasażera = random.choice(wielkośćSzybu)
        losowyKierunekJazdyPasażera = random.randint(2, 3)
        weights = [5, 3, 1, 1]
        losowaLiczbaPasażerów = random.choices(dostępnaLiczbaPasażerów, weights=weights, k=1)[0]
        aktualizujLiczbePasazerow(losowaLokalizacjaPasażera, losowaLiczbaPasażerów)
        wskażPiętro(losowaLokalizacjaPasażera, losowyKierunekJazdyPasażera)        
    else:
        return


def symulujWybórPięter(wagaDlaPiętra=5):
    global liczbaOczekującychPasażerów
    if dane_symulacji['statusSymulacji'] == 1:
        if windy_data['lokalizacjaWindy'] > 0:
            losowePiętro = random.choices(wielkośćSzybu, weights=[wagaDlaPiętra if piętro == 0 else 1 for piętro in wielkośćSzybu], k=1)[0]
        else:   
            losowePiętro = random.choice(wielkośćSzybu)
        wskażPiętro(losowePiętro, 1)
        liczbaOczekującychPasażerów = next((l for p, l in pietraIPasazerowie if p == windy_data['lokalizacjaWindy']), 0)
        statystyki["liczba_oczekujacych_pasazerow"] = liczbaOczekującychPasażerów
        statystyki['przewiezieni_pasazerowie']['typ1'] += liczbaOczekującychPasażerów
        aktualizujLiczbePasazerow(windy_data['lokalizacjaWindy'], -liczbaOczekującychPasażerów)
        liczbaOczekującychPasażerów = sum(l for p, l in pietraIPasazerowie)
        statystyki["liczba_oczekujacych_pasazerow"] = liczbaOczekującychPasażerów
    else:
        return

def definiujCzasZwłokiGenerowaniaPasażerów(wartośćZmienna, wartośćStała=18): #wartość stałą jest drugim komponentem defiuniującym delay
    losowaCzęśćCzęstotliwości = random.randint(0, 4)
    czasZwłokiGenerowaniaPasażerów = (wartośćStała + int(losowaCzęśćCzęstotliwości) - int(wartośćZmienna))
    return czasZwłokiGenerowaniaPasażerów


def aktualizujLiczbePasazerow(pietro, liczbaPasazerow):
    global pietraIPasazerowie
    pietraIPasazerowie = [(p, l + liczbaPasazerow if p == pietro else l) for p, l in pietraIPasazerowie]



statystyki = odczytajStatystykiJSON()
liczbaPokonanychPięter = statystyki["pokonane_pietra"]
przebytaOdległość = statystyki["przebyta_odleglosc"]
liczbaPrzystanków = statystyki["zaliczone_przystanki"]
statystykaPrzewiezieniPasażerowie = statystyki["przewiezieni_pasazerowie"]["typ1"]
liczbaOczekującychPasażerów = statystyki["liczba_oczekujacych_pasazerow"]



"""
python -m venv venv
venv\Scripts\activate
set FLASK_APP=winda_server.py

flask run --debug
flask --app winda_server.py run --debug
"""
