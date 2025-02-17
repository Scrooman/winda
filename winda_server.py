
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
#wydarzenieSymulacjaPodaży = threading.Event() # Event do zarządzania aktywnością wątku symulacji podaży
zatrzymanieSymulacjiPodaży = threading.Event() # Event do zarządzania aktywnością wątku zatrzymania symulacji podaży    
zapisywanieStatystyk = threading.Event() # Event do zarządzania aktywnością wątku zapisywania statystyk
#losowanieInicjatoraPozytywnego = threading.Event() # Event do zarządzania aktywnością wątku losowania inicjatora pozytywnego
#zatrzymanieLosowaniaInicjatoraPozytywnego = threading.Event()
#losowanieInicjatoraNegatywnego = threading.Event() # Event do zarządzania aktywnością wątku losowania inicjatora negatywnego
#wydarzenieLosowaniaInicjatoraNegatywnego = False
#sprawdzanieDezaktywacjiInicjatoraPozytywnego = threading.Event() # Event do zarządzania aktywnością wątku dezaktywacji inicjatora
#zatrzymanieSprawdzaniaDezaktywacjiInicjatoraPozytywnego = threading.Event()
losowanieInicjatoraPozytywnego = threading.Thread(target=lambda: cyklicznieLosujInicjatorPozytywny('normalny'), daemon=True)
losowanieInicjatoraNegatywnego = threading.Thread(target=lambda: cyklicznieLosujInicjatorNegatywny('normalny'), daemon=True)




jsonFilePathStatistics = '/data/statystyki_windy.json'
jsonFilePathInicjatoryRuchu = '/data/inicjatory_ruchu.json'
jsonFilePathInicjatoryRuchuNegatywne = '/data/inicjatory_negatywne_windy.json'
BASE_URL = 'https://winda.onrender.com'
URL_POST_WLACZ_WYLACZ_SYMULACJE = f'{BASE_URL}/wlacz_wylacz_symulacje'


# KOD ZMIENNYCH GLOABALNYCH
#___________________________________________________________________________________________________________________________

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

wylaczone_pietra = {
    'słownik': []
}

wylaczone_przyciski = { 
    'słownik': []
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
    'dataZakonczeniaInicjatoraPozytywnego': None,
    'inicjatoryRuchuNegatywne': {}
}

listaWagPieterDoWzywania = {pietro: 1 for pietro in wlasciwosci_windy['wielkośćSzybu']}
dane_symulacji['listaWagPieterDoWzywania'] = listaWagPieterDoWzywania

listaWagPieterDoWybrania = {pietro: 1 for pietro in wlasciwosci_windy['wielkośćSzybu']}
dane_symulacji['listaWagPieterDoWybrania'] = listaWagPieterDoWybrania

