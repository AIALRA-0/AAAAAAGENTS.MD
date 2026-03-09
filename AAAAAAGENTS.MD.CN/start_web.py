from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / (".venv-win" if os.name == "nt" else ".venv-linux")
REQUIRED_MODULES = ("fastapi", "uvicorn", "jinja2", "markdown")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

LOGGER = logging.getLogger("start_web")


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[start_web] %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动 AGENTS 本地可视化服务")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"监听地址，默认 {DEFAULT_HOST}")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"监听端口，默认 {DEFAULT_PORT}")
    parser.add_argument("--no-reload", action="store_true", help="关闭 uvicorn 自动重载")
    parser.add_argument("--skip-install", action="store_true", help="跳过依赖安装检查")
    parser.add_argument("--verbose", action="store_true", help="输出调试日志")
    return parser.parse_args()


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run_checked(command: list[str]) -> None:
    LOGGER.debug("exec: %s", " ".join(command))
    subprocess.check_call(command, cwd=str(ROOT))


def ensure_venv() -> Path:
    py = venv_python()
    if py.exists():
        return py
    LOGGER.info("creating %s ...", VENV_DIR.name)
    run_checked([sys.executable, "-m", "venv", str(VENV_DIR)])
    return py


def modules_ready(py: Path) -> bool:
    script = (
        "import importlib.util,sys;"
        f"mods={REQUIRED_MODULES!r};"
        "missing=[m for m in mods if importlib.util.find_spec(m) is None];"
        "sys.exit(0 if not missing else 1)"
    )
    return subprocess.call([str(py), "-c", script], cwd=str(ROOT)) == 0


def ensure_dependencies(py: Path) -> None:
    if modules_ready(py):
        return
    LOGGER.info("installing dependencies into %s ...", VENV_DIR.name)
    run_checked(
        [
            str(py),
            "-m",
            "pip",
            "--disable-pip-version-check",
            "install",
            "-r",
            str(ROOT / "requirements.txt"),
        ]
    )


def build_uvicorn_command(py: Path, host: str, port: int, reload_enabled: bool) -> list[str]:
    command = [
        str(py),
        "-m",
        "uvicorn",
        "agents_web.server:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload_enabled:
        command.append("--reload")
    return command


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    try:
        py = ensure_venv()
        if not args.skip_install:
            ensure_dependencies(py)
        command = build_uvicorn_command(py, args.host, args.port, not args.no_reload)
        LOGGER.info("serving at http://%s:%s", args.host, args.port)
        return subprocess.call(command, cwd=str(ROOT))
    except subprocess.CalledProcessError as exc:
        LOGGER.error("command failed with exit code %s", exc.returncode)
        return exc.returncode
    except Exception as exc:  # pragma: no cover - launcher fallback
        LOGGER.error("startup failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
