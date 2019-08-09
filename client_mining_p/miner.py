import hashlib
import requests
from uuid import uuid4

import sys

# TODO: Implement functionality to search for a proof 

def proof_of_work(last_proof):
  """
  Simple Proof of Work Algorithm
  Find a number p such that hash(last_block_string, p) contains 
  6 leading zeroes.
      
  :return: <int> A valid proof
  """

  print('Starting working on new proof.\n')

  proof = 0

  # Example for block 1: hash(1, p) = 000000x

  while not valid_proof(last_proof, proof):
    proof += 1
  
  print(f'Found new valid proof - {proof}\n')

  return proof

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

if __name__ == '__main__':
  # What node are we interacting with?

  if len(sys.argv) > 1:
    node = sys.argv[1]
  else:
    node = "http://localhost:5000"
  
  # Generate a globally unique address for this node
  client_node = str(uuid4()).replace('-', '')

  coins_mined = 0

  # Run forever until interrupted
  while True:
    # TODO: Get the last proof from the server and look for a new one
    
    response = requests.get(f'{node}/last_proof')
    last_proof = response.json()['last_proof']

    new_proof = proof_of_work(last_proof)

    # TODO: When found, POST it to the server {"proof": new_proof}
    # TODO: We're going to have to research how to do a POST in Python
    # HINT: Research `requests` and remember we're sending our data as JSON

    result = requests.post(f'{node}/mine', json = {
      'proof': new_proof,
      'node': client_node
    })

    # TODO: If the server responds with 'New Block Forged'
    # add 1 to the number of coins mined and print it.  Otherwise,
    # print the message from the server.

    if result.status_code == 200:
      coins_mined += 1
    
    print(f'Server Response: {result.json()}\n')
    print(f'Coins: {coins_mined}\n')
