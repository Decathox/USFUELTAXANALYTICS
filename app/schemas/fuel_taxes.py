from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class FuelTaxItemResponse(BaseModel):
    fuel_type: str
    fuel_type_code: str
    rate: Decimal
    effective_date: date

class StateTaxesResponse(BaseModel):
    state_code: str
    date: date
    taxes: list[FuelTaxItemResponse]

class FuelAverageItemResponse(BaseModel):
    fuel_type: str
    fuel_type_code: str
    average_rate: Decimal

class StateAverageTaxResponse(BaseModel):
    state_code: str
    average_rates: list[FuelAverageItemResponse]

class RankingItemResponse(BaseModel):
    rank: int
    state: str
    state_code: str
    fuel_type: str
    fuel_type_code: str
    average_rate: Decimal


class RankingResponse(BaseModel):
    year: int
    fuel_type_code: str
    ranking: list[RankingItemResponse]