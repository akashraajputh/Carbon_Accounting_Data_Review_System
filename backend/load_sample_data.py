from pathlib import Path
from django.utils import timezone

from dataapp.utils import parse_sap_rows, parse_utility_rows, parse_travel_rows
from dataapp.models import Tenant, ImportBatch, EmissionRecord

BASE = Path(__file__).resolve().parent.parent
SAMPLES_DIR = BASE / 'samples'

def import_rows(tenant, source_type, file_path):
    parsers = {'sap': parse_sap_rows, 'utility': parse_utility_rows, 'travel': parse_travel_rows}
    parser = parsers.get(source_type)
    if not parser or not file_path.exists():
        return 0
    with open(file_path, 'rb') as f:
        rows = parser(f)
    if not rows:
        return 0
    batch = ImportBatch.objects.create(
        tenant=tenant,
        source_name=source_type.title(),
        source_type=source_type,
        original_filename=file_path.name,
        row_count=len(rows),
        source_details={"imported_from": str(file_path.name), "imported_at": timezone.now().isoformat()},
    )
    created = 0
    for row in rows:
        EmissionRecord.objects.create(
            tenant=tenant,
            batch=batch,
            source_type=source_type,
            source_name=batch.source_name,
            source_row_id=row.get('source_row_id', ''),
            source_raw=row.get('source_raw', {}),
            observation_date=row.get('observation_date'),
            category=row.get('category'),
            scope=row.get('scope'),
            commodity=row.get('commodity', ''),
            location_code=row.get('location_code', ''),
            supplier=row.get('supplier', ''),
            quantity_value=row.get('quantity_value'),
            quantity_unit=row.get('quantity_unit', ''),
            normalized_quantity=row.get('normalized_quantity'),
            normalized_unit=row.get('normalized_unit', ''),
            emission_kg_co2e=row.get('emission_kg_co2e'),
            cost_usd=row.get('cost_usd'),
            description=row.get('description', ''),
            flagged_reasons=row.get('flagged_reasons', []),
        )
        created += 1
    return created


def main():
    tenant = Tenant.objects.filter(slug='acme-corp').first()
    if not tenant:
        print('No tenant acme-corp found; skipping sample import')
        return
    if EmissionRecord.objects.exists():
        print('Records already exist; skipping sample import')
        return
    mapping = {
        'sap': BASE / 'samples' / 'acme-sap.csv',
        'utility': BASE / 'samples' / 'acme-utility.csv',
        'travel': BASE / 'samples' / 'acme-travel.csv',
    }
    total = 0
    for src, path in mapping.items():
        added = import_rows(tenant, src, path)
        print(f'Imported {added} rows for {src}')
        total += added
    print(f'Total imported rows: {total}')


if __name__ == '__main__':
    main()
