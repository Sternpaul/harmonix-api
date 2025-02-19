from datetime import datetime, timezone
import logging
import uuid

from sqlmodel import Session, select
from core import constants
from core.db import engine
from log import setup_logging_to_console, setup_logging_to_file
from models import Vault
from models.vaults import VaultMetadata
from services.gold_link_service import (
    get_borrow_apr,
    get_health_factor_score,
    get_position_size,
)
from services.market_data import get_price
from utils.vault_utils import get_vault_currency_price

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("goldlink_metrics_daily")

session = Session(engine)

LEVERAGE: float = 4


def get_vault_metadata(vault_id: uuid.UUID) -> VaultMetadata:
    vault_metadata = session.exec(
        select(VaultMetadata).where(VaultMetadata.vault_id == vault_id)
    ).first()
    return vault_metadata


def update_vault_metadata(
    vault_metadata: VaultMetadata,
    borrow_apr: float,
    health_factor: float,
    leverage: float,
    open_position: float,
):

    now = datetime.now(timezone.utc)
    # Update existing vault metadata
    vault_metadata.borrow_apr = borrow_apr
    vault_metadata.health_factor = health_factor
    vault_metadata.leverage = leverage
    vault_metadata.open_position_size = open_position
    vault_metadata.last_updated = now

    session.commit()


def get_vault_metrics(vault: Vault):
    try:
        vault_metadata = get_vault_metadata(vault_id=vault.id)

        if not vault_metadata:
            logger.error(
                "No vault metadata found for vault %s. Cannot update.",
                vault.id,
                exc_info=True,
            )
            raise ValueError(f"No vault metadata found for vault {vault.id}.")

        health_factor_score = (
            get_health_factor_score(vault_metadata.goldlink_trading_account) * 100
        )
        borrow_apr = get_borrow_apr() * 100

        size_in_tokens = get_position_size(vault_metadata.goldlink_trading_account)
        token_price = get_vault_currency_price(vault.vault_currency)

        update_vault_metadata(
            vault_metadata,
            borrow_apr=borrow_apr,
            health_factor=health_factor_score,
            leverage=LEVERAGE,
            open_position=size_in_tokens * token_price,
        )
    except Exception as vault_error:
        logger.error(
            "An error occurred while processing vault %s: %s",
            vault.id,
            vault_error,
            exc_info=True,
        )


def main():
    try:
        logger.info("Start fetch info Gold Link metrics daily for vaults...")
        vaults = session.exec(
            select(Vault)
            .where(Vault.slug == constants.GOLD_LINK_SLUG)
            .where(Vault.is_active.is_(True))
        ).all()

        for vault in vaults:
            get_vault_metrics(vault)

    except Exception as e:
        logger.error(
            "An error occurred during Gold Link metrics fetch info: %s",
            e,
            exc_info=True,
        )


if __name__ == "__main__":
    setup_logging_to_console()
    setup_logging_to_file("goldlink_metrics_daily", logger=logger)
    main()
