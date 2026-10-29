"""Recompute S20 metrics with network/model calls forbidden."""
import runpy
import socket
import sys
from pathlib import Path

def forbidden(*args, **kwargs):
    raise AssertionError("Network/model calls forbidden during offline reporting")

socket.socket.connect = forbidden
socket.create_connection = forbidden
sys.argv = [str(Path(__file__).with_name("run_model.py")), "--report-only"]
runpy.run_path(sys.argv[0], run_name="__main__")
