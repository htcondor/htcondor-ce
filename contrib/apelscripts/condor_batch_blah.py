#!/usr/bin/python3
import os
import argparse
import subprocess
import time
from pathlib import Path


CLI = argparse.ArgumentParser()
CLI.add_argument(
    "--dry-run",
    help="do not perform destructive actions, write data to stdout",
    action="store_true",
)


def read_lrms_config_val(key: str) -> str:
    return _read_any_config_val("condor_config_val", key)


def read_ce_config_val(key: str) -> str:
    return _read_any_config_val("condor_ce_config_val", key)


def _read_any_config_val(prog: str, key: str) -> str:
    return subprocess.run(
        [prog, key], check=True, stdout=subprocess.PIPE, universal_newlines=True
    ).stdout.strip()


def condor_q_format(job_history: Path, *formats: str) -> str:
    """Run `condor_q` with several `-format` fields for a given `job_history` file"""
    assert len(formats) % 2 == 0
    format_fields = ["-format"] * (len(formats) // 2 * 3)
    format_fields[1::3] = formats[::2]
    format_fields[2::3] = formats[1::2]
    return subprocess.run(
            ["condor_q", "-job", str(job_history)] + format_fields,
            check=True, stdout=subprocess.PIPE, universal_newlines=True,
            env={**os.environ, "TZ": "GMT"},
        ).stdout


options = CLI.parse_args()
dry_run: bool = options.dry_run

history_dir = Path(read_lrms_config_val("PER_JOB_HISTORY_DIR"))
output_dir = Path(read_ce_config_val("APEL_OUTPUT_DIR"))
ce_host = read_ce_config_val("APEL_CE_HOST")
ce_id = read_ce_config_val("APEL_CE_ID")
scaling_attr = read_ce_config_val("APEL_SCALING_ATTR") or "1.0"
output_datetime = time.strftime("%Y%m%d-%H%M")

for directory in (history_dir / "quarantine", output_dir):
    directory.mkdir(exist_ok=True)
    (directory / ".write_test").touch()
    (directory / ".write_test").unlink()


if not dry_run:
    batch_path = output_dir / f"batch-{output_datetime}-{ce_host.split('.')[0]}"
    blah_path = output_dir / f"blah-{output_datetime}-{ce_host.split('.')[0]}"
else:
    batch_path = blah_path = Path("/dev/stdout")
histories = [path for path in history_dir.iterdir() if path.is_file()]


with batch_path.open("w") as batch_stream, blah_path.open("w") as blah_stream:
    for history in histories:
        # basic check that the file contains valid history
        if (
            not condor_q_format(history, "%s", "GlobalJobId").strip()
            or not condor_q_format(history, "%f", scaling_attr).strip()
        ):
            if not dry_run:
                history.rename(history_dir / "quarantine" / history.stem)
            continue
        batch_stream.write(
            condor_q_format(
                history,
                "%s|", "GlobalJobId",
                "%s|", "Owner",
                "%lld|", "RemoteWallClockTime",
                "%lld|", "RemoteUserCpu",
                "%lld|", "RemoteSysCpu",
                "%lld|", "JobStartDate",
                "%lld|", "EnteredCurrentStatus",
                "%lld|", "ResidentSetSize_RAW",
                "%lld|", "ImageSize_RAW",
                "%lld|", "RequestCpus",
                "%v|\n", scaling_attr,
            )
        )
        blah_stream.write(
            condor_q_format(
                history,
                '"timestamp=%s" ', 'formatTime(EnteredCurrentStatus, "%Y-%m-%d %H:%M:%S")',
                '"userDN=%s" ', "x509userproxysubject",
                '"userFQAN=%s" ', "x509UserProxyFirstFQAN",
                f'"ceID={ce_id}" ', "EMPTY",
                f'"jobID=%v_{ce_host}" ', "RoutedFromJobId",
                '"lrmsID=%s" ', "GlobalJobId",
                '"localUser=%s"\n', "Owner",
            )
        )
        if not dry_run:
            history.unlink()
