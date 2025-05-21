import unittest
import hashlib
import time
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from blockchain import Transaction, Block, Blockchain, TransactionPool

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        # Configuration initiale pour chaque test
        self.key = RSA.generate(2048)
        self.private_key = self.key
        self.public_key = self.key.publickey()
        self.blockchain = Blockchain(difficulty=4)
        self.transaction_pool = TransactionPool()

    def test_transaction_valid(self):
        # Teste la création et la validation d'une transaction valide
        transaction = Transaction("Alice", "Bob", 10)
        transaction.sign_transaction(self.private_key)
        self.assertTrue(transaction.is_valid())
        self.assertTrue(transaction.verify_signature(self.public_key))

    def test_transaction_invalid_amount(self):
        # Teste une transaction avec un montant invalide (négatif)
        with self.assertRaises(ValueError):
            Transaction("Alice", "Bob", -10)

    def test_transaction_invalid_addresses(self):
        # Teste une transaction avec des adresses vides
        with self.assertRaises(ValueError):
            Transaction("", "Bob", 10)
        with self.assertRaises(ValueError):
            Transaction("Alice", "", 10)

    def test_block_creation_and_hash(self):
        # Teste la création d'un bloc et la cohérence de son hash
        transaction = Transaction("Alice", "Bob", 10)
        transaction.sign_transaction(self.private_key)
        block = Block(1, [transaction], "0")
        block_hash = block.hash
        self.assertEqual(block_hash, block.calculate_hash())

    def test_block_mining(self):
        # Teste le minage d'un bloc
        transaction = Transaction("Alice", "Bob", 10)
        transaction.sign_transaction(self.private_key)
        block = Block(1, [transaction], "0")
        block.mine_block(4)
        self.assertTrue(block.hash.startswith("0000"))
        self.assertTrue(block.is_valid())

    def test_blockchain_genesis_block(self):
        # Teste la création du bloc genesis
        genesis_block = self.blockchain.chain[0]
        self.assertEqual(genesis_block.index, 0)
        self.assertEqual(genesis_block.transactions, [])
        self.assertEqual(genesis_block.previous_hash, "0")

    def test_blockchain_add_block(self):
        # Teste l'ajout d'un bloc avec une transaction
        transaction = Transaction("Alice", "Bob", 10)
        transaction.sign_transaction(self.private_key)
        self.transaction_pool.add_transaction(transaction)
        transactions = self.transaction_pool.select_transactions()
        self.assertTrue(self.blockchain.add_block(transactions))
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(self.blockchain.chain[1].transactions[0].sender, "Alice")

    def test_blockchain_validity(self):
        # Teste la validation de la chaîne
        transaction = Transaction("Alice", "Bob", 10)
        transaction.sign_transaction(self.private_key)
        self.transaction_pool.add_transaction(transaction)
        transactions = self.transaction_pool.select_transactions()
        self.blockchain.add_block(transactions)
        self.assertTrue(self.blockchain.is_chain_valid())

    def test_blockchain_invalid_chain(self):
        # Teste une chaîne invalide en modifiant un hash
        transaction = Transaction("Alice", "Bob", 10)
        transaction.sign_transaction(self.private_key)
        self.transaction_pool.add_transaction(transaction)
        transactions = self.transaction_pool.select_transactions()
        self.blockchain.add_block(transactions)
        # Corrompre la chaîne en modifiant un hash
        self.blockchain.chain[1].hash = "invalid_hash"
        self.assertFalse(self.blockchain.is_chain_valid())

    def test_transaction_pool(self):
        # Teste l'ajout et la sélection dans le pool de transactions
        transaction = Transaction("Alice", "Bob", 10)
        transaction.sign_transaction(self.private_key)
        self.assertTrue(self.transaction_pool.add_transaction(transaction))
        selected = self.transaction_pool.select_transactions(1)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].sender, "Alice")
        self.assertEqual(len(self.transaction_pool.transactions), 0)

if __name__ == '__main__':
    unittest.main()
