from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from Signature import *
from Transaction import Tx
import time  # Import the time module


class CBlock:
    data = None
    previousHash = None
    previousBlock = None
    block_id = None
    miner = None
    validity = None
    isvalid = False
    timestamp = None  # Add mined_time attribute

    def __init__(self, data, previousBlock, block_id, miner=None):
        self.data = data
        self.previousBlock = previousBlock
        self.nonce = 0
        if previousBlock != None:
            self.previousHash = previousBlock.computeHash()
        self.blockHash = None
        self.block_id = block_id
        self.miner = miner
        self.validity = {}

    def computeHash(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data),'utf8'))
        digest.update(bytes(str(self.previousHash),'utf8'))
        digest.update(bytes(str(self.nonce),'utf8'))
        return digest.finalize()    

    def is_valid(self):
        if self.previousBlock == None:
            if self.blockHash == self.computeHash():
                return True
            else:
                return False
        else:
            current_block_validity = self.blockHash == self.computeHash()
            previous_block_validity = self.previousBlock.is_valid()
            return current_block_validity and previous_block_validity
        
    def __repr__(self):
        repr_str = "Block ID: " + str(self.block_id) + "\n"
        repr_str += "Nonce: " + str(self.nonce) + "\n"
        repr_str += "Block Hash: " + str(self.blockHash) + "\n"
        repr_str += "Previous Block Hash: " + str(self.previousHash) + "\n"
        repr_str += "Number of Transactions: " + str(len(self.data)) + "\n"
        repr_str += "Mined By: " + str(self.miner) + "\n"  # Adding miner info
        repr_str += "Validity: " + str(self.validity) + "\n"
        repr_str += "Validity: " + str(self.isvalid) + "\n"
        repr_str += "Time of mining: " + self.get_formatted_mined_time() + "\n"  # Adding formatted mined time
        return repr_str
    
    def get_formatted_mined_time(self):
            return time.strftime("%d-%m %H:%M", time.localtime(self.timestamp))


class TxBlock (CBlock):

    def __init__(self, previousBlock, block_id, miner=None):
        super(TxBlock,self).__init__([],previousBlock, block_id, miner)

    def addTx(self, Tx_in):
        self.data.append(Tx_in)

    def is_valid(self):
        if not super(TxBlock,self).is_valid():
            print("Error: Invalid block")
            return False
        for i in range(len(self.data)):
            if not self.data[i].is_valid():
                print( self.data[i])
                print("Error: Invalid transaction")
                return False       
        return True
    
    # Bij de onderstaande functie hebben we ervoor gezorgd dat de mining time een bepaald aantal duurt heeft, in dit geval tussen de 10 en 20 seconde. We hebben hierbij gezamenlijk bedacht wat het beste kon werken
    def mine(self, leading_zero):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf-8'))
        digest.update(bytes(str(self.previousHash), 'utf-8'))

        found = False
        nonce = 0
        starttime = time.time()
        timing_variable = 1
        difficulty_timer = 0
        while not found:
            h = digest.copy()
            h.update(bytes(str(nonce), 'utf-8'))
            hash = h.finalize()
            if(time.time() - starttime > 10 and difficulty_timer > 500): # 50000 on good pc
                timing_variable += 1
                leading_zero = 2
                difficulty_timer = 0
            if hash[:leading_zero] == bytes('0'*leading_zero, 'utf-8'):
                if int(hash[leading_zero]) < timing_variable:
                    found = True
                    self.nonce = nonce
            nonce += 1
            difficulty_timer += 1
            del h
        self.blockHash = self.computeHash()
        self.timestamp = time.time()  # Record mined time
    
    def get_total_fee(self):
        total_fee = 0
        for tx in self.data:
            total_fee += tx.fee

        return total_fee
