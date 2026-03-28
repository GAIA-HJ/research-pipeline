import hashlib
import json
from datetime import datetime
from web3 import Web3


class BlockchainAnchor:
    def __init__(self, rpc_url: str, private_key: str, contract_addr: str = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.w3.eth.account.from_key(private_key)
        self.contract_addr = contract_addr

    def hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def anchor_hash(self, content_hash: str, metadata: dict = None) -> dict:
        payload = json.dumps({
            "hash": content_hash,
            "ts": datetime.utcnow().isoformat(),
            "type": "research_anchor",
            **(metadata or {})
        }).encode()
        tx = {
            "to": self.contract_addr or self.account.address,
            "value": 0,
            "data": self.w3.to_hex(payload),
            "gas": 50000,
            "gasPrice": self.w3.eth.gas_price,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "chainId": 137,
        }
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        return {
            "tx_hash": receipt.transactionHash.hex(),
            "block": receipt.blockNumber,
            "content_hash": content_hash,
            "status": "anchored" if receipt.status == 1 else "failed",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def verify_hash(self, tx_hash: str, expected_hash: str) -> bool:
        tx = self.w3.eth.get_transaction(tx_hash)
        payload = json.loads(bytes.fromhex(tx.input.hex()[2:]))
        return payload.get("hash") == expected_hash
