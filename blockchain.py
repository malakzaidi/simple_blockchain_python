import hashlib
import time
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import json
class Transaction:
    def __init__(self, sender, receiver, amount, timestamp=None):
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be positive")
        if not sender or not receiver:
            raise ValueError("Sender and receiver addresses must be non-empty")
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp or time.time()
        self.signature = None
        self.hash = self.calculate_hash()
    def calculate_hash(self):
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    def sign_transaction(self, private_key):
        try:
            key = RSA.import_key(private_key)
            h = SHA256.new(self.hash.encode())
            self.signature = pkcs1_15.new(key).sign(h)
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {e}")
    def verify_signature(self, public_key):
        if not self.signature:
            return False
        try:
            key = RSA.import_key(public_key)
            h = SHA256.new(self.hash.encode())
            pkcs1_15.new(key).verify(h, self.signature)
            return True
        except:
            return False
    def is_valid(self):
        return (isinstance(self.amount, (int, float)) and self.amount > 0 and
                self.sender and self.receiver and self.hash == self.calculate_hash())

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = (f"{self.index}{self.previous_hash}{self.timestamp}{self.nonce}"
                f"{json.dumps([t.__dict__ for t in self.transactions], sort_keys=True)}")
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")

    def is_valid(self):
        return self.hash == self.calculate_hash() and all(t.is_valid() for t in self.transactions)


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.transaction_pool = TransactionPool()
    def create_genesis_block(self):
        return Block(0, [], "0")
    def get_latest_block(self):
        return self.chain[-1]
    def add_block(self, transactions):
        block = Block(len(self.chain), transactions, self.get_latest_block().hash)
        block.mine_block(self.difficulty)
        if block.is_valid():
            self.chain.append(block)
            return True
        return False
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if not current.is_valid():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

class TransactionPool:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        if transaction.is_valid():
            self.transactions.append(transaction)
            return True
        return False

    def select_transactions(self, max_transactions=10):
        selected = self.transactions[:max_transactions]
        self.transactions = self.transactions[max_transactions:]
        return selected

    def clear(self):
        self.transactions = []

def main():
    blockchain = Blockchain(difficulty=4)
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    while True:
        print("\n=== Blockchain Menu ===")
        print("1. Afficher l'état de la blockchain")
        print("2. Créer une transaction")
        print("3. Afficher les transactions en attente")
        print("4. Miner un bloc")
        print("5. Valider la chaîne")
        print("6. Quitter")
        choice = input("Entrez votre choix (1-6) : ")
        if choice == "1":
            print("\nÉtat de la blockchain :")
            for block in blockchain.chain:
                print(f"Block #{block.index}:")
                print(f"  Hash: {block.hash}")
                print(f"  Previous Hash: {block.previous_hash}")
                print(f"  Transactions: {[t.__dict__ for t in block.transactions]}")
        elif choice == "2":
            sender = input("Émetteur : ")
            receiver = input("Destinataire : ")
            amount = float(input("Montant : "))
            try:
                transaction = Transaction(sender, receiver, amount)
                transaction.sign_transaction(private_key)
                if blockchain.transaction_pool.add_transaction(transaction):
                    print("Transaction ajoutée avec succès")
                else:
                    print("Transaction invalide")
            except ValueError as e:
                print(f"Erreur : {e}")
        elif choice == "3":
            print("\nTransactions en attente :")
            for t in blockchain.transaction_pool.transactions:
                print(f"Transaction: {t.__dict__}")
        elif choice == "4":
            transactions = blockchain.transaction_pool.select_transactions()
            if blockchain.add_block(transactions):
                print("Bloc miné et ajouté avec succès")
                blockchain.transaction_pool.clear()
            else:
                print("Échec du minage")
        elif choice == "5":
            if blockchain.is_chain_valid():
                print("La chaîne est valide")
            else:
                print("La chaîne est invalide")
        elif choice == "6":
            print("Quitter...")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()