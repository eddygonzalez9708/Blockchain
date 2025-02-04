# Paste your version of blockchain.py from the basic_block_gp
# folder here

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
  def __init__(self):
    self.chain = []
    self.current_transactions = []
    self.nodes = set()

    self.new_block(previous_hash = 1, proof = 99)

  def new_block(self, proof, previous_hash = None):
    """
    Create a new Block in the Blockchain

    :param proof: <int> The proof given by the Proof of Work algorithm
    :param previous_hash: (Optional) <str> Hash of previous Block
    :return: <dict> New Block
    """

    block = {
      'index': len(self.chain) + 1,
      'timestamp': time(),
      'transactions': self.current_transactions,
      'proof': proof,
      'previous_hash': previous_hash or self.hash(self.chain[-1]),
    }

    # Reset the current list of transactions
    self.current_transactions = []

    self.chain.append(block)

    return block

  def new_transaction(self, sender, recipient, amount):
    """
    Creates a new transaction to go into the next mined Block

    :param sender: <str> Address of the Sender
    :param recipient: <str> Address of the Recipient
    :param amount: <int> Amount
    :return: <int> The index of the BLock that will hold this transaction
    """

    self.current_transactions.append({
      'sender': sender,
      'recipient': recipient,
      'amount': amount,
    })

    return self.last_block['index'] + 1

  @staticmethod
  def hash(block):
    """
    Creates a SHA-256 hash of a Block

    :param block": <dict> Block
    "return": <str>
    """

    # We must make sure that the Dictionary is Ordered,
    # or we'll have inconsistent hashes

    # Convert from Pyton to JSON.
    # The encode() method encodes the string,
    # using the specified encoding.
    # If no encoding is specified, UTF-8 will be used.

    block_string = json.dumps(block, sort_keys = True).encode()

    # Hash the block string and return it as a hexadecimal string.
    
    return hashlib.sha256(block_string).hexdigest()

  @property
  def last_block(self):
    return self.chain[-1]

  @staticmethod
  def valid_proof(last_proof, proof):
    """
    Validates the Proof: Does hash(last_block_string, proof) contain 6
    leading zeroes?
    
    :param proof: <string> The proposed proof
    :return: <bool> Return true if the proof is valid, false if it is not
    """
    
    # Build string to hash.
    guess = f'{last_proof}{proof}'.encode()

    # Use hash function.
    guess_hash = hashlib.sha256(guess).hexdigest()
  
    # Check if 6 leading 0's in hash result.
    beginning = guess_hash[0:6]

    return beginning == '000000'

  def valid_chain(self, chain):
    """
    Determine if a given blockchain is valid

    :param chain: <list> A blockchain
    :return: <bool> True if valid, False if not
    """

    prev_block = chain[0]
    current_index = 1

    while current_index < len(chain):
      block = chain[current_index]
      print(f'{prev_block}')
      print(f'{block}')
      print("\n-------------------\n")
      # Check that the hash of the block is correct
      # TODO: Return false if hash isn't correct

      # Check that the Proof of Work is correct
      # TODO: Return false if proof isn't correct

      prev_block = block
      current_index += 1

    return True

# Instantiate our Node
app = Flask(__name__)

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['POST'])
def mine():
  # Modify the mine endpoint to instead receive and validate or
  # reject a new proof sent by a client.

  request_body = request.get_json()
  last_proof = blockchain.last_block['proof']
  check_proof = blockchain.valid_proof(last_proof, request_body['proof'])

  if check_proof:
    # Client must receive a reward for finding the proof.

    # The sender is "0" to signify that this node has mine a new coin
    # The recipient is the current node, it did the mining!
    # The amount is 1 coin as a reward for mining the next block

    blockchain.new_transaction(0, request_body['node'], 1)

    # Forge the new Block by adding it to the chain

    last_block = blockchain.last_block
    prev_block_hashed = blockchain.hash(last_block)
    block = blockchain.new_block(request_body['proof'], prev_block_hashed)

    # Send a response with the new block

    response = {
      'message': "New Block Forged",
      'index': block['index'],
      'transactions': block['transactions'],
      'proof': block['proof'],
      'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200
  else:
    response = { 'message': 'Invalid Proof' }
    return jsonify(response), 400

@app.route('/last_proof', methods=['GET'])
def last_proof():
  response = {
    'last_proof': blockchain.last_block['proof']
  }

  return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
  values = request.get_json()

  # Check that the required fields are in the POST'ed data
  required = ['sender', 'recipient', 'amount']
  if not all(k in values for k in required):
    return 'Missing Values', 400

  # Create a new Transaction
  index = blockchain.new_transaction(values['sender'],
    values['recipient'],
    values['amount'])

  response = {'message': f'Transaction will be added to Block {index}'}
  
  return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
  response = {
    # TODO: Return the chain and its current length
    'chain': blockchain.chain,
    'length': len(blockchain.chain),
  }
  
  return jsonify(response), 200

# Run the program on port 5000
if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 5000)