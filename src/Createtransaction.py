import os
import pickle
import sqlite3
from Transaction import *
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from Checkbalance import CheckBalance
from hashfiles import update_file_hashes
clear = lambda: os.system('cls')


class CreateTransaction():
    def __init__(self):
        self.balance = 0

    def CreateTransaction(self, username):
        clear()
        senderpbckey = self.GetPublcKey(username)
        senderprvkey = self.GetPrivateKey(username)
        recipient = input("Recipient: ")
        if(recipient == username):
            print("You cannot send coins to yourself.")
            input("Press [ENTER] to return to the main menu")
            return
        
        while not self.GetPublcKey(recipient):
            clear()
            print("Recipient does not exist.")
            input("Press [ENTER] to return to the main menu")
            return

        recipientpbckey = self.GetPublcKey(recipient)
        while True:
            amount = input("Amount: ")
            transactionfee = input("Transaction Fee: ")

            # Validate amount and transactionfee inputs
            try:
                amount = float(amount)
                transactionfee = float(transactionfee)
                if amount <= 0 or transactionfee < 0:
                    raise ValueError
            except ValueError:
                print("Amount must bigger than 0. All inputs should be positive numbers.")
                continue

            break
        
        # Check if the sender has enough balance
        balance = CheckBalance().check_balance(username)
        if balance < amount + transactionfee:
            print("Insufficient balance.")
            input("Press [ENTER] to return to the main menu")
            return
        
        # Create a new transaction
        path = os.path.join('./data', 'pool.dat')
        with open(path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                pool = []
        tx = Tx()
        tx.add_input(senderpbckey, amount)
        tx.add_fee(transactionfee)
        tx.add_output(recipientpbckey, amount)
        decodedprvkey = load_pem_private_key(senderprvkey, password=None)
        tx.sign(decodedprvkey)
        if tx.is_valid():
            print("Success! Transaction is valid.")
        else:
            print("Error! Transaction is invalid.")
            return
        
        pool.append(tx)
        with open(path, 'wb') as file_handle:
            pickle.dump(pool, file_handle)
        
        
        update_file_hashes('pool', path)

        print("Transaction created successfully.")
        input("Press [ENTER] to return to the main menu")


    def Load_Tx(self):
        path = os.path.join('./data', 'pool.dat')
        with open(path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                pool = []
        return pool

    def GetPrivateKey(self, username):
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        if(user == None):
            return
        conn.close()
        return user[4]
        

    def GetPublcKey(self, username):
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        if(user == None):
            return
        conn.close()
        return user[3]




        
if __name__ == '__main__':
    createtransaction = CreateTransaction()
    createtransaction.CreateTransaction('sami')