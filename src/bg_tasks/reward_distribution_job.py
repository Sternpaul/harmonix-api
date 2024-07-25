import logging
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from core import constants
from models.campaigns import Campaign
from models.referralcodes import ReferralCode
from models.referrals import Referral
from models.reward_thresholds import RewardThresholds
from models.rewards import Reward
from models.user import User
from models.user_last_30_days_tvl import UserLast30DaysTVL
from models.user_portfolio import UserPortfolio
from core.db import engine
from sqlmodel import Session, select


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session = Session(engine)


def distribute_referral_101_rewards(current_time):
    with Session(engine) as session:
        campaign_101 = session.exec(
            select(Campaign).where(
                Campaign.name == constants.Campaign.REFERRAL_101.value
            )
        ).first()
        if campaign_101 is None or campaign_101.status == constants.Status.CLOSED.value:
            return
        logger.info("Starting reward distribution job...")
        unique_referrers = []
        referrals_query = select(Referral).order_by(Referral.created_at)
        referrals = session.exec(referrals_query).all()
        for referral in referrals:
            if len(unique_referrers) >= constants.REWARD_HIGH_LIMIT:
                break

            if referral.referrer_id in unique_referrers:
                continue

            reward_query = (
                select(Reward)
                .where(Reward.user_id == referral.referrer_id)
                .order_by(Reward.start_date)
            )
            rewards = session.exec(reward_query).all()
            is_already_in_101_campaign = False
            for reward in rewards:
                if reward.campaign_name == campaign_101.name:
                    unique_referrers.append(referral.referrer_id)
                    is_already_in_101_campaign = True
                    break
            last_reward = rewards[-1]
            if rewards is None:
                continue

            if last_reward.campaign_name == campaign_101.name:
                if (
                    last_reward.end_date is not None
                    and last_reward.end_date.replace(tzinfo=timezone.utc) < current_time
                ):
                    last_reward.status = constants.Status.CLOSED
                    new_reward = Reward(
                        user_id=referral.referrer_id,
                        referral_code_id=referral.referral_code_id,
                        reward_percentage=constants.REWARD_DEFAULT_PERCENTAGE,
                        start_date=current_time,
                        end_date=None,
                        campaign_name=constants.Campaign.DEFAULT.value,
                    )
                    session.add(new_reward)
                    session.commit()
                continue
            if is_already_in_101_campaign:
                continue
            user_query = select(User).where(User.user_id == referral.referee_id)
            user = session.exec(user_query).first()
            if not user:
                continue

            user_portfolio_query = select(UserPortfolio).where(
                UserPortfolio.user_address == user.wallet_address
            )
            user_portfolios = session.exec(user_portfolio_query).all()
            for user_portfolio in user_portfolios:
                if user_portfolio.total_balance >= constants.MIN_FUNDS_FOR_HIGH_REWARD:
                    last_reward.status = constants.Status.CLOSED
                    last_reward.end_date = current_time
                    high_reward = Reward(
                        user_id=referral.referrer_id,
                        referral_code_id=referral.referral_code_id,
                        reward_percentage=constants.REWARD_HIGH_PERCENTAGE,
                        start_date=current_time,
                        end_date=current_time
                        + timedelta(constants.HIGH_REWARD_DURATION_DAYS),
                        campaign_name=campaign_101.name,
                    )
                    session.add(high_reward)
                    session.commit()
                    unique_referrers.append(referral.referrer_id)
                    break

        logger.info("Reward distribution job completed.")


def distribute_kol_and_partner_rewards(current_time):
    statement = select(Campaign).where(
        Campaign.name == constants.Campaign.KOL_AND_PARTNER.value
    )
    campaign = session.exec(statement).first()
    if campaign is None or campaign.status == constants.Status.CLOSED.value:
        return
    logger.info("Starting KOL and Partner reward distribution job...")
    rewards_thresholds = session.exec(
        select(RewardThresholds).order_by(RewardThresholds.tier)
    ).all()
    user_query = select(User).where(
        User.tier.in_([constants.UserTier.KOL.value, constants.UserTier.PARTNER.value])
    )
    users = session.exec(user_query).all()
    for user in users:
        reward_query = (
            select(Reward)
            .where(Reward.user_id == user.user_id)
            .order_by(Reward.start_date)
        )
        rewards = session.exec(reward_query).all()
        
        last_reward = rewards[-1]
        if (
            last_reward.campaign_name == constants.Campaign.KOL_AND_PARTNER.value
            or last_reward.campaign_name == constants.Campaign.DEFAULT.value
        ):
            reward_percentage = get_reward_percentage_by_user_tvl(
                rewards_thresholds, user
            )
            if reward_percentage != last_reward.reward_percentage:
                last_reward.status = constants.Status.CLOSED
                last_reward.end_date = current_time
                new_reward = Reward(
                    user_id=user.user_id,
                    referral_code_id=last_reward.referral_code_id,
                    reward_percentage=reward_percentage,
                    start_date=current_time,
                    end_date=None,
                    campaign_name=constants.Campaign.KOL_AND_PARTNER.value,
                )
                session.add(new_reward)
        session.commit()


def get_reward_percentage_by_user_tvl(rewards_thresholds, user):
    tvl = 0
    reward_percentage = 0
    user_last_30_days_tvl_query = (
        select(UserLast30DaysTVL)
        .where(UserLast30DaysTVL.user_id == user.user_id)
        .order_by(UserLast30DaysTVL.created_at.desc())
    )
    user_last_30_days_tvl = session.exec(user_last_30_days_tvl_query).first()
    if user_last_30_days_tvl is not None:
        tvl = user_last_30_days_tvl.total_value_locked
    for rewards_threshold in rewards_thresholds:
        if tvl >= rewards_threshold.threshold:
            reward_percentage = rewards_threshold.commission_rate
    return reward_percentage


if __name__ == "__main__":
    current_time = datetime.now(timezone.utc)
    distribute_referral_101_rewards(current_time)
    distribute_kol_and_partner_rewards(current_time)
