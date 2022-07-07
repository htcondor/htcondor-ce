#!/usr/bin/python3
import os
import sys
import argparse
from subprocess import check_output, CalledProcessError
import time
import configparser
from pathlib import Path


CLI = argparse.ArgumentParser(
    description="Generate APEL accounting records for an HTCondor CE and LRMS",
    epilog="""
HTCondor configuration values:

  condor_config_val:
    PER_JOB_HISTORY_DIR  path to which per-job history files are written

  condor_ce_config_val:
    APEL_OUTPUT_DIR      path to which APEL record files should be written
    APEL_CE_HOST         hostname of the CE
    APEL_CE_ID           APEL identifier for the CE
    APEL_SCALING_ATTR    job attribute for optional performance factor
    APEL_SPEC_ATTR       job attribute for optional absolute performance
""".strip(),
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
CLI.add_argument(
    "--apel-config",
    help="path to apel client configuration file [default: %(default)s]",
    default="/etc/apel/client.cfg",
    type=Path,
)
CLI.add_argument(
    "--dry-run",
    help="do not perform destructive actions, write data to stdout",
    action="store_true",
)


def read_lrms_config_val(key: str) -> str:
    return check_output(["condor_config_val", key], universal_newlines=True).strip()


def read_ce_config_val(key: str) -> str:
    return check_output(["condor_ce_config_val", key], universal_newlines=True).strip()


def read_apel_specs(apel_config: Path, ce_id: str) -> "dict[str, float]":
    """Read APEL manual_specX entries for a given CE identifier"""
    config = configparser.ConfigParser()
    with apel_config.open() as config_stream:
        config.read_file(config_stream)
    specs = {}
    for spec_id in range(1, len(config["spec_updater"]) + 1):
        try:
            spec = config["spec_updater"][f"manual_spec{spec_id}"]
        except KeyError:
            break
        spec_ce_id, spec_type, spec_value, *_ = spec.split(",")
        if ce_id == spec_ce_id:
            specs[spec_type] = float(spec_value)
    return specs


def format_apel_scaling(apel_config: Path, ce_id: str) -> str:
    """Build a ClassAd expression for the factor of used vs average performance"""
    specs = read_apel_specs(apel_config, ce_id)
    # assume average performance by default
    scale_query = "1.0"
    try:
        scaling_attr = read_ce_config_val("APEL_SCALING_ATTR")
    except CalledProcessError:
        pass
    else:
        scale_query = f"({scaling_attr} ?: {scale_query})"
    try:
        spec_attr = read_ce_config_val("APEL_SPEC_ATTR")
    except CalledProcessError:
        return scale_query
    else:
        spec_scale_query = scale_query
        for spec_type, spec_value in reversed(list(specs.items())):
            spec_scale_query = (
                f"(({spec_attr}.'{spec_type}' / {spec_value}) ?: {spec_scale_query})"
            )
        return spec_scale_query


def condor_q_format(job_history: Path, *formats: str) -> str:
    """Run `condor_q` with several `-format` fields for a given `job_history` file"""
    assert len(formats) % 2 == 0
    format_fields = ["-format"] * (len(formats) // 2 * 3)
    format_fields[1::3] = formats[::2]
    format_fields[2::3] = formats[1::2]
    return check_output(
            ["condor_q", "-job", str(job_history)] + format_fields,
            universal_newlines=True, env={**os.environ, "TZ": "GMT"},
        )


options = CLI.parse_args()
dry_run: bool = options.dry_run

history_dir = Path(read_lrms_config_val("PER_JOB_HISTORY_DIR"))
output_dir = Path(read_ce_config_val("APEL_OUTPUT_DIR"))
ce_host = read_ce_config_val("APEL_CE_HOST")
ce_id = read_ce_config_val("APEL_CE_ID")
scaling_expr = format_apel_scaling(options.apel_config, ce_id)
output_datetime = time.strftime("%Y%m%d-%H%M")

for directory in (history_dir / "quarantine", output_dir):
    directory.mkdir(exist_ok=True)
    (directory / ".write_test").touch()
    (directory / ".write_test").unlink()


if not dry_run:
    batch_stream = (output_dir / f"batch-{output_datetime}-{ce_host.split('.')[0]}").open("w")
    blah_stream = (output_dir / f"blah-{output_datetime}-{ce_host.split('.')[0]}").open("w")
else:
    batch_stream = blah_stream = sys.stdout


with batch_stream, blah_stream:
    for history in history_dir.iterdir():
        if not history.is_file():
            continue
        # basic check that the file contains valid history
        if (
            not condor_q_format(history, "%s", "GlobalJobId").strip()
            or not condor_q_format(history, "%f", scaling_expr).strip()
        ):
            if not dry_run:
                history.rename(history_dir / "quarantine" / history.name)
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
                "%v|\n", scaling_expr,
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