#KOD POŁĄCZENIA Z SERWEREM
#___________________________________________________________________________________________________________________________

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
        'wybrane_przyciski': wybrane_przyciski.get('słownik'),
        'wskazane_pietra': wskazane_pietra.get('słownik'),
        'dane_symulacji': { 
            'status_symulacji': dane_symulacji.get('statusSymulacji'),
            'zmienna_częstotliwości_generowania_pasażerów': dane_symulacji.get('zmiennaCzęstotliwościGenerowaniaPasażerów'),
            'wydarzenieStatusSymulacji': dane_symulacji.get('wydarzenieStatusSymulacji'),
            'lista_wag_pieter_do_wzywania': dane_symulacji.get('listaWagPieterDoWzywania'),
            'lista_wag_pieter_do_wybrania': dane_symulacji.get('listaWagPieterDoWybrania'),
            'inicjatory_ruchu': dane_symulacji.get('inicjatoryRuchu'),
            'data_zakonczenia_inicjatora_pozytywnego': dane_symulacji.get('dataZakonczeniaInicjatoraPozytywnego'),
            'inicjatory_ruchu_negatywne': dane_symulacji.get('inicjatoryRuchuNegatywne')
        },
        'wiezieni_pasazerowie': {
            'wiezieni_pasazerowie': zawartosc_windy.get('wiezieniPasazerowie')
        },
        'zawartosc_pieter': {
            'oczekujacy_pasazerowie': zawartosc_pieter.get('oczekujacyPasazerowie')
        },
        'wylaczone_pietra': {
            'wylaczone_pietra': wylaczone_pietra.get('słownik')
        },
        'wylaczone_przyciski': {
            'wylaczone_przyciski': wylaczone_przyciski.get('słownik')
        },
        'wlasciwosci_drzwi': {
            'polecenia_drzwi': wlasciwosci_drzwi.get('poleceniaDrzwi'),
            'status_pracy_drzwi': wlasciwosci_drzwi.get('statusPracyDrzwi')
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
    global losowanieInicjatoraNegatywnego, sprawdzanieDezaktywacjiInicjatoraPozytywnego
    #dane_symulacji['statusSymulacji'] = request.json.get('statusSymulacji')
    aktywujDomyslnyInicjator()
    losowanieInicjatoraPozytywnego.start()
    sprawdzanieDezaktywacjiInicjatoraPozytywnego = threading.Thread(target=dezaktywujInicjatorPozytywnyPoZakonczeniu, daemon=True).start()
    aktywujZapisywanieStatystyk()
    losowanieInicjatoraNegatywnego.start()
    return jsonify({'statusSymulacji': dane_symulacji['statusSymulacji']})
if __name__ == '__main__':
    app.run(debug=True)
    

@app.route('/zmien_czestotliwosc', methods=['POST'])
def zmien_czestotliwosc():
    dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów'] = int(request.json.get('zmiennaCzęstotliwościGenerowaniaPasażerów'))
    return jsonify({'zmiennaCzęstotliwościGenerowaniaPasażerów': dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów']})


@app.route('/dezaktywuj_inicjator_negatywny', methods=['DELETE'])
def dezaktywujInicjatorNegatywny():
    data = request.get_json()
    kluczZdarzenia = data.get('kluczZdarzenia')
    if kluczZdarzenia:
        dezaktywujInicjatorNegatywny(kluczZdarzenia)
        return jsonify({"message": "Inicjator negatywny dezaktywowany"}), 200
    else:
        return jsonify({"error": "Brak klucza zdarzenia"}), 400

# KOD STATYSTYK
#___________________________________________________________________________________________________________________________

def odczytajStatystykiJSON():
    try:
        with open(jsonFilePathStatistics, 'r') as json_file:
            print("Plik istnieje przy wczytaniu")
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
                "nieobsluzeni_pasazerowie": {
                    "typ1": 0,
                    "typ2": 0,
                    "typ3": 0
                },
                "liczba_otworzen_drzwi": 0,
                "liczba_oczekujacych_pasazerow": 0
        }
    except json.JSONDecodeError as e:
        print(f"Błąd dekodowania JSON: {e}")
        return {
            "przebyta_odleglosc": 0,
            "zaliczone_przystanki": 0,
            "pokonane_pietra": 0,
            "przewiezieni_pasazerowie": {
                "typ1": 0,
                "typ2": 0,
                "typ3": 0
            },
            "nieobsluzeni_pasazerowie": {
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


#KOD FUNKCJI WINDY
#___________________________________________________________________________________________________________________________

def zaktualizujPolecenia():
    if windy_data['kierunekJazdy'] == 2: #jazda do góry
        windy_data['polecenia'] = sorted([p for p in windy_data['polecenia'] if p >= windy_data['lokalizacjaWindy']]) + sorted([p for p in windy_data['polecenia'] if p < windy_data['lokalizacjaWindy']], reverse=True)
    if windy_data['kierunekJazdy'] == 1: #jazda w dół
        windy_data['polecenia'] = sorted([p for p in windy_data['polecenia'] if p < windy_data['lokalizacjaWindy']], reverse=True) + sorted([p for p in windy_data['polecenia'] if p >= windy_data['lokalizacjaWindy']])
    zmianaKierunkuJazdy()


def wskażPiętro(nowePolecenie, źródłoPolecenia): # do zmiany, aby nie bylo mozliwe dodanie pietra na ktorym znajduje sie klient - ale to raczej zmiana do generowania pasazerow
    if sprawdzCzyDubel(nowePolecenie, źródłoPolecenia) == False:
        if nowePolecenie not in wylaczone_pietra['słownik'] and nowePolecenie not in wylaczone_przyciski['słownik']: # do weryfikacji i zmiany jesli pasazer wybierze wylaczone pietro lub przycisk
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
            return False # do zmiany, aby zwracało komunikat o niedostępności piętra lub pietra
    else:
        return False


def zapiszWybranyPrzycisk(nowePolecenie, źródłoPolecenia):
    if 'słownik' not in wybrane_przyciski:
        wybrane_przyciski['słownik'] = {}
    if not isinstance(wybrane_przyciski.get('słownik'), dict):
        wybrane_przyciski['słownik'] = {}
    klucz = int(nowePolecenie)
    wybrane_przyciski['słownik'].update({klucz: źródłoPolecenia})


def usunPiętroZListyWybranychPięter(lokalizacja):
    print("usuwam piętro z listy wybranych pięter")
    lokalizacja = int(lokalizacja)
    if lokalizacja in wybrane_przyciski['słownik']:
        del wybrane_przyciski['słownik'][lokalizacja]
        print("usunięto piętro z listy wybranych pięter")


def zapiszWskazanePiętro(nowePolecenie, źródłoPolecenia):
    if 'słownik' not in wskazane_pietra:
        wskazane_pietra['słownik'] = {}
    if not isinstance(wskazane_pietra.get('słownik'), dict):
        wskazane_pietra['słownik'] = {}
    klucz = str(nowePolecenie)
    wskazane_pietra['słownik'].update({klucz: źródłoPolecenia})


def usunPiętroZListyWskazanychPieter(lokalizacja):
    print("usuwam piętro z listy wskazanych pięter")
    lokalizacja = str(lokalizacja)
    if str(lokalizacja) in wskazane_pietra['słownik']:
        del wskazane_pietra['słownik'][str(lokalizacja)]
        print("usunięto piętro z listy wskazanych pięter")



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
                print("Winda zatrzymała się na piętrze", windy_data['lokalizacjaWindy'])
                usunPiętroZListyWskazanychPieter(windy_data['lokalizacjaWindy'])
                usunPiętroZListyWybranychPięter(windy_data['lokalizacjaWindy'])
                windy_data['polecenia'].pop(0)
                liczbaPrzystanków += 1
                statystyki['zaliczone_przystanki'] = liczbaPrzystanków
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


#KOD FUNCKJI ZDARZEN/INICJATORÓW
#___________________________________________________________________________________________________________________________

def aktywujDomyslnyInicjator():
    inicjatorDoUruchomienia, inicjatorValue = wybierzInicjatorRuchuPozytywnyZListy('idle', None)
    aktywujInicjatorRuchu(inicjatorDoUruchomienia, inicjatorValue) # podstawiony domyslny tryb pracy


def cyklicznieLosujInicjatorPozytywny(unikalnoscInicjatora):
    while True:
        if 'idle' in dane_symulacji['inicjatoryRuchu']:
            print("Aktywny pozytywny inicjator idle - losuję")
            if 4 < datetime.datetime.now().hour < 23: # testowe wartości
                print("rozpoczęto losowanie inicjatora pozytywnego po unikalności")
            if losujInicjatorPozytywnyPoUnikalnosc(unikalnoscInicjatora) == False:
                print("odwleczenie w czasie losowania")
                losowaWartosc = random.randint(1600, 2600)
                time.sleep(losowaWartosc)
        else:
            print("Aktywny pozytywny inicjator ruchu - nie losuję")
            time.sleep(1800)



def losujInicjatorPozytywnyPoUnikalnosc(unikalnoscInicjatora):
    losowaWartosc = random.randint(1, 3)
    if losowaWartosc == 1:  
        keyDoAktywacji, valueDoAktywacji = wybierzInicjatorRuchuPozytywnyZListy(None, unikalnoscInicjatora)
        if keyDoAktywacji is not None and valueDoAktywacji is not None:
            klucze_do_dezaktywacji = list(dane_symulacji['inicjatoryRuchu'].keys())
            for key in klucze_do_dezaktywacji:
                print('dezaktywowano inicjatory pozytywne')
                dezaktywujInicjator(key)
            print('rozpoczęto aktywację inicjatora pozytywnego po unikalności')
            aktywujInicjatorRuchu(keyDoAktywacji, valueDoAktywacji)
        else:
            print('nie znaleziono inicjatora pozytywnego po unikalności')
            pass
    else:
        print("losowanie zakończone negatywnie")
        return False


def dezaktywujInicjator(kluczZdarzenia):
    global zatrzymanieSymulacjiPodaży, wydarzenieSymulacjaPodaży
    print("rozpoczynam dezaktywację inicjatora pozytywnego")
    if kluczZdarzenia in dane_symulacji['inicjatoryRuchu']:
        print("Dezaktywuję inicjator pozytywny", kluczZdarzenia)
        dane_symulacji['inicjatoryRuchu'].pop(kluczZdarzenia)
        zatrzymanieSymulacjiPodaży.set()
        wydarzenieSymulacjaPodaży.join()
        dane_symulacji['wydarzenieStatusSymulacji'] = False
    else:
        print("nie dezaktywuję inicjatora pozytywnego")
        pass


def wybierzInicjatorRuchuPozytywnyZListy(nazwaInicjatora=None, unikalnoscInicjatora=None):
    global wydarzenieSymulacjaPodaży, zatrzymanieSymulacjiPodaży
    inicjatoryRuchu = pobierzInicjatoryRuchuJSON()
    if nazwaInicjatora is not None:
        for key, value in inicjatoryRuchu.items():
            if nazwaInicjatora == key:
                print("znaleziono inicjator po nazwie:", key)
                return key, value
    elif unikalnoscInicjatora is not None:
        klucze_do_wylosowania = []
        for key, value in inicjatoryRuchu.items():
            if unikalnoscInicjatora == value.get('unikalnosc'):
                klucze_do_wylosowania.append(key)
                print("znaleziono inicjator po rodzaju:", unikalnoscInicjatora)
        if len(klucze_do_wylosowania) > 0:
            key = random.choice(klucze_do_wylosowania)
            return key, inicjatoryRuchu[key]
    print("nie znaleziono inicjatora")
    zatrzymanieSymulacjiPodaży.set()
    wydarzenieSymulacjaPodaży.join()
    dane_symulacji['wydarzenieStatusSymulacji'] = False
    return None, None


def aktywujInicjatorRuchu(key, value):
    global wydarzenieSymulacjaPodaży, zatrzymanieSymulacjiPodaży
    print("uruchomiono inicjator", key)
    dane_symulacji['inicjatoryRuchu'][key] = value
    trybPracy = value.get('trybPracy')
    limitPolecen = value.get('limitPolecen')
    zmiennaMinimalnegoOpoznienia = value.get('zmiennaMinimalnegoOpoznienia')
    zmiennaMaksymalnegoOpoznienia = value.get('zmiennaMaksymalnegoOpoznienia')
    listaWagPieterLosowanych = value.get('wagaPietraLosowanego')
    aktualizujWagiPięterDoWzywania(listaWagPieterLosowanych)
    listaWagPieterWybieranych = value.get('wagaPietraWybieranego')
    aktualizujWagiPięterDoWybrania(listaWagPieterWybieranych)
    wyliczZakonczenieInicjatoraPozytywnego(value.get('czasTrwania'))
    print("uruchamiany inicjator dla:", trybPracy, limitPolecen, zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia)
    dane_symulacji['wydarzenieStatusSymulacji'] = True
    zatrzymanieSymulacjiPodaży.clear()
    wydarzenieSymulacjaPodaży = threading.Thread(target=lambda: dostosujCzestotliwoscGenerowaniaPasazerow(trybPracy, limitPolecen, zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia), daemon=True)
    wydarzenieSymulacjaPodaży.start()



def wyliczZakonczenieInicjatoraPozytywnego(czasTrwania):
    if czasTrwania != 0:
        losowaWartoscCzasuTrwania = round(random.uniform(0, 2), 2)
        dataZakonczeniaInicjatoraPozytywnego = datetime.datetime.now() + datetime.timedelta(hours=(czasTrwania+losowaWartoscCzasuTrwania))
    else:
        dataZakonczeniaInicjatoraPozytywnego = None
    dane_symulacji['dataZakonczeniaInicjatoraPozytywnego'] = dataZakonczeniaInicjatoraPozytywnego


def dezaktywujInicjatorPozytywnyPoZakonczeniu():
    while True:
        time.sleep(60)  # testowo
        print("Sprawdzam inicjatory pozytywne do dezaktywacji")
        if dane_symulacji['dataZakonczeniaInicjatoraPozytywnego'] is not None and datetime.datetime.now() >= dane_symulacji['dataZakonczeniaInicjatoraPozytywnego']:
            print("rozpoczęto dezaktywację inicjatorów pozytywnych")
            klucze_do_dezaktywacji = list(dane_symulacji['inicjatoryRuchu'].keys())  # Tworzenie kopii kluczy
            for key in klucze_do_dezaktywacji:
                print("dezaktywuję inicjator pozytywny", key)
                dezaktywujInicjator(key)
            aktywujDomyslnyInicjator()
        else:
            print("nie dezaktywuję inicjatorów pozytywnych")
            pass
    

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


def cyklicznieLosujInicjatorNegatywny(unikalnoscInicjatora):
    while True:
        if dane_symulacji['inicjatoryRuchuNegatywne']:
            print("Aktywny negatywny inicjator - nie losuję")
            time.sleep(15) #testowow time.sleep(1300)
        else:
            print("Incijator negatywny nie aktywny - sprawdzam warunki do losowania")
            if datetime.datetime.now().hour > 4 and datetime.datetime.now().hour < 23:
                print("rozpoczęto losowanie inicjatora negatywnego po unikalności")
                if losujInicjatorNegatywnyPoUnikalnosc(unikalnoscInicjatora) == False:
                    print("odwleczenie w czasie losowania inicjatora negatywnego")
                    losowaWartosc = 15 # testowo random.randint(1100, 2100)
                    time.sleep(losowaWartosc)
            else:
                print("poza godzinami pracy - nie losuję")
                time.sleep(1800)


def losujInicjatorNegatywnyPoUnikalnosc(unikalnoscInicjatora):
    losowaWartosc = 1 # testowo random.randint(1, 3) # testowo wskazana 100% szansa na aktywację
    #testowo unikalnoscInicjatora = ["normalny"] * 10 + ["rzadki"] * 4 + ["unikalny"] * 2
    wylosowanaUnikalnosc = "rzadki"  # testowo random.choice(unikalnoscInicjatora)
    if losowaWartosc == 1: 
        keyDoAktywacji, valueDoAktywacji = wybierzInicjatorRuchuNegatywnyZListy(None, wylosowanaUnikalnosc) # testowo wskazany konkretny inicjator negatywny
        if keyDoAktywacji is not None and valueDoAktywacji is not None:
            print('rozpoczęto aktywację inicjatora negatywnego po unikalności')
            aktywujInicjatorRuchuNegatywny(keyDoAktywacji, valueDoAktywacji)
        else:
            print('nie znaleziono inicjatora negatywnego po unikalności')
            pass
    else:
        print("losowanie zakończone negatywnie")
        return False
    

def wybierzInicjatorRuchuNegatywnyZListy(nazwaInicjatora=None, unikalnoscInicjatora=None):
    inicjatoryRuchu = pobierzInicjatoryRuchuNegatywneJSON()
    if nazwaInicjatora is not None:
        for key, value in inicjatoryRuchu.items():
            if nazwaInicjatora == key:
                print("znaleziono inicjator negatywny po nazwie:", key)
                return key, value
    elif unikalnoscInicjatora is not None:
        klucze_do_wylosowania = []
        for key, value in inicjatoryRuchu.items():
            if unikalnoscInicjatora == value.get('unikalnosc'):
                klucze_do_wylosowania.append(key)
                print("znaleziono inicjator negatywny po rodzaju:", unikalnoscInicjatora)
        if len(klucze_do_wylosowania) > 0:
            key = random.choice(klucze_do_wylosowania)
            return key, inicjatoryRuchu[key]
    print("nie znaleziono inicjatora negatywnego")
    return None, None

# funkcja do rozbudowania o kolejne inicjatory negatywne
def aktywujInicjatorRuchuNegatywny(key, value):
    print("uruchomiono inicjator negatywny", key)
    dane_symulacji['inicjatoryRuchuNegatywne'][key] = value
    liczbaPaneliWezwaniaPietra = value.get('awariaKierunkuJazdy') # 0 - nie ma awarii,  > 0 - liczba pięter ulegających awarii
    if liczbaPaneliWezwaniaPietra is not None:
        print("uruchamiany inicjator negatywny", key, "dla piętra")
        wylosujPietroDoWylaczeniaZGenerowaniaPasazerow(liczbaPaneliWezwaniaPietra, key) # losowanie piętra, które ulegnie awarii
    liczbaPrzyciskowWyboruPietra = value.get('awariaWybraniaPietra') # 0 - nie ma awarii,  > 0 - liczba przycisków ulegających awarii
    if liczbaPrzyciskowWyboruPietra is not None:
        print("uruchamiany inicjator negatywny", key, "dla panelu windy")
        wylosujPrzyciskiDoWylaczeniaZWybierania(liczbaPrzyciskowWyboruPietra, key) # TO DO: do zrobienia wyłączanie wybrania piętra


def dezaktywujInicjatorNegatywny(kluczZdarzenia): 
    print("rozpoczęto dezaktywację inicjatora negatywnego")
    if kluczZdarzenia in dane_symulacji['inicjatoryRuchuNegatywne']:
        awariaKierunkuJazdy = dane_symulacji['inicjatoryRuchuNegatywne'][kluczZdarzenia].get('awariaKierunkuJazdy', [])
        wylaczone_pietra['słownik'] = [x for x in wylaczone_pietra['słownik'] if x not in awariaKierunkuJazdy]
        dane_symulacji['inicjatoryRuchuNegatywne'].pop(kluczZdarzenia)
    else:
        print("Klucz zdarzenia nie istnieje w 'inicjatoryRuchuNegatywne'")
        pass


def pobierzInicjatoryRuchuNegatywneJSON():  
    try:
        with open(jsonFilePathInicjatoryRuchuNegatywne, 'r') as json_file:
            print("Plik z inicjatorami negatywnymi istnieje przy wczytaniu")
            return json.load(json_file)
    except FileNotFoundError:
        print("Plik jsonFilePathInicjatoryRuchuNegatywne nie istnieje do wczytania.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Błąd dekodowania JSON: {e}")
        return {}
    

def wylosujPietroDoWylaczeniaZGenerowaniaPasazerow(liczbaPieter, klucz):
    if isinstance(liczbaPieter, list) and len(liczbaPieter) == 1:
        liczbaPieter = liczbaPieter[0]
        losowePietro = random.choice(wlasciwosci_windy['wielkośćSzybu'])
        wylaczone_pietra['słownik'].extend([losowePietro])
        dane_symulacji['inicjatoryRuchuNegatywne'][klucz].update({'awariaKierunkuJazdy': losowePietro})
        if isinstance(dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaKierunkuJazdy'], list):
            dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaKierunkuJazdy'].append(losowePietro)
        else:
            dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaKierunkuJazdy'] = [losowePietro]
    else:
        for x in range(0, liczbaPieter):
            losowePietro = random.choice(wlasciwosci_windy['wielkośćSzybu'])
            wylaczone_pietra['słownik'].extend([losowePietro])
            if isinstance(dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaKierunkuJazdy'], list):
                dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaKierunkuJazdy'].append(losowePietro)
            else:
                dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaKierunkuJazdy'] = [losowePietro]


def wylosujPrzyciskiDoWylaczeniaZWybierania(liczbaPrzyciskow, klucz): # TO DO: do zrobienia wyłączanie wybrania piętra
    if isinstance(liczbaPrzyciskow, list) and len(liczbaPrzyciskow) == 1:
        liczbaPrzyciskow = liczbaPrzyciskow[0]
    for x in range(0, liczbaPrzyciskow):
        losowyPrzycisk = random.choice(wlasciwosci_windy['wielkośćSzybu'])
        wylaczone_przyciski['słownik'][int(losowyPrzycisk)] = 1
        if isinstance(dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaWybraniaPietra'], list):
            dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaWybraniaPietra'].append(losowyPrzycisk)
        else:
            dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaWybraniaPietra'] = [dane_symulacji['inicjatoryRuchuNegatywne'][klucz]['awariaWybraniaPietra'], losowyPrzycisk]

#KOD GENEROWANIA PASAŻERÓW
#___________________________________________________________________________________________________________________________


# 0 - idle, 1 - zmieniony_zdarzeniem, 2 - tbd
def dostosujCzestotliwoscGenerowaniaPasazerow(trybPracy, limitPolecen, zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia):
    while not zatrzymanieSymulacjiPodaży.is_set():
        if trybPracy == 0 and len(windy_data['polecenia']) < limitPolecen: # nowe piętro dodawane jest wtedy kiedy lista zadań pusta
            print("losuj pasażera dla trybu pracy 0", trybPracy)
            losowaWartoscOpoznienia = random.randint(zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia)
            time.sleep(int(losowaWartoscOpoznienia))
            generujPodażPasażerów()
            #dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów'] = sredniRealnyCzasPomiedzyGenerowaniem - do dodania w przyszłości, aby zbierać dane o odstępie
        elif trybPracy == 1 and len(zawartosc_pieter['oczekujacyPasazerowie']) < limitPolecen: # nowe piętro dodawane jest wtedy kiedy lista wzywjących pięter jest mniejsza niż zadana
            print("losuj pasażera dla trybu pracy 1", trybPracy)
            losowaWartoscOpoznienia = random.randint(zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia)
            time.sleep(int(losowaWartoscOpoznienia))
            generujPodażPasażerów()
            #dane_symulacji['zmiennaCzęstotliwościGenerowaniaPasażerów'] = sredniRealnyCzasPomiedzyGenerowaniem - j.w.
        else:
            losowaWartoscOpoznienia = random.randint(zmiennaMinimalnegoOpoznienia, zmiennaMaksymalnegoOpoznienia)
            time.sleep(int(losowaWartoscOpoznienia))
            pass

def generujPodażPasażerów():
    if dane_symulacji.get('wydarzenieStatusSymulacji') == True:
        #time.sleep(definiujCzasZwłokiGenerowaniaPasażerów(dane_symulacji.get('zmiennaCzęstotliwościGenerowaniaPasażerów')))
        liczbaPasazerow = generujLiczbePasazerowNaPiętrze()
        lokalizacjaPasażerów = generujLokalizacjePasazerow()
        celPasazerow = generujCelPasazera(lokalizacjaPasażerów)
        kierunekJazdyPasażerów = zdefiniujKierunekJazdyPasażera(celPasazerow, lokalizacjaPasażerów)
        generujGrupePasazerowNaPietrze(lokalizacjaPasażerów, liczbaPasazerow, celPasazerow, kierunekJazdyPasażerów)
        oznaczWygenerowanychPasazerowJakoNieobsluzonych() # do zmiany jako wydarzenie wątkowe, aby wyświetlać przez jakiś czas tych utraconych posażerów
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
    lokalizacjaPasazerow = random.choices(wlasciwosci_windy['wielkośćSzybu'], weights=dane_symulacji['listaWagPieterDoWzywania'], k=1)[0]
    return lokalizacjaPasazerow


def aktualizujWagiPięterDoWzywania(pietraDoZmiany):
    for key, value in pietraDoZmiany.items():
        dane_symulacji['listaWagPieterDoWzywania'][int(key)] = value


def aktualizujWagiPięterDoWybrania(pietraDoZmiany):
    for key, value in pietraDoZmiany.items():
        dane_symulacji['listaWagPieterDoWybrania'][int(key)] = value


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
            

def oznaczWygenerowanychPasazerowJakoNieobsluzonych():
    for pietra in wylaczone_pietra['słownik']: # weryfikacja czy grupa pasazerow zostala wygenerowana na wyłączonym piętrze
        for grupa_key in list(zawartosc_pieter['oczekujacyPasazerowie'].keys()):
            if zawartosc_pieter['oczekujacyPasazerowie'][grupa_key]['zrodlo'] == pietra:
                for rodzaj, lista in zawartosc_pieter['oczekujacyPasazerowie'][grupa_key]['rodzaje_pasazerow'].items():
                    statystyki['nieobsluzeni_pasazerowie'][f'typ{["normalny", "unikalny", "legendarny"].index(rodzaj) + 1}'] += len(lista)
                zawartosc_pieter['oczekujacyPasazerowie'].pop(grupa_key)


def symulujWybórPięter(celPasazerow):
    global liczbaOczekującychPasażerów
    if dane_symulacji['statusSymulacji'] == 1:
        if wskażPiętro(celPasazerow, 1) != False:
            zapiszWskazanePiętro(celPasazerow, 1)
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


def aktywujZapisywanieStatystyk():
    global wydarzenieZapisywaniaStatystyk
    wydarzenieZapisywaniaStatystyk = True
    threading.Thread(target=zapiszStatystykiOkresowo, daemon=True).start()
    zapisywanieStatystyk.set()

statystyki = odczytajStatystykiJSON()
liczbaPokonanychPięter = statystyki["pokonane_pietra"]
przebytaOdległość = statystyki["przebyta_odleglosc"]
liczbaPrzystanków = statystyki["zaliczone_przystanki"]
liczbaOczekującychPasażerów = statystyki["liczba_oczekujacych_pasazerow"]
