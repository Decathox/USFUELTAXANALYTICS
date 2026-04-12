from datetime import date
from decimal import Decimal

from app.domain.models import StateRankingEntry, TaxRecord, FuelTaxAverages
from app.repositories.tax_repository import TaxRepository


class StateNotFoundError(Exception):
    pass

class FuelTypeNotFoundError(Exception):
    pass

# Service pour gérer la logique métier liée aux taxes sur les carburants

class TaxService:
    def __init__(self, repository: TaxRepository) -> None:
        self._repository = repository


    # Méthode pour récupérer les taxes applicables pour un code d'état et une date donnée

    def get_taxes_for_state_at_date(self, state_code: str, target_date: date) -> list[TaxRecord]:
        normalized_state = state_code.upper()

        if not self._repository.has_state(normalized_state):
            raise StateNotFoundError(f"Code état inconnu: {normalized_state}")

        return self._repository.get_applicable_taxes(normalized_state, target_date)
    

    # Méthode pour récupérer la moyenne des taxes pour un code d'état donné pour chaque type de carburant

    def get_average_taxes_for_state(self, state_code: str) -> list[FuelTaxAverages]:
        normalized_state = state_code.upper()

        if not self._repository.has_state(normalized_state):
            raise StateNotFoundError(f"Code état inconnu: {normalized_state}")

        return self._repository.get_applicable_taxes_average(normalized_state)
    

    # Méthode pour récupérer le classement des états pour une année et un type de carburant donné

    def get_state_ranking_for_year(
        self,
        year: int,
        fuel_type_code: str,
    ) -> list[StateRankingEntry]:
        normalized_fuel_code = fuel_type_code.lower()

        period_start = date(year, 1, 1)
        period_end = date(year + 1, 1, 1)

        ranking_candidates: list[tuple[str, str, str, Decimal]] = []

        for state_code, fuels in self._repository.by_state_fuel.items():
            records = fuels.get(normalized_fuel_code)
            if not records:
                continue

            average = self._repository._compute_weighted_average_for_period(
                records=records,
                period_start=period_start,
                period_end=period_end,
            )
            if average is None:
                continue

            state_name = records[0].state
            fuel_type = records[0].fuel_type

            ranking_candidates.append(
                (state_code, state_name, fuel_type, average)
            )

        if not ranking_candidates:
            raise FuelTypeNotFoundError(
                f"No ranking data found for fuel type '{normalized_fuel_code}' in year {year}"
            )

        ranking_candidates.sort(key=lambda item: (-item[3], item[0]))

        results: list[StateRankingEntry] = []
        for index, (state_code, state_name, fuel_type, average) in enumerate(ranking_candidates, start=1):
            results.append(
                StateRankingEntry(
                    rank=index,
                    state=state_name,
                    state_code=state_code,
                    fuel_type=fuel_type,
                    fuel_type_code=normalized_fuel_code,
                    average_rate=average,
                )
            )

        return results