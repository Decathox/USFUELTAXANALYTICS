from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.schemas.fuel_taxes import FuelTaxItemResponse, RankingItemResponse, RankingResponse, StateAverageTaxResponse, FuelAverageItemResponse, StateTaxesResponse
from app.services.tax_service import FuelTypeNotFoundError, StateNotFoundError, TaxService

router = APIRouter(prefix="/USFuelTaxes", tags=["Fuel Taxes Data"])


def get_tax_service(request: Request) -> TaxService:
    return request.app.state.tax_service

# Endpoint pour récupérer les taxes applicables pour un code d'état et une date donnée

@router.get("/{state_code}/taxes_at_date", response_model=StateTaxesResponse)
def get_state_taxes_at_date(
    state_code: str,
    date_value: date = Query(..., alias="date"),
    tax_service: TaxService = Depends(get_tax_service),
) -> StateTaxesResponse:
    try:
        records = tax_service.get_taxes_for_state_at_date(state_code, date_value)
    except StateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return StateTaxesResponse(
        state_code=state_code.upper(),
        date=date_value,
        taxes=[
            FuelTaxItemResponse(
                fuel_type=record.fuel_type,
                fuel_type_code=record.fuel_type_code,
                rate=record.rate,
                effective_date=record.effective_date,
            )
            for record in records
        ],
    )



# Endpoint pour récupérer la moyenne des taxes pour un code d'état donné pour chaque type de carburant (pas de moyenne pondérée)

@router.get("/{state_code}/taxes_averages_by_fuels", response_model=StateAverageTaxResponse)
def get_state_average_taxes(
    state_code: str,
    tax_service: TaxService = Depends(get_tax_service),
) -> StateAverageTaxResponse:
    try:
        records = tax_service.get_average_taxes_for_state(state_code)
    except StateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return StateAverageTaxResponse(
        state_code=state_code.upper(),
        average_rates=[
            FuelAverageItemResponse(
                fuel_type=record.fuel_type,
                fuel_type_code=record.fuel_type_code,
                average_rate=record.average_rate,
            )
            for record in records
        ],
    )


# Endpoint pour récupérer le classement des états pour une année et un type de carburant donné

@router.get("/rankings", response_model=RankingResponse)
def get_ranking(
    year: int = Query(..., ge=1),
    fuel_type_code: str = Query(...),
    tax_service: TaxService = Depends(get_tax_service),
) -> RankingResponse:
    try:
        ranking = tax_service.get_state_ranking_for_year(year, fuel_type_code)
    except FuelTypeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RankingResponse(
        year=year,
        fuel_type_code=fuel_type_code.lower(),
        ranking=[
            RankingItemResponse(
                rank=item.rank,
                state=item.state,
                state_code=item.state_code,
                fuel_type=item.fuel_type,
                fuel_type_code=item.fuel_type_code,
                average_rate=item.average_rate,
            )
            for item in ranking
        ],
    )