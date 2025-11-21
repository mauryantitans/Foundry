from dataclasses import dataclass

@dataclass
class TierConfig:
    requests_per_minute: int
    tokens_per_minute: int
    name: str

# Free Tier: 15 RPM (conservative to avoid 429s)
FREE_TIER = TierConfig(
    requests_per_minute=15,
    tokens_per_minute=1000000, # High enough to not be the bottleneck usually
    name="FREE"
)

# Paid Tier: 1000 RPM (standard paid limit)
PAID_TIER = TierConfig(
    requests_per_minute=1000,
    tokens_per_minute=4000000,
    name="PAID"
)

def get_config(tier_name: str) -> TierConfig:
    if tier_name.lower() == "paid":
        return PAID_TIER
    return FREE_TIER
