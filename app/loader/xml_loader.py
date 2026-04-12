import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.domain.models import TaxRecord
from app.repositories.tax_repository import TaxRepository


class XmlParsingError(Exception):
    """Erreur structurelle liée au fichier XML."""


@dataclass(frozen=True)
class LoadResult:
    total_rows_seen: int
    loaded_rows: int
    skipped_duplicate_ids: int
    skipped_invalid_rows: int


class XmlTaxLoader:
    """Charge les enregistrements de taxes depuis un fichier XML et les ajoute à une structure TaxRepository."""
    def load_into_repository(self, file_path: str | Path, repository: TaxRepository) -> LoadResult:
        path = Path(file_path)

        if not path.exists():
            raise XmlParsingError(f"Fichier XML introuvable : {path}")

        if not path.is_file():
            raise XmlParsingError(f"Le chemin ne pointe pas vers un fichier : {path}")

        seen_ids: set[str] = set()
        total_rows_seen = 0
        skipped_duplicate_ids = 0
        skipped_invalid_rows = 0

        try:
            context = ET.iterparse(path, events=("end",))

            for _, elem in context:
                if elem.tag != "row":
                    continue

                if elem.find("id") is None:
                    elem.clear()
                    continue

                total_rows_seen += 1

                record = self._parse_row_or_none(elem)
                if record is None:
                    skipped_invalid_rows += 1
                    elem.clear()
                    continue

                if record.id in seen_ids:
                    skipped_duplicate_ids += 1
                    elem.clear()
                    continue

                seen_ids.add(record.id)
                repository.add_record(record)
                elem.clear()

        except ET.ParseError as exc:
            raise XmlParsingError(f"XML invalide : {exc}") from exc

        repository.finalize()

        return LoadResult(
            total_rows_seen=total_rows_seen,
            loaded_rows=repository.total_records,
            skipped_duplicate_ids=skipped_duplicate_ids,
            skipped_invalid_rows=skipped_invalid_rows,
        )

    def _parse_row_or_none(self, elem: ET.Element) -> TaxRecord | None:
        def get_required_text(tag: str) -> str | None:
            child = elem.find(tag)
            if child is None or child.text is None:
                return None

            value = child.text.strip()
            return value or None

        try:
            row_id = get_required_text("id")
            state = get_required_text("state")
            state_code = get_required_text("abbrev")
            fuel_type = get_required_text("fuel_type")
            fuel_type_code = get_required_text("fuel_type_code")
            effective_date_raw = get_required_text("effective_date")
            mmfr_year_raw = get_required_text("mmfr_year")
            rate_raw = get_required_text("rate")

            if not all([
                row_id,
                state,
                state_code,
                fuel_type,
                fuel_type_code,
                effective_date_raw,
                mmfr_year_raw,
                rate_raw,
            ]):
                return None

            return TaxRecord(
                id=row_id,
                state=state,
                state_code=state_code.upper(),
                fuel_type=fuel_type,
                fuel_type_code=fuel_type_code.lower(),
                effective_date=datetime.fromisoformat(effective_date_raw).date(),
                mmfr_year=int(mmfr_year_raw),
                rate=Decimal(rate_raw),
            )

        except (ValueError, InvalidOperation):
            return None