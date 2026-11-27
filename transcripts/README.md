# AI practice records

Use one Markdown file per assisted exercise session. This records how you asked for help, what the tutor said, and what you verified yourself. Independent work needs no fabricated conversation.

## Capture during practice

Keep local drafts under `.ai-transcripts/` in your checkout. Git ignores this directory. Use a unique name, for example `2026-11-30-HelloWorld-01.md`. Start from [the session template](SESSION-TEMPLATE.md). A repository-aware tutor can append turns as you work. For web chat or a client without file access, copy the visible exchange yourself. Record the original wording, including unproductive prompts, and label each speaker. Mark missing turns as missing.

Write your own follow-up. Record the experiment, prediction and actual result. Keep records scoped to the assignment. Redact secrets, personal details and unrelated conversation before saving or sharing. Omit hidden instructions, internal reasoning, raw tool logs and private assessment material. Do not export an entire account's chat history.

## Submit to your private GitHub copy

1. Open your **private student repository** in GitHub. On first use, create a branch named `ai-transcripts` from your current main branch. Switch to that branch in the browser.
2. Open its `transcripts/` directory. Use **Add file → Upload files** to upload the reviewed Markdown file. Commit directly to `ai-transcripts`. Check the branch selector before committing.
3. Link the transcript from the exercise issue in your private student repository. Give the assigned reviewer read access. Keep the transcript branch separate from the code branch throughout the course. Do not merge it into main or push it to Gitea. Continue pushing the same **code** commit to GitHub and Gitea as described in the root README.

Only the instructions and blank template belong in the public starter. Repository instructions guide compatible clients; they cannot enforce tutoring in external chats or capture those chats automatically. Disable inline code generation while practising if it supplies implementations.

## Review prompts and learning

For each dimension record **demonstrated**, **partial**, or **insufficient evidence**, with a turn number or an observed learner action.

| Dimension | Evidence to look for |
| --- | --- |
| Framing the problem | The learner identifies the confusing behavior, expected result or an initial prediction. |
| Owning the decision | They ask for an explanation or diagnostic hint, then decide what to try. |
| Checking the advice | They test a prediction and compare the actual result with it, including when the tutor was wrong. |
| Independent understanding | They explain their change or handle a small variation unaided during review. |

Example: “With input X I predicted Y but got Z. Which assumption should I check first?” gives the reviewer an observable starting point. A request for a solution can still lead to good learning if the next turns show an independent attempt. Evaluate the sequence; prompt length, English fluency and message count are poor proxies for understanding. Treat an incomplete record as a gap to discuss.

## Why this design

- A randomized study of 52 developers learning a Python library reported lower immediate quiz scores with AI assistance. Asking conceptual questions was associated with stronger performance within the assisted group. That latter comparison is observational. We ask learners to predict and debug before accepting a suggestion. [Anthropic study](https://www.anthropic.com/research/AI-assistance-coding-skills)
- In a high-school mathematics field experiment, students with unrestricted GPT assistance did better during practice but worse on the subsequent unassisted exam. The guided tutor largely avoided the decline. We use small hints followed by an unaided check; transfer to this Java course is a design choice. [Paper](https://doi.org/10.1073/pnas.2422633122) · [Research repository](https://github.com/obastani/GenAICanHarmLearning)
- GitHub documents configuring Copilot as a tutor and publishes a mentor agent. These are implementation references for the tutoring instructions. [GitHub learning guide](https://docs.github.com/en/get-started/learning-to-code/setting-up-copilot-for-learning-to-code) · [Mentor agent](https://github.com/github/awesome-copilot/blob/main/agents/mentor.agent.md)
