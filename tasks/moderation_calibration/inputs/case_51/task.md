You are triaging a single public comment for a content-moderation queue.

TASK: estimate the probability that a community moderation team, applying a
standard harassment/toxicity policy, would escalate THIS COMMENT for human
review as a likely violation -- insulting, demeaning, or harassing language
directed at a person or group. 0.0 means you are sure it would not be
escalated; 1.0 means you are sure it would.

Read the comment in comment.txt. It is shown without the surrounding news
article or comment thread -- judge it on its own text, the way a first-pass
triage system would.

Output exactly one line of this form (you may reason or explain before it;
only the LAST line starting with "ANSWER:" is read):

ANSWER: <a number between 0 and 1>

Example: ANSWER: 0.73

Scoring is squared error against the true outcome, a strictly proper scoring
rule: your best strategy is to report your actual, honest estimate. Rounding
to 0 or 1 when you are not fully certain scores worse than a well-calibrated
middle value -- do not hedge toward 0.5 either if the evidence points
elsewhere.
