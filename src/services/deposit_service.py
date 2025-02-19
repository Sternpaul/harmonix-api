from sqlmodel import select
from typing import List
from datetime import datetime

from core import constants
from models.onchain_transaction_history import OnchainTransactionHistory
from models.vaults import Vault
from utils.extension_utils import to_tx_aumount


class DepositService:
    def __init__(self, session):
        self.session = session

    def get_deposits(
        self, vault_contract_address: str, start_date: int, end_date: int
    ) -> List[OnchainTransactionHistory]:
        deposits_query = (
            select(OnchainTransactionHistory)
            .where(
                OnchainTransactionHistory.method_id == constants.MethodID.DEPOSIT.value
            )
            .where(
                OnchainTransactionHistory.to_address == vault_contract_address.lower()
            )
            .where(OnchainTransactionHistory.timestamp <= end_date)
            .where(OnchainTransactionHistory.timestamp >= start_date)
        )

        deposits = self.session.exec(deposits_query).all()
        return deposits

    def get_total_deposits(self, vault: Vault, start_date: int, end_date: int) -> float:
        deposits = self.get_deposits(vault.contract_address, start_date, end_date)
        total_deposit = sum(to_tx_aumount(tx.input) for tx in deposits)
        return total_deposit
