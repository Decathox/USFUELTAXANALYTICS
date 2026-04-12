from bisect import bisect_right
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import DefaultDict

from app.domain.models import FuelTaxAverages, TaxRecord


@dataclass
class TaxRepository:
    by_state_fuel: DefaultDict[str, DefaultDict[str, list[TaxRecord]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )
    total_records: int = 0



    # Méthode pour ajouter un enregistrement de taxe à la structure de données

    def add_record(self, record: TaxRecord) -> None:
        self.by_state_fuel[record.state_code][record.fuel_type_code].append(record)
        self.total_records += 1



    # Méthode à appeler après avoir ajouté tous les enregistrements pour trier les listes par date effective

    def finalize(self) -> None:
        for fuels in self.by_state_fuel.values():
            for records in fuels.values():
                records.sort(key=lambda r: r.effective_date)



    # Méthode pour vérifier si un code d'état est connu

    def has_state(self, state_code: str) -> bool:
        return state_code.upper() in self.by_state_fuel



    # Méthode pour récupérer les taxes applicables pour un code d'état et une date donnée

    def get_applicable_taxes(self, state_code: str, target_date: date) -> list[TaxRecord]:
        fuels = self.by_state_fuel.get(state_code.upper())
        if not fuels:
            return []

        result: list[TaxRecord] = []

        for records in fuels.values():
            applicable = self._find_applicable_record(records, target_date)
            if applicable is not None:
                result.append(applicable)

        result.sort(key=lambda r: r.fuel_type_code)
        return result

    # Méthode pour récupérer la moyenne des taxes pour un code d'état donné pour chaque type de carburant

    def get_applicable_taxes_average(self, state_code: str) -> list[FuelTaxAverages]:
        fuels = self.by_state_fuel.get(state_code.upper())
        if not fuels:
            return []

        result: list[FuelTaxAverages] = []

        for records in fuels.values():
            applicable = self._calc_average(records)
            if applicable is not None:
                result.append(applicable)

        result.sort(key=lambda r: r.fuel_type_code)
        return result

    # Méthode utilitaire pour trouver l'enregistrement de taxe applicable dans une liste triée par date effective

    @staticmethod
    def _find_applicable_record(records: list[TaxRecord], target_date: date) -> TaxRecord | None:
        if not records:
            return None

        dates = [record.effective_date for record in records]
        idx = bisect_right(dates, target_date) - 1

        if idx < 0:
            return None

        return records[idx]
    


    # Méthode utilitaire pour calculer la moyenne des taux à partir d'une liste d'enregistrements

    @staticmethod    
    def _calc_average(records: list[TaxRecord]) -> FuelTaxAverages | None:
        if not records:
            return None

        total = sum(record.rate for record in records)
        count = len(records)
        average_rate = total / count if count > 0 else Decimal(-1)

        return FuelTaxAverages(
            fuel_type=records[0].fuel_type,
            fuel_type_code=records[0].fuel_type_code,
            average_rate=average_rate,
        )
    

    @staticmethod
    def _compute_weighted_average_for_period(
    records: list[TaxRecord],
    period_start: date,
    period_end: date,
) -> Decimal | None:
        
        if not records or period_start >= period_end:
            return None

        dates = [record.effective_date for record in records]

        active_index = bisect_right(dates, period_start) - 1
        next_index = bisect_right(dates, period_start)

        relevant_records: list[TaxRecord] = []

        # Taux actif au début de période
        if active_index >= 0:
            relevant_records.append(records[active_index])

        # Changements intervenant pendant la période
        idx = next_index
        while idx < len(records) and records[idx].effective_date < period_end:
            relevant_records.append(records[idx])
            idx += 1

        if not relevant_records:
            return None

        weighted_sum = Decimal("0")
        total_days = 0

        for i, record in enumerate(relevant_records):
            segment_start = max(record.effective_date, period_start)

            if i + 1 < len(relevant_records):
                segment_end = min(relevant_records[i + 1].effective_date, period_end)
            else:
                segment_end = period_end

            duration_days = (segment_end - segment_start).days
            if duration_days <= 0:
                continue

            weighted_sum += record.rate * Decimal(duration_days)
            total_days += duration_days

        if total_days == 0:
            return None

        return weighted_sum / Decimal(total_days)