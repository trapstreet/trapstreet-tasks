# Pick the next element to act on

You are driving a web page toward a goal. You are given the goal, the actions
already completed, and the page's full HTML in `page.html`.

Every element you may act on carries a `backend_node_id` attribute. Name the
one element the next action should target.

`page.html` is large — a median of about 730 actionable elements, up to 2,159.
There is no shortlist: narrowing the page down is part of the task.

Print these three lines. Anything else you write is ignored, and only the LAST
occurrence of each line is read:

    ELEMENT: <backend_node_id>
    OP: <CLICK | TYPE | SELECT>
    VALUE: <the text to type or option to select, or leave empty for CLICK>

Scoring is on `ELEMENT` first: naming the right element is the task. `OP` and
`VALUE` are scored beside it and a case counts as a full step success only when
all three are right. One element is scored -- the last `ELEMENT:` line -- so
listing several candidates does not help.
