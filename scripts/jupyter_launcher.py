"""Loopback-only authenticated Jupyter entry point for an on-demand task."""

import os
import secrets
import sys
from pathlib import Path

from local_settings import configure_jupyter_environment, load_settings


def main():
    spec = load_settings()
    if not Path(sys.executable).samefile(spec["python"]):
        raise RuntimeError("Use the configured project Python, not a different interpreter")
    configure_jupyter_environment()
    os.chdir(spec["project"])
    from jupyterlab.labapp import LabApp
    from traitlets.config import Config

    config = Config()
    config.IdentityProvider.token = secrets.token_urlsafe(32)
    # Random token is never written into a reusable command or printed here.
    # Jupyter retains it in its protected runtime JSON as required for operation.
    config.ServerApp.allow_remote_access = False
    config.ServerApp.disable_check_xsrf = False
    LabApp.launch_instance(
        argv=[
            "--ip=127.0.0.1",
            f"--port={spec['port']}",
            "--no-browser",
            "--ServerApp.port_retries=0",
            "--ServerApp.log_level=30",
            f"--ServerApp.root_dir={spec['project']}",
        ],
        config=config,
    )


if __name__ == "__main__":
    main()
