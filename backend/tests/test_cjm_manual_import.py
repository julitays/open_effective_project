from pathlib import Path

from openpyxl import load_workbook
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Base, ClientExpectation, LPRProfile, ProjectBarrier
from app.services.imports.cjm_excel_reader import read_cjm_workbook
from app.services.imports.cjm_importer import (
    CJMImporter,
    normalize_external_lpr_aliases,
    should_skip_plan_commit,
)
from app.services.imports.cjm_validator import validate_cjm_workbook
from scripts.generate_cjm_mvp_template import generate_template


def _minimal_workbook(path: Path) -> Path:
    generate_template(path)
    workbook = load_workbook(path)
    workbook["01_Паспорт проекта"].append(["project_001", "external_project_001"])
    workbook["02_ЛПР"].append(["lpr_001", "external_lpr_001", "Роль контроля качества"])
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
    assert "09_Что нужно дозапросить" in workbook.sheetnames
    assert "04_История опросов" not in workbook.sheetnames
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


def test_validator_rejects_prohibited_methodology_sheet(tmp_path: Path) -> None:
    workbook_path = _minimal_workbook(tmp_path / "ai_resume.xlsx")
    workbook = load_workbook(workbook_path)
    workbook.create_sheet("AI-резюме")
    workbook.save(workbook_path)
    workbook.close()

    result = validate_cjm_workbook(read_cjm_workbook(workbook_path))

    assert result.has_errors
    assert any(issue.sheet_name == "AI-резюме" for issue in result.issues)


def test_ai_hypothesis_plan_is_marked_for_commit_skip(tmp_path: Path) -> None:
    workbook_path = _minimal_workbook(tmp_path / "ai_plan.xlsx")
    workbook = load_workbook(workbook_path)
    workbook["04_Барьеры"].append(
        ["barrier_001", "Риск задержки", "Сроки", "Есть сейчас", None, "Высокая"]
    )
    workbook["08_Планы действий"].append(
        [
            "plan_001",
            "barrier_001",
            None,
            "Профилактика",
            "Проверить статус договоренностей",
            "Роль проекта",
            None,
            "Сделать",
            "Восстановленный CJM",
            "AI-гипотеза",
        ]
    )
    workbook.save(workbook_path)
    workbook.close()

    result = validate_cjm_workbook(read_cjm_workbook(workbook_path))

    plan_row = result.normalized_sheets["08_Планы действий"][0]
    assert should_skip_plan_commit(plan_row)


def test_validator_accepts_optional_project_goals_sheet(tmp_path: Path) -> None:
    workbook_path = _minimal_workbook(tmp_path / "goals.xlsx")
    workbook = load_workbook(workbook_path)
    worksheet = workbook.create_sheet("08_Цели проекта")
    worksheet.append(
        [
            "Goal ID",
            "Project ID",
            "Тип цели",
            "Цель проекта",
            "Источник",
            "Связанный KPI / критерий",
            "Статус актуальности",
            "Уверенность вывода",
            "Комментарий",
        ]
    )
    worksheet.append(["goal_001", "project_001", "service", "Сохранить качество услуги"])
    workbook.save(workbook_path)
    workbook.close()

    result = validate_cjm_workbook(read_cjm_workbook(workbook_path))

    assert not result.has_errors
    assert len(result.normalized_sheets["08_Цели проекта"]) == 1


def test_external_lpr_aliases_are_kept_on_one_profile() -> None:
    assert normalize_external_lpr_aliases("845", "55", "845; 55") == "845; 55"


def test_commit_import_keeps_text_kpi_links(tmp_path: Path) -> None:
    workbook_path = _minimal_workbook(tmp_path / "text_kpi_links.xlsx")
    workbook = load_workbook(workbook_path)
    workbook["02_ЛПР"].append(["lpr_007", "845", "Региональная роль"])
    workbook["02_ЛПР"].append(["lpr_007", "55", "Региональная роль"])
    workbook["04_Барьеры"].append(
        [
            "barrier_001",
            "Риск задержки",
            "timing",
            "current",
            None,
            "high",
            "lpr_007",
            "845; 55",
            None,
            "scorecard; эффективность мерча",
        ]
    )
    workbook["05_Ожидания клиента"].append(
        [
            "expectation_001",
            "Стабильное качество исполнения",
            "quality",
            "explicit",
            "high",
            "lpr_007",
            "845; 55",
            None,
            "OSA; ISA; PSS",
        ]
    )
    workbook.save(workbook_path)
    workbook.close()

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    test_session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    result = CJMImporter(
        session_factory=test_session_factory,
        report_dir=tmp_path / "reports",
    ).run(workbook_path, "commit")

    assert result.committed
    with test_session_factory() as session:
        lpr = session.scalar(select(LPRProfile).where(LPRProfile.lpr_code == "lpr_007"))
        barrier = session.scalar(
            select(ProjectBarrier).where(ProjectBarrier.source_id == "barrier_001")
        )
        expectation = session.scalar(
            select(ClientExpectation).where(
                ClientExpectation.expectation_text == "Стабильное качество исполнения"
            )
        )

    assert lpr is not None
    assert lpr.external_lpr_id == "845; 55"
    assert barrier is not None
    assert barrier.linked_kpi_text == "scorecard; эффективность мерча"
    assert expectation is not None
    assert expectation.linked_kpi_text == "OSA; ISA; PSS"
