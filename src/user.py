from menu import Menu
from Checkpool import Checkpool
from Createtransaction import *
from mineblock import MineBlock
from Checkbalance import CheckBalance
from validateblock import ValidateBlock
from Checkchain import CheckChain
from canceltransaction import CancelTransaction
from transactionhistory import display_transaction_history
from notifications import generate_block_notifications
from userprofile import Profile
from deletetransaction import DeleteTransaction
from edittransaction import EditTransaction
from blockinfo import BlockInfo
from hashfiles import check_blockchain_integrity

class User():

    def __init__(self, username):
        self.username = username
        self.menuItems = {"Check Transaction Pool": "check_pool", "Transfer Coins": "transfer_coins", "Mine Block": "mine_block",
                          "Check Balance": "check_balance", "Explore the Blockchain": "see_ledger", "Check Block":"checkblock", "View Transaction History": "view_transaction_history",
                           "Edit Transaction" : "edit_transaction", "Delete Transaction": "delete_transaction" ,"Profile" : "profile", "Log Out": "log_out"}
        self.logged_out = False
        self.notification()

    def main(self):
        validate_block = ValidateBlock()
        validate_block.validate_block(self.username)
        CancelTransaction().cancel_transaction(self.username)
        
        while not self.logged_out:
            menu = Menu(f" Username: {self.username}\n\n Welcome to Goodchain\n", self.menuItems)
            index = menu.display()
            selected_item = list(self.menuItems.keys())[index]
            getattr(self, self.menuItems[selected_item])()

    def mine_block(self):
        mineblock = MineBlock()
        mineblock.mineBlock(self.username)
    
    def checkblock(self):
        blockinfo = BlockInfo()
        blockinfo.get_block_info()

    def check_pool(self):
        checkpool = Checkpool()
        checkpool.PrintPool()
        
    def transfer_coins(self):
        createtransaction = CreateTransaction()
        createtransaction.CreateTransaction(self.username)

    def load_blockchain(self):
        check_blockchain_integrity()
        filepath = os.path.join('./data', 'blockchain.dat')
        with open(filepath, "rb") as loadfile:
            try:
                blockchain = pickle.load(loadfile)
            except EOFError:
                blockchain = []
        return blockchain

    def load_pool(self):
        filepath = os.path.join('./data', 'pool.dat')
        with open(filepath, "rb") as loadfile:
            try:
                pool = pickle.load(loadfile)
            except EOFError:
                pool = []
        return pool
    
    def notification(self):
        blockchain = self.load_blockchain()  # Load blockchain data using the method
        notifications = generate_block_notifications(blockchain, self.username)
        
        # Retrieve and print rejection message from the database
        with sqlite3.connect('./data/goodchain.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rejected_block FROM users WHERE username = ?", (self.username,))
            result = cursor.fetchone()
            if result[0] is not None:
                print(result[0])
        
        for notification in notifications:
            print(notification)
        
        # Clear rejection message from the database
        with sqlite3.connect('./data/goodchain.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET rejected_block = NULL WHERE username = ?", (self.username,))
            conn.commit()
        update_file_hashes('db','./data/goodchain.db')
        input('Press [ENTER] to continue..')
    
    def check_balance(self):
        checkbalance = CheckBalance()
        checkbalance.main(self.username)
    
    def see_ledger(self):
        seeledger = CheckChain()
        seeledger.PrintChain()
    
    def log_out(self):
        self.logged_out = True
        from goodchain import Goodchain
        Goodchain().Main()
    
    def view_transaction_history(self):
        display_transaction_history(self.username)
    
    def profile(self):
        profile = Profile(self.username)
        profile.showprofile()

    def edit_transaction(self):
        edit_transaction = EditTransaction()
        edit_transaction.editTransaction(self.username)

    def delete_transaction(self):
        delete_transaction = DeleteTransaction()
        delete_transaction.deleteTransaction(self.username)


if __name__ == '__main__':
    username = input("Enter username: ")
    user = User(username)
    user.main()
