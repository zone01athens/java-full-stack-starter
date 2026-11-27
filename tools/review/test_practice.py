"""Synthetic end-to-end check. Requires Python 3 and the openssl CLI."""
import json
import os
from pathlib import Path
import shutil
import sqlite3
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import HTTPServer

import practice


class PracticeTest(unittest.TestCase):
    def test_offline_queue_tls_delivery_retries_and_report(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script = root / "tools/review/practice.py"
            script.parent.mkdir(parents=True)
            shutil.copyfile(practice.__file__, script)
            (root / "HelloWorld").mkdir()
            (root / "HelloWorld/pom.xml").touch()
            env = dict(os.environ, PISCINE_REVIEW_INTAKE="", PISCINE_REVIEW_OFF="1",
                       SSL_CERT_FILE=str(root / "cert"), NO_PROXY="localhost")

            def run(*args):
                return subprocess.check_output([sys.executable, script, *args], env=env, text=True)

            record = ("record", "HelloWorld")
            run(*record, "described_difficulty")
            queue = root / ".ai-transcripts/events.sqlite3"
            self.assertFalse(queue.exists())
            env["PISCINE_REVIEW_OFF"] = "0"
            run(*record, "predicted_result")
            self.assertFalse(queue.exists())
            self.assertIn("on", run("opt-in"))
            run(*record, "described_difficulty")
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                            "-days", "1", "-subj", "/CN=localhost", "-addext",
                            "subjectAltName=DNS:localhost", "-keyout", "key", "-out", "cert"],
                           cwd=root, check=True, capture_output=True)
            tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            tls.load_cert_chain(root / "cert", root / "key")
            cohort = root / "cohort.sqlite3"
            db = sqlite3.connect(cohort, check_same_thread=False)
            self.addCleanup(db.close)
            db.execute("CREATE TABLE observations(token TEXT PRIMARY KEY, mask INTEGER)")
            with HTTPServer(("127.0.0.1", 0), practice.Intake) as server:
                server.db = db
                server.socket = tls.wrap_socket(server.socket, server_side=True)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    url = f"https://localhost:{server.server_port}/samples"
                    env["PISCINE_REVIEW_INTAKE"] = url
                    run("sync")
                    run("sync")
                    run(*record, "asked_for_hint", "chose_experiment", "ran_check")
                    run(*record, "described_difficulty")
                    self.assertEqual(db.execute("SELECT mask FROM observations").fetchall(), [(29,)])
                    self.assertEqual(json.loads(run("report", cohort)), {"exercise_samples": 1})
                    report = root / "report.json"
                    run("report", cohort, "--output", report)
                    self.assertEqual(json.loads(report.read_text()), {"exercise_samples": 1})
                    with self.assertRaises(HTTPError) as exc:
                        urlopen(Request(url, data=b'{"email":"private"}'),
                                context=ssl.create_default_context(cafile=root / "cert"))
                    self.assertEqual(exc.exception.code, 400)
                    exc.exception.close()
                    for i in range(4):
                        practice.accept(db, {"sample": format(i, "032x"), "events": 0})
                    self.assertEqual(json.loads(run("report", cohort))["decision"]["demonstrated"], 1)
                finally:
                    server.shutdown()
                    thread.join()
            run(*record, "compared_result")
            with sqlite3.connect(queue) as local:
                self.assertEqual(local.execute("SELECT pending FROM queue").fetchone(), (1,))
            self.assertIn("off", run("opt-out"))
            run(*record, "ran_check")
            run("sync")
            with sqlite3.connect(queue) as local:
                self.assertEqual(local.execute("SELECT count(*) FROM queue").fetchone(), (0,))
            self.assertIn("off", run("status"))
            run("opt-in")
            with sqlite3.connect(queue) as local:
                self.assertEqual(local.execute("SELECT count(*) FROM queue").fetchone(), (0,))



if __name__ == "__main__":
    unittest.main()
