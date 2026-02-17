from sqlalchemy.orm import Session
from app.models.master_model import Plant, Unit, FileIngestionLog, UploadStatus
from app.utils.file_parser import read_file
import traceback
import pandas as pd


# ============================
# COLUMN NORMALIZATION
# ============================

COLUMN_MAPPING_PLANT = {
    "plant_name": ["plant_name", "name", "plant"],
    "plant_code": ["plant_code", "code"],
    "type_id": ["type_id", "type"],
    "state": ["state"],
    "district": ["district"],
    "status": ["status"],
    "installed_capacity_mw": ["installed_capacity_mw", "capacity"],
    "implementing_agency": ["implementing_agency", "agency"],
    "sector": ["sector"],
    "commissioning_date": ["commissioning_date"],
    "retirement_date": ["retirement_date"]
}

COLUMN_MAPPING_UNIT = {
    "plant_id": ["plant_id"],
    "unit_code": ["unit_code"],
    "unit_capacity_mw": ["unit_capacity_mw", "capacity"],
    "commissioning_date": ["commissioning_date"],
    "status": ["status"]
}


# ============================
# NORMALIZE COLUMN NAMES
# ============================

def normalize_columns(df, mapping):

    df.columns = df.columns.str.strip().str.lower()

    new_columns = {}

    for standard, variations in mapping.items():

        for col in df.columns:

            if col in variations:
                new_columns[col] = standard

    df = df.rename(columns=new_columns)

    return df


# ============================
# VALIDATE REQUIRED FIELDS
# ============================

def validate_required(df, required_fields):

    errors = []

    for field in required_fields:

        if field not in df.columns:
            errors.append(f"Missing column: {field}")
            continue

        empty_rows = df[df[field].isna()]

        if not empty_rows.empty:
            errors.append(f"{field} has empty values in rows: {list(empty_rows.index)}")

    return errors


# ============================
# PREVIEW PLANTS
# ============================

def preview_plants(upload_file):

    df = read_file(upload_file)

    df = normalize_columns(df , COLUMN_MAPPING_PLANT)


    required = ["plant_name", "type_id", "state", "district"]

    errors = validate_required(df, required)

    return {
        "preview": df.fillna("").to_dict(orient="records"),
        "errors": errors,
        "total_rows": len(df)
    }


