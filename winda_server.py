
from flask import Flask, jsonify, render_template, request
import random
import json
import threading
import time
import tkinter as tk
from tkinter import messagebox
import datetime
import sqlite3
import json
import os
import requests
from flask_cors import CORS


#ruchWindy = False
#pracaDrzwiWindy = False
#wydarzenieStatusSymulacji = False
wydarzenieZapisywaniaStatystyk = False
wydarzenieJazda = threading.Event() # Event do zarządzania aktywnością wątku jazdaWindy
wydarzeniePracaDrzwi = threading.Event() # Event do zarządzania aktywnością wątku pracaDrzwi
wydarzenieSymulacjaPodaży = threading.Event() # Event do zarządzania aktywnością wątku symulacji podaży
zapisywanieStatystyk = threading.Event() # Event do zarządzania aktywnością wątku zapisywania statystyk
losowanieInicjatoraPozytywnego = threading.Event() # Event do zarządzania aktywnością wątku losowania inicjatora pozytywnego
wydarzenieLosowaniaInicjatoraPozytywnego = False


jsonFilePathStatistics = '/data/statystyki_windy.json'
jsonFilePathInicjatoryRuchu = '/data/inicjatory_ruchu.json'
BASE_URL = 'https://winda.onrender.com'
URL_POST_WLACZ_WYLACZ_SYMULACJE = f'{BASE_URL}/wlacz_wylacz_symulacje'


app = Flask(__name__)
CORS(app)

wlasciwosci_windy = {
    'wielkośćSzybu': []
}

wielkośćSzybu = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
wlasciwosci_windy['wielkośćSzybu'] = wielkośćSzybu

wlasciwosci_drzwi = {
    'poleceniaDrzwi': [],
    'statusPracyDrzwi': 2
}

windy_data = {
    'polecenia': [],
    'kierunekJazdy': 0,
    'lokalizacjaWindy': 0,
    'ruchWindy': False,
    'pracaDrzwiWindy': False,
    'statusWindy': 1,
    'statusDrzwi': 1,
    'trybPracy': 1,
    'obciazenie': 0.0,
    'maxObciazenie': 800.0,
    'indeksZuzycia': 0.0,
    'ostatniSerwis': '1970-01-01',
    'predkoscWindy': 0.65
}

wybrane_przyciski = {
    'słownik': {}
}

wskazane_pietra = { # dodać wysyłanie do strony
    'słownik': {}
}

zawartosc_pieter = {
    'oczekujacyPasazerowie': {}
}


zawartosc_windy = {
    'wiezieniPasazerowie': {}
}

dane_symulacji = {
    'statusSymulacji': 1,
    'zmiennaCzęstotliwościGenerowaniaPasażerów': 5,
    'wydarzenieStatusSymulacji': False,
    'listaWagPieterDoWzywania': {},
    'listaWagPieterDoWybrania': {},
    'inicjatoryRuchu': {},
    'dataZakonczeniaInicjatoraPozytywnego': None
}

listaWagPieterDoWzywania = {pietro: 1 for pietro in wlasciwosci_windy['wielkośćSzybu']}
dane_symulacji['listaWagPieterDoWzywania'] = listaWagPieterDoWzywania

listaWagPieterDoWybrania = {pietro: 1 for pietro in wlasciwosci_windy['wielkośćSzybu']}
dane_symulacji['listaWagPieterDoWybrania'] = listaWagPieterDoWybrania


@app.route("/")
def home():
    return "Witam w aplikacji Flask dla serwera Windy!"


