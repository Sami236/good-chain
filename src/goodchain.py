from menu import *
from signup import SignupScreen
import time
import sqlite3
from Checkchain import CheckChain
from menu import Menu
from hashfiles import *
import pickle

class Goodchain():
    def __init__(self):
        self.menuItems = {'Login': 'login', 'Sign up': 'SignUp', 'Explore the blockchain' : 'Seeledger' ,'Exit' : 'Exit'}
        self.database_dir = 'data'

    def startup(self):
        self.create_files()
        self.check_integrity()
        self.Main()
    
    def Main(self):
        while True:
            menu = Menu("Select an option",self.menuItems)
            index = menu.display()
            selected_item = list(self.menuItems.keys())[index]
            getattr(self, self.menuItems[selected_item])()
    
    def SignUp(self):
        signUpScreen = SignupScreen()
        signUpScreen.SignUp()

    def login(self):
        from login import LoginScreen
        loginscreen = LoginScreen()
        loginscreen.Login()

    def Exit(self):
        print("Exiting...")
        time.sleep(2)
        exit()
    
    def Seeledger(self):
        seeledger = CheckChain()
        seeledger.PrintChain()


    def create_files(self):
        database_dir = './data'
        if not os.path.exists(database_dir):
            os.makedirs(database_dir)
        db_path = os.path.join(database_dir, 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY, username TEXT, password TEXT, public_key TEXT, private_key TEXT, notifications TEXT, last_recorded_block_id INT, rejected_block TEXT)''')
        conn.commit()
        conn.close()

        pool_file_path = os.path.join(database_dir, 'pool.dat')
        if not os.path.exists(pool_file_path):
            with open(pool_file_path, 'w'):
                pass

        # Create blockchain.dat file
        blockchain_file_path = os.path.join(database_dir, 'blockchain.dat')
        if not os.path.exists(blockchain_file_path):
            with open(blockchain_file_path, 'w'):
                pass

        filehashes = os.path.join(database_dir, 'filehashes.dat')
        if not os.path.exists(filehashes):
            with open(filehashes, 'w'):
                pass
            self.save_file_hashes()
        

    def save_file_hashes(self):
        db_path = os.path.join(self.database_dir, 'goodchain.db')
        pool_file_path = os.path.join(self.database_dir, 'pool.dat')
        blockchain_file_path = os.path.join(self.database_dir, 'blockchain.dat')

        db_hash = generate_hash(db_path)
        pool_hash = generate_hash(pool_file_path)
        blockchain_hash = generate_hash(blockchain_file_path)

        file_hashes = {'db': db_hash, 'pool': pool_hash, 'blockchain': blockchain_hash}
        
        filehashes_path = os.path.join(self.database_dir, 'filehashes.dat')
        with open(filehashes_path, 'wb') as file:
            pickle.dump(file_hashes, file)

    def load_file_hashes(self):
        filehashes_path = os.path.join(self.database_dir, 'filehashes.dat')
        if os.path.exists(filehashes_path):
            with open(filehashes_path, 'rb') as file:
                self.file_hashes = pickle.load(file)
        return self.file_hashes
    
    def check_integrity(self):
        clear()
        loadedhashes = self.load_file_hashes()
        db_path = os.path.join(self.database_dir, 'goodchain.db')
        pool_file_path = os.path.join(self.database_dir, 'pool.dat')
        blockchain_file_path = os.path.join(self.database_dir, 'blockchain.dat')

        # Generate current hashes
        current_hashes = {
            'db': generate_hash(db_path),
            'pool': generate_hash(pool_file_path),
            'blockchain': generate_hash(blockchain_file_path)
        }

        # Compare current hashes with stored hashes
        for key, stored_hash in loadedhashes.items():
            current_hash = current_hashes.get(key)
            print(current_hash + "\n" +  stored_hash)
            if current_hash != stored_hash:
                print(f"Integrity check failed for {key} file. Potential tampering detected.")
                print("Exiting...")
                time.sleep(2)
                exit()
            else:
                print(f"{key} file integrity check passed.")
        
        
    
if __name__ == '__main__':
    goodchain = Goodchain()
    goodchain.startup()
