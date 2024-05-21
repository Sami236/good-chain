import pickle
import os
from hashfiles import check_blockchain_integrity
clear = lambda: os.system('cls')

class CheckChain():
    
    def PrintChain(self):
        clear()
        check_blockchain_integrity()
        filepath = os.path.join('./data', 'blockchain.dat')
        blocks = 0
        transactions =0
        with open(filepath, "rb") as loadfile:
            try:
                blockchain = pickle.load(loadfile)
                print("\nBlockchain Details:")
                print("====================")
                for block in blockchain:
                    blocks+=1
                    print(block)
                    for tx in block.data:
                        transactions+=1
                print("====================\n")
            except EOFError:
                print("Blockchain is empty")
        print(f"Total Blocks: {blocks} , Total Transactions {transactions}." )
        input("Press [ENTER] to return to the main menu")

if __name__ == '__main__':
    checkchain = CheckChain()
    checkchain.PrintChain()
