from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class TaxRecord:
    id: str
    state: str
    state_code: str
    fuel_type: str
    fuel_type_code: str
    effective_date: date
    mmfr_year: int
    rate: Decimal

@dataclass(frozen=True)
class FuelTaxAverages:
    fuel_type: str
    fuel_type_code: str
    average_rate: Decimal

@dataclass(frozen=True)
class StateRankingEntry:
    rank: int
    state: str
    state_code: str
    fuel_type: str
    fuel_type_code: str
    average_rate: Decimal