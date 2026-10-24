# -*- coding: utf-8 -*-
import subprocess
import sys
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLI_PATH = os.path.join(REPO_ROOT, "vorabpauschale_dach", "cli.py")


def _run_cli(args):
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{REPO_ROOT}{os.pathsep}{existing_pp}" if existing_pp else REPO_ROOT
    cmd = [sys.executable, CLI_PATH] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_cli_help():
    res = _run_cli(["--help"])
    assert res.returncode == 0
    assert "DACH Vorabpauschale" in res.stdout


def test_cli_de_json():
    res = _run_cli([
        "--start-value", "10000",
        "--end-value", "11000",
        "--fund-type", "equity",
        "--allowance", "1000",
        "--json",
    ])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["country"] == "DE"
    assert data["vorabpauschale"] == 178.50
    assert data["teilfreistellung_percent"] == 30.0
    assert data["allowance_used"] == 124.95
    assert data["total_tax"] == 0.0


def test_cli_simulation_json():
    res = _run_cli([
        "--start-value", "5000",
        "--monthly-savings", "300",
        "--simulate-years", "5",
        "--json",
    ])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert "simulation" in data
    assert data["simulation"]["years"] == 5
    assert len(data["simulation"]["details"]) == 5
