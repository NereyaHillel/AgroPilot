#!/usr/bin/env python3
"""Grade one iteration of irrigation-calc-reference evals.

    grade.py <iteration_dir>

"number" and "regex_all" assertions are checked here against outputs/answer.md.
"judge" assertions are read from <run_dir>/judge.json ({"<assertion id>": [passed, "evidence"]}),
written by a human or model grader. Writes grading.json in each run dir.
"""

import json
import re
import sys
from pathlib import Path

EVALS = json.loads((Path(__file__).parent / "evals.json").read_text())["evals"]
NUM = re.compile(r"(?<![\d.])-?\d+(?:\.\d+)?")


def check(a, text):
    if a["check"] == "number":
        hits = [n for n in NUM.findall(text.replace(",", "")) if abs(float(n) - a["value"]) <= a["tol"]]
        return bool(hits), f"found {hits[0]}" if hits else f"no number within {a['tol']} of {a['value']}"
    if a["check"] == "regex_all":
        missing = [p for p in a["patterns"] if not re.search(p, text)]
        return not missing, "all patterns found" if not missing else f"missing {missing}"
    raise ValueError(a["check"])


def main(it: Path) -> None:
    for e in EVALS:
        for run in sorted(it.glob(f"eval-{e['id']}-*/*/run-*/")):
            answer = run / "outputs/answer.md"
            if not answer.exists():
                continue
            text = answer.read_text()
            judge_file = run / "judge.json"
            judge = json.loads(judge_file.read_text()) if judge_file.exists() else {}
            exps = []
            for a in e["assertions"]:
                if a["check"] == "judge":
                    passed, ev = judge.get(a["id"], (False, "not judged"))
                else:
                    passed, ev = check(a, text)
                exps.append({"text": a["text"], "passed": bool(passed), "evidence": ev})
            n = sum(x["passed"] for x in exps)
            (run / "grading.json").write_text(json.dumps({
                "expectations": exps,
                "summary": {"passed": n, "failed": len(exps) - n, "total": len(exps),
                            "pass_rate": round(n / len(exps), 4)},
            }, indent=2))
            print(f"{run.relative_to(it)}: {n}/{len(exps)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
