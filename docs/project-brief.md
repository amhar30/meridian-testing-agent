Buildr
Labs
Group Project Brief
Eight weeks, a real client, and a system you have to prove
Agentic AI Bootcamp · Cohort 1
W H A T T H I S B R I E F C O V E R S
Three things, in order
01 What are you given?
A client requirement document and a set of engineering standards. Not a
specification, and not an architecture.
02 How are you judged?
On whether your system meets the client's constraints, and whether you can prove it
with evidence rather than assert it in slides.
03 What do you hand over?
Six deliverables, a live pitch, a failure demonstration, and an individual defence of
your own work.
1
T H E M E A S U R I N G S T I C K U S E D T H R O U G H O U T
Five stages of delivery
Every requirement in this brief sits on the same five-stage scale. The stages are a framing device for the project, not a formal marking
scheme.
01
Interpret
Turn a business brief into
requirements
02
Design
Choose an architecture and
defend it
03
Build
Write the system in code
04
Prove
Show it meets every
constraint
05
Pitch
Sell it, price it, and defend it
Most student projects put nearly all of their effort into stage 03 and treat the rest as paperwork. On this project, stages 04 and 05 carry as much weight
as the build.
2
01
What you
are given
Two documents, and nothing else. Read both before you write any code.
Buildr
Labs
3
S E C T I O N 0 1
The project at a glance
8
weeks
From brief release to live pitch,
running alongside the rest of
the programme
2
documents
A client requirement, and your
firm's engineering standards
6
deliverables
A system, a decision record,
evidence, a cost model, a
proposal, a pitch
0
specifications given
Nobody will tell you what to
build or how to build it
Constraints in the requirement document are set by the client. They are not negotiable, and they are not decoration.
4
DOC-A business language · no technical direction · issued week 1
The Client RFP
Written by the client. Every item below is a constraint you will be marked against.
S I X S E C T I O N S
1. The business problem, and who it affects
2. The outcome the client expects
3. Monthly infrastructure budget ceiling
4. Peak and average traffic volumes
5. Acceptable response latency
6. Compliance and human escalation requirements
R E A D S A S
A brief from a business, not a task from a lecturer.
No framework, architecture, agent count or data model is named
anywhere in it. If a question is not answered in the document, it
is a question for the client, not an assumption for you to make
quietly.
G O V E R N S
Interpret · Design · Prove
5
DOC-B mandatory · deviations must be defended in your ADR
Engineering Standards
Written by your firm. This is how a BuildrLabs engagement is delivered, on every project.
T H E S T A C K
LangGraph for orchestration
Context engineering and context budgeting
MCP servers for tool and resource access
Agentic memory: working context plus long term store
Recognised agentic design patterns, chosen and justified
Langfuse instrumentation across every trace
Containerised delivery, reproducible from a clean machine
R E A D S A S
A delivery standard, not a suggestion.
Anything outside this list is a decision you own. Take it if the
client's constraints justify it, record it in your architecture decision
record, and expect to be asked about it at the pitch.
G O V E R N S
Design · Build · Prove · Pitch
6
S E C T I O N 0 1 · W E E K O N E
The client Q and A round
Anything the requirement document leaves open is a question for the client. You get one formal round.
01
You submit
Your team sends written questions to the
client during week one. There is no limit
on how many.
02
The client answers
Answered in character, as a client would
answer a consultancy that is bidding for
work.
03
Everyone sees them
All answers are published to every team.
No team gets a private advantage from
asking well, but every team is exposed by
not asking at all.
This is how real procurement runs. Teams that interrogate the brief build the right thing. Teams that guess build something impressive that nobody
asked for.
7
02
How you
are judged
The rule that governs every mark on this project
Buildr
Labs
8
T H E R U L E T H A T M A T T E R S M O S T
Constraints must be
proven, not asserted.
Every constraint in the requirement document has a matching artifact you must produce.
9
S E C T I O N 0 2
Constraint to evidence mapping
C O N S T R A I N T R E Q U I R E D E V I D E N C E
Budget ceiling Cost model derived from measured trace costs at the stated volume
Peak concurrent load Load test executed, with results and observed latency reported
Response latency Latency distribution from Langfuse, not an average
Human escalation path Demonstrated live during the pitch
Compliance requirement Audit trail or control shown in the running system
No artifact, no mark. A claim in a slide is not evidence.
10
S E C T I O N 0 2
Four roles, declared in writing
Your role is traceable to your individual mark. The commercial work is not a side task.
01
Technical Lead
Delivery, integration, code
quality, and the system
actually running on demo day.
02
Agent Architect
Graph design, agentic
patterns, memory strategy,
MCP servers, and the
reasoning behind each.
03
Observability Owner
Instrumentation, trace quality,
load testing, and every piece
of evidence you present.
04
Commercial Lead
Cost model, unit economics,
pricing structure, and the
client-facing proposal.
Roles may rotate, but they must be declared at kickoff and recorded. Undeclared contribution cannot be marked.
11
S E C T I O N 0 2 · C O N C L U S I O N
How the marks are distributed
Agentic architecture and design patterns 20
Requirement interpretation and solution fit 15
Context engineering, MCP and memory 15
Observability and evidence quality 15
Constraint compliance, proven 15
Commercial model and unit economics 10
Pitch and individual defence 10
65 of 100 is engineering, and most of it is evidence based rather than impression based. A polished presentation over a weak system will not carry
you. A strong system with no evidence will not either.
12
03
What you
hand over
Six deliverables, a failure demonstration, and a defence of your own work
Buildr
Labs
13
S E C T I O N 0 3
Six deliverables
01
Working system
Containerised and reproducible from a
clean machine.
02
Architecture Decision
Record
What you chose, what you rejected, and
why.
03
Langfuse dashboard
Evidence against every constraint in the
requirement.
04
Cost model
Unit economics derived from measured
trace data.
05
Commercial proposal
Pricing model, tiering, and margin logic.
06
Live pitch and defence
Presented to a client panel, with individual
questioning.
14
S E C T I O N 0 3 · A T T H E P I T C H
You will break your own system
On stage, in front of the panel. Your system must degrade gracefully and visibly.
Kill a tool
An API your agent depends on goes
down mid conversation.
Feed malformed input
Something the happy path never
anticipated.
Exceed the context
Push past the window and show what
your memory strategy does.
W H Y T H I S I S H E R E
This is the difference between a demo and a system, and it is very difficult to fake. Prepare for it. Do not improvise it on the day.
15
C O M M E R C I A L
Your pricing must cover your
measured cost per interaction.
At the client's stated volume. If it does not, the commercial section fails outright, with no partial credit.
16
S E C T I O N 0 3
How the eight weeks are spent
Week 1
Brief release, teams formed,
roles declared, client questions
submitted
Week 2
Client answers published,
architecture spikes, first draft
of the ADR
Weeks 3 to 4
Core build. Agent graph, tools,
MCP servers, memory
Week 5
Observability layer. Full
Langfuse instrumentation
across every trace
Week 6
Load testing, cost model, and
constraint evidence gathered
Week 7
Commercial proposal, failure
hardening, pitch rehearsal
Week 8
Live pitch, failure demo,
individual defence
Instrument early
Evidence reconstructed in
week seven looks exactly like
what it is.
The project runs alongside the rest of the programme. Week eight is fixed and will not move.
17
S E C T I O N 0 3 · N O N N E G O T I A B L E
You will be questioned individually
On the components attributed to you in your declared role, by a panel that has read your architecture decision record.
How does it work? Why was it built this way? What breaks it?
If you cannot answer all three, the mark does not stand, regardless of how well the team performed.
This is announced now so that nobody is ambushed in week eight.
Use every AI tool available to you. Cursor, Claude Code, all of it. Then understand what you shipped.
18
C O N C L U S I O N
Where this project takes you
Grey stages are covered by the taught programme. Orange stages are what this project adds.
01
Interpret
Turn a business brief into
requirements
02
Design
Choose an architecture and
defend it
03
Build
Write the system in code
04
Prove
Show it meets every
constraint
05
Pitch
Sell it, price it, and defend it
One brief, one client, and the full arc from a business requirement to a system you can stand behind under questioning.
19
S T A R T H E R E
Four things, this week.
01 Form your team
02 Declare your roles
03 Read both documents end to end
04 Submit your client questions
Then, and only then, open your editor.
Buildr Labs Hatch Works, Colombo · buildrlabs.ai
20