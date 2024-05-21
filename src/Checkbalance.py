import os
import pickle
import sqlite3
from Signature import *
from hashfiles import check_blockchain_integrity

clear = lambda: os.system('cls')

class CheckBalance:
    def __init__(self):
        self.confirmed_balance = 0
        self.unconfirmed_balance = 0

    def main(self, username):
        clear()
        self.check_balance(username)
        input("Press [ENTER] to return to the main menu")

    def check_balance(self, username):
        path = os.path.join('./data', 'goodchain.db')
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if not user:
            print("User not found.")
            input("Press [ENTER] to return to the main menu")
            return

        public_key = user[3]
        check_blockchain_integrity()
        ledger_path = os.path.join('./data', 'blockchain.dat')
        with open(ledger_path, 'rb') as ledger_file:
            try:
                ledger = pickle.load(ledger_file)
                for block in ledger:
                    if block.isvalid:
                        for tx in block.data:
                            for addr, amount in tx.inputs:
                                if addr == public_key:
                                    self.confirmed_balance -= (amount + tx.fee)
                            for addr, amount in tx.outputs:
                                if addr == public_key:
                                    self.confirmed_balance += amount
                    else:
                        for tx in block.data:
                            for addr, amount in tx.inputs:
                                if addr == public_key:
                                    self.unconfirmed_balance -= (amount + tx.fee)
            except EOFError:
                pass

        pool_path = os.path.join('./data', 'pool.dat')
        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
                for tx in pool:
                    for addr, amount in tx.inputs:
                        if addr == public_key:
                            self.unconfirmed_balance -= (amount +  tx.fee)
            except EOFError:
                pass
        self.confirmed_balance += self.unconfirmed_balance
        print("Balance for " + username + ": {:.2f}".format(self.confirmed_balance))
        return self.confirmed_balance

if __name__ == '__main__':
    checkbalance = CheckBalance()
    checkbalance.check_balance('jq')
