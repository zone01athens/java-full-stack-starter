"""Local tutor recorder and private cohort receiver. Python 3, standard library."""
import argparse
import http.server
import json
import os
from pathlib import Path
import secrets
import sqlite3
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

DIMENSIONS = ("framing", "decision", "verification")
LEVELS = ("unobserved", "partial", "demonstrated")
ROOT = Path(__file__).resolve().parents[2]
EVENTS = ("described_difficulty", "predicted_result", "asked_for_hint", "chose_experiment",
          "ran_check", "compared_result")
LOCAL = ROOT / ".ai-transcripts" / "events.sqlite3"


def connect(path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    return sqlite3.connect(path, timeout=10)


def record(db, exercise, events):
    if exercise not in {p.parent.name for p in ROOT.glob("*/pom.xml")}:
        raise ValueError("Unknown exercise")
    mask = sum(1 << EVENTS.index(event) for event in set(events))
    db.execute("""INSERT INTO queue VALUES (?,?,?,1)
        ON CONFLICT(exercise) DO UPDATE SET mask=mask|excluded.mask, pending=1
        WHERE (mask|excluded.mask)!=mask""", (exercise, secrets.token_hex(16), mask))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def sync(db, endpoint):
    if not endpoint:
        return
    url = urllib.parse.urlsplit(endpoint)
    if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError("Use an HTTPS intake URL without credentials or query parameters")
    client = urllib.request.build_opener(NoRedirect())
    for token, mask in db.execute("SELECT token,mask FROM queue WHERE pending=1").fetchall():
        payload = json.dumps({"sample": token, "events": mask}).encode()
        req = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
        with client.open(req, timeout=3) as response:
            if response.status != 204:
                raise ValueError("Intake did not acknowledge the sample")
        db.execute("UPDATE queue SET pending=0 WHERE token=?", (token,))


def accept(db, payload):
    if not isinstance(payload, dict) or set(payload) != {"sample", "events"}:
        raise ValueError
    token, mask = payload["sample"], payload["events"]
    if (not isinstance(token, str) or len(token) != 32 or
            any(c not in "0123456789abcdef" for c in token)):
        raise ValueError
    if type(mask) is not int or not 0 <= mask < 1 << len(EVENTS):
        raise ValueError
    with db:
        db.execute("""INSERT INTO observations VALUES (?,?) ON CONFLICT(token)
            DO UPDATE SET mask=mask|excluded.mask""", (token, mask))


def batch_report(db):
    counts = {dimension: dict.fromkeys(LEVELS, 0) for dimension in DIMENSIONS}
    total = 0
    for mask, n in db.execute("SELECT mask,count(*) FROM observations GROUP BY mask"):
        total += n
        for i, dimension in enumerate(DIMENSIONS):
            pair = (mask >> (2*i)) & 3
            level = 2 if pair == 3 else int(bool(pair))
            counts[dimension][LEVELS[level]] += n
    return {"exercise_samples": total, **(counts if total >= 5 else {})}


class Intake(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        if self.path != "/samples":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 256:
                raise ValueError
            accept(self.server.db, json.loads(self.rfile.read(size)))
        except (ValueError, UnicodeError, RecursionError):
            self.send_error(400)
            return
        self.send_response(204)
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("record")
    add.add_argument("exercise")
    add.add_argument("events", nargs="+", choices=EVENTS)
    for command in ("opt-in", "opt-out", "status"):
        commands.add_parser(command)
    commands.add_parser("sync")
    serve = commands.add_parser("serve")
    serve.add_argument("database", type=Path)
    serve.add_argument("--port", type=int, default=8765)
    report = commands.add_parser("report")
    report.add_argument("database", type=Path)
    report.add_argument("--output", type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    if args.command in ("serve", "report"):
        if args.command == "report" and not args.database.is_file():
            parser.error("Missing cohort database")
        db = connect(args.database)
        db.execute("CREATE TABLE IF NOT EXISTS observations(token TEXT PRIMARY KEY, mask INTEGER)")
        if args.command == "serve":
            with http.server.HTTPServer(("127.0.0.1", args.port), Intake) as server:
                server.db = db
                server.serve_forever()
        else:
            result = json.dumps(batch_report(db), indent=2) + "\n"
            if args.output:
                if args.output.resolve() == args.database.resolve():
                    parser.error("Choose a report file separate from the database")
                with tempfile.NamedTemporaryFile(mode="w", dir=args.output.parent, delete=False) as tmp:
                    tmp.write(result)
                os.replace(tmp.name, args.output)
            else:
                print(result, end="")
        return
    if args.command != "opt-in" and not LOCAL.exists():
        if args.command in ("status", "opt-out"):
            print("Practice review off")
        return
    with connect(LOCAL) as db:
        # Serialize opt-out with delivery. Once opt-out returns no queued send can start.
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS consent(enabled INTEGER PRIMARY KEY CHECK(enabled=1))")
        db.execute("CREATE TABLE IF NOT EXISTS queue(exercise TEXT PRIMARY KEY, token TEXT UNIQUE, mask INTEGER, pending INTEGER)")
        if args.command == "opt-in":
            db.execute("INSERT OR IGNORE INTO consent VALUES (1)")
        if args.command == "opt-out":
            db.execute("DELETE FROM consent")
            db.execute("DELETE FROM queue")
        enabled = bool(db.execute("SELECT 1 FROM consent").fetchone()) and os.environ.get("PISCINE_REVIEW_OFF") != "1"
        if args.command in ("status", "opt-in", "opt-out"):
            print("Practice review on" if enabled else "Practice review off")
        elif enabled:
            if args.command == "record":
                record(db, args.exercise, args.events)
            try:
                sync(db, os.environ.get("PISCINE_REVIEW_INTAKE"))
            except (OSError, ValueError):
                print("Practice review queued locally. Retry on the next run.", file=sys.stderr)


if __name__ == "__main__":
    main()
