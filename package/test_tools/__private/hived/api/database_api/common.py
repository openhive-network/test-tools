from __future__ import annotations

from typing import Literal


class DatabaseApiCommons:
    PACK_TYPES = Literal["legacy", "hf26"]
    PROPOSAL_STATUS = Literal["all", "inactive", "active", "expired", "votable"]
    SORT_DIRECTION = Literal["ascending", "descending"]
    SORT_TYPES = Literal[
        "by_name",
        "by_proxy",
        "by_next_vesting_withdrawal",
        "by_account",
        "by_expiration",
        "by_effective_date",
        "by_vote_name",
        "by_schedule_time",
        "by_account_witness",
        "by_witness_account",
        "by_from_id",
        "by_ratification_deadline",
        "by_withdraw_route",
        "by_destination",
        "by_complete_from_id",
        "by_to_complete",
        "by_delegation",
        "by_account_expiration",
        "by_conversion_date",
        "by_cashout_time",
        "by_permlink",
        "by_parent",
        "by_comment_voter",
        "by_voter_comment",
        "by_price",
        "by_symbol_contributor",
        "by_symbol",
        "by_control_account",
        "by_symbol_time",
        "by_creator",
        "by_start_date",
        "by_end_date",
        "by_total_votes",
        "by_voter_proposal",
        "by_proposal_voter",
        "by_contributor",
        "by_symbol_id",
        "not_set",
    ]
