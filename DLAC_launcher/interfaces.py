from epics import PV

class multiplePV(object):
    '''
    A class describing a collection of PVs.
    Implements the destructor to disconnect the PVs
    '''

    pvList = []

    def __del__(self):
        try:
            for pv in self.pvList:
                pv.disconnect()
        except Exception as e:
            print('Warning: destructor not working correctly')
            print(e)
        pass

class magnetWithRB(multiplePV):
    '''A class for power supply with readback'''
    def __init__(self, name):
        '''TODO: add limits for setting'''
        self.mainName = name
        self.pv_I = PV(self.mainName + ':I-SET')
        self.pv_Irb = PV(self.mainName + ':I-READ')
        self.pvON = PV(self.mainName + ':')
        self.pvList = [self.pv_I, self.pv_Irb, self.pvON]

    @property
    def I(self):
        return self.pv_Irb.value
    @I.setter
    def I(self, value):
        self.pv_I.value = value

    # Silly methods for pyqt
    def setI(self, value):
        self.I = value

class Corrector(magnetWithRB):

    def __init__(self, cname):
        super().__init__(cname)

class Quadrupole(magnetWithRB):
    '''A class describing a quadrupole'''

    def __init__(self, qname):
        '''
        TODO: insert the right endings for the PVs
        TODO: add on/off control
        TODO: add status
        '''
        super().__init__(qname)
        self.pv_B = PV(self.mainName + ':BP-SET'); self.pvList.append(self.pv_B)
        self.pv_Brb = PV(self.mainName + ':BP-READ'); self.pvList.append(self.pv_Brb)
        self.pv_Dirty = PV(self.mainName + ':CYCLE-STATE'); self.pvList.append(self.pv_Dirty)
        self.pv_Energy = PV(self.mainName + ':ENERGY'); self.pvList.append(self.pv_Energy)
        self.pv_Cycle = PV(self.mainName + ':'); self.pvList.append(self.pv_Cycle)

    @property
    def B(self):
        return self.pv_Brb.value

    @B.setter
    def B(self, value):
        self.pv_B.value = value

    @property
    def dirty(self):
        return self.pv_Dirty.value == 'DIRTY'

    @property
    def energy(self):
        return self.pv_Energy.value

    @energy.setter
    def energy(self, value):
        self.pv_Energy.value = value

    def setB(self, value):
        self.B = value
    def setE(self, value):
        self.energy = value


class Valve(multiplePV):
    def __init__(self, vname):
        '''
        TODO: status of the valve
        TODO: open/close the valve
        '''
        self.mainName = vname


class BPM(multiplePV):
    '''
    We don't need a description for that right?
    read returns (x, y)
    readAll returns (x, y, q)
    '''
    def __init__(self, bpmName):
        self.pv_x = PV(bpmName + ':X1')
        self.pv_y = PV(bpmName + ':Y1')
        self.pv_q = PV(bpmName + ':Q1')
        self.pvList = [self.pv_x, self.pv_y, self.pv_q]

    @property
    def x(self):
        return self.pv_x.value
    @property
    def y(self):
        return self.pv_y.value
    @property
    def q(self):
        return self.pv_q.value

    def read(self):
        return (self.x, self.y)

    def readFull(self):
        return (self.x, self.y, self.q)
