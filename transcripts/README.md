# Optional cohort review

Use your usual coding assistant. You can complete every exercise with review switched off. Each checkout starts with collection disabled. To participate, run this once in the project terminal:

    python3 tools/review/practice.py opt-in

Check or withdraw at any time:

    python3 tools/review/practice.py status
    python3 tools/review/practice.py opt-out

Opt-out persists across restarts and clears the local delivery queue. Samples already delivered cannot be located by student identity. PISCINE_REVIEW_OFF=1 also suspends collection and delivery wherever the variable is set. Old score queues from earlier starter versions are ignored.

## During practice

The existing shell-enabled tutor checks status, then records only actions it observed. Python 3 is sufficient. No model installation is required. Example:

    python3 tools/review/practice.py record HelloWorld predicted_result ran_check

| Action | Evidence from the learner |
| --- | --- |
| described_difficulty | Identified the specific difficulty |
| predicted_result | Gave an expectation before a check |
| asked_for_hint | Requested diagnostic guidance |
| chose_experiment | Selected the next experiment |
| ran_check | Reported running it |
| compared_result | Compared an observation with a prediction |

The device sends a random per-exercise token and a bit mask of observed actions. It sends no prompts, replies, names, exercise titles or grades. Repeated observations merge into the same sample. The tester retries queued deliveries. The tutor client's own chat history is separate. Browser-only chats cannot record through this mechanism.

## Staff batch

Run the intake on a controlled campus host. Use a database outside the checkout:

    python3 tools/review/practice.py serve /var/lib/piscine-review/cohort.sqlite3

Expose HTTPS POST /samples through a campus proxy to loopback port 8765. Verify access logging and tracing are disabled throughout the route before enabling collection. The network edge sees connection IPs. Configure PISCINE_REVIEW_INTAKE in the tutor and IDE environments. With no endpoint, observations remain local.

Run this repeatable batch after the practice window. It calculates scores over all received samples from the event masks:

    python3 tools/review/practice.py report /var/lib/piscine-review/cohort.sqlite3

For a daily batch at 04:00 host time, install this entry in the receiver service account's crontab after deployment. Use the actual installation paths. The completed report replaces the previous file atomically.

    0 4 * * * /usr/bin/python3 /opt/piscine/tools/review/practice.py report /var/lib/piscine-review/cohort.sqlite3 --output /var/lib/piscine-review/report.json

Framing uses the first pair of actions, decision the second, verification the third. Zero observed actions yields unobserved, one partial, both demonstrated. These labels describe evidence within an exercise. They do not establish independent understanding or evaluate the original wording. Report totals count exercise samples; dimension counts appear from five samples. One learner may contribute multiple samples. Records are unauthenticated, tutor-reported signals.

## Why this design

- A randomized study of 52 developers learning a Python library reported lower immediate quiz scores with AI assistance. Asking conceptual questions was associated with stronger performance within the assisted group. That latter comparison is observational. We ask learners to predict and debug before accepting a suggestion. [Anthropic study](https://www.anthropic.com/research/AI-assistance-coding-skills)
- In a high-school mathematics field experiment, students with unrestricted GPT assistance did better during practice but worse on the subsequent unassisted exam. The guided tutor largely avoided the decline. We use small hints followed by an unaided check; transfer to this Java course is a design choice. [Paper](https://doi.org/10.1073/pnas.2422633122) · [Research repository](https://github.com/obastani/GenAICanHarmLearning)
- GitHub documents configuring Copilot as a tutor and publishes a mentor agent. These are implementation references for the tutoring instructions. [GitHub learning guide](https://docs.github.com/en/get-started/learning-to-code/setting-up-copilot-for-learning-to-code) · [Mentor agent](https://github.com/github/awesome-copilot/blob/main/agents/mentor.agent.md)
