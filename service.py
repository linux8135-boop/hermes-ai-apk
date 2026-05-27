"""Hermes AI — Android foreground service."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gateway as _gateway


def start(*args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_gateway.start())
    except Exception as e:
        _debug(f"Service error: {e}")
    finally:
        loop.close()


def _debug(msg):
    try:
        with open(str(os.path.expanduser("~/hermes_debug.log")), "a") as f:
            f.write(f"{msg}\n")
    except:
        pass


if __name__ == "__main__":
    start()
