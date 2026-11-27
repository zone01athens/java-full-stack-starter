"""Local tutor recorder and private cohort receiver. Python 3, standard library."""
import argparse
import http.server
import json
import os
from pathlib import Path
import secrets
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request

DIMENSIONS = ("framing", "decision", "verification")
LEVELS = ("unobserved", "partial", "demonstrated")
ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".ai-transcripts" / "review.sqlite3"


def connect(path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    return sqlite3.connect(path, timeout=10)


def record(db, exercise, levels):
    # Exercise is a local aggregation key only, never part of the wire format.
    if exercise not in {p.parent.name for p in ROOT.glob("*/pom.xml")}:
        raise ValueError("Unknown exercise")
    db.execute("""CREATE TABLE IF NOT EXISTS practice (
        exercise TEXT PRIMARY KEY, token TEXT UNIQUE, framing INTEGER,
        decision INTEGER, verification INTEGER, pending INTEGER)""")
    with db:
        db.execute("""INSERT INTO practice VALUES (?,?,?,?,?,1)
            ON CONFLICT(exercise) DO UPDATE SET
            framing=max(framing,excluded.framing),
            decision=max(decision,excluded.decision),
            verification=max(verification,excluded.verification),
            pending=1 WHERE excluded.framing>framing OR
            excluded.decision>decision OR excluded.verification>verification""",
                   (exercise, secrets.token_hex(16), *(LEVELS.index(v) for v in levels)))


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
    for token, *scores in db.execute(
            "SELECT token,framing,decision,verification FROM practice WHERE pending=1").fetchall():
        payload = json.dumps({"sample": token, "scores": scores}).encode()
        req = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
        with client.open(req, timeout=3) as response:
            if response.status != 204:
                raise ValueError("Intake did not acknowledge the sample")
        with db:
            db.execute("""UPDATE practice SET pending=0 WHERE token=? AND
                framing=? AND decision=? AND verification=?""", (token, *scores))


def accept(db, payload):
    if not isinstance(payload, dict) or set(payload) != {"sample", "scores"}:
        raise ValueError
    token, scores = payload["sample"], payload["scores"]
    if (not isinstance(token, str) or len(token) != 32 or
            any(c not in "0123456789abcdef" for c in token)):
        raise ValueError
    if not isinstance(scores, list) or len(scores) != 3 or any(type(s) is not int or s not in range(3) for s in scores):
        raise ValueError
    with db:
        db.execute("""INSERT INTO samples VALUES (?,?,?,?) ON CONFLICT(token)
            DO UPDATE SET framing=max(framing,excluded.framing),
            decision=max(decision,excluded.decision),
            verification=max(verification,excluded.verification)""", (token, *scores))


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
    for dimension in DIMENSIONS:
        add.add_argument(dimension, choices=LEVELS)
    commands.add_parser("sync")
    serve = commands.add_parser("serve")
    serve.add_argument("database", type=Path)
    serve.add_argument("--port", type=int, default=8765)
    report = commands.add_parser("report")
    report.add_argument("database", type=Path)
    args = parser.parse_args()
    if args.command in ("record", "sync") and os.environ.get("PISCINE_REVIEW_OFF") == "1":
        return
    os.umask(0o077)
    if args.command in ("serve", "report"):
        if args.command == "report" and not args.database.is_file():
            parser.error("Missing cohort database")
        db = connect(args.database)
        db.execute("CREATE TABLE IF NOT EXISTS samples(token TEXT PRIMARY KEY, framing INTEGER, decision INTEGER, verification INTEGER)")
        if args.command == "serve":
            with http.server.HTTPServer(("127.0.0.1", args.port), Intake) as server:
                server.db = db
                server.serve_forever()
        else:
            count = db.execute("SELECT count(*) FROM samples").fetchone()[0]
            result = {"exercise_samples": count}
            if count >= 5:
                for dimension in DIMENSIONS:
                    result[dimension] = {LEVELS[level]: n for level, n in db.execute(
                        f"SELECT {dimension}, count(*) FROM samples GROUP BY {dimension}")}
            print(json.dumps(result, indent=2))
        return
    if args.command == "sync" and not LOCAL.exists():
        return
    with connect(LOCAL) as db:
        if args.command == "record":
            record(db, args.exercise, [getattr(args, d) for d in DIMENSIONS])
        try:
            sync(db, os.environ.get("PISCINE_REVIEW_INTAKE"))
        except (OSError, ValueError):
            print("Practice review queued locally. Retry on the next run.", file=sys.stderr)


if __name__ == "__main__":
    main()
