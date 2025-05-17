import hashlib
import time
import json
import os

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(
            f"{self.index}{self.timestamp}{self.data}{self.previous_hash}".encode()
        ).hexdigest()
    
    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, block_dict):
        block = cls(
            block_dict['index'],
            block_dict['timestamp'],
            block_dict['data'],
            block_dict['previous_hash']
        )
        block.hash = block_dict['hash']
        return block

class Blockchain:
    def __init__(self, blockchain_file='blockchain_data.json'):
        self.blockchain_file = blockchain_file
        
        # Check if blockchain file exists
        if os.path.exists(blockchain_file):
            self.load_chain()
        else:
            self.chain = [self.create_genesis_block()]
            self.save_chain()

    def create_genesis_block(self):
        return Block(0, time.strftime("%d/%m/%Y %H:%M:%S"), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_block = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            timestamp=time.strftime("%d/%m/%Y %H:%M:%S"),
            data=data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        self.save_chain()
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
                
            if current_block.previous_hash != previous_block.hash:
                return False
                
        return True

    def search_certificate(self, certificate_hash):
        for block in self.chain[1:]:  # Skip genesis block
            if block.data == certificate_hash:
                return True, block
        return False, None
    
    def save_chain(self):
        """Save blockchain to file"""
        chain_data = []
        for block in self.chain:
            chain_data.append(block.to_dict())
        
        with open(self.blockchain_file, 'w') as f:
            json.dump(chain_data, f, indent=4)
    
    def load_chain(self):
        """Load blockchain from file"""
        with open(self.blockchain_file, 'r') as f:
            chain_data = json.load(f)
        
        self.chain = []
        for block_data in chain_data:
            block = Block.from_dict(block_data)
            self.chain.append(block)
