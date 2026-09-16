from dagster import (
    DefaultScheduleStatus,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules,
)
from . import assets

all_assets = load_assets_from_modules([assets])
book_pipeline_job = define_asset_job("book_pipeline_job")
daily_schedule = ScheduleDefinition(
    job=book_pipeline_job,
    cron_schedule="0 2 * * *",
    execution_timezone="UTC",
    default_status=DefaultScheduleStatus.RUNNING,
)

defs = Definitions(
    assets=all_assets,
    jobs=[book_pipeline_job],
    schedules=[daily_schedule],
)
