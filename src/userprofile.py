import os
import pickle
import sqlite3
clear = lambda: os.system('cls')


class Profile():
    def __init__(self,username):
        self.username = username
    
    def showprofile(self):
        clear()
        db_path = os.path.join('./data', 'goodchain.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (self.username,))
        user = c.fetchone()
        conn.close()
        
        pbkey = user[3]
        prvkey = user[4]

        print("Username: ", self.username+"\n")
        print("Public Key: ", str(pbkey) + "\n")
        print("Private Key: ", str(prvkey) + "\n")

        input("Press [ENTER] to return to the main menu")


if __name__ == '__main__':
    profile = Profile("jq")
    profile.showprofile()

