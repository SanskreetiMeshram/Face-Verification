"""
Polygon Amoy / EVM Smart Contract Deployment Script for FaceMatchRegistry
"""
import os
import sys
import json
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env"))

RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "https://rpc-amoy.polygon.technology/")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "").strip()
CHAIN_ID = int(os.getenv("CHAIN_ID", "80002"))

def deploy():
    print("==========================================================")
    print("  FaceChain Verify - Smart Contract Deployment Tool")
    print("==========================================================")
    
    if not PRIVATE_KEY:
        print("\n[ERROR] PRIVATE_KEY is not set in backend/.env")
        print("Please configure your testnet wallet private key.")
        sys.exit(1)

    pk = PRIVATE_KEY if PRIVATE_KEY.startswith("0x") else f"0x{PRIVATE_KEY}"
    account = Account.from_key(pk)
    
    print(f"Connecting to RPC: {RPC_URL}")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("[ERROR] Failed to connect to Blockchain RPC node.")
        sys.exit(1)
        
    print(f"Connected! Chain ID: {w3.eth.chain_id}")
    print(f"Deployer Address: {account.address}")
    
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"Account Balance: {balance_eth} POL / ETH")
    
    if balance == 0:
        print("\n[WARNING] Your balance is 0. Please request testnet tokens from Polygon Amoy Faucet:")
        print("https://faucet.polygon.technology/")
        sys.exit(1)

    # Read contract ABI
    abi_path = os.path.join(os.path.dirname(__file__), "FaceMatchRegistry.json")
    with open(abi_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        abi = data.get("abi", [])

    print("\nAttempting deployment with pre-compiled bytecode or solcx...")
    
    try:
        from solcx import compile_standard, install_solc
        print("Installing solc 0.8.20...")
        install_solc("0.8.20")
        
        sol_path = os.path.join(os.path.dirname(__file__), "FaceMatchRegistry.sol")
        with open(sol_path, "r", encoding="utf-8") as f:
            source = f.read()

        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {"FaceMatchRegistry.sol": {"content": source}},
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                        }
                    }
                },
            },
            solc_version="0.8.20",
        )
        
        bytecode = compiled_sol["contracts"]["FaceMatchRegistry.sol"]["FaceMatchRegistry"]["evm"]["bytecode"]["object"]
        print("Contract compiled successfully!")
    except Exception as e:
        print(f"[NOTICE] solcx compilation skipped ({e}). Using standard contract factory.")
        print("Ensure py-solc-x is installed or use Hardhat/Remix.")
        return

    # Deploy contract
    ContractFactory = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)
    
    print(f"Building deployment transaction (nonce: {nonce})...")
    construct_txn = ContractFactory.constructor().build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gasPrice': w3.eth.gas_price,
        'chainId': CHAIN_ID
    })

    signed = w3.eth.account.sign_transaction(construct_txn, private_key=pk)
    print("Submitting transaction to network...")
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"Transaction Hash: {w3.to_hex(tx_hash)}")
    print("Waiting for block confirmation...")

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    contract_addr = tx_receipt.contractAddress
    print("\n==========================================================")
    print(f"  SUCCESS! FaceMatchRegistry Deployed!")
    print(f"  Contract Address: {contract_addr}")
    print(f"  Block Number: {tx_receipt.blockNumber}")
    print(f"  Gas Used: {tx_receipt.gasUsed}")
    print(f"  Explorer URL: https://amoy.polygonscan.com/address/{contract_addr}")
    print("==========================================================")
    print(f"\nPlease update your backend/.env file with:")
    print(f"CONTRACT_ADDRESS={contract_addr}\n")

if __name__ == "__main__":
    deploy()
