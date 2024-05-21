
import os
import sqlite3
from cryptography.exceptions import *
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from Transaction import *
import hashlib
import pickle
from user import User
from Createtransaction import *
from hashfiles import *
clear = lambda: os.system('cls')

class UserRegistration:
    
    def __init__(self, username, password):
        self.username = username
        self.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.pbc_key, self.prv_key = self.generate_keys()
        self.insert_into_database()

    def generate_keys(self):
        private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048)
        public_key = private_key.public_key()

        prv_ser = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()

        )
        pbc_ser = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pbc_ser, prv_ser
    
    def insert_into_database(self):
       
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO users (username, password, public_key, private_key)
             VALUES (?,?,?,?)""",
          (self.username, self.password, self.pbc_key, self.prv_key))
        conn.commit()
        conn.close()
        update_file_hashes('db' ,db_path)
        

class SignupScreen():

    def UniqueUsername(self, username):
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        correct = True
        c.execute("SELECT * FROM users")
        for row in c.fetchall():
            if row[1] == username:
                clear()
                print("Username already exists")
                correct = False
                break
            else:
                correct = True

        if(len(username) < 2):
            clear()
            print("Username must be at least 2 characters long")
            correct = False
        return correct
    

    def SignUp(self):
        clear()
        username = input("Username: ")
        while not self.UniqueUsername(username):
            username = input("Username: ")
        
        password = input("Password: ")
        user = UserRegistration(username, password)
        path = os.path.join('./data', 'pool.dat')
        with open(path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                pool = []
        pbkeyreceiver = self.GetPublcKey(username)
        Transaction = Tx(REWARD)
        Transaction.add_input("SYSTEM_SIGNUP_REWARD", REWARD_VALUE)
        Transaction.add_output(pbkeyreceiver, REWARD_VALUE) # hier nog naar kijken!!!!!!

        Transaction.is_valid()
        pool.append(Transaction)

        with open(path, 'wb') as file_handle:
            pickle.dump(pool, file_handle)

        update_file_hashes('pool', path)
        usr = User(username)
        usr.main()

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
    signupScreen = SignupScreen()
    signupScreen.SignUp()
