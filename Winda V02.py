polecenia = [4, 2]
kierunekJazdy = 1 # gdzie: 0 to postój, 1 - to dół, 2 to góra
lokalizacjaWindy = 8

def wskażPiętro(wskażPozycję):
    nowePolecenie = int(input("podaj numer piętra: "))
    print(polecenia)
    if sprawdźCzyDubel(nowePolecenie) == False:
        pozycja = wyliczPozycję(nowePolecenie) # sprawdzenie docelowej pozycji polecenia na liście poleceń
        if pozycja is not None:
            polecenia.insert(pozycja, nowePolecenie) # umieszcza sprawdzone piętro do listy poleceń
            print(polecenia)
        else:
            return 
            print(polecenia)
    else:
        print(polecenia)
    
def wyliczPozycję(sprawdzanePiętro): # sprawdza pozycję piętra na liście poleceń
    global lokalizacjaWindy
    global kierunekJazdy
    global polecenia
    if kierunekJazdy == 1: #jazda w dół POPRAWIĆ ALGORYTM DLA JAZDY W DÓŁ - NA WZÓR TEGO DO GÓRY
        if lokalizacjaWindy > sprawdzanePiętro: #winda powyżej nowego polecenia
            piętroMax = 0
            piętroMin = 999
            for x in polecenia:
                if x > piętroMax:
                    piętroMax = x
                if x < piętroMin:
                    piętroMin = x
                print("piętro Max:", piętroMax, 'piętro Min:', piętroMin)
            print(polecenia)
            for y in polecenia:
                if polecenia[0] == y:
                    pass
                else:
                    pozycjaPoprzedniejPozycji = (polecenia.index(y) - 1)
                    if polecenia.index(y) == len(polecenia) - 1:
                        pozycjaNastępnejPozycji = len(polecenia) - 1
                    else:
                        pozycjaNastępnejPozycji = (polecenia.index(y) + 1)
                    print('poprzednia:', pozycjaPoprzedniejPozycji, 'następna', pozycjaNastępnejPozycji)
                    if 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro > polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro > polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro > piętroMax: 
                        print('warunek a3')
                        return polecenia.index(piętroMax) # dodaj przed największym piętrem
                    elif 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro < polecenia[pozycjaPoprzedniejPozycji] and (sprawdzanePiętro > polecenia[pozycjaNastępnejPozycji] or sprawdzanePiętro < polecenia[pozycjaNastępnejPozycji]) and sprawdzanePiętro < piętroMax and sprawdzanePiętro > y: 
                        print('warunek b3')
                        return polecenia.index(y) # dodaj po sprawdzanym piętrze
                    elif 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro > polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro < polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro < piętroMax and sprawdzanePiętro > y: 
                        print('warunek c3')
                        return polecenia.index(y) + 1 # dodaj jako następne po sprawdzanym piętrze
                    if sprawdzanePiętro < piętroMin: 
                        print('warunek d3')
                        return len(polecenia) #  dodaj jako ostatnie jeśli najmniejsze ze wszystkich
                    else:
                        print('warunek e3')
                        pass
        elif lokalizacjaWindy < sprawdzanePiętro: #winda poniżej nowego polecenia
            piętroMax = 0
            piętroMin = 999
            for x in polecenia:
                if x > piętroMax:
                    piętroMax = x
                if x < piętroMin:
                    piętroMin = x
                print(piętroMax, piętroMin)
            if piętroMin == polecenia[-1] or polecenia[-1] <= sprawdzanePiętro: # dodaj na końcu jeśli polecenie większe niż ostatnie
                return x 
            else:
                for y in polecenia:
                    if polecenia[0] == y:
                        pass
                    else:
                        pozycjaPoprzedniejPozycji = (polecenia.index(y) - 1)
                        pozycjaNastępnejPozycji = (polecenia.index(y))
                        print(pozycjaPoprzedniejPozycji, pozycjaNastępnejPozycji)
                        if 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro > polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro < polecenia[pozycjaNastępnejPozycji]: # dodaj pomiędzy mniejszą a większą
                            return pozycjaNastępnejPozycji
                        else:
                            pass
    elif kierunekJazdy == 2: #jazda do góry
        if lokalizacjaWindy < sprawdzanePiętro: #winda poniżej nowego polecenia
            piętroMax = 0
            piętroMin = 999
            for x in polecenia:
                if x > piętroMax:
                    piętroMax = x
                if x < piętroMin:
                    piętroMin = x
                print("piętro Max:", piętroMax, 'piętro Min:', piętroMin)
            print(polecenia)
            for y in polecenia:
                if polecenia[0] == y:
                    pass
                else:
                    pozycjaPoprzedniejPozycji = (polecenia.index(y) - 1)
                    if polecenia.index(y) == len(polecenia) - 1:
                        pozycjaNastępnejPozycji = len(polecenia) - 1
                    else:
                        pozycjaNastępnejPozycji = (polecenia.index(y) + 1)
                    print('poprzednia:', pozycjaPoprzedniejPozycji, 'następna', pozycjaNastępnejPozycji)
                    if 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro > polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro > polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro > piętroMax: 
                        print('warunek a1')
                        return polecenia.index(piętroMax) + 1 # dodaj po największym piętrze
                    elif 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro > polecenia[pozycjaPoprzedniejPozycji] and (sprawdzanePiętro < polecenia[pozycjaNastępnejPozycji] or sprawdzanePiętro > polecenia[pozycjaNastępnejPozycji]) and sprawdzanePiętro < piętroMax and sprawdzanePiętro < y: 
                        print('warunek b1')
                        return polecenia.index(y) # dodaj po sprawdzanym piętrze
                    elif 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro > polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro < polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro < piętroMax and sprawdzanePiętro > y: 
                        print('warunek c1')
                        return polecenia.index(y) + 1 # dodaj jako następne po sprawdzanym piętrze
                    if sprawdzanePiętro < piętroMin: 
                        print('warunek d1')
                        return 0 #  dodaj jako pierwsze jeśli najmniejsze ze wszystkich
                    else:
                        print('warunek e1')
                        pass
        elif lokalizacjaWindy > sprawdzanePiętro: #winda powyżej nowego polecenia
            piętroMax = 0
            piętroMin = 999
            for x in polecenia:
                if x > piętroMax:
                    piętroMax = x
                if x < piętroMin:
                    piętroMin = x
                print("piętro Max:", piętroMax, 'piętro Min:', piętroMin)
            print(polecenia)
            for y in polecenia:
                if polecenia[0] == y:
                    pass
                else:
                    pozycjaPoprzedniejPozycji = (polecenia.index(y) - 1)
                    if polecenia.index(y) == len(polecenia) - 1:
                        pozycjaNastępnejPozycji = len(polecenia) - 1
                    else:
                        pozycjaNastępnejPozycji = (polecenia.index(y) + 1)
                    print('poprzednia:', pozycjaPoprzedniejPozycji, 'następna', pozycjaNastępnejPozycji)
                    if 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro < polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro < polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro < piętroMin: 
                        print('warunek a2')
                        return polecenia.index(piętroMin) + 1 # dodaj po najmniejszym piętrze
                    elif 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro < polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro > polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro < piętroMax and sprawdzanePiętro > y: 
                        print('warunek b2')
                        return polecenia.index(y) # dodaj po sprawdzanym piętrze
                    elif 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro < polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro > polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro < piętroMax and sprawdzanePiętro < y: 
                        print('warunek c2')
                        return polecenia.index(y) + 1 # dodaj jako następne po sprawdzanym piętrze
                    if sprawdzanePiętro < piętroMin: 
                        print('warunek d2')
                        return len(polecenia) #  dodaj jako ostatnie jeśli najmniejsze ze wszystkich
                    else:
                        print('warunek e2')
                        pass
    return

