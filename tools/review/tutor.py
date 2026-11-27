"""Local terminal tutor. Keep dialogue in memory and record rubric levels per reply."""
import argparse
import http.client
import json
import os
import sys

import practice


def ollama(path, payload):
    conn = http.client.HTTPConnection("127.0.0.1", 11434, timeout=120)
    try:
        conn.request("POST", path, json.dumps(payload), {"Content-Type": "application/json"})
        response = conn.getresponse()
        if response.status != 200:
            raise ValueError("Local model request failed")
        return json.load(response)
    finally:
        conn.close()


def tutor(exercise, model, ask=input, show=print, request=ollama):
    details = request("/api/show", {"model": model})
    if details.get("remote_model") or details.get("remote_host") or not details.get("model_info"):
        raise ValueError("Select an installed local model")
    rules = (practice.ROOT / "AGENTS.md").read_text().split("## Record learning signals")[0]
    rubric = (practice.ROOT / "transcripts/README.md").read_text().split("## Automatic delivery")[0]
    messages = [{"role": "system", "content": rules + "\n" + rubric +
                 "\nExercise: " + exercise + ". Return one tutoring reply and rate the learner evidence seen so far."}]
    fields = {"reply": {"type": "string"}, **{
        key: {"type": "string", "enum": practice.LEVELS} for key in practice.DIMENSIONS}}
    schema = {"type": "object", "properties": fields, "required": list(fields), "additionalProperties": False}
    show("Local tutor. Type /exit to finish. The review keeps three rubric levels per exercise.")
    while True:
        try:
            prompt = ask("> ").strip()
        except EOFError:
            return
        if prompt == "/exit":
            return
        if not prompt:
            continue
        messages.append({"role": "user", "content": prompt})
        answer = request("/api/chat", {"model": model, "messages": messages, "stream": False, "format": schema})
        turn = json.loads(answer["message"]["content"])
        if set(turn) != set(fields) or not isinstance(turn["reply"], str) or not turn["reply"].strip():
            raise ValueError("Invalid tutor response")
        levels = [turn[key] for key in practice.DIMENSIONS]
        if any(level not in practice.LEVELS for level in levels):
            raise ValueError("Invalid rubric response")
        if os.environ.get("PISCINE_REVIEW_OFF") != "1":
            with practice.connect(practice.LOCAL) as db:
                practice.record(db, exercise, levels)
                try:
                    practice.sync(db, os.environ.get("PISCINE_REVIEW_INTAKE"))
                except (OSError, ValueError):
                    show("Practice review queued locally.")
        messages.append({"role": "assistant", "content": turn["reply"]})
        show(turn["reply"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exercise", choices=sorted(p.parent.name for p in practice.ROOT.glob("*/pom.xml")))
    parser.add_argument("--model", required=True)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        tutor(args.exercise, args.model)
    except (KeyError, TypeError, ValueError, OSError, http.client.HTTPException):
        sys.exit("Tutor unavailable. Check the local Ollama service, installed model and structured-output support.")