@app.route('/get_winda_status')
def get_winda_status():
    combined_data = {
        'windy_data': {
            'lokalizacjaWindy': windy_data.get('lokalizacjaWindy'),
            'kierunekJazdy': windy_data.get('kierunekJazdy'),
            'polecenia': windy_data.get('polecenia'),
            'ruchWindy': windy_data.get('ruchWindy'),
            'pracaDrzwiWindy': windy_data.get('pracaDrzwiWindy'),
            'statusWindy': windy_data.get('statusWindy'),
            'statusDrzwi': windy_data.get('statusDrzwi'),
            'trybPracy': windy_data.get('trybPracy'),
            'obciazenie': windy_data.get('obciazenie'),
            'maxObciazenie': windy_data.get('maxObciazenie'),
            'indeksZuzycia': windy_data.get('indeksZuzycia'),
            'ostatniSerwis': windy_data.get('ostatniSerwis'),
            'predkoscWindy': windy_data.get('predkoscWindy')
        },
        'wybrane_przyciski': wybrane_przyciski,
        'dane_symulacji': { 
            'status_symulacji': dane_symulacji.get('statusSymulacji'),
            'zmienna_częstotliwości_generowania_pasażerów': dane_symulacji.get('zmiennaCzęstotliwościGenerowaniaPasażerów'),
            'wydarzenieStatusSymulacji': dane_symulacji.get('wydarzenieStatusSymulacji'),
            'lista_wag_pieter_do_wzywania': dane_symulacji.get('listaWagPieterDoWzywania'),
            'lista_wag_pieter_do_wybrania': dane_symulacji.get('listaWagPieterDoWybrania'),
            'inicjatory_ruchu': dane_symulacji.get('inicjatoryRuchu'),
            'data_zakonczenia_inicjatora_pozytywnego': dane_symulacji.get('dataZakonczeniaInicjatoraPozytywnego')
        },
        'wiezieni_pasazerowie': {
            'wiezieni_pasazerowie': zawartosc_windy.get('wiezieniPasazerowie')
        },
        'zawartosc_pieter': {
            'oczekujacy_pasazerowie': zawartosc_pieter.get('oczekujacyPasazerowie')
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
    dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów'] = int(dane_symulacji.get('zmiennaCzęstotliwościGenerowaniaPasażerów', 0))
    return jsonify(dane_symulacji)


@app.route('/wlacz_wylacz_symulacje', methods=['POST'])
def wlacz_wylacz_symulacje():
    global wydarzenieLosowaniaInicjatoraPozytywnego
    #dane_symulacji['statusSymulacji'] = request.json.get('statusSymulacji')
    inicjatorDoUruchomienia, inicjatorValue = wybierzInicjatorRuchuZListy('idle', None)
    aktywujInicjatorRuchu(inicjatorDoUruchomienia, inicjatorValue) # podstawiony domyslny tryb pracy
    wydarzenieLosowaniaInicjatoraPozytywnego = True
    threading.Thread(target=lambda: losujInicjatorPozytywnyPoUnikalnosc(10, 1, 'normalny'), daemon=True).start() # do zmiany na dane pobierane z JSON
    losowanieInicjatoraPozytywnego.set()
    return jsonify({'statusSymulacji': dane_symulacji['statusSymulacji']})
if __name__ == '__main__':
    app.run(debug=True)
    

@app.route('/zmien_czestotliwosc', methods=['POST'])
def zmien_czestotliwosc():
    dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów'] = int(request.json.get('zmiennaCzęstotliwościGenerowaniaPasażerów'))
    return jsonify({'zmiennaCzęstotliwościGenerowaniaPasażerów': dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów']})


def odczytajStatystykiJSON():
    try:
        with open(jsonFilePathStatistics, 'r') as json_file:
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
        with open(jsonFilePathStatistics, 'w') as json_file:
            print("Plik istnieje przy zapisywaniu")
            json.dump(statystyki, json_file)
    except FileNotFoundError:
        print("Plik nie istnieje do zapisu. Zwracam pusty słownik.")
        return
        

def zapiszStatystykiOkresowo():
    while wydarzenieZapisywaniaStatystyk == True:
        time.sleep(60)
        zapiszStatystykiJSON(statystyki)


def zapiszStatystykiPrzyZamykaniu():
    zapiszStatystykiJSON(statystyki)


def zaktualizujPolecenia():
    if windy_data['kierunekJazdy'] == 2: #jazda do góry
        windy_data['polecenia'] = sorted([p for p in windy_data['polecenia'] if p >= windy_data['lokalizacjaWindy']]) + sorted([p for p in windy_data['polecenia'] if p < windy_data['lokalizacjaWindy']], reverse=True)
    if windy_data['kierunekJazdy'] == 1: #jazda w dół
        windy_data['polecenia'] = sorted([p for p in windy_data['polecenia'] if p < windy_data['lokalizacjaWindy']], reverse=True) + sorted([p for p in windy_data['polecenia'] if p >= windy_data['lokalizacjaWindy']])
    zmianaKierunkuJazdy()


def wskażPiętro(nowePolecenie, źródłoPolecenia):
    if sprawdzCzyDubel(nowePolecenie, źródłoPolecenia) == False:
        windy_data['polecenia'].append(nowePolecenie)
        zaktualizujPolecenia()
        #zapiszLog(1, źródłoPolecenia, None, nowePolecenie, polecenia, None, typUsera)
        #wyświetlLogWWidżecie()
        if windy_data.get('ruchWindy') is False and wlasciwosci_drzwi['statusPracyDrzwi'] == 2:
            windy_data['ruchWindy'] = True
            threading.Thread(target=jazdaWindy, daemon=True).start()
            wydarzenieJazda.set()
        else:
            return 
    else:
        return


def zapiszWybranyPrzycisk(nowePolecenie, źródłoPolecenia):
    if 'słownik' not in wybrane_przyciski:
        wybrane_przyciski['słownik'] = {}
    if not isinstance(wybrane_przyciski.get('słownik'), dict):
        wybrane_przyciski['słownik'] = {}
    klucz = int(nowePolecenie)
    wybrane_przyciski['słownik'].update({klucz: źródłoPolecenia})


def zapiszWybranePiętro(nowePolecenie, źródłoPolecenia):
    if 'słownik' not in wskazane_pietra:
        wskazane_pietra['słownik'] = {}
    if not isinstance(wybrane_przyciski.get('słownik'), dict):
        wskazane_pietra['słownik'] = {}
    klucz = int(nowePolecenie)
    wskazane_pietra['słownik'].update({klucz: źródłoPolecenia})


def usunPiętroZListyWybranychPięter(lokalizacja):
    if lokalizacja in wybrane_przyciski['słownik']:
        wybrane_przyciski['słownik'].pop(lokalizacja, None)


def sprawdzCzyDubel(nowePolecenie, źródłoPolecenia):
    if nowePolecenie == windy_data['lokalizacjaWindy']:
        return True
    else:
        for x in windy_data['polecenia']:
            if x == nowePolecenie or nowePolecenie == windy_data['lokalizacjaWindy']:
                return True
            else:
                pass
        return False 


def jazdaWindy():
    global liczbaPrzystanków
    while windy_data.get('ruchWindy'):
        time.sleep(5) 
        zmianaLokalizacjiWindy()
        zmianaKierunkuJazdy()
        if windy_data['polecenia']:
            if windy_data['lokalizacjaWindy'] == windy_data['polecenia'][0]:
                windy_data['polecenia'].pop(0)
                liczbaPrzystanków += 1
                statystyki['zaliczone_przystanki'] = liczbaPrzystanków
                usunPiętroZListyWybranychPięter(windy_data['lokalizacjaWindy'])
                zapiszStatystykiPrzewiezionychPasazerow()
                usunGrupePasazerowZWindy(windy_data['lokalizacjaWindy'])
                celPasazera = pobierzCelGrupyPasazerow(windy_data['lokalizacjaWindy'])
                symulujWybórPięter(celPasazera)
                przeniesGrupePasazerowDoWindy()
                zmianaKierunkuJazdy()
                dodajPolecenieDrzwi(1)
                if not windy_data['polecenia']:
                    wydarzenieJazda.clear()
                    windy_data['ruchWindy'] = False
        else:
            wydarzenieJazda.clear()
            windy_data['ruchWindy'] = False


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
    if windy_data.get('ruchWindy') == False:
        wlasciwosci_drzwi['poleceniaDrzwi'].append(rodzajPracy)
        windy_data['pracaDrzwiWindy'] = True
        threading.Thread(target=uruchomPracęDrzwi, daemon=True).start()
        wydarzeniePracaDrzwi.set()
    if windy_data.get('ruchWindy') == True:
        wydarzenieJazda.clear()
        windy_data['ruchWindy'] = False
        wlasciwosci_drzwi['poleceniaDrzwi'].append(rodzajPracy)
        windy_data['pracaDrzwiWindy'] = True
        threading.Thread(target=uruchomPracęDrzwi, daemon=True).start()
        wydarzeniePracaDrzwi.set()


def uruchomPracęDrzwi():
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
    windy_data['pracaDrzwiWindy'] = False
    #if polecenia:
        #zapiszLog(3, None, kierunekJazdy, polecenia[0], polecenia, None)
        #wyświetlLogWWidżecie()
    #else:
        #pass
    windy_data['ruchWindy'] = True
    threading.Thread(target=jazdaWindy, daemon=True).start()
    wydarzenieJazda.set()


def otwórzDrzwi(): # 0 - zamykanie, 1 - otwieranie, 2 - zamknięte, 3 - otwarte
    wlasciwosci_drzwi['statusPracyDrzwi'] = 1
    time.sleep(2)
    wlasciwosci_drzwi['statusPracyDrzwi'] = 3
    
    
def zamknijDrzwi(): # 0 - zamykanie, 1 - otwieranie, 2 - zamknięte, 3 - otwarte
    wlasciwosci_drzwi['statusPracyDrzwi'] = 0
    time.sleep(2)
    wlasciwosci_drzwi['statusPracyDrzwi'] = 2


def losujInicjatorPozytywnyPoUnikalnosc(czestotliwosc, szansaNaWylosowanieInicjatora, unikalnoscInicjatora):
    global wydarzenieLosowaniaInicjatoraPozytywnego
    while wydarzenieLosowaniaInicjatoraPozytywnego == True:
        time.sleep(czestotliwosc)
        losowaWartosc = random.randint(1, 2) # wartośc testowa, do zmiany na realną wartość
        if losowaWartosc >= szansaNaWylosowanieInicjatora: # testowa wartość, do zmiany na realną wartość
            keyDoAktywacji, valueDoAktywacji = wybierzInicjatorRuchuZListy(None, unikalnoscInicjatora)
            if keyDoAktywacji is not None and valueDoAktywacji is not None:
                klucze_do_dezaktywacji = list(dane_symulacji['inicjatoryRuchu'].keys())
                for key in klucze_do_dezaktywacji:
                    print('dezaktywowano inicjatory pozytywne')
                    dezaktywujInicjator(key)
                print('rozpoczęto aktywację inicjatora pozytywnego po unikalności')
                aktywujInicjatorRuchu(keyDoAktywacji, valueDoAktywacji)
                wydarzenieLosowaniaInicjatoraPozytywnego = False
                losowanieInicjatoraPozytywnego.clear()
            else:
                print('nie znaleziono inicjatora pozytywnego po unikalności')
                pass
        else:
            print('nie spełniono warunku częstotliwości losowania inicjatora pozytywnego')
            pass


def dezaktywujInicjator(kluczZdarzenia):
    if kluczZdarzenia in dane_symulacji['inicjatoryRuchu']:
        dane_symulacji['inicjatoryRuchu'].pop(kluczZdarzenia)
    else:
        pass


def wybierzInicjatorRuchuZListy(nazwaInicjatora=None, unikalnoscInicjatora=None):
    global wydarzenieZapisywaniaStatystyk, wydarzenieSymulacjaPodaży, zapisywanieStatystyk
    inicjatoryRuchu = pobierzInicjatoryRuchuJSON()
    if nazwaInicjatora is not None:
        for key, value in inicjatoryRuchu.items():
            if nazwaInicjatora == key:
                print("znaleziono inicjator po nazwie:", key)
                return key, value
    elif unikalnoscInicjatora is not None:
        for key, value in inicjatoryRuchu.items():
            if unikalnoscInicjatora == value.get('unikalnosc'):
                print("znaleziono inicjator po rodzaju:", unikalnoscInicjatora)
                return key, value
    print("nie znaleziono inicjatora")
    wydarzenieSymulacjaPodaży.clear()
    dane_symulacji['wydarzenieStatusSymulacji'] = False
    zapisywanieStatystyk.clear()
    wydarzenieZapisywaniaStatystyk = False 
    return None, None


def aktywujInicjatorRuchu(key, value):
    global wydarzenieZapisywaniaStatystyk
    print("uruchomiono inicjator", key)
    dane_symulacji['inicjatoryRuchu'][key] = value
    trybPracy = value.get('trybPracy')
    limitPolecen = value.get('limitPolecen')
    zmiennaMinimalnegoOpoznienia = value.get('zmiennaMinimalnegoOpoznienia')
    zmiennaMaksymalnegoOpoznienia = value.get('zmiennaMaksymalnegoOpoznienia')
    listaWagPieterLosowanych = value.get('wagaPietraLosowanego')
    aktualizujWagiPięterDoWzywania(listaWagPieterLosowanych)
    dane_symulacji['wydarzenieStatusSymulacji'] = True
    listaWagPieterWybieranych = value.get('wagaPietraWybieranego')
    aktualizujWagiPięterDoWybrania(listaWagPieterWybieranych)
    wyliczZakonczenieInicjatoraPozytywnego(value.get('czasTrwania'))
    threading.Thread(target=lambda: dostosujCzestotliwoscGenerowaniaPasazerow(trybPracy, limitPolecen, zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia), daemon=True).start() # do zmiany na dane pobierane z JSON
    wydarzenieSymulacjaPodaży.set()
    aktywujZapisywanieStatystyk()    


def wyliczZakonczenieInicjatoraPozytywnego(czasTrwania):
    if czasTrwania > 0:
        dataZakonczeniaInicjatoraPozytywnego = datetime.datetime.now() + datetime.timedelta(hours=czasTrwania)
    else:
        dataZakonczeniaInicjatoraPozytywnego = None
    dane_symulacji['dataZakonczeniaInicjatoraPozytywnego'] = dataZakonczeniaInicjatoraPozytywnego

def aktywujZapisywanieStatystyk():
    global wydarzenieZapisywaniaStatystyk
    wydarzenieZapisywaniaStatystyk = True
    threading.Thread(target=zapiszStatystykiOkresowo, daemon=True).start()
    zapisywanieStatystyk.set()


def pobierzInicjatoryRuchuJSON():  
    try:
        with open(jsonFilePathInicjatoryRuchu, 'r') as json_file:
            print("Plik z inicjatorami istnieje przy wczytaniu")
            return json.load(json_file)
    except FileNotFoundError:
        print("Plik jsonFilePathInicjatoryRuchu nie istnieje do wczytania.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Błąd dekodowania JSON: {e}")
        return {}


# 0 - idle, 1 - zmieniony_zdarzeniem, 2 - tbd
#przykłady realnych trybów: idle = (0, 1, 5, 10), zmieniony_zdarzeniem = (1, zmienna_ze_zdarzenia, 2, 7)
def dostosujCzestotliwoscGenerowaniaPasazerow(trybPracy, limitPolecen, zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia):
    while dane_symulacji.get('wydarzenieStatusSymulacji') == True:
        if trybPracy == 0 and len(windy_data['polecenia']) < limitPolecen: # nowe piętro dodawane jest wtedy kiedy lista zadań pusta
            losowaWartoscOpoznienia = random.randint(zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia)
            time.sleep(int(losowaWartoscOpoznienia))
            generujPodażPasażerów()
            #dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów'] = sredniRealnyCzasPomiedzyGenerowaniem - do dodania w przyszłości, aby zbierać dane o odstępie
        elif trybPracy == 1 and len(zawartosc_pieter['oczekujacyPasazerowie']) < limitPolecen: # nowe piętro dodawane jest wtedy kiedy lista wzywjących pięter jest mniejsza niż zadana
            losowaWartoscOpoznienia = random.randint(zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia)
            time.sleep(int(losowaWartoscOpoznienia))
            generujPodażPasażerów()
            #dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów'] = sredniRealnyCzasPomiedzyGenerowaniem - j.w.
        else:
            pass

def generujPodażPasażerów():
    if dane_symulacji.get('wydarzenieStatusSymulacji') == True:
        #time.sleep(definiujCzasZwłokiGenerowaniaPasażerów(dane_symulacji.get('zmiennaCzęstotliwościGenerowaniaPasażerów')))
        liczbaPasazerow = generujLiczbePasazerowNaPiętrze()
        lokalizacjaPasażerów = generujLokalizacjePasazerow()
        celPasazerow = generujCelPasazera(lokalizacjaPasażerów)
        kierunekJazdyPasażerów = zdefiniujKierunekJazdyPasażera(celPasazerow, lokalizacjaPasażerów)
        generujGrupePasazerowNaPietrze(lokalizacjaPasażerów, liczbaPasazerow, celPasazerow, kierunekJazdyPasażerów)
        #aktualizujLiczbePasazerowNaPietrze(lokalizacjaPasażerów, liczbaPasazerow)
        wskażPiętro(lokalizacjaPasażerów, kierunekJazdyPasażerów)
        if kierunekJazdyPasażerów > 1:
            zapiszWybranyPrzycisk(lokalizacjaPasażerów, kierunekJazdyPasażerów)
        else:
            pass
    else:
        return


def definiujCzasZwłokiGenerowaniaPasażerów(wartośćZmienna, wartośćStała=18): #wartość stałą jest drugim komponentem defiuniującym delay
    losowaCzęśćCzęstotliwości = random.randint(0, 4)
    czasZwłokiGenerowaniaPasażerów = (wartośćStała + int(losowaCzęśćCzęstotliwości) - int(wartośćZmienna))
    return czasZwłokiGenerowaniaPasażerów


def generujLiczbePasazerowNaPiętrze():
    dostępnaLiczbaPasażerów = [1, 2, 3, 4]	# w przyszłości do zmiany na zmienną definiującą liczbe generowanych pasażerów
    weights = [5, 3, 1, 1]
    losowaLiczbaPasażerów = random.choices(dostępnaLiczbaPasażerów, weights=weights, k=1)[0]
    return losowaLiczbaPasażerów


def generujLokalizacjePasazerow():
    lokalizacjaPasazerow = random.choices(wlasciwosci_windy['wielkośćSzybu'], weights=dane_symulacji['listaWagPieterDoWzywania'], k=1)[0] # w przyszłości do zmiany na zmienną definiującą pożądane źródła poleceń
    return lokalizacjaPasazerow


def aktualizujWagiPięterDoWzywania(pietraDoZmiany):
    for key, value in pietraDoZmiany.items():
        dane_symulacji['listaWagPieterDoWzywania'][key] = value


def aktualizujWagiPięterDoWybrania(pietraDoZmiany):
    for key, value in pietraDoZmiany.items():
        dane_symulacji['listaWagPieterDoWybrania'][key] = value


def generujCelPasazera(lokalizacjaPasażerów): # w przyszłości do zmiany na zmienną definiującą pożądane cele jazdy
    while True:
        celPasazera = random.choices(wlasciwosci_windy['wielkośćSzybu'], weights=dane_symulacji['listaWagPieterDoWybrania'], k=1)[0]
        if celPasazera != lokalizacjaPasażerów:
            break
    return celPasazera


def zdefiniujKierunekJazdyPasażera(celPasazera, lokalizacjaPasażerów):
    if celPasazera > lokalizacjaPasażerów:
        kierunekJazdyPasażerów = 2
    else:
        kierunekJazdyPasażerów = 3
    return kierunekJazdyPasażerów


startGUID = 0
def generujGUID():
    global startGUID
    if startGUID == 99:
        startGUID = 1
    else:
        startGUID += 1
    return str(startGUID)

# baza bohaterów zostanie przenieisona do SQL
characters_pool = {
"1": {"chance": 300, "description": "normalny"},
"2": {"chance": 300, "description": "normalny"},
"3": {"chance": 300, "description": "unikalny"},
"4": {"chance": 300, "description": "unikalny"},
"5": {"chance": 300, "description": "legendarny"},
"6": {"chance": 300, "description": "legendarny"},
}

def draw_character():
    # Losowanie liczby od 1 do 10 000
    roll = random.randint(1, 1800)
    cumulative = 0

    for id, data in characters_pool.items():
        cumulative += data["chance"]
        if roll <= cumulative:
            return id, data["description"]

def generujGrupePasazerowNaPietrze(zrodloPasazera, liczbaPasazerow, celPasazerow, kierunekJazdyPasażerów):
    GUID = generujGUID()
    zawartosc_pieter['oczekujacyPasazerowie'][GUID] = {
        'zrodlo': zrodloPasazera,
        'kierunek': kierunekJazdyPasażerów,
        'cel': celPasazerow,
        'rodzaje_pasazerow': {
            'normalny': [],
            'unikalny': [],
            'legendarny': []
        },
        'liczba_wygenerowanych_pasazerow': None
    }
    for i in range(liczbaPasazerow):
        id, rodzaj = draw_character()
        zawartosc_pieter['oczekujacyPasazerowie'][GUID]['rodzaje_pasazerow'][rodzaj].append(id)
    zawartosc_pieter['oczekujacyPasazerowie'][GUID]['liczba_wygenerowanych_pasazerow'] = sum(len(zawartosc_pieter['oczekujacyPasazerowie'][GUID]['rodzaje_pasazerow'][key]) for key in zawartosc_pieter['oczekujacyPasazerowie'][GUID]['rodzaje_pasazerow'])
    

def symulujWybórPięter(celPasazerow):
    global liczbaOczekującychPasażerów
    if dane_symulacji['statusSymulacji'] == 1:

        wskażPiętro(celPasazerow, 1)
        zapiszWybranePiętro(celPasazerow, 1)
        #liczbaOczekującychPasażerówNaPietrze = next((l for p, l in pietraIPasazerowie if p == windy_data['lokalizacjaWindy']), 0)
        #statystyki["liczba_oczekujacych_pasazerow"] = liczbaOczekującychPasażerów
        #statystyki['przewiezieni_pasazerowie']['typ1'] += liczbaOczekującychPasażerówNaPietrze
        #powiekszLiczbePasazerowWWindzie(liczbaOczekującychPasażerówNaPietrze)
        #liczbaOczekującychPasażerów = sum(l for p, l in pietraIPasazerowie)
        #statystyki["liczba_oczekujacych_pasazerow"] = liczbaOczekującychPasażerów
    else:
        return


def usunGrupePasazerowZPietra(lokalizacja):
    keys_to_remove = [key for key in zawartosc_pieter['oczekujacyPasazerowie'].keys() if zawartosc_pieter['oczekujacyPasazerowie'][key]['zrodlo'] == lokalizacja]
    for key in keys_to_remove:
        zawartosc_pieter['oczekujacyPasazerowie'].pop(key)
    return


def pobierzCelGrupyPasazerow(lokalizacjaPasazerow):
    kluczGrupyPasazerow = [key for key in zawartosc_pieter['oczekujacyPasazerowie'].keys() if zawartosc_pieter['oczekujacyPasazerowie'][key]['zrodlo'] == lokalizacjaPasazerow]
    if kluczGrupyPasazerow:
        celGrupyPasazerow = zawartosc_pieter['oczekujacyPasazerowie'][kluczGrupyPasazerow[0]]['cel']
        return celGrupyPasazerow
    return windy_data['lokalizacjaWindy']


def pobierzZrodloGrupyPasazerow(lokalizacjaPasazerow):
    if not zawartosc_pieter['oczekujacyPasazerowie']:
        return windy_data['lokalizacjaWindy']
    kluczGrupyPasazerow = [key for key in zawartosc_pieter['oczekujacyPasazerowie'].keys() if zawartosc_pieter['oczekujacyPasazerowie'][key]['zrodlo'] == lokalizacjaPasazerow]
    if kluczGrupyPasazerow:
        zrodloGrupyPasazerow = zawartosc_pieter['oczekujacyPasazerowie'][kluczGrupyPasazerow[0]]['zrodlo']
        return zrodloGrupyPasazerow
    return windy_data['lokalizacjaWindy']


def przeniesGrupePasazerowDoWindy():
    zrodloGrupyPasazerow = pobierzZrodloGrupyPasazerow(windy_data['lokalizacjaWindy'])
    kluczGrupyPasazerow = [key for key in zawartosc_pieter['oczekujacyPasazerowie'].keys() if zawartosc_pieter['oczekujacyPasazerowie'][key]['zrodlo'] == zrodloGrupyPasazerow]
    if kluczGrupyPasazerow:
        for key in kluczGrupyPasazerow:
            zawartosc_windy['wiezieniPasazerowie'][key] = zawartosc_pieter['oczekujacyPasazerowie'][key]
        usunGrupePasazerowZPietra(zrodloGrupyPasazerow)
        aktualizujObciazenieWindy()
    else:
        return


def usunGrupePasazerowZWindy(lokalizacja):
    keys_to_remove = [key for key in zawartosc_windy['wiezieniPasazerowie'].keys() if zawartosc_windy['wiezieniPasazerowie'][key]['cel'] == lokalizacja]
    for key in keys_to_remove:
        zawartosc_windy['wiezieniPasazerowie'].pop(key)
    aktualizujObciazenieWindy()


def aktualizujObciazenieWindy(): # W przyszłości zastąpić losową wagą pasażera, dodać do słownika więcej danych o pasażerach
    #losowaWagaPasazera = random.randint(60, 100)
    if not zawartosc_windy['wiezieniPasazerowie']:
        windy_data['obciazenie'] = 0
    else:
        liczbaPasazerow = 0
        for key in zawartosc_windy['wiezieniPasazerowie'].keys():
            liczbaPasazerow += zawartosc_windy['wiezieniPasazerowie'][key]['liczba_wygenerowanych_pasazerow']
        obciazenie = liczbaPasazerow * 70 #losowaWagaPasazera
        windy_data['obciazenie'] = obciazenie 


def zapiszStatystykiPrzewiezionychPasazerow():
    for key, pasazerowie in zawartosc_windy['wiezieniPasazerowie'].items():
        if pasazerowie['cel'] == windy_data['lokalizacjaWindy']:
            for rodzaj, lista in pasazerowie['rodzaje_pasazerow'].items():
                statystyki['przewiezieni_pasazerowie'][f'typ{["normalny", "unikalny", "legendarny"].index(rodzaj) + 1}'] += len(lista)
    return

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
