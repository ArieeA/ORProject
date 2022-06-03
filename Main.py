from random import randint
import time
from Data import CData
from Reservations import CReservation

class CMain:
    '''
    klasse waarin alles wordt uitgevoerd bij de methode plan_reservering(reservering_id)
    Vul overal in. Als niet mogelijk return 'None'
    '''
    def __init__(self):
        self._data = CData(r"C:\Users\arent\Documents\Toegepaste Wiskunde\Jaar 2\Blok 34\OR-Project\El Orteca Resorts - Dataset 2.xlsx")
        self._df_reservations = self._data.reservations
        self._df_cottages = self._data.cottages
        self._assignreservering_tabel = self._df_reservations.reset_index()[['ID', 'Cottage (Fixed)']].to_numpy()
    def plan_reservering(self, reservering_id):
        reservering = CReservation(self._data, reservering_id)
        mogelijkheden = reservering.beschikbare_huizenids()
        if mogelijkheden:
            cottage_id = mogelijkheden[0]
            reservering.koppel_huis(cottage_id)
            return cottage_id
            print(f"Reservering {i} is ingedeelt op huis {cottage_id}")
        else:
            print(f"Kan niet voor {reservering_id}\n--------------------\n--------------------")
            return None
        
if __name__ == "__main__":
    start = time.localtime()
    main = CMain()
    data = CData(r"C:\Users\arent\Documents\Toegepaste Wiskunde\Jaar 2\Blok 34\OR-Project\El Orteca Resorts - Dataset 2.xlsx")
    data.reset_reserveringen()
    
    for i in range(1, len(data.reservations)+1):
        if CReservation(data, i)._huis != 0:
            continue
        else:
            cottage_id = main.plan_reservering(i)
    reserveringen = data._assignreservering_tabel
    duur = time.localtime()
    missers = sum(data._assignreservering_tabel[:,1] == 0)
