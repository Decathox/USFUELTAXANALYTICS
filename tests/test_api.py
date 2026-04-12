from datetime import date
from decimal import Decimal

import pytest

from domain.models import TaxRecord
from repositories.tax_repository import TaxRepository
from services.tax_service import StateNotFoundError, TaxService


def make_record(
    *,
    record_id: str,
    state: str,
    state_code: str,
    fuel_type: str,
    fuel_type_code: str,
    effective_date: date,
    mmfr_year: int,
    rate: str,
) -> TaxRecord:
    return TaxRecord(
        id=record_id,
        state=state,
        state_code=state_code,
        fuel_type=fuel_type,
        fuel_type_code=fuel_type_code,
        effective_date=effective_date,
        mmfr_year=mmfr_year,
        rate=Decimal(rate),
    )


@pytest.fixture
def repository() -> TaxRepository:
    repo = TaxRepository()

    # Alabama - Gasoline
    repo.add_record(
        make_record(
            record_id="al-gas-1",
            state="Alabama",
            state_code="AL",
            fuel_type="Gasoline",
            fuel_type_code="1a",
            effective_date=date(2020, 1, 1),
            mmfr_year=2020,
            rate="10",
        )
    )
    repo.add_record(
        make_record(
            record_id="al-gas-2",
            state="Alabama",
            state_code="AL",
            fuel_type="Gasoline",
            fuel_type_code="1a",
            effective_date=date(2020, 7, 1),
            mmfr_year=2020,
            rate="20",
        )
    )

    # Alabama - Diesel
    repo.add_record(
        make_record(
            record_id="al-diesel-1",
            state="Alabama",
            state_code="AL",
            fuel_type="Diesel",
            fuel_type_code="2a",
            effective_date=date(2020, 1, 1),
            mmfr_year=2020,
            rate="15",
        )
    )

    # Alaska - Gasoline
    repo.add_record(
        make_record(
            record_id="ak-gas-1",
            state="Alaska",
            state_code="AK",
            fuel_type="Gasoline",
            fuel_type_code="1a",
            effective_date=date(2020, 1, 1),
            mmfr_year=2020,
            rate="30",
        )
    )

    # Arizona - Gasoline
    repo.add_record(
        make_record(
            record_id="az-gas-1",
            state="Arizona",
            state_code="AZ",
            fuel_type="Gasoline",
            fuel_type_code="1a",
            effective_date=date(2020, 1, 1),
            mmfr_year=2020,
            rate="30",
        )
    )

    repo.finalize()
    return repo


@pytest.fixture
def service(repository: TaxRepository) -> TaxService:
    return TaxService(repository)


def test_get_taxes_for_state_at_date_returns_applicable_rates(service: TaxService) -> None:
    records = service.get_taxes_for_state_at_date("AL", date(2020, 8, 1))

    assert len(records) == 2

    gasoline = next(r for r in records if r.fuel_type_code == "1a")
    diesel = next(r for r in records if r.fuel_type_code == "2a")

    assert gasoline.rate == Decimal("20")
    assert gasoline.effective_date == date(2020, 7, 1)

    assert diesel.rate == Decimal("15")
    assert diesel.effective_date == date(2020, 1, 1)


def test_get_taxes_for_state_at_date_raises_for_unknown_state(service: TaxService) -> None:
    with pytest.raises(StateNotFoundError):
        service.get_taxes_for_state_at_date("ZZ", date(2020, 8, 1))


def test_weighted_average_for_state_gasoline(service: TaxService) -> None:
    """
    Alabama / Gasoline en 2020 :
    - 10 du 2020-01-01 au 2020-07-01
    - 20 du 2020-07-01 au 2021-01-01

    La moyenne pondérée doit donc être strictement entre 10 et 20,
    et proche de 15 sur une année découpée en deux moitiés presque égales.
    """
    averages = service.get_average_taxes_for_state("AL")

    gasoline = next(item for item in averages if item.fuel_type_code == "1a")
    diesel = next(item for item in averages if item.fuel_type_code == "2a")

    assert gasoline.average_rate == Decimal("15")
    assert diesel.average_rate == Decimal("15")


def test_ranking_returns_complete_order_for_year(service: TaxService) -> None:
    ranking = service.get_state_ranking_for_year(2020, "1a")

    assert [item.state_code for item in ranking] == ["AK", "AZ", "AL"]
    assert ranking[0].average_rate == Decimal("30")
    assert ranking[1].average_rate == Decimal("30")
    assert ranking[2].average_rate == Decimal("15.02732240437158469945355191")


def test_ranking_handles_ties_with_same_rank(service: TaxService) -> None:
    ranking = service.get_state_ranking_for_year(2020, "1a")

    ak = next(item for item in ranking if item.state_code == "AK")
    az = next(item for item in ranking if item.state_code == "AZ")
    al = next(item for item in ranking if item.state_code == "AL")

    assert ak.rank == 1
    assert az.rank == 2
    assert al.rank == 3