from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.fuel_taxes import router as fuel_taxes_router
from app.loader.xml_loader import XmlTaxLoader
from app.repositories.tax_repository import TaxRepository
from app.services.tax_service import TaxService


# Démarrage de l'API avec un contexte de durée de vie pour charger les données depuis le fichier XML avant de servir les requêtes

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Création du repository et chargement des données depuis le fichier XML

    repository = TaxRepository()
    loader = XmlTaxLoader()



    # Chargement des données et affichage d'un résumé dans la console

    result = loader.load_into_repository("app/dataset.xml", repository)

    app.state.tax_repository = repository
    app.state.tax_service = TaxService(repository)

    print(
        "Fuel tax data loaded | "
        f"seen={result.total_rows_seen} "
        f"loaded={result.loaded_rows} "
        f"invalid={result.skipped_invalid_rows} "
        f"duplicate_ids={result.skipped_duplicate_ids}"
    )

    yield




app = FastAPI(
    title="US Fuel Tax Analytics API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(fuel_taxes_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}