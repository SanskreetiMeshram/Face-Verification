"""
ProofLink Smart Contract Deployment Script
Deploy ProofRegistry.sol to Polygon Amoy Testnet, Sepolia, or Local EVM Network
"""
import os
import sys
import json
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "https://rpc-amoy.polygon.technology/")
PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY") or os.getenv("PRIVATE_KEY", "").strip()
CHAIN_ID = int(os.getenv("CHAIN_ID", "80002"))
EXPLORER_URL = os.getenv("BLOCKCHAIN_EXPLORER_URL", "https://amoy.polygonscan.com")

def deploy():
    print("==========================================================")
    print("  ProofLink - ProofRegistry Smart Contract Deployer")
    print("==========================================================")
    
    if not PRIVATE_KEY:
        print("\n[ERROR] BLOCKCHAIN_PRIVATE_KEY / PRIVATE_KEY is not configured in backend/.env")
        print("Please configure your testnet wallet private key.")
        print("For testing without gas fees, you can use a local Hardhat/Anvil node or local RPC.")
        sys.exit(1)

    pk = PRIVATE_KEY if PRIVATE_KEY.startswith("0x") else f"0x{PRIVATE_KEY}"
    try:
        account = Account.from_key(pk)
    except Exception as err:
        print(f"[ERROR] Invalid private key: {err}")
        sys.exit(1)
    
    print(f"Connecting to RPC: {RPC_URL}")
    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 20}))
    
    if not w3.is_connected():
        print("[ERROR] Failed to connect to Blockchain RPC node.")
        print(f"Check network status or RPC URL: {RPC_URL}")
        sys.exit(1)
        
    actual_chain_id = w3.eth.chain_id
    print(f"Connected! Chain ID: {actual_chain_id}")
    print(f"Deployer Address: {account.address}")
    
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"Account Balance: {balance_eth} POL / ETH")
    
    if balance == 0 and actual_chain_id != 31337:
        print("\n[WARNING] Your wallet balance is 0.")
        print("Please request testnet tokens from Polygon Amoy Faucet:")
        print("  -> https://faucet.polygon.technology/")
        print("  -> https://www.alchemy.com/faucets/polygon-amoy")
        sys.exit(1)

    # Read contract ABI
    abi_path = os.path.join(os.path.dirname(__file__), "ProofRegistry.json")
    with open(abi_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        abi = data.get("abi", [])

    print("\nAttempting compilation with solcx...")
    bytecode = None
    
    try:
        from solcx import compile_standard, install_solc
        print("Ensuring solc 0.8.20 is installed...")
        install_solc("0.8.20")
        
        sol_path = os.path.join(os.path.dirname(__file__), "ProofRegistry.sol")
        with open(sol_path, "r", encoding="utf-8") as f:
            source = f.read()

        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {"ProofRegistry.sol": {"content": source}},
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
        
        bytecode = compiled_sol["contracts"]["ProofRegistry.sol"]["ProofRegistry"]["evm"]["bytecode"]["object"]
        print("ProofRegistry compiled successfully!")
    except Exception as e:
        print(f"[NOTICE] solcx compile notice: {e}")
        print("Please ensure py-solc-x is installed or compile via Hardhat.")
        return

    if not bytecode:
        print("[ERROR] No bytecode generated.")
        return

    # Deploy contract
    ContractFactory = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)
    
    print(f"\nBuilding deployment transaction (nonce: {nonce})...")
    tx_params = {
        'from': account.address,
        'nonce': nonce,
        'gasPrice': w3.eth.gas_price,
        'chainId': actual_chain_id
    }
    
    construct_txn = ContractFactory.constructor().build_transaction(tx_params)
    
    print("Signing deployment transaction...")
    signed_tx = account.sign_transaction(construct_txn)
    
    print("Broadcasting transaction to blockchain...")
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = tx_hash.hex() if hasattr(tx_hash, 'hex') else f"0x{tx_hash.hex()}"
    print(f"Transaction broadcasted! Tx Hash: {tx_hash_hex}")
    print(f"Explorer URL: {EXPLORER_URL}/tx/{tx_hash_hex}")
    print("Waiting for block confirmation...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    contract_address = receipt.contractAddress
    
    print("\n==========================================================")
    print("  [SUCCESS] ProofRegistry Deployed Successfully!")
    print("==========================================================")
    print(f"Contract Address:  {contract_address}")
    print(f"Block Number:      {receipt.blockNumber}")
    print(f"Gas Used:          {receipt.gasUsed}")
    print(f"Explorer Contract: {EXPLORER_URL}/address/{contract_address}")
    print("==========================================================")
    print(f"\nUpdate your backend/.env and .env with:")
    print(f"CONTRACT_ADDRESS={contract_address}")
    print(f"PROOF_REGISTRY_ADDRESS={contract_address}")

if __name__ == "__main__":
    deploy()
