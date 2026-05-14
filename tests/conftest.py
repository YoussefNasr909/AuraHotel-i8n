import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture()
def base_url():
    return BASE_URL


@pytest.fixture()
def driver():
    options = Options()

    # Optional headless mode:
    # set HEADLESS=1 in terminal to run without opening browser
    if os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)

    yield drv
    drv.quit()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    After pytest finishes, export results to JSON files for the Flask dashboard.
    """
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)

    # counts
    total = getattr(terminalreporter, "_numcollected", None)
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", [])) + len(terminalreporter.stats.get("error", []))
    skipped = len(terminalreporter.stats.get("skipped", []))

    if total is None:
        total = passed + failed + skipped

    run = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "exitstatus": exitstatus,  # 0 means success
    }

    # write latest
    (results_dir / "latest.json").write_text(json.dumps(run, indent=2), encoding="utf-8")

    # append history
    history_file = results_dir / "history.json"
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
        except Exception:
            history = []
    else:
        history = []

    history.append(run)

    # keep last 30 runs
    history = history[-30:]
    history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")


 # Now every time you run pytest, those JSON files update automatically.   