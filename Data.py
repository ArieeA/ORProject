import pandas as pd
import datetime
import numpy as np
from random import randint

class CData:
    _instance = None
    def __new__(cls, excelfile_path):
        if not cls._instance:
            cls._instance = cls._CData(excelfile_path)
        return cls._instance
    class _CData:
        def __init__(self, excelfile_path):
            '''
            self._df_cottages: cottages dataframe
            self._df_reservations: reservations dataframe
            self._assignreservering_tabel: id van reservering met toegegeven cottage
            self._assignhuis_tabel: huis met reserveringen die in de periode plaats zullen vinden
            self._huisbezetting_tijd: cottage_id-1 x dagen na eerste planningsdag. Als ingepland staat in de (huis, dag) de geplande reservering
            self._randvoorwaarden: aantal cottages x aantal reserveringen, zie maak_mglarr
            '''
            self._path = excelfile_path
            self._df_cottages = pd.read_excel(io = excelfile_path, sheet_name = 0)
            self._df_reservations = pd.read_excel(io=excelfile_path, sheet_name = 1)
            self._df_reservations['Max Leave Date'] = self._df_reservations['Arrival Date'] + self._df_reservations['Length of Stay'].apply(datetime.timedelta)
            self._assignreservering_tabel = self._df_reservations.reset_index()[['ID', 'Cottage (Fixed)']].to_numpy()
            self._assignhuis_tabel = [[] for x in range(len(self._df_cottages))]
            self._huisbezetting_tijd = np.array([[None]*(self._df_reservations['Max Leave Date'].max() - self._df_reservations['Arrival Date'].min()).days]*len(self._df_cottages))
            self._randvoorwaarden = self.maak_mglarr()
            
        @property
        def aantal_huizen(self):
            return len(self._df_cottages)
        @property
        def aantal_reserveringen(self):
            return len(self._df_reservations)
        @property
        def eerste_planningsdag(self):
            return self._df_reservations['Arrival Date'].min()
        @property
        def cottages(self):
            return self._df_cottages
        @property
        def reservations(self):
            return self._df_reservations
        
        def huis_van_reservering(self, reservering):
            return self._assignreservering_tabel[reservering-1,1]
        
        def allevoorwaarden(self):
            '''
            Zet 'Cottages'-sheet en 'Reservations'-sheet om in arrays en voer maak_mglarr uit
            
            Returns
            -------
            arr_allevoorwaarden(aantal cottages x aantal reserveringen) : np.array
                0: De reservering kan niet in het huis plaatsvinden
                1: De reservering kan wel in het huis plaatsvinden
            '''
            
            #Dag dat ze weggaan
            
            arr_reservations = self._df_reservations.to_numpy(dtype = int, copy = True)
            arr_cottages = self._df_cottages.to_numpy(dtype = int, copy = True)
            return {'arr_reservations':arr_reservations, 'arr_cottages':arr_cottages}
        def maak_mglarr(self):
            '''
        
            Parameters
            ----------
            arr_reservations(aantal reserveringen x attributen) : np.array
                Reservations sheet als een array
            arr_cottages(aantal cottages x attributen): np.array
                Cottages sheet als een array
                
            max # pers[0], class[1], face south[2], near playground[3], close to the centre[4], near lake[5],
            near car park[6], accessible for wheelchair[7], child friendly[8], dish washer[9], wi-fi coverage[10],
            covered terrace[11]
        
            Returns
            -------
            arr_allevoorwaarden(aantal cottages x aantal reserveringen) : np.array
                0: De reservering kan niet in het huis plaatsvinden
                1: De reservering kan wel in het huis plaatsvinden
        
            '''
            reservation_indexes = list(range(2, 14))
            cottages_indexes = list(range(0, 12))
            #groter_dan = [1, 1] + [1] * (len(reservation_indexes) - 2)
            
            arr_cottages = self.allevoorwaarden()['arr_cottages']
            arr_reservations = self.allevoorwaarden()['arr_reservations']
            
            arr_klasseover = np.zeros(shape = (len(arr_cottages), len(arr_reservations)))
            #Meegenomen restricties
                #- Max aantal personen
                #- Klasse
                #- Voorkeuren
            for i in range(len(reservation_indexes)):
                r_index = reservation_indexes[i]
                c_index = cottages_indexes[i]
                res_i = arr_reservations[:,r_index]
                cot_i = arr_cottages[:,c_index]
                #if groter_dan[i]:
                bleqa = cot_i[:, np.newaxis].astype(int) >= res_i
                arr_klasseover = (bleqa + arr_klasseover).astype(int)
            
            arr_allevoorwaarden = (arr_klasseover == len(reservation_indexes)).astype(int)
            return arr_allevoorwaarden        
        def reset_reserveringen(self):
            '''
            Maak een nieuwe init aan. Hierdoor worden alle geregistreerde reserveringen verwijdert
            '''
            self.__init__(self._path)
