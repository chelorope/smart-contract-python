from solcx import compile_standard, install_solc;
from web3 import Web3;
from dotenv import load_dotenv;
import json;
import os;

load_dotenv()
install_solc("0.6.0")
with open("./SimpleStorage.sol", "r") as file:
  simple_storage_file = file.read()
  # print(simple_storage_file)
  
# Compile Our Solidity
compiled_sol = compile_standard({
  "language": "Solidity",
  "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
  "settings": {
    "outputSelection": {
      "*": {
        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
      }
    },
  }
},
  solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get Bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# Get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connect to Rinkeby
w3 = Web3(Web3.HTTPProvider(os.getenv("NET_URL")))
chain_id = os.getenv("CHAIN_ID")
my_address = os.getenv("MY_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

# Create contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
print(SimpleStorage)
# Get latest transaction
nonce = w3.eth.getTransactionCount(my_address)
print(nonce)
# 1. Build a transaction
# 2. Sing a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
  {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce}
)
print(transaction)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print(signed_txn)

# Send signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Working with the contract
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value
# Transact -> Actually makes a state change

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(15).buildTransaction(
  {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_store_txn = w3.eth.account.sign_transaction(
  store_transaction, private_key=private_key
)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)