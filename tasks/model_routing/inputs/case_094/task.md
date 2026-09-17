Answer one multiple-choice question as cheaply as you can without losing accuracy.

question.json holds `question` and `options` (lettered A, B, C, ...). Exactly
one option is correct. Questions come from law and engineering exams.

End your output with one line naming the option (anything before it is
ignored; only the LAST "ANSWER:" line is read, and markdown around it, such as
**ANSWER: C**, is fine):

ANSWER: <letter>

The score is the share of questions answered correctly. Cost and latency are
measured by the runner and shown next to the score, so a solution that gets the
same accuracy for less is the better one.

If your solution can hand a question from one model to another (for example a
cheap model first, a stronger one when needed), also print:

ESCALATED: yes|no
FIRST_ANSWER: <letter>

`ESCALATED: yes` when the final answer came from a different, more expensive
step than the first one tried. `FIRST_ANSWER` is the first step's answer,
before any escalation (omit it if the first step gave none, or if no answer was
produced before routing). Neither is scored; the run page uses them to report
how often escalation was needed.
