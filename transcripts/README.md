# Automatic practice review

For automatic scoring on every completed turn, use the local tutor from the IntelliJ terminal. Install Ollama and a local model with structured-output support once. Run the Ollama service in local-only mode (OLLAMA_NO_CLOUD=1). Supply the installed model name:

    python3 tools/review/tutor.py HelloWorld --model MODEL

The tutor returns a hint and three rubric values together. The runner validates and records the values before displaying the hint. Dialogue stays in process memory. Type /exit to finish. This runner does not read the exercise source; paste the relevant attempt or error in the chat.

Other shell-enabled repository tutors can record the same levels by following AGENTS.md. The recorder accepts only an exercise folder and three fixed levels. No transcript is exported. The AI client may keep its own chat history under its own settings.

    python3 tools/review/practice.py record HelloWorld demonstrated partial unobserved

Use the positions in this order:

| Dimension | Partial | Demonstrated |
| --- | --- | --- |
| Framing | Identifies the difficulty | Gives expected and observed behavior or a specific prediction |
| Decision | Requests a diagnostic hint | Chooses a next experiment and explains why |
| Verification | Reports running a check | Compares its result with a prediction and explains the outcome |

Use **unobserved** when evidence is missing. Score only the learner's contribution. Treat these as tutor estimates for cohort mentoring. Verify independent understanding separately with an unaided exercise.

## Automatic delivery

Python 3 is required. The ignored local queue retains the strongest observed level per dimension per exercise. An improved score updates the same random sample. Repeated delivery is safe. The tutor attempts delivery after each record. The IntelliJ/Maven tester retries queued changes on each run. Without an intake URL, records stay on the device. No personal commits, uploads or API keys are required.

Staff: run the receiver on an access-controlled campus host with a database outside the checkout:

    python3 tools/review/practice.py serve /var/lib/piscine-review/cohort.sqlite3

Route HTTPS POST /samples to its loopback port 8765. Disable access logs and request tracing throughout the route, and verify infrastructure retention before enabling collection. Set PISCINE_REVIEW_INTAKE to the campus HTTPS URL in the tutor and IDE environments. The receiver stores a random exercise-sample token and three integers. It has no student account, exercise name, timestamp or text field. Different samples have independent tokens. The network edge can see the connection IP. Keep the receiver on the controlled network. Submissions are unauthenticated self-reports.

    python3 tools/review/practice.py report /var/lib/piscine-review/cohort.sqlite3

The report counts exercise samples. Dimension breakdowns appear from five samples onward. One learner may contribute multiple samples. Review participation and scores cannot establish attendance, mastery or cohort membership. Set PISCINE_REVIEW_OFF=1 in the tutor and IDE environments to disable recording and delivery. Browser-only chats and clients that ignore repository instructions provide no automatic evidence.

## Why this design

- A randomized study of 52 developers learning a Python library reported lower immediate quiz scores with AI assistance. Asking conceptual questions was associated with stronger performance within the assisted group. That latter comparison is observational. We ask learners to predict and debug before accepting a suggestion. [Anthropic study](https://www.anthropic.com/research/AI-assistance-coding-skills)
- In a high-school mathematics field experiment, students with unrestricted GPT assistance did better during practice but worse on the subsequent unassisted exam. The guided tutor largely avoided the decline. We use small hints followed by an unaided check; transfer to this Java course is a design choice. [Paper](https://doi.org/10.1073/pnas.2422633122) · [Research repository](https://github.com/obastani/GenAICanHarmLearning)
- GitHub documents configuring Copilot as a tutor and publishes a mentor agent. These are implementation references for the tutoring instructions. [GitHub learning guide](https://docs.github.com/en/get-started/learning-to-code/setting-up-copilot-for-learning-to-code) · [Mentor agent](https://github.com/github/awesome-copilot/blob/main/agents/mentor.agent.md)
