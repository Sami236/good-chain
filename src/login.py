import os
import sqlite3
import hashlib
from user import User
from goodchain import Goodchain

class LoginScreen:
    def __init__(self):
        pass

    def Login(self):
        os.system('cls')
        username = input("Username: ")
        password = input("Password: ")
        
        if self.ValidateUser(username, password):
            user = User(username)
            user.main()
        else:
            input("Invalid username or password, Press [ENTER] to go back to the main menu.")
            

    def ValidateUser(self, username, password):
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if user[2] == hashed_password:
                return True
            else:
                return False

if __name__ == '__main__':
    loginScreen = LoginScreen()
    loginScreen.Login()
