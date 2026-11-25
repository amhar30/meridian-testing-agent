C LIENT ENGAGEMENT BRIEF CONFIDENTI A L
Meridian Systems
Regression Safety Net for a Legacy Service
Enterprise software, 40 engineers · Issued to Group 04, Mohamed Mahushook Mohamed Amhar · Omar Ejaz · Mohamed Ilyas Abdullah ·
Brief v1.0, 18 Sep 2026
1 · WHO WE ARE, AND WHAT HURTS
We run a Python service that has been in production for nine years. It earns most of our revenue and it terrifies us. Test
coverage is 23% and concentrated in the easy parts.
We ship regressions. Not often, but reliably, and always in the modules nobody wants to touch. Our engineers will not
write tests for code they did not write and do not understand, and we cannot blame them. We need tests that actually
catch the bugs we actually introduce.
2 · WHERE WE ARE, AND WHERE WE NEED TO BE
Measure Today Where we need to be
Test coverage 23% meaningful coverage on the 20 highest-risk
modules
Regressions reaching production roughly one per
fortnight
halved, and provably so
Time an engineer spends writing tests for unfamiliar
code
hours, and they avoid
it
minutes of review on a generated test
Tests that pass but assert nothing useful we suspect many zero from your system: we will check
3 · WHAT WE NEED YOU TO BUILD
Read a module it has never seen and work out what it is supposed to do.
Generate tests that genuinely exercise its behaviour, including the awkward paths, errors, boundaries, and the states
the original author forgot.
Run them, see what fails, and work out whether the test is wrong or the code is.
Refine the tests that are wrong, and report the code that is.
Hand an engineer a reviewable test file with a short note on what it covers and what it deliberately does not.
4 · THE SHAPE OF THE WORK
Window Volume Notes
Target modules 20 modules, 200–1,500 lines each The highest-risk ones; we will point them
out
Runs On demand, and on every pull request touching those
modules
Per-module
budget
under 10 minutes of wall clock
5 · OUR CONSTRAINTS
Constraint The requirement
Budget USD 400 per month. Our engineers cost more than this per hour, so the bar is low, but you must show the
arithmetic.
Proof of value A generated test that passes is worthless to us. We will seed deliberate bugs into our code and measure
how many of your tests catch them. That is your score, not coverage percentage.
No production
access
The system reads our repository. It does not touch our running service.
Human authority No generated test is merged without an engineer approving it.
Determinism Re-running on unchanged code should not produce wildly different tests. We need to trust it.
MERIDI AN SYSTEMS: REGRESSION S A FET Y NET FOR A LEGACY SERV I C E PAGE 2 OF 2
6 · YOUR COST MODEL
The unit for this engagement is one module covered. Your budget goes on convergence, not on first generation. A
module that takes seven refinement cycles costs seven times one that takes one, so measure the retries, not just the
output.
Line item What drives it
Model: code comprehension module size in tokens
Model: test generation attempts per module
Model: failure diagnosis and refinement this is where your budget actually goes
Test execution compute runs per module x refinement cycles
CI integration per pull request touching a covered module
Observability spans per module run
Engineer time the cost you displace, and the reason the bar is low
Report: cost per one module covered, monthly cost at normal and at peak volume, and the point at which this stops being cheaper than
the people doing it today. Every unit price must carry its source and the date you looked it up.
7 · WHERE YOUR DATA COMES FROM
Use a real open-source Python codebase as your subject, one large enough to be genuinely unfamiliar. Create your
evaluation by mutation: seed known bugs into the code and measure what fraction of them your generated tests catch.
That number is the whole project. A coverage percentage is not evidence; a caught mutation is.
8 · IN SCOPE
Test generation and self-refinement for an existing
codebase.
Mutation-based evaluation with a reported catch rate.
Reviewable output in our conventions.
9 · OUT OF SCOPE
Writing or refactoring production code. You write tests,
not features.
A general-purpose tool-building agent. Your original
proposal was unbounded; this is the bounded version of
it, and it is still hard enough.
10 · WHAT WE HAVE NOT TOLD YOU
Which 20 modules. Ask, and ask why those.
What our test conventions are, you will produce something our engineers reject if you guess.
Whether we want unit tests, integration tests, or both.
What we mean by 'high risk'. It is not what you think.
ASKING IS PART OF THE WORK, AND IT IS GRADED
You have a standing channel to us and we answer within one working day. A team that pins down what "good enough" means
in week one is doing the job. A team that never asks has assumed, and will build the wrong thing.
11 · DEFINITION OF DONE
1. Twenty named modules are covered by tests that an engineer reviewed and merged.
2. Your mutation catch rate is reported, the fraction of deliberately seeded bugs your tests detect. This is your score,
not coverage percentage.
3. Zero generated tests pass while asserting nothing meaningful, proven by your own check rather than by assurance.
4. Re-running on unchanged code produces stable, comparable tests.
5. Under 10 minutes of wall clock per module.
6. Cost per module covered, with the average retry count shown.
A NOTE FROM THE ENGAGEMENT SPONSOR
Your original proposal: an agent that autonomously builds useful tools while another generates and refines their tests, has no
edge. There is no way to say when it is finished and no way to say whether it is good. This brief keeps the interesting half, selfrefining generation against real feedback, and gives it something to be measured against.