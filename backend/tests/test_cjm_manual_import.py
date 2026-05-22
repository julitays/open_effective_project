from pathlib import Path

from openpyxl import load_workbook

from app.services.imports.cjm_excel_reader import read_cjm_workbook
from app.services.imports.cjm_importer import CJMImporter
from app.services.imports.cjm_validator import validate_cjm_workbook
from scripts.generate_cjm_mvp_template import generate_template


def _minimal_workbook(path: Path) -> Path:
    generate_template(path)
    workbook = load_workbook(path)
    workbook["01_Паспорт проекта"].append(["project_001"])
    workbook["02_ЛПР"].append(["lpr_001", "Роль контроля качества"])
    workbook.save(path)
    workbook.close()
    return path


def test_generate_template_creates_excel_file(tmp_path: Path) -> None:
    output_path = tmp_path / "cjm_template.xlsx"

    generated_path = generate_template(output_path)

    assert generated_path == output_path
    assert output_path.exists()
    workbook = load_workbook(output_path)
    assert "00_Инструкция" in workbook.sheetnames
    assert "10_Что нужно дозапросить" in workbook.sheetnames
    workbook.close()


def test_reader_reads_test_excel_rows(tmp_path: Path) -> None:
    workbook_path = _minimal_workbook(tmp_path / "reader.xlsx")

    workbook = read_cjm_workbook(workbook_path)

    assert workbook.sheets["01_Паспорт проекта"].rows[0].values["Project ID"] == "project_001"
    assert workbook.sheets["02_ЛПР"].rows[0].values["LPR ID"] == "lpr_001"


def test_validator_rejects_forbidden_pii_columns(tmp_path: Path) -> None:
    workbook_path = _minimal_workbook(tmp_path / "pii.xlsx")
    workbook = load_workbook(workbook_path)
    worksheet = workbook["02_ЛПР"]
    worksheet.cell(row=1, column=worksheet.max_column + 1, value="Email")
    workbook.save(workbook_path)
    workbook.close()

    result = validate_cjm_workbook(read_cjm_workbook(workbook_path))

    assert result.has_errors
    assert any(issue.field_name == "Email" for issue in result.issues)


def test_validator_accepts_anonymized_project_and_lpr_codes(tmp_path: Path) -> None:
    workbook_path = _minimal_workbook(tmp_path / "valid.xlsx")

    result = validate_cjm_workbook(read_cjm_workbook(workbook_path))

    assert not result.has_errors
    assert result.primary_project_id == "project_001"
    assert result.identifiers["lpr_ids"] == {"lpr_001"}


def test_dry_run_does_not_open_database_session(tmp_path: Path) -> None:
    workbook_path = _minimal_workbook(tmp_path / "dry_run.xlsx")

    def fail_if_called() -> None:
        raise AssertionError("dry-run must not open a DB session")

    result = CJMImporter(
        session_factory=fail_if_called,
        report_dir=tmp_path / "reports",
    ).run(workbook_path, "dry-run")

    assert result.status == "validated"
    assert result.report_path.exists()
