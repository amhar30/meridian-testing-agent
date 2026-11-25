ENGAGEMENT HANDBOOK A LL TE AMS
Phase 2 Engagement Handbook
Agentic AI Bootcamp · Cohort 01 · Group Project
Read alongside your Client Brief. The brief tells you what your client wants. This tells you how the engagement runs, what you deliver, and
how you are marked. It is identical for every team.
1 · HOW THIS WORKS
You have been given a client, not an assignment. Your brief was written by someone with a business problem, not by an
instructor with a marking scheme. It is deliberately incomplete, because real briefs are, and part of your job is to find out
what is missing.
Your brief is yours alone. No two teams have the same client, the same constraints, or the same way of measuring cost,
so there is nothing to be gained by comparing solutions, and a great deal to be gained by comparing approaches.
2 · WHAT EVERY TEAM DELIVERS
# Artefact What it must contain
1 Working system Deployed, reachable, running your golden path end to end. One path that works completely beats five
that half-work.
2 Architecture
decision record
Every significant choice, the alternatives you rejected, and why. Where you assumed something
because the client had not told you, write the assumption down, you will be glad you did.
3 Cost model Built on the unit in your brief, which differs by team. Cost per unit, monthly cost at normal and peak
volume, margin at three price points, and your break-even. Every unit price cited with source and
date.
4 Evaluation report A named set of cases covering ordinary, awkward and hostile inputs. Your pass rate. What fails, and
whether you know why.
5 Load or scale test Evidence you survive the peak described in your brief. Latency at p95 and p99, error rate, and cost
under load.
6 Operations runbook What breaks, how you would know, what it costs, and how to roll back.
3 · HOW YOU ARE ASSESSED
Weight Area What we look for
25% Does it work Your golden path, completed live, under load.
20% Engineering
judgement
The ADR. Did you choose, or did you accumulate? Rejected alternatives count as much as
chosen ones.
20% Evidence Evaluation and load testing. An honest failure scores higher than silence.
15% Commercial thinking The cost model. Arithmetic, not adjectives.
10% Operability Runbook, observability, and behaviour when a dependency is down.
10% Working as a team Requirements you elicited, questions you asked, and a git history showing everyone built
something.
WHAT WILL FAIL YOU
An impressive demonstration with no evidence behind it. If you cannot show the evaluation, the scale test and the cost
arithmetic, we will assume the demonstration was staged, because in our experience it usually was.
4 · TALKING TO YOUR CLIENT
You have a standing channel to your client and they answer within one working day. Ask anything. The questions you ask
are assessed: a team that establishes what "resolved" means in week one is doing the job, and a team that never asks
has assumed, and will build the wrong thing.
Expect the brief to change. Briefs do. How you absorb a change is worth more than how neatly you executed the
original.
5 · PRICING: WHAT WE ACTUALLY WANT
Not a guess. The arithmetic. What one unit costs to serve, how that behaves as volume rises, and what you would have
to charge for this to be worth doing. Most engineers have never done this calculation, which is exactly why it is here.
Every unit price carries its source and the date you looked it up. Prices move; an undated number is worthless. Where
you cannot find a price, say so and state the assumption you used instead.
6 · GROUND RULES
Use AI assistance freely, and disclose it. We care whether you understand what you shipped, and we will find out by
asking.
Everything ships through GitHub. We review the history, not only the final state.
Use no real personal data. Synthesise it, and document how.
Each member owns a named component and will be asked about it directly. “I did a bit of everything” is not an answer.
If you are blocked on your client, say so the same day. We would rather answer a question than receive an excuse.