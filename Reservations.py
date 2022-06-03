import numpy as np

class CReservation:
    def __init__(self, data, ID):
        '''
        self._id: id van de reservatie
        self._reservation[17]: reservatierij in df_reservations (ID, Arrival Date, Length of Stay, ...)
        self._bezet[5698]: welke reserveringen al een huis hebben, True als bezet
        self._beschikbaar[819]: 1 als huis kan anders 0(inclusief al ingepland)
        self._data: dataklasse
        self._huis: toegewezen huis
        '''
        if ID > len(data._df_reservations):
            raise NonexistentError(f"Huis met id {ID} bestaat niet, er zijn maar {len(data._df_reservations)} reserveringen")
        self._id = ID
        self._reservation = data._df_reservations.iloc[ID-1,]
        self._data = data
        self._bezet = ((data._assignreservering_tabel[:,1] != 0) + self.overlappende_reservaties() == 2)
        self._beschikbaar = (data._randvoorwaarden * np.invert(self._bezet.transpose()))[:,self._id-1]
        if self._data._df_reservations['Cottage (Fixed)'][self._id - 1] != 0:
            self._huis = self._data._df_reservations['Cottage (Fixed)'][self._id - 1]
        else:
            self._huis = None
    def beschikbare_huizenids(self):
        '''
        return: list met huizen waar reservering kan (ingeplande huizen kunnen niet)
        '''
        voorwaarden_nummers = self._beschikbaar * range(1, len(self._beschikbaar)+1)
        lst_voorwaarden_nummers = list(voorwaarden_nummers)
        mgl_nummers = [nummer for nummer in lst_voorwaarden_nummers if nummer != 0]
        return mgl_nummers
    def geschikte_huizenids(self):
        '''
        return: list met huizen waar reservering kan (ingeplande huizen kunnen wel)
        '''
        voorwaarden_nummers =  (self._data._randvoorwaarden[:,self._id]) * range(1, len(self._beschikbaar)+1)
        lst_voorwaarden_nummers = list(voorwaarden_nummers)
        mgl_nummers = [nummer for nummer in lst_voorwaarden_nummers if nummer != 0]
        return mgl_nummers
    def overlappende_reservaties(self):
        '''
        return
            overlapbools: list met
                True: overlapt wel met de reservatie
                False: overlapt niet met de reservatie
        '''
        arrivalDate = self._reservation['Arrival Date']
        leaveDate = self._reservation['Max Leave Date']
        
        df_overlap = self._data._df_reservations[(leaveDate > self._data._df_reservations['Arrival Date']) & (arrivalDate < self._data._df_reservations['Max Leave Date'])]
        overlapids = df_overlap['ID'].to_list()
        overlapbools = np.array([x in overlapids for x in range(1, len(self._data._df_reservations)+1)])
        return overlapbools
    # def zelfde_begin_reservaties(self):
    #     arrivalDate = self._reservation['Arrival Date']
    #     df_zelfdebegindag = self._data._df_reservations[(self._data._df_reservations['Arrival Date'] > arrivalDate) & (self._data._df_reservations['Max Leave Date'] < arrivalDate)]
    #     mogelijkeids = df_zelfdebegindag['ID'].to_list()
    #     mogelijkehuizen = data._assign
    def reservatie_overlapt(self, reservatie):
        overlappend = self.overlappende_reservaties()
        return overlappend[reservatie-1] 
    def koppel_huis(self, cottage_id):
        self._data._assignreservering_tabel[self._id-1, 1] = cottage_id
        self._data._assignhuis_tabel[cottage_id-1].append(self._id)
        
        eerste_dag = (self._data._df_reservations['Arrival Date'][self._id - 1] - self._data.eerste_planningsdag).days
        laatste_dag = (self._data._df_reservations['Max Leave Date'][self._id - 1] - self._data.eerste_planningsdag).days
        
        for i in range(eerste_dag, laatste_dag):
            self._data._huisbezetting_tijd[cottage_id - 1, i] = self._id
        self._huis = cottage_id

class NonexistentError(Exception):
    pass