"""
            for y in polecenia:
                if polecenia[0] == y:
                    pass
                else:
                    pozycjaPoprzedniejPozycji = (polecenia.index(y) - 1)
                    if polecenia.index(y) == len(polecenia) - 1:
                        pozycjaNastępnejPozycji = len(polecenia) - 1
                    else:
                        pozycjaNastępnejPozycji = (polecenia.index(y) + 1)
                    print('poprzednia:', pozycjaPoprzedniejPozycji, 'następna', pozycjaNastępnejPozycji)
                    if 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro < polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro < polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro < piętroMin: 
                        print('warunek a2')
                        return polecenia.index(piętroMin) + 1 # dodaj po najmniejszym piętrze
                    elif 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro < polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro > polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro < piętroMax and sprawdzanePiętro > y: 
                        print('warunek b2')
                        return polecenia.index(y) # dodaj po sprawdzanym piętrze
                    elif 0 <= pozycjaPoprzedniejPozycji < len(polecenia) and 0 <= pozycjaNastępnejPozycji < len(polecenia) and sprawdzanePiętro < polecenia[pozycjaPoprzedniejPozycji] and sprawdzanePiętro > polecenia[pozycjaNastępnejPozycji] and sprawdzanePiętro < piętroMax and sprawdzanePiętro < y: 
                        print('warunek c2')
                        return polecenia.index(y) + 1 # dodaj jako następne po sprawdzanym piętrze
                    if sprawdzanePiętro > piętroMax: 
                        print('warunek d2')
                        return 0 #  dodaj jako pierwsze jeśli największe ze wszystkich
                    else:
                        print('warunek e2')
                        pass
"""




def sprawdźCzyDubel(nowePolecenie):
    global lokalizacjaWindy
    for x in polecenia:
        if x == nowePolecenie or nowePolecenie == lokalizacjaWindy:
            print('dubel')
            return True
        else:
            pass
    return False 


while True:
    wskażPiętro(0)