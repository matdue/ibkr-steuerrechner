from dataclasses import dataclass


@dataclass
class Asset:
    symbol: str
    con_id: str
    asset_class: str
    sub_category: str | None = None