# ============================
# SAVE PLANTS
# ============================
# 
def upload_plants(upload_file, db: Session):

    log = FileIngestionLog(
        filename=upload_file.filename,
        data_category="plant",
        status=UploadStatus.PROCESSING
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    try:

        df = read_file(upload_file)

        df = normalize_columns(df, COLUMN_MAPPING_PLANT)

        required = ["plant_name", "type_id", "state", "district"]

        errors = validate_required(df, required)

        if errors:

            log.status = UploadStatus.FAILED
            log.error_log = str(errors)
            db.commit()

            return {
                "status": "error",
                "errors": errors
            }

        rows = 0

        for _, row in df.iterrows():

            plant = Plant(

                plant_code=row.get("plant_code") or row["plant_name"],

                plant_name=row["plant_name"],

                type_id=int(row["type_id"]),

                state=row["state"],

                district=row["district"],

                status=row.get("status") or "ACTIVE",

                installed_capacity_mw=row.get("installed_capacity_mw"),

                implementing_agency=row.get("implementing_agency"),

                sector=row.get("sector"),

                commissioning_date=row.get("commissioning_date"),

                retirement_date=row.get("retirement_date")

            )

            db.add(plant)

            rows += 1

        db.commit()

        log.status = UploadStatus.SUCCESS
        log.rows_inserted = rows

        db.commit()

        return {
            "status": "success",
            "rows_inserted": rows
        }

    except Exception as e:

        log.status = UploadStatus.FAILED
        log.error_log = traceback.format_exc()

        db.commit()

        raise e


# ============================
# PREVIEW UNITS
# ============================

def preview_units(upload_file):

    df = read_file(upload_file)

    df = normalize_columns(df, COLUMN_MAPPING_UNIT)

    required = ["plant_id"]

    errors = validate_required(df, required)

    return {
        "preview": df.fillna("").to_dict(orient="records"),
        "errors": errors,
        "total_rows": len(df)
        
    }


# ============================
# SAVE UNITS
# ============================

def upload_units(upload_file, db: Session):

    log = FileIngestionLog(
        filename=upload_file.filename,
        data_category="unit",
        status=UploadStatus.PROCESSING
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    try:

        df = read_file(upload_file)

        df = normalize_columns(df, COLUMN_MAPPING_UNIT)

        required = ["plant_id"]

        errors = validate_required(df, required)

        if errors:

            log.status = UploadStatus.FAILED
            log.error_log = str(errors)
            db.commit()

            return {
                "status": "error",
                "errors": errors
            }

        rows = 0

        for _, row in df.iterrows():

            unit = Unit(

                plant_id=int(row["plant_id"]),

                unit_code=row.get("unit_code"),

                unit_capacity_mw=row.get("unit_capacity_mw"),

                commissioning_date=row.get("commissioning_date"),

                status=row.get("status") or "ACTIVE"

            )

            db.add(unit)

            rows += 1

        db.commit()

        log.status = UploadStatus.SUCCESS
        log.rows_inserted = rows

        db.commit()

        return {
            "status": "success",
            "rows_inserted": rows
        }

    except Exception as e:

        log.status = UploadStatus.FAILED
        log.error_log = traceback.format_exc()

        db.commit()

        raise e




# =========================
# REQUIRED FIELDS
# =========================

PLANT_REQUIRED = ["plant_name", "type_id"]
UNIT_REQUIRED = ["plant_id", "unit_code"]


# =========================
# DUPLICATE CHECK
# =========================

def is_duplicate_plant(db, plant_code):

    return db.query(Plant)\
        .filter(Plant.plant_code == plant_code)\
        .first() is not None


def is_duplicate_unit(db, plant_id, unit_code):

    return db.query(Unit)\
        .filter(
            Unit.plant_id == plant_id,
            Unit.unit_code == unit_code
        ).first() is not None


# =========================
# PREVIEW
# =========================

def preview_upload(file, category, db: Session):

    df = read_file(file)

    total = len(df)

    valid = 0
    invalid = 0
    duplicate = 0

    preview = []

    for index, row in df.iterrows():

        row_dict = row.to_dict()

        errors = []

        if category == "plant":

            for field in PLANT_REQUIRED:
                if pd.isna(row.get(field)):
                    errors.append(f"{field} required")

            plant_code = row.get("plant_code") or row.get("plant_name")

            if plant_code and is_duplicate_plant(db, plant_code):
                duplicate += 1
                errors.append("Duplicate")

        else:

            for field in UNIT_REQUIRED:
                if pd.isna(row.get(field)):
                    errors.append(f"{field} required")

            if is_duplicate_unit(
                db,
                row.get("plant_id"),
                row.get("unit_code")
            ):
                duplicate += 1
                errors.append("Duplicate")


        if errors:
            invalid += 1
        else:
            valid += 1

        row_dict["errors"] = errors

        preview.append(row_dict)


    return {

        "filename": file.filename,

        "total_rows": total,

        "valid_rows": valid,

        "invalid_rows": invalid,

        "duplicate_rows": duplicate,

        "preview_data": preview[:10],

        "message": "Preview generated"
    }


# =========================
# FINAL UPLOAD
# =========================

def upload_file(file, category, db: Session):

    log = FileIngestionLog(

        filename=file.filename,

        data_category=category,

        status=UploadStatus.PROCESSING
    )

    db.add(log)
    db.commit()
    db.refresh(log)


    try:

        df = read_file(file)

        inserted = 0
        duplicate = 0


        for _, row in df.iterrows():

            if category == "plant":

                plant_code = row.get("plant_code") or row.get("plant_name")

                if is_duplicate_plant(db, plant_code):
                    duplicate += 1
                    continue


                plant = Plant(

                    plant_code=plant_code,

                    plant_name=row.get("plant_name"),

                    type_id=row.get("type_id"),

                    state=row.get("state"),

                    district=row.get("district"),

                    status=row.get("status", "ACTIVE"),

                    installed_capacity_mw=row.get("installed_capacity_mw"),

                    implementing_agency=row.get("implementing_agency"),

                    sector=row.get("sector"),

                    commissioning_date=row.get("commissioning_date")
                )

                db.add(plant)
                inserted += 1


            else:

                if is_duplicate_unit(
                    db,
                    row.get("plant_id"),
                    row.get("unit_code")
                ):
                    duplicate += 1
                    continue


                unit = Unit(

                    plant_id=row.get("plant_id"),

                    unit_code=row.get("unit_code"),

                    unit_capacity_mw=row.get("unit_capacity_mw"),

                    commissioning_date=row.get("commissioning_date"),

                    status=row.get("status", "ACTIVE")
                )

                db.add(unit)
                inserted += 1


        db.commit()


        log.status = UploadStatus.SUCCESS
        log.rows_inserted = inserted

        db.commit()


        return {

            "status": "success",

            "rows_inserted": inserted,

            "duplicate_rows": duplicate,

            "message": "Upload successful"
        }


    except Exception as e:

        log.status = UploadStatus.FAILED

        log.error_log = traceback.format_exc()

        db.commit()

        raise e






# =========================
# CONFIRM UPLOAD FUNCTION
# =========================

def confirm_upload(upload_file, data_type: str, db: Session):

    # select correct mapping
    if data_type == "plant":
        mapping = COLUMN_MAPPING_PLANT
        required = PLANT_REQUIRED
    else:
        mapping = COLUMN_MAPPING_UNIT
        required = UNIT_REQUIRED

    df = read_file(upload_file)

    # normalize columns
    df = normalize_columns(df, mapping)

    inserted = 0
    failed = 0
    duplicate = 0
    errors = []

    # create ingestion log
    log = FileIngestionLog(
        filename=upload_file.filename,
        data_category=data_type,
        status=UploadStatus.PROCESSING
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    try:

        for i, row in df.iterrows():

            try:

                # check required fields
                missing = False
                for field in required:
                    if pd.isna(row.get(field)):
                        missing = True
                        break

                if missing:
                    failed += 1
                    continue


                # =====================
                # PLANT INSERT
                # =====================

                if data_type == "plant":

                    plant_code = str(
                        row.get("plant_code") or row.get("plant_name")
                    ).strip()

                    if is_duplicate_plant(db, plant_code):
                        duplicate += 1
                        continue

                    plant = Plant(
                        plant_code=plant_code,
                        plant_name=row.get("plant_name"),
                        type_id=int(row.get("type_id")),
                        state=row.get("state"),
                        district=row.get("district"),
                        installed_capacity_mw=row.get("installed_capacity_mw"),
                        implementing_agency=row.get("implementing_agency"),
                        sector=row.get("sector"),
                        commissioning_date=row.get("commissioning_date"),
                        retirement_date=row.get("retirement_date"),
                        status=row.get("status", "ACTIVE")
                    )

                    db.add(plant)
                    inserted += 1


                # =====================
                # UNIT INSERT
                # =====================

                else:

                    plant_id = int(row.get("plant_id"))
                    unit_code = row.get("unit_code")

                    if is_duplicate_unit(db, plant_id, unit_code):
                        duplicate += 1
                        continue

                    unit = Unit(
                        plant_id=plant_id,
                        unit_code=unit_code,
                        unit_capacity_mw=row.get("unit_capacity_mw"),
                        commissioning_date=row.get("commissioning_date"),
                        status=row.get("status", "ACTIVE")
                    )

                    db.add(unit)
                    inserted += 1


            except Exception as e:

                failed += 1
                errors.append(f"Row {i+1}: {str(e)}")


        db.commit()

        # update log
        log.status = UploadStatus.SUCCESS
        log.rows_inserted = inserted
        log.error_log = "\n".join(errors)

        db.commit()

        # ✅ IMPORTANT: return ALL schema fields
        return {

            "success": True,

            "message": "Upload completed",

            "inserted": inserted,

            "failed": failed,

            "errors": errors,

            "status": "SUCCESS",

            "rows_inserted": inserted,

            "duplicate_rows": duplicate
        }


    except Exception as e:

        log.status = UploadStatus.FAILED
        log.error_log = traceback.format_exc()

        db.commit()

        raise e
