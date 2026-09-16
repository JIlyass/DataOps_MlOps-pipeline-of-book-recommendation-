"""
Assets Dagster pour le pipeline DataOps Book Recommender.
Chaque asset = une étape du pipeline.
"""
import subprocess
import sys
import shutil
import os
from pathlib import Path
from dagster import asset, AssetExecutionContext

# --- Chemins ----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DBT_PROJECT_DIR = PROJECT_ROOT / "dataops" / "dbt_project" / "book_transform"
INGEST_SCRIPT = PROJECT_ROOT / "dataops" / "ingestion" / "ingest.py"
DBT_EXECUTABLE = shutil.which("dbt")


def run_command(cmd: list, cwd: Path, step_name: str) -> str:
    """Execute une commande en forcant l'encodage UTF-8."""
    print(f"\n{'=' * 70}")
    print(f">>> {step_name}")
    print(f"    cwd : {cwd}")
    print(f"    cmd : {' '.join(str(c) for c in cmd)}")
    print(f"{'=' * 70}")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    result = subprocess.run(
        [str(c) for c in cmd],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    print(f"--- {step_name} STDOUT ---")
    print(result.stdout)

    if result.returncode != 0:
        print(f"--- {step_name} STDERR ---")
        print(result.stderr)
        raise Exception(f"[ERROR] Echec de {step_name} (code {result.returncode})")

    return result.stdout


# --- ASSETS -----------------------------------------------------------------

@asset(description="Ingestion des CSV bruts dans DuckDB via dlt.")
def raw_ingestion(context: AssetExecutionContext) -> str:
    context.log.info("Etape 1/3 : Ingestion dlt")
    run_command(
        [sys.executable, str(INGEST_SCRIPT)],
        cwd=PROJECT_ROOT,
        step_name="dlt ingestion",
    )
    return "Ingestion terminee"


@asset(
    deps=[raw_ingestion],
    description="Execution des modeles dbt (dbt run).",
)
def dbt_run(context: AssetExecutionContext) -> str:
    context.log.info("Etape 2/3 : dbt run")
    run_command(
        [DBT_EXECUTABLE, "run"],
        cwd=DBT_PROJECT_DIR,
        step_name="dbt run",
    )
    return "Modeles dbt executes"


@asset(
    deps=[dbt_run],
    description="Tests qualite dbt (dbt test).",
)
def dbt_test(context: AssetExecutionContext) -> str:
    context.log.info("Etape 3/3 : dbt test")
    run_command(
        [DBT_EXECUTABLE, "test"],
        cwd=DBT_PROJECT_DIR,
        step_name="dbt test",
    )
    return "Tests qualite passes"