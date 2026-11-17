# Status reports

Use for recurring team status reports that are presented to leadership, such as fortnightly cycle reports, sprint reviews and initiative updates. The general writing rules in [documentation.md](documentation.md) still apply.

## STATUS-TEMPLATE — keep the team's template

- Reuse the existing template exactly: header table, section order, risk tables. Change the content, never the structure.
- If the template has a panel or macro the write tool cannot reproduce, say so before the write. Keep it if the tool allows; otherwise report the loss after the write.
- Read the team's best earlier report before drafting and use it as the style reference.

## STATUS-SHAPE — outcome first, one initiative at a time

- Give one executive summary per initiative. Each names the outcome for users or the business, and the next step.
- Group delivered work by initiative, in short nested bullets of plain language. Put no ticket ids in the prose.
- Show progress as a table with these columns: metric, baseline, current, target, trend.
- Each initiative's metric is backed by data and is not a code count. Examples: traffic served, services migrated, go-live readiness, time saved. Cite the metric's source and the date it was read.
- Learnings are observed facts with numbers that change a decision. Good: "93% of requests hit two charts, so port those first". Opinions are not learnings.
- A risk is a real blocker, or a decision needed from someone outside the team. It names an owner. Work that is in progress or in testing toward a date is not a risk.

## STATUS-DATA — research the whole board, present the outcomes

- Pull the tracker for the period through the cheap tier. Cover:
  - done work, and in-progress work by status
  - the review and test queue
  - stale or unowned items
  - epics
  - commitment against completion
  - cycle time
  - the share of bugs
- Use velocity, counts and cycle time to decide what to say: bottlenecks, release order, over-commitment. A presented report shows outcomes, not throughput, so leave those numbers out of the text.
- Leave automated dependency-bump tickets out of every count. An item closed as won't-do is not delivered.
- Check each claim against the latest notes and the tracker, because a stale plan can name the wrong target.
- If a claim comes from notes older than the report, flag it to the user before publishing.

## STATUS-VOICE — balanced and specific, no self-praise

- Give the full picture: what shipped, what is waiting and why, what comes next. Include work that is stuck.
- Do not congratulate the team or yourself. Phrases like "moved from scoping to shipping", "ahead of plan" and "scope held" do not belong.
- Specific dependencies, release order and named bottlenecks show command of the work better than adjectives do.
- Never credit the author's own contributions. The report speaks for the team.
- Keep each bullet to one line. A presenter reads the report aloud.

## STATUS-DELIVER — draft, approve, publish, then message

- Show the full draft in chat. Publish only after explicit approval, and publish the approved text word for word, as `DOC-DELEGATE` in [documentation.md](documentation.md) requires.
- After publishing, draft two short messages. One asks the team to review the report and raise questions. The other summarises the report for the lead and includes the link. Both follow the same rules: outcome first, no velocity.
