from math import sqrt
import json
import os
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np


class UAR:
    pid = {
        'error': [0, ],  # uchyb regulacji
        'gain': 1.0,  # wartość wzmocnienia regulatora
        'sample_time': 0.05,  # czas próbkowania
        'differential_time': 0.05,  # czas wyprzedzenia
        'integration_time': 0.75,  # czas zdwojenia
        'h_z': [],  # wartość zadana
        'h': [0, ],  # poziom substancji w zbiorniku
    }
    valvee = {
        'u_max': 10,  # wartość max poziomu substancji w zbiorniku
        'u_min': -10,  # wartość min poziomu substancji w zbiorniku
        'u': [0.1, ],  # wartość aktualna sygnału sterującego
        'Q_d_min': 0,  # minimalne natężenie dopływu
        'Q_d_max': 1,  # maksymalne natężenie dopływu
        'Q_d': []  # wartość aktualna natężenia dopływu
    }
    tank = {
        'h_max': 10,  # maksymalny poziom substancji w zbiorniku
        'h_min': 0,  # minimalny poziom substancji w zbiorniku
        'A': 2.5,  # pole powierzchni przekroju poprzecznego zbiornika
        'B': 0.25,  # współczynnik wypływu
        'Q_o': [],  # natężenie odpływu
    }
    fuzzy_pid = {
        'k_e': [],  # uchyb regulacji dla PID rozmytego
        'k_ce': [],  # zmiana uchybu regulacji dla PID rozmytego
        'k_u': [],  # wielkość sterująca dla PID rozmytego
        'y': [[], [], [], [], []],  # macierz dla h, Q_d, Q_o, h_z
        'costFuzzy': 0,  # koszty regulacji
        'qualityFuzzy': 0  # jakość regulacji

    }
    N = 10000
    x = [0, ]

    # JSON
    def ComplexOpenData(self):
        listUAR = []
        with open('static/data/data.json') as json_data:
            data_dict = json.load(json_data)
            for key, value in data_dict.items():
                listUAR.append(value)
        listUAR.remove(listUAR[0])
        listUAR.remove(listUAR[-1])

        self.pid['sample_time'] = float(listUAR[0])
        self.pid['differential_time'] = float(listUAR[1])
        self.pid['integration_time'] = float(listUAR[2])
        self.pid['gain'] = float(listUAR[3])
        self.pid['h_z'].append(float(listUAR[4]))
        self.pid['A'] = float(listUAR[5])
        self.pid['B'] = float(listUAR[6])
        self.pid['h_max'] = int(listUAR[7])
        self.pid['u_max'] = int(listUAR[8])
        self.pid['u_min'] = int(listUAR[9])
        self.pid['Q_d_max'] = int(listUAR[10])

    # PID
    def pid_controler(self):
        self.pid['error'].append((self.pid['h_z'][-1] - self.pid['h'][-1]) / 10)
        self.valvee['u'].append(
            (self.pid['gain'] * (self.pid['error'][-1] + (self.pid['sample_time'] / self.pid['integration_time']) * sum(
                self.pid['error']) + (self.pid['differential_time'] / self.pid['sample_time']) * (
                                             self.pid['error'][1] - self.pid['error'][-1]))) / 10)

    # Zawór
    def valve(self):
        if (self.valvee['u'][-1] <= self.valvee['Q_d_min']):
            self.valvee['Q_d'].append(self.valvee['u_min'])
        elif (self.valvee['u'][-1] >= self.valvee['Q_d_max']):
            self.valvee['Q_d'].append(self.valvee['u_max'])
        else:
            self.valvee['Q_d'].append(self.valvee['u'][-1])

    # Zbiornik
    def tankk(self):
        self.tank['Q_o'].append(self.tank['B'] * sqrt(self.pid['h'][-1]))
        self.pid['h'].append(max(min(((-self.tank['Q_o'][-1] + self.valvee['Q_d'][-1]) * self.pid['sample_time'] /
                                      self.tank['A'] + self.pid['h'][-1]), self.tank['h_max']), self.tank['h_min']))

    # Koszty regulacji
    def costsController(self):

        cost = 0
        result_costs = [abs(ele_c) for ele_c in self.valvee['u']]
        for e in range(0, len(result_costs)):
             cost = cost + result_costs[e]

        return float(str(round((cost/self.N), 2)))

    # Jakość regulacji
    def qualityController(self):

        quality = 0
        result_quality = [abs(ele_q) for ele_q in self.pid['error']]
        for eq in range(0, len(result_quality)):
            quality = quality + result_quality[eq]

        return float(str(round((quality/self.N), 2)))

    def resetData(self):
        self.N = 10000
        self.x = [0, ]
        self.pid['h_z'] = []
        self.pid['h'] = [0, ]
        self.fuzzy_pid['y'] = [[], [], [], [], []]

    def count(self):
        self.ComplexOpenData()
        for n in range(0, self.N):
            self.x.append(obiekt.pid['sample_time'] * n)
            self.pid['h_z'].append(obiekt.pid['h_z'][-1])
            self.pid_controler()
            self.valve()
            self.tankk()
            self.costsController()
            self.qualityController()
        filePath = '/static/data/data_x.json'
        if os.path.exists(filePath):
            os.remove(filePath)
        else:
            jsonList = []
            for i in range(0, len(self.x)):
                jsonList.append({"x": float(round(self.x[i],2)), "h_z": self.pid['h_z'][i], "h": self.pid['h'][i],
                                 "Q_d": self.valvee['Q_d'][i-1], "Q_o": self.tank['Q_o'][i-1],
                                 "e": self.pid['error'][i]})
            with open('static/data/data_x.json', 'w') as d_x:
                json.dump(jsonList, d_x)
            d_x.close()

    def FUZZY(self):
        self.ComplexOpenData()

        ins = ['DU', 'SU', 'MU', 'Z', 'MD', 'SD', 'DD']
        outs = ['BDU', 'DU', 'SU', 'MU', 'Z', 'MD', 'SD', 'DD', 'BDD']

        e = ctrl.Antecedent(np.arange(-1, 1, 0.01), 'e')
        ce = ctrl.Antecedent(np.arange(-1, 1, 0.01), 'ce')
        cu = ctrl.Consequent(np.arange(-1, 1, 0.01), 'cu')

        e['DU'] = fuzz.trimf(e.universe, [-1.3, -1, -0.667])
        e['SU'] = fuzz.trimf(e.universe, [-1, -0.667, -0.333])
        e['MU'] = fuzz.trimf(e.universe, [-0.667, -0.333, 0.0])
        e['Z'] = fuzz.trimf(e.universe, [-0.333, 0.0, 0.333])
        e['MD'] = fuzz.trimf(e.universe, [0.0, 0.333, 0.667])
        e['SD'] = fuzz.trimf(e.universe, [0.333, 0.667, 1])
        e['DD'] = fuzz.trimf(e.universe, [0.667, 1, 1.33])

        ce['DU'] = fuzz.trimf(ce.universe, [-1.3, -1, -0.667])
        ce['SU'] = fuzz.trimf(ce.universe, [-1, -0.667, -0.333])
        ce['MU'] = fuzz.trimf(ce.universe, [-0.667, -0.333, 0.0])
        ce['Z'] = fuzz.trimf(ce.universe, [-0.333, 0.0, 0.333])
        ce['MD'] = fuzz.trimf(ce.universe, [0.0, 0.333, 0.667])
        ce['SD'] = fuzz.trimf(ce.universe, [0.333, 0.667, 1])
        ce['DD'] = fuzz.trimf(ce.universe, [0.667, 1, 1.33])

        cu['BDU'] = fuzz.trimf(cu.universe, [-1.25, -1, -0.75])
        cu['DU'] = fuzz.trimf(cu.universe, [-1, -0.75, -0.5])
        cu['SU'] = fuzz.trimf(cu.universe, [-0.75, -0.5, -0.25])
        cu['MU'] = fuzz.trimf(cu.universe, [-0.5, -0.25, 0])
        cu['Z'] = fuzz.trimf(cu.universe, [-0.25, 0.0, 0.25])
        cu['MD'] = fuzz.trimf(cu.universe, [0, 0.25, 0.5])
        cu['SD'] = fuzz.trimf(cu.universe, [0.25, 0.5, 0.75])
        cu['DD'] = fuzz.trimf(cu.universe, [0.5, 0.75, 1])
        cu['BDD'] = fuzz.trimf(cu.universe, [0.75, 1, 1.25])

        # BDU
        rules = [ctrl.Rule(e[ins[0]] & ce[ins[0]], cu[outs[0]])]
        rules.append(ctrl.Rule(e[ins[1]] & ce[ins[0]], cu[outs[0]]))
        rules.append(ctrl.Rule(e[ins[0]] & ce[ins[1]], cu[outs[0]]))
        rules.append(ctrl.Rule(e[ins[1]] & ce[ins[1]], cu[outs[0]]))
        rules.append(ctrl.Rule(e[ins[2]] & ce[ins[0]], cu[outs[0]]))
        rules.append(ctrl.Rule(e[ins[0]] & ce[ins[2]], cu[outs[0]]))
        # DU
        rules.append(ctrl.Rule(e[ins[3]] & ce[ins[0]], cu[outs[1]]))
        rules.append(ctrl.Rule(e[ins[2]] & ce[ins[1]], cu[outs[1]]))
        rules.append(ctrl.Rule(e[ins[1]] & ce[ins[2]], cu[outs[1]]))
        rules.append(ctrl.Rule(e[ins[0]] & ce[ins[3]], cu[outs[1]]))
        # SU
        rules.append(ctrl.Rule(e[ins[0]] & ce[ins[4]], cu[outs[2]]))
        rules.append(ctrl.Rule(e[ins[1]] & ce[ins[3]], cu[outs[2]]))
        rules.append(ctrl.Rule(e[ins[2]] & ce[ins[2]], cu[outs[2]]))
        rules.append(ctrl.Rule(e[ins[3]] & ce[ins[1]], cu[outs[2]]))
        rules.append(ctrl.Rule(e[ins[4]] & ce[ins[0]], cu[outs[2]]))
        # MU
        rules.append(ctrl.Rule(e[ins[5]] & ce[ins[0]], cu[outs[3]]))
        rules.append(ctrl.Rule(e[ins[4]] & ce[ins[1]], cu[outs[3]]))
        rules.append(ctrl.Rule(e[ins[3]] & ce[ins[2]], cu[outs[3]]))
        rules.append(ctrl.Rule(e[ins[2]] & ce[ins[3]], cu[outs[3]]))
        rules.append(ctrl.Rule(e[ins[1]] & ce[ins[4]], cu[outs[3]]))
        rules.append(ctrl.Rule(e[ins[0]] & ce[ins[5]], cu[outs[3]]))
        # Z
        rules.append(ctrl.Rule(e[ins[0]] & ce[ins[6]], cu[outs[4]]))
        rules.append(ctrl.Rule(e[ins[1]] & ce[ins[5]], cu[outs[4]]))
        rules.append(ctrl.Rule(e[ins[2]] & ce[ins[4]], cu[outs[4]]))
        rules.append(ctrl.Rule(e[ins[3]] & ce[ins[3]], cu[outs[4]]))
        rules.append(ctrl.Rule(e[ins[4]] & ce[ins[2]], cu[outs[4]]))
        rules.append(ctrl.Rule(e[ins[5]] & ce[ins[1]], cu[outs[4]]))
        rules.append(ctrl.Rule(e[ins[6]] & ce[ins[0]], cu[outs[4]]))
        # MD
        rules.append(ctrl.Rule(e[ins[1]] & ce[ins[6]], cu[outs[5]]))
        rules.append(ctrl.Rule(e[ins[2]] & ce[ins[5]], cu[outs[5]]))
        rules.append(ctrl.Rule(e[ins[3]] & ce[ins[4]], cu[outs[5]]))
        rules.append(ctrl.Rule(e[ins[4]] & ce[ins[3]], cu[outs[5]]))
        rules.append(ctrl.Rule(e[ins[5]] & ce[ins[2]], cu[outs[5]]))
        rules.append(ctrl.Rule(e[ins[6]] & ce[ins[1]], cu[outs[5]]))
        # SD
        rules.append(ctrl.Rule(e[ins[6]] & ce[ins[2]], cu[outs[6]]))
        rules.append(ctrl.Rule(e[ins[5]] & ce[ins[3]], cu[outs[6]]))
        rules.append(ctrl.Rule(e[ins[4]] & ce[ins[4]], cu[outs[6]]))
        rules.append(ctrl.Rule(e[ins[3]] & ce[ins[5]], cu[outs[6]]))
        rules.append(ctrl.Rule(e[ins[2]] & ce[ins[6]], cu[outs[6]]))
        # DD
        rules.append(ctrl.Rule(e[ins[3]] & ce[ins[6]], cu[outs[7]]))
        rules.append(ctrl.Rule(e[ins[4]] & ce[ins[5]], cu[outs[7]]))
        rules.append(ctrl.Rule(e[ins[5]] & ce[ins[4]], cu[outs[7]]))
        rules.append(ctrl.Rule(e[ins[6]] & ce[ins[3]], cu[outs[7]]))
        # BDD
        rules.append(ctrl.Rule(e[ins[6]] & ce[ins[4]], cu[outs[8]]))
        rules.append(ctrl.Rule(e[ins[5]] & ce[ins[5]], cu[outs[8]]))
        rules.append(ctrl.Rule(e[ins[4]] & ce[ins[6]], cu[outs[8]]))
        rules.append(ctrl.Rule(e[ins[6]] & ce[ins[5]], cu[outs[8]]))
        rules.append(ctrl.Rule(e[ins[5]] & ce[ins[6]], cu[outs[8]]))
        rules.append(ctrl.Rule(e[ins[6]] & ce[ins[6]], cu[outs[8]]))

        cu_ctrl = ctrl.ControlSystem(rules)
        reg_cu = ctrl.ControlSystemSimulation(cu_ctrl)

        # h, Q_d, Q_o, h_z
        temp = [0]

        self.fuzzy_pid['y'][0].append(0)
        self.fuzzy_pid['y'][1].append(self.pid['h'][0])
        self.fuzzy_pid['y'][2].append(self.valvee['Q_d'][0])
        self.fuzzy_pid['y'][3].append((self.tank['B']) * (sqrt(self.pid['h'][0])))
        self.fuzzy_pid['y'][4].append(self.pid['h_z'][0])
        e_delay = 0
        self.fuzzy_pid['k_u'] = self.valvee['u']

        for x in range(1, self.N):

            self.fuzzy_pid['k_e'].append(self.pid['gain'] / self.fuzzy_pid['k_u'][-1])
            self.fuzzy_pid['k_ce'].append(
                (self.pid['differential_time'] / self.pid['sample_time']) / self.fuzzy_pid['k_u'][-1])

            e = self.pid['h_z'][x] - self.fuzzy_pid['y'][1][x - 1]
            ke = e * (1 / self.fuzzy_pid['k_e'][-1])
            temp.append(ke)
            if e > 1:
                e = 1
            elif e < -1:
                e = -1

            ce = e - e_delay
            ce *= (1 / obiekt.pid['sample_time'])
            ce *= (1 / self.fuzzy_pid['k_ce'][-1])
            if ce > 1:
                ce = 1
            elif ce < -1:
                ce = -1

            reg_cu.input['e'] = e
            reg_cu.input['ce'] = ce
            reg_cu.compute()
            cu = reg_cu.output['cu']
            self.fuzzy_pid['k_u'].append(cu * self.pid['sample_time'] + self.fuzzy_pid['k_u'][-1])

            self.valvee['Q_d'][x] = self.fuzzy_pid['k_u'][1] * self.fuzzy_pid['k_u'][-1]

            if (self.valvee['Q_d'][x] > self.valvee['Q_d_max']):
                self.valvee['Q_d'][x] = self.valvee['Q_d_max']
            elif (self.valvee['Q_d'][x] < self.valvee['Q_d_min']):
                self.valvee['Q_d'][x] = self.valvee['Q_d_min']

            self.fuzzy_pid['y'][0].append((x) * obiekt.pid['sample_time'])
            self.fuzzy_pid['y'][2].append(self.valvee['Q_d'][x])
            self.fuzzy_pid['y'][3].append(self.tank['B'] * (sqrt(self.fuzzy_pid['y'][1][x - 1])))
            self.fuzzy_pid['y'][1].append(((self.fuzzy_pid['y'][2][x] - self.fuzzy_pid['y'][3][x]) * obiekt.pid['sample_time']) / self.tank['A'] + self.fuzzy_pid['y'][1][x - 1])
            self.fuzzy_pid['y'][4].append(self.pid['h_z'][x])

            e_delay = e

    # Koszty regulacji
    def costsControllerFuzzy(self):
        cost_fuzzy = 0
        result_costsf = [abs(ele_cf) for ele_cf in self.fuzzy_pid['k_u']]
        for ele in range(0, len(result_costsf)):
             cost_fuzzy = cost_fuzzy + result_costsf[ele]
        return float(str(round((cost_fuzzy/self.N), 2)))

    # Jakość regulacji
    def qualityControllerFuzzy(self):

        quality_fuzzy = 0
        result_qualities = [abs(ele_qf) for ele_qf in self.fuzzy_pid['k_e']]
        for el in range(0, len(result_qualities)):
            quality_fuzzy = quality_fuzzy + result_qualities[el]

        return float(str(round((quality_fuzzy/self.N), 2)))

    def FuzzyDisplay(self):
        self.FUZZY()
        self.costsControllerFuzzy()
        self.qualityControllerFuzzy()
        fuzzyfilePath = '/static/data/data_fuzzy.json'
        if os.path.exists(fuzzyfilePath):
            os.remove(fuzzyfilePath)
        else:
            jsonListFuzzy = []
            for i in range(0, (len(self.x)-1)):
                jsonListFuzzy.append({"x": float(round(self.fuzzy_pid['y'][0][i],2)), "h_z": self.fuzzy_pid['y'][4][i], "h": self.fuzzy_pid['y'][1][i],
                                      "Q_d": self.fuzzy_pid['y'][2][i], "Q_o": self.fuzzy_pid['y'][3][i],
                                      "e": self.fuzzy_pid['k_e'][i-1]})
            with open('static/data/data_fuzzy.json', 'w') as d_fuzzy:
                json.dump(jsonListFuzzy, d_fuzzy)
            d_fuzzy.close()
        self.resetData()

obiekt = UAR()
