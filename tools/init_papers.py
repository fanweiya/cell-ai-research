import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers.json"
SNAPSHOT = "df5c5e186ef60e677b265d64006bb3430a5b507f"


def main() -> None:
    if PAPERS.exists():
        raise SystemExit(f"论文数据库已存在：{PAPERS}")

    source = subprocess.run(
        ["git", "show", f"{SNAPSHOT}:papers.json"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    if not isinstance(json.loads(source).get("database"), list):
        raise ValueError("论文数据库快照缺少 database 数组")

    with PAPERS.open("xb") as database:
        database.write(source)
    print(f"已创建论文数据库：{PAPERS}")


if __name__ == "__main__":
    main()
