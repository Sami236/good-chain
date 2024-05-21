REWARD_VALUE = 50.0
NORMAL = 0
REWARD = 1

from Signature import *
from Checkbalance import CheckBalance
import time  # Import the time module for timestamp functionality

class Tx:
    inputs = None
    outputs = None
    sigs = None
    reqd = None
    timestamp = None  
    def __init__(self, type = NORMAL):
        self.type = type
        self.inputs = []
        self.outputs = []
        self.sigs = []
        self.reqd = []
        self.fee = 0
        self.validtx = False
        self.timestamp = time.time()  

    def add_input(self, from_addr, amount):
        self.inputs.append((from_addr, amount))

    def add_output(self, to_addr, amount):
        self.outputs.append((to_addr, amount))
    
    def add_fee(self, fee):
        self.fee += fee

    def add_reqd(self, addr):
        self.reqd.append(addr)

    def sign(self, private):
        message = self.__gather()
        newsig = sign(message, private)
        self.sigs.append(newsig)
               
    def is_valid(self):
        if self.type == REWARD:
            if len(self.inputs)!=0 and len(self.outputs)!=1:
                self.validtx = False
                return False
            for _, amount in self.inputs:
                if amount > REWARD_VALUE + self.fee:
                    self.validtx = False
                    return False
            for _, amount in self.outputs:
                if amount > REWARD_VALUE + self.fee:
                    self.validtx = False
                    return False
            self.validtx = True
            return True
        else:
            total_in = 0
            total_out = 0
            message = self.__gather()
            for addr,amount in self.inputs:
                found = False
                for s in self.sigs:
                    if verify(message, s, addr):
                        found = True
                if not found:
                    print ("No good sig found for " + str(message))
                    self.validtx = False
                    return False
                if amount < 0:
                    self.validtx = False
                    return False
                total_in = total_in + amount
            for addr in self.reqd:
                found = False
                for s in self.sigs:
                    if verify(message, s, addr):
                        found = True
                if not found:
                    self.validtx = False
                    return False
            for addr,amount in self.outputs:
                if amount < 0:
                    self.validtx = False
                    return False
                total_out = total_out + amount

            if total_out != total_in:
                self.validtx = False
                return False
            
            if(self.fee < 0):
                print("Fee is negative")
                self.validtx = False
                return False
            

            
            self.validtx = True
            return True

    def __gather(self):
        data=[]
        data.append(self.inputs)
        data.append(self.outputs)
        data.append(self.reqd)
        return data

    def __repr__(self):
        repr_str = "Inputs:\n"
        for addr, amt in self.inputs:
            repr_str += str(amt) + " from " + str(addr) + "\n"
        repr_str += "Outputs:\n"
        for addr, amt in self.outputs:
            repr_str += str(amt) + " to " + str(addr) + "\n"
        repr_str += "Signature:\n"
        for s in self.sigs:
            repr_str += str(s) + "\n"
        repr_str += "Validity:" + str(self.validtx) + "\n"
        repr_str += "Fee:" + str(self.fee) + "\n"
        return repr_str