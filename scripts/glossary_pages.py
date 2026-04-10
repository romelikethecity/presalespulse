# scripts/glossary_pages.py
# Glossary section page generators (40 term pages + index).
# Each term page: 300-600 words, breadcrumb schema, FAQ schema, related terms, newsletter CTA.

import os
import re
import json

from nav_config import *
from templates import (get_page_wrapper, write_page, get_breadcrumb_schema,
                       get_faq_schema, breadcrumb_html, newsletter_cta_html,
                       faq_html)


def slugify(text):
    """Convert term name to URL slug."""
    text = text.lower()
    text = re.sub(r'\(.*?\)', '', text)  # strip parenthetical abbreviations
    text = text.strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


# ---------------------------------------------------------------------------
# Category groupings (for index page)
# ---------------------------------------------------------------------------

GLOSSARY_CATEGORIES = {
    "Sales Process": [
        "proof-of-concept", "technical-win", "discovery-call", "technical-discovery",
        "proof-of-value", "sales-cycle", "technical-close", "mutual-action-plan",
        "reference-call", "custom-demo", "first-call-deck",
    ],
    "Tools & Infrastructure": [
        "demo-environment", "sandbox", "demo-script", "feature-matrix",
        "competitive-battlecard", "sandbox-provisioning", "security-questionnaire",
    ],
    "Roles & Org Structure": [
        "champion", "buying-committee", "technical-decision-maker", "economic-buyer",
        "overlay-se", "se-to-ae-ratio", "presales-operations", "solution-consulting",
    ],
    "Methodologies": [
        "value-selling", "meddpicc", "solution-architecture", "stakeholder-mapping",
        "white-space-analysis", "win-loss-analysis",
    ],
    "Metrics": [
        "demo-to-close-rate", "poc-success-criteria",
    ],
    "Procurement & Documentation": [
        "request-for-proposal", "request-for-information", "deal-desk",
        "integration-requirements", "technical-objection",
    ],
    "Concepts": [
        "pre-sales",
    ],
}


# ---------------------------------------------------------------------------
# Term database (40 terms)
# ---------------------------------------------------------------------------

GLOSSARY_TERMS = [
    {
        "term": "Proof of Concept (POC)",
        "slug": "proof-of-concept",
        "abbr": "POC",
        "definition": "A structured evaluation where a prospect tests your product against specific success criteria before committing to purchase.",
        "body": """<p>A POC is the proving ground. The prospect picks a real use case, you configure the product, and both sides agree on what success looks like before the evaluation starts. Unlike a demo, a POC puts the product in the prospect's hands with their data, their workflows, and their edge cases.</p>

<p>Most POCs run 14 to 30 days. Shorter is better. Long POCs lose momentum, invite scope creep, and give competitors time to counter. The best SEs set tight timelines with clear milestones so the evaluation stays focused.</p>

<h2>Why It Matters for SEs</h2>
<p>POCs are where deals are won or lost on technical merit. A strong demo can get you to the POC stage, but only a well-run POC earns the <a href="/glossary/technical-win/">technical win</a>. SEs who run sloppy POCs (vague success criteria, no check-ins, open-ended timelines) lose deals they should win.</p>

<p>POCs also carry real cost. Engineering resources, SE time, and sometimes infrastructure spend all go into a POC. That means SEs need to qualify hard before agreeing to one. Not every deal deserves a POC, and running one for an unqualified prospect burns cycles that could go toward winnable deals.</p>

<h2>How SEs Use This</h2>
<p>Before the POC starts, get the <a href="/glossary/poc-success-criteria/">success criteria</a> documented and signed off by the <a href="/glossary/technical-decision-maker/">technical decision maker</a>. Build a <a href="/glossary/mutual-action-plan/">mutual action plan</a> that includes weekly check-ins, a mid-point review, and a final readout. During the POC, stay close to the evaluation team. Answer questions within hours, not days. At the end, walk through each criterion and get explicit confirmation that the product passed.</p>

<p>The strongest SEs treat the POC readout as a mini-close. If every criterion is met, ask for the technical win on the spot. Don't let the evaluation drift into "we need to discuss internally" without a next step on the calendar.</p>""",
        "faq": [
            ("How long should a POC last?", "Most B2B SaaS POCs run 14 to 30 days. Shorter is almost always better. Longer POCs lose momentum and invite scope creep. Set a firm end date and hold to it."),
            ("What is the difference between a POC and a free trial?", "A free trial is self-serve with minimal structure. A POC is a guided evaluation with defined success criteria, SE support, and a formal readout. POCs are common in enterprise sales where the buying committee needs documented proof."),
            ("Should every deal include a POC?", "No. POCs require significant SE and engineering time. Reserve them for deals where the prospect has a genuine technical concern that a demo cannot address. Many deals close after a strong custom demo and reference calls."),
        ],
        "related": ["poc-success-criteria", "technical-win", "proof-of-value", "mutual-action-plan", "demo-environment"],
    },
    {
        "term": "Technical Win",
        "slug": "technical-win",
        "definition": "When the SE has convinced the technical evaluators that the product meets their requirements, clearing the technical hurdle even though commercial, legal, and procurement close remain.",
        "body": """<p>The technical win is the SE's finish line. It means the technical evaluation team has agreed that your product works for their use case. The deal still needs pricing approval, legal review, and procurement signoff, but the technical objections are resolved.</p>

<p>Getting to a technical win requires more than a good demo. It means answering every technical question, surviving the <a href="/glossary/proof-of-concept/">POC</a> (if there is one), addressing <a href="/glossary/security-questionnaire/">security questionnaires</a>, and satisfying the <a href="/glossary/integration-requirements/">integration requirements</a>. The technical evaluators need to feel confident recommending your product to the <a href="/glossary/buying-committee/">buying committee</a>.</p>

<h2>Why It Matters for SEs</h2>
<p>Technical win rate is the clearest measure of SE performance. AEs own the commercial close, but SEs own the technical close. If your technical win rate is high but overall close rate is low, the bottleneck is pricing, procurement, or deal strategy, not your work. If your technical win rate is low, you need to improve your discovery, demos, or POC execution.</p>

<p>Tracking technical wins separately from closed deals also protects SEs in comp discussions. An SE who wins 80% of their technical evaluations is performing well even if some of those deals stall in legal for months.</p>

<h2>How SEs Use This</h2>
<p>Document the technical win explicitly. Get the <a href="/glossary/technical-decision-maker/">TDM</a> to confirm in writing (email works) that the product meets their requirements. This creates a record you can reference if the deal slows down and also gives your AE ammunition for the commercial negotiation.</p>

<p>After securing the technical win, shift your focus to supporting the AE on procurement. Help build the business case, prep for executive presentations, and be available for any last-minute technical questions from finance or legal stakeholders.</p>""",
        "faq": [
            ("What is a good technical win rate?", "Top-performing SEs achieve technical win rates of 70-85% on qualified opportunities. Below 50% suggests issues with discovery, demo quality, or prospect qualification. Above 90% may mean the team is not competing in enough challenging deals."),
            ("How do you document a technical win?", "Get written confirmation from the technical decision maker that the product meets their evaluation criteria. An email summarizing the POC results with explicit approval is the standard approach. Log it in your CRM so leadership has visibility."),
            ("What happens after a technical win?", "The deal moves to commercial negotiation, legal review, and procurement. The SE stays involved for technical questions but the AE leads. In complex deals, the SE may present to the economic buyer or help build the ROI case."),
        ],
        "related": ["proof-of-concept", "technical-close", "technical-decision-maker", "buying-committee", "poc-success-criteria"],
    },
    {
        "term": "Champion",
        "slug": "champion",
        "definition": "An internal advocate at the prospect organization who actively sells your solution to other stakeholders, built through technical credibility and trust.",
        "body": """<p>A champion is not just someone who likes your product. A real champion has influence inside their organization, understands the internal politics, and is willing to spend their own political capital to push your deal forward. They attend meetings you are not in and argue your case when objections come up.</p>

<p>Champions are built, not found. SEs create champions by solving real problems during <a href="/glossary/discovery-call/">discovery</a> and <a href="/glossary/proof-of-concept/">POC</a> phases. When you help someone look good in front of their leadership, they become invested in your success. The relationship is mutual: you make them the hero internally, and they give you access to stakeholders, budget information, and competitive intelligence.</p>

<h2>Why It Matters for SEs</h2>
<p>Deals without a champion close at dramatically lower rates. The <a href="/glossary/meddpicc/">MEDDPICC</a> framework lists Champion as one of its core qualification criteria for this reason. An SE who cannot identify or build a champion in a deal is flying blind through the <a href="/glossary/buying-committee/">buying committee</a>.</p>

<p>Champions also reduce wasted effort. A good champion tells you when a deal is dead before you invest another 40 hours in it. They warn you about competing priorities, budget freezes, and internal politics that would otherwise blindside you.</p>

<h2>How SEs Use This</h2>
<p>Test your champion early. Ask them to do something small but meaningful: introduce you to another stakeholder, share internal evaluation criteria, or confirm the timeline. If they cannot or will not do these things, they are a coach at best, not a champion.</p>

<p>Arm your champion with materials they can use internally. <a href="/glossary/competitive-battlecard/">Battlecards</a> they can reference, one-pagers for their boss, ROI summaries for finance. Make it easy for them to sell on your behalf. The less work they have to do, the more likely they are to do it.</p>""",
        "faq": [
            ("How do you identify a champion?", "A real champion has three qualities: access to the decision-making process, influence with other stakeholders, and willingness to advocate for your solution. Test each quality by asking them to take small actions like making introductions or sharing internal requirements."),
            ("What is the difference between a champion and a coach?", "A coach gives you information about the organization and the deal. A champion actively advocates for your solution. Coaches are helpful but passive. Champions spend political capital on your behalf. Many deals have coaches but no champion."),
            ("Can you have multiple champions in one deal?", "Yes, and for complex enterprise deals, multiple champions across different functions strengthen your position. A technical champion and a business champion covering different parts of the buying committee is a strong combination."),
        ],
        "related": ["buying-committee", "economic-buyer", "technical-decision-maker", "meddpicc", "stakeholder-mapping"],
    },
    {
        "term": "Demo Environment",
        "slug": "demo-environment",
        "definition": "A pre-configured instance of your product used for demonstrations, which can be a sandbox, staging environment, or overlay tool.",
        "body": """<p>Your demo environment is your stage. It is where prospects see your product for the first time, and first impressions set the tone for the entire evaluation. A clean, well-configured demo environment loaded with realistic data makes you look like a company that cares about details. A buggy, empty, or obviously fake environment undermines your credibility before you say a word.</p>

<p>Demo environments come in several forms. Some companies use a shared staging instance that multiple SEs present from. Others give each SE their own <a href="/glossary/sandbox/">sandbox</a>. Overlay tools like Saleo or Navattic let SEs customize the front-end presentation without touching the actual product. Each approach has tradeoffs in flexibility, maintenance, and realism.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs spend a surprising amount of time maintaining demo environments. Data goes stale, features break after releases, and configuration drift creates inconsistencies between what you show and what the product does in production. A reliable demo environment is the foundation of every <a href="/glossary/custom-demo/">custom demo</a> and <a href="/glossary/proof-of-concept/">POC</a> you run.</p>

<p>The best SE orgs invest in <a href="/glossary/sandbox-provisioning/">sandbox provisioning</a> automation. Spinning up a fresh, pre-configured environment in minutes instead of hours changes how SEs approach deal prep.</p>

<h2>How SEs Use This</h2>
<p>Treat your demo environment like production. Check it before every call. Load data that matches the prospect's industry and use case. Remove anything that could distract or confuse. If your product supports it, create saved states so you can quickly reset between demos.</p>

<p>Keep a running list of demo environment issues and escalate them to product or engineering. Broken demo environments cost deals. Smart SE leaders track demo environment uptime and reliability as a metric for <a href="/glossary/presales-operations/">presales operations</a>.</p>""",
        "faq": [
            ("What makes a good demo environment?", "Realistic data that matches common prospect use cases, reliable uptime, fast load times, and the ability to customize quickly for specific prospects. The data should look like a real company uses the product, not placeholder text."),
            ("Should each SE have their own demo environment?", "For teams running more than a few demos per week, yes. Shared demo environments create conflicts when two SEs need different configurations at the same time. Individual sandboxes with a shared data baseline is the most common enterprise approach."),
            ("How often should demo environments be refreshed?", "After every major product release, at minimum. Many teams reset weekly. Stale demo environments with outdated UI or missing features create a gap between what you show and what the prospect will see in production."),
        ],
        "related": ["sandbox", "sandbox-provisioning", "custom-demo", "demo-script", "presales-operations"],
    },
    {
        "term": "Sandbox",
        "slug": "sandbox",
        "definition": "An isolated product environment where prospects or SEs can experiment without affecting production data or configurations.",
        "body": """<p>A sandbox is a safe space for exploration. For SEs, it is where you build <a href="/glossary/custom-demo/">custom demos</a>, test configurations, and prep for <a href="/glossary/proof-of-concept/">POCs</a>. For prospects, it is where they kick the tires during an evaluation. The defining characteristic is isolation: nothing done in a sandbox affects real data or other users.</p>

<p>Sandboxes range from fully functional product replicas to stripped-down evaluation instances. The best sandboxes mirror production capabilities closely enough that prospect testing is meaningful. A sandbox that is missing critical features or has artificial limits frustrates evaluators and creates doubt about the real product.</p>

<h2>Why It Matters for SEs</h2>
<p>Sandbox quality directly affects your <a href="/glossary/proof-of-concept/">POC</a> outcomes. If the sandbox is slow, buggy, or limited, prospects will attribute those problems to the product itself. SEs need to know exactly where the sandbox differs from production and be upfront about those differences before the evaluation starts.</p>

<p>Access and provisioning speed matter too. If it takes a week to get a prospect a sandbox, you have lost momentum. Competitors who can provision in hours or minutes have an advantage in fast-moving evaluations.</p>

<h2>How SEs Use This</h2>
<p>Pre-load sandboxes with data relevant to the prospect's industry before handing them over. An empty sandbox feels like homework. A pre-configured one feels like a preview of their future. Walk the prospect through the sandbox on a call before letting them explore independently, so they know where to focus.</p>

<p>After the prospect has access, check in regularly. Monitor their activity if the product supports it. If they have not logged in after three days, call them. Sandbox evaluations that stall usually mean the prospect is busy, confused, or losing interest, and all three require your intervention.</p>""",
        "faq": [
            ("What is the difference between a sandbox and a demo environment?", "A demo environment is configured for SEs to present from. A sandbox is configured for prospects to explore independently. In practice, many companies use the same infrastructure for both, with different data and access levels."),
            ("How long should prospect sandbox access last?", "Two to four weeks is standard for enterprise evaluations. Shorter for simpler products. Avoid open-ended access because evaluations without deadlines lose urgency and rarely convert."),
            ("Should sandboxes have real or synthetic data?", "Use realistic synthetic data that represents common use cases. Real prospect data raises privacy and compliance concerns. The data should be believable enough that the prospect can imagine their own workflows, not obviously fake."),
        ],
        "related": ["demo-environment", "sandbox-provisioning", "proof-of-concept", "custom-demo", "poc-success-criteria"],
    },
    {
        "term": "Request for Proposal (RFP)",
        "slug": "request-for-proposal",
        "abbr": "RFP",
        "definition": "A formal procurement document where prospects detail their requirements and ask vendors to propose solutions, pricing, and implementation plans.",
        "body": """<p>RFPs are the enterprise buying process in document form. The prospect lists their requirements (often hundreds of them), sets a response deadline, and distributes the document to multiple vendors. Your job is to respond with a proposal that demonstrates you meet those requirements better than the competition.</p>

<p>RFPs vary wildly in quality. Some are thoughtful, well-structured evaluations. Others are copy-pasted templates that do not reflect the prospect's actual needs. Experienced SEs learn to distinguish between the two quickly because the level of effort you invest should match the quality and seriousness of the RFP.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs typically own the technical sections of RFP responses. That means answering questions about product capabilities, <a href="/glossary/integration-requirements/">integrations</a>, security, scalability, and architecture. In large organizations, the SE coordinates with product, engineering, and security teams to assemble accurate responses.</p>

<p>RFPs are time-intensive. A thorough response can take 20 to 40 hours. SEs who treat every RFP the same burn out fast. Learn to qualify RFPs: Is there a <a href="/glossary/champion/">champion</a> inside? Did you help shape the requirements? Or did this RFP land cold, meaning you are likely column fodder?</p>

<h2>How SEs Use This</h2>
<p>Build an RFP response library. Most technical questions repeat across RFPs with minor variations. A well-organized library of pre-approved answers cuts response time dramatically. Tools like Loopio and Responsive exist specifically for this purpose.</p>

<p>Go beyond just answering the questions. Add context, examples, and links to documentation. Where your product excels, highlight it. Where there are gaps, be honest but frame the workaround. Prospects who catch you claiming capabilities you do not have will disqualify you and never tell you why.</p>""",
        "faq": [
            ("How long does an RFP response typically take?", "A complete RFP response usually takes 20 to 40 SE hours depending on complexity. Teams with strong response libraries and RFP automation tools can cut that by 40-60%."),
            ("Should you respond to every RFP?", "No. Cold RFPs where you have no existing relationship, no champion, and did not help shape the requirements have very low win rates. Qualify RFPs the same way you qualify any deal before investing significant SE time."),
            ("What is the difference between an RFP and an RFI?", "An RFI (Request for Information) is a preliminary, less formal document used to gather vendor information and narrow the field. An RFP is a formal procurement step that asks for specific proposals and pricing. RFIs often precede RFPs."),
        ],
        "related": ["request-for-information", "feature-matrix", "security-questionnaire", "integration-requirements", "competitive-battlecard"],
    },
    {
        "term": "Request for Information (RFI)",
        "slug": "request-for-information",
        "abbr": "RFI",
        "definition": "A preliminary information-gathering document prospects send to multiple vendors to understand capabilities and narrow the field before a formal RFP.",
        "body": """<p>An RFI is the first filter in formal procurement. The prospect is early in their evaluation, usually trying to understand which vendors to shortlist for deeper evaluation. RFIs ask broader questions than <a href="/glossary/request-for-proposal/">RFPs</a>: company background, high-level capabilities, customer references, and general pricing ranges.</p>

<p>RFIs are lower effort than RFPs but should not be dismissed. They determine who makes the shortlist. A strong RFI response that clearly communicates your differentiation gets you to the next round. A generic, template-heavy response gets you eliminated.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs typically spend less time on RFIs than RFPs, but the technical sections still need your input. The key is calibrating your effort. RFI responses should be thorough enough to demonstrate competence but concise enough that you are not writing a full proposal for a preliminary step.</p>

<p>RFIs are also a signal. If a prospect sends you an RFI, they are early enough in the process that you can still influence the <a href="/glossary/request-for-proposal/">RFP</a> requirements. Smart SEs use the RFI as an opening to request a <a href="/glossary/discovery-call/">discovery call</a> where they can learn what the prospect cares about and shape the evaluation criteria.</p>

<h2>How SEs Use This</h2>
<p>Respond promptly. RFIs often have tight turnarounds, and late submissions are automatic disqualifications. Use your RFP response library for the technical sections. Customize the executive summary and differentiators for this specific prospect's industry and stated needs.</p>

<p>Include a clear call to action in your response. Suggest a technical briefing or <a href="/glossary/discovery-call/">discovery call</a> as a next step. RFIs are impersonal by design. Getting a conversation started before the RFP drops gives you an advantage over vendors who only communicate through documents.</p>""",
        "faq": [
            ("What is the difference between an RFI and an RFP?", "An RFI is a preliminary, less formal document used to narrow the vendor field. An RFP is a formal procurement step requesting specific solutions and pricing. RFIs come first and determine who gets invited to the RFP stage."),
            ("How much time should an SE spend on an RFI?", "Typically 4 to 8 hours. Use existing response library content for technical sections. Focus custom effort on the executive summary and any sections that differentiate your product for this prospect's specific needs."),
            ("Should you always respond to an RFI?", "Yes, if you are a reasonable fit. RFIs are lower effort than RFPs and determine shortlist inclusion. Not responding guarantees you will not be invited to the RFP. Respond and use the opportunity to request a discovery conversation."),
        ],
        "related": ["request-for-proposal", "discovery-call", "feature-matrix", "competitive-battlecard"],
    },
    {
        "term": "Value Selling",
        "slug": "value-selling",
        "definition": "A sales methodology that focuses on quantifying the business impact of your solution rather than listing features and capabilities.",
        "body": """<p>Value selling flips the conversation from "what does it do" to "what is it worth." Instead of walking through a feature list, you calculate the revenue gained, costs saved, or time recovered by implementing your solution. The prospect evaluates your product in terms of ROI, not feature checkboxes.</p>

<p>The approach requires strong <a href="/glossary/discovery-call/">discovery</a>. You cannot quantify value without understanding the prospect's current costs, inefficiencies, and business objectives. Value selling starts with questions, not slides.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs who sell on features compete on feature parity. SEs who sell on value compete on outcomes. When a prospect compares two products with similar feature sets, the vendor who quantified the business impact wins. Value selling also shifts conversations away from price because a product that saves $500K per year is cheap at $100K even if the competitor charges $80K.</p>

<p>Value selling gives SEs a way to engage the <a href="/glossary/economic-buyer/">economic buyer</a> directly. Technical evaluators care about capabilities. Budget holders care about returns. An SE who can speak both languages is more effective than one who only speaks tech.</p>

<h2>How SEs Use This</h2>
<p>Build a value framework for your product. Identify 3 to 5 quantifiable outcomes your solution delivers (time saved per week, revenue increase, cost reduction). During <a href="/glossary/technical-discovery/">technical discovery</a>, collect the data points needed to calculate those outcomes for this specific prospect.</p>

<p>Present the value calculation during your demo or <a href="/glossary/proof-of-value/">POV</a>. Show the math, not just the conclusion. Prospects trust calculations they can verify more than claims they cannot. And give your <a href="/glossary/champion/">champion</a> the value summary so they can present it internally to stakeholders you cannot reach directly.</p>""",
        "faq": [
            ("How is value selling different from solution selling?", "Solution selling focuses on matching product capabilities to requirements. Value selling goes further by quantifying the financial impact of that solution. You can use both together: solution selling to establish fit, value selling to establish ROI."),
            ("What tools support value selling?", "Dedicated platforms like Ecosystems (ValueSelling) and Mediafly help SEs build interactive ROI calculators and value assessments. Some teams build custom spreadsheets or use presentation tools with embedded calculations."),
            ("Do SEs or AEs own value selling?", "Both. SEs typically own the technical value quantification (efficiency gains, integration savings, reduced engineering time). AEs own the business framing and commercial negotiation. The strongest deals have SE and AE aligned on the same value narrative."),
        ],
        "related": ["proof-of-value", "economic-buyer", "discovery-call", "technical-discovery", "demo-to-close-rate"],
    },
    {
        "term": "Discovery Call",
        "slug": "discovery-call",
        "definition": "A structured conversation where SEs uncover the prospect's current state, pain points, technical requirements, and decision criteria.",
        "body": """<p>Discovery is the most important skill an SE can develop. A great discovery call surfaces the information that shapes everything downstream: demo customization, POC design, competitive positioning, and value quantification. A weak discovery call means you are guessing at what matters, and guessing loses deals.</p>

<p>Good discovery calls follow a structure without feeling scripted. You are mapping the prospect's current state (what they use today), desired state (what they want), pain points (what is not working), and decision criteria (how they will choose a vendor). Each answer informs the next question.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs who skip discovery or treat it as a formality end up delivering generic demos that do not resonate. The prospect sits through features they do not need, misses the ones they do, and leaves thinking your product is "fine but not differentiated." That outcome is almost always a discovery failure, not a product failure.</p>

<p>Discovery also qualifies the deal. If the prospect's requirements fall outside your product's strengths, it is better to know that in the first call than after a 30-day <a href="/glossary/proof-of-concept/">POC</a>. SEs who qualify out of bad-fit deals early protect their time and their team's resources.</p>

<h2>How SEs Use This</h2>
<p>Prepare 8 to 12 open-ended questions before the call. Prioritize questions that reveal technical architecture, current pain, and decision process. Take detailed notes. Share a summary with the AE after the call so you are aligned on what you learned and what to present in the <a href="/glossary/custom-demo/">custom demo</a>.</p>

<p>Separate the initial discovery from <a href="/glossary/technical-discovery/">technical discovery</a>. The first call covers business context and high-level requirements. The technical deep-dive (integrations, data flows, security) happens in a follow-up with the right technical stakeholders. Trying to cover everything in one call overwhelms the prospect and misses depth on what matters.</p>""",
        "faq": [
            ("How long should a discovery call last?", "Thirty to 45 minutes is the sweet spot for an initial discovery call. Long enough to cover key questions, short enough that the prospect stays engaged. A follow-up technical discovery call can go longer."),
            ("What questions should SEs ask on a discovery call?", "Focus on current state (what tools and processes exist today), pain points (what is not working), desired outcomes (what success looks like), and decision criteria (timeline, budget, stakeholders, competing vendors)."),
            ("Should the AE or SE lead the discovery call?", "The AE typically opens and covers business context. The SE takes over for technical requirements. The best teams prep together before the call and debrief after. Avoid two people asking redundant questions."),
        ],
        "related": ["technical-discovery", "custom-demo", "champion", "stakeholder-mapping", "sales-cycle"],
    },
    {
        "term": "Technical Discovery",
        "slug": "technical-discovery",
        "definition": "The deeper, SE-led phase of discovery focused on architecture, integrations, data flows, security requirements, and technical constraints.",
        "body": """<p>Technical discovery goes beyond "what are your requirements?" into "show me how your systems work." This is where SEs map the prospect's tech stack, understand data flows between systems, identify <a href="/glossary/integration-requirements/">integration</a> dependencies, and uncover technical constraints that will shape the <a href="/glossary/solution-architecture/">solution architecture</a>.</p>

<p>This conversation typically happens with technical stakeholders: engineers, architects, IT admins, or the <a href="/glossary/technical-decision-maker/">TDM</a>. It is more detailed and more technical than the initial <a href="/glossary/discovery-call/">discovery call</a>, which often includes business stakeholders who do not need (or want) to hear about API authentication methods.</p>

<h2>Why It Matters for SEs</h2>
<p>Technical discovery prevents surprises during <a href="/glossary/proof-of-concept/">POCs</a> and implementation. The SE who discovers a firewall restriction, a legacy system dependency, or a data residency requirement during technical discovery can plan around it. The SE who discovers it during the POC scrambles and looks unprepared.</p>

<p>It also builds credibility. Asking precise, informed questions about the prospect's architecture shows you understand their world. Technical stakeholders respect SEs who can speak their language and understand their constraints.</p>

<h2>How SEs Use This</h2>
<p>Come prepared with a technical discovery template specific to your product. If your product requires API integrations, have questions about their API gateway, authentication standards, and rate limit preferences. If security is a common concern, ask about their compliance frameworks, SSO provider, and data classification policies.</p>

<p>Document everything. Technical discovery notes become the blueprint for your <a href="/glossary/solution-architecture/">solution architecture</a> and POC configuration. Share the notes with your team and the prospect to confirm alignment. Misunderstandings caught in a follow-up email are infinitely cheaper than those caught during a live POC.</p>""",
        "faq": [
            ("When does technical discovery happen in the sales cycle?", "After the initial discovery call and before the custom demo or POC. Some teams combine initial and technical discovery for smaller deals, but enterprise evaluations usually split them into separate calls with different stakeholders."),
            ("What should SEs document during technical discovery?", "Current tech stack, integration requirements, authentication and SSO setup, data flows, compliance and security frameworks, performance expectations, and any known constraints or blockers. This documentation feeds directly into solution architecture."),
            ("How do you handle prospects who will not share technical details?", "Push back gently. Explain that without understanding their environment, you cannot tailor the evaluation or avoid wasting their time on irrelevant features. If they still refuse, it may signal low engagement or that you are being used as column fodder."),
        ],
        "related": ["discovery-call", "solution-architecture", "integration-requirements", "security-questionnaire", "technical-decision-maker"],
    },
    {
        "term": "Proof of Value (POV)",
        "slug": "proof-of-value",
        "definition": "An evaluation similar to a POC but focused on demonstrating measurable business value rather than just confirming technical capability.",
        "body": """<p>A POV goes beyond "does it work?" to "what is it worth?" While a <a href="/glossary/proof-of-concept/">POC</a> validates technical fit, a POV measures business outcomes: time saved, revenue generated, errors reduced, or processes accelerated. The success criteria are tied to business metrics, not feature checkboxes.</p>

<p>POVs are more work than POCs but produce stronger results. A prospect who has measured a 40% reduction in process time during a POV has a quantified reason to buy. That number shows up in the business case, the budget request, and the internal presentation to the <a href="/glossary/economic-buyer/">economic buyer</a>.</p>

<h2>Why It Matters for SEs</h2>
<p>POVs align with <a href="/glossary/value-selling/">value selling</a> methodology. They turn the evaluation from a technical exercise into a business exercise. SEs who can design and execute a POV are operating at a higher level than SEs who only run feature-focused POCs.</p>

<p>The challenge is measurement. Business value is harder to quantify than technical pass/fail. SEs need to work with the prospect to define baseline metrics before the POV starts and agree on how improvement will be measured. Without a clear baseline, the results are anecdotal rather than quantified.</p>

<h2>How SEs Use This</h2>
<p>Propose a POV when the prospect's primary concern is ROI rather than technical fit. Frame it around 2 to 3 measurable outcomes. Work with the prospect to establish baselines, then configure the product to optimize for those outcomes during the evaluation period.</p>

<p>At the end of the POV, present the results in business terms. "Your team processed 35% more requests in the same time" is more compelling than "the product met all technical requirements." Give your <a href="/glossary/champion/">champion</a> a one-page summary with the key metrics so they can sell the results internally.</p>""",
        "faq": [
            ("What is the difference between a POV and a POC?", "A POC validates technical capability: does the product work as advertised? A POV measures business value: is the product worth the investment? POVs use business metrics (time saved, revenue impact) as success criteria rather than technical feature checklists."),
            ("How long does a POV typically run?", "Two to four weeks, similar to a POC. The key difference is that POVs need enough time to generate measurable data. Very short POVs may not produce statistically meaningful results."),
            ("When should you suggest a POV instead of a POC?", "When the technical fit is not in question but the business case needs proof. POVs work best with prospects who have clear KPIs and can articulate what success means in business terms."),
        ],
        "related": ["proof-of-concept", "value-selling", "economic-buyer", "poc-success-criteria", "champion"],
    },
    {
        "term": "Solution Architecture",
        "slug": "solution-architecture",
        "definition": "The technical design that maps your product's capabilities to the prospect's specific environment, integrations, workflows, and requirements.",
        "body": """<p>Solution architecture is the blueprint. It shows how your product fits into the prospect's existing tech stack, what integrations are needed, how data flows between systems, and where customization is required. It turns abstract product capabilities into a concrete plan for this specific customer.</p>

<p>SEs build solution architectures after <a href="/glossary/technical-discovery/">technical discovery</a>. The discovery reveals the prospect's environment. The solution architecture shows how your product lives in that environment. Good solution architectures are visual (diagrams, flow charts) and specific (named systems, identified data flows, authentication paths).</p>

<h2>Why It Matters for SEs</h2>
<p>Solution architecture is one of the most valuable artifacts an SE creates. It demonstrates that you understand the prospect's technical world and have thought carefully about how your product fits. Technical stakeholders who see a thoughtful architecture diagram gain confidence that the implementation will go smoothly.</p>

<p>It also surfaces objections early. When you diagram the integration between your product and their legacy ERP system, someone in the room will say "wait, that system does not have an API." Better to learn that now than during the <a href="/glossary/proof-of-concept/">POC</a>.</p>

<h2>How SEs Use This</h2>
<p>Create a solution architecture for every enterprise deal. Even if the prospect does not ask for one, presenting it during the <a href="/glossary/custom-demo/">custom demo</a> or POC kickoff shows preparation that competitors rarely match. Use tools like Lucidchart, Miro, or Excalidraw to build clean, professional diagrams.</p>

<p>The architecture should cover: data ingestion, core processing, output/reporting, <a href="/glossary/integration-requirements/">integrations</a> with existing systems, authentication/SSO, and deployment model (cloud, on-prem, hybrid). Label everything clearly. The audience includes both technical evaluators and less-technical <a href="/glossary/buying-committee/">buying committee</a> members who need to see the big picture.</p>""",
        "faq": [
            ("Who creates the solution architecture in a deal?", "The SE creates it, typically after technical discovery. In complex deals, the SE may collaborate with a solutions architect or professional services team. The SE owns it during the sales cycle."),
            ("When should you present the solution architecture?", "During the custom demo or at the POC kickoff. Presenting it early gives the prospect confidence and surfaces integration concerns before they become blockers."),
            ("What tools do SEs use for solution architecture diagrams?", "Lucidchart, Miro, and Excalidraw are the most common. Some SEs use Visio or draw.io. The tool matters less than the clarity of the diagram. Keep it clean, labeled, and focused on the prospect's specific environment."),
        ],
        "related": ["technical-discovery", "integration-requirements", "custom-demo", "proof-of-concept", "technical-decision-maker"],
    },
    {
        "term": "Pre-Sales",
        "slug": "pre-sales",
        "definition": "The umbrella term for all sales activities that happen before contract signing, where SEs serve as the primary technical resource.",
        "body": """<p>Pre-sales covers everything from the first <a href="/glossary/discovery-call/">discovery call</a> to the moment ink hits the contract. It includes demos, <a href="/glossary/proof-of-concept/">POCs</a>, <a href="/glossary/request-for-proposal/">RFP</a> responses, <a href="/glossary/solution-architecture/">solution architecture</a>, competitive positioning, and the <a href="/glossary/technical-close/">technical close</a>. SEs are the backbone of the pre-sales function at most B2B software companies.</p>

<p>The pre-sales motion varies by deal size and complexity. A $10K self-serve deal might involve a single demo. A $500K enterprise deal might involve months of technical evaluation with multiple stakeholders across the <a href="/glossary/buying-committee/">buying committee</a>. SEs adapt their approach to the deal, not the other way around.</p>

<h2>Why It Matters for SEs</h2>
<p>Understanding where pre-sales fits in the broader sales organization helps SEs communicate their value. Pre-sales is a revenue function. Every dollar of new business passes through the SE before it closes. SEs who understand this framing negotiate better comp, justify headcount requests, and earn a seat at the strategy table.</p>

<p>Pre-sales is also the career identity. Whether your title is Solutions Engineer, Sales Engineer, <a href="/glossary/solution-consulting/">Solutions Consultant</a>, or Pre-Sales Engineer, you work in pre-sales. The function is the same even when the title changes between companies.</p>

<h2>How SEs Use This</h2>
<p>Frame your work in pre-sales terms when talking to leadership. "I run pre-sales technical evaluations for enterprise accounts" is clearer to executives than listing individual activities. Track your pre-sales metrics: <a href="/glossary/demo-to-close-rate/">demo-to-close rate</a>, technical win rate, average deal cycle, and POC success rate. These numbers tell the story of your impact.</p>

<p>Invest in the pre-sales community. Organizations like PreSales Collective, SE-specific Slack groups, and local meetups connect you with peers who face the same challenges. The best career moves in pre-sales come through referrals and relationships, not job boards.</p>""",
        "faq": [
            ("What roles are part of the pre-sales team?", "Solutions Engineers (the core), SE Managers, Solutions Architects, Demo Engineers, and Presales Operations. Some organizations also include Sales Development Reps (SDRs) in the pre-sales umbrella."),
            ("How is pre-sales different from post-sales?", "Pre-sales handles everything before the contract is signed: discovery, demos, POCs, and technical close. Post-sales handles implementation, onboarding, customer success, and renewals. The handoff between the two is a common friction point."),
            ("Is pre-sales a cost center or revenue function?", "Revenue function. SEs directly influence deal outcomes, and their technical win rate correlates with closed revenue. The strongest SE orgs report directly to a CRO or VP of Sales, not to a support or services org."),
        ],
        "related": ["sales-cycle", "technical-win", "technical-close", "solution-consulting", "presales-operations"],
    },
    {
        "term": "Sales Cycle",
        "slug": "sales-cycle",
        "definition": "The complete journey from initial prospect engagement to closed deal, with SEs involved from discovery through the technical close.",
        "body": """<p>A sales cycle is the timeline of a deal. It starts when a prospect enters the pipeline (inbound lead, outbound outreach, or event contact) and ends when the contract is signed. For enterprise B2B software, sales cycles typically run 3 to 9 months. Complex deals with large <a href="/glossary/buying-committee/">buying committees</a> and formal procurement processes can stretch to 12 months or more.</p>

<p>SEs engage at different depths throughout the cycle. Early stages involve <a href="/glossary/discovery-call/">discovery</a> and qualification. Mid-stages involve <a href="/glossary/custom-demo/">demos</a>, <a href="/glossary/proof-of-concept/">POCs</a>, and <a href="/glossary/request-for-proposal/">RFP</a> responses. Late stages involve <a href="/glossary/technical-close/">technical close</a>, executive presentations, and supporting procurement.</p>

<h2>Why It Matters for SEs</h2>
<p>Understanding where a deal sits in the sales cycle determines how you allocate your time. Early-stage deals need discovery effort. Mid-stage deals need demo prep and POC execution. Late-stage deals need objection handling and stakeholder alignment. SEs who treat every deal the same regardless of stage waste effort.</p>

<p>Sales cycle length also affects SE capacity planning. If your average cycle is 6 months, your SE team is carrying 6 months of active deals simultaneously. Shorter cycles mean higher throughput per SE. Longer cycles mean each SE can carry fewer deals before quality suffers.</p>

<h2>How SEs Use This</h2>
<p>Track where your deals are and plan your week around the highest-impact activities. A deal entering POC needs 10 to 15 hours of focused prep. A deal in early discovery needs 2 hours. Use a <a href="/glossary/mutual-action-plan/">mutual action plan</a> to keep deals moving through the cycle on schedule, and flag any deal that has been stuck in the same stage for more than two weeks.</p>

<p>Work with your AE to compress the cycle where possible. Fast discovery, tight POC timelines, and proactive objection handling all reduce cycle length. Every week you shave off the cycle is a week you can spend on the next deal.</p>""",
        "faq": [
            ("How long is a typical B2B SaaS sales cycle?", "Three to nine months for enterprise deals. SMB and mid-market deals with smaller buying committees and less formal procurement can close in four to eight weeks. Product complexity and deal size are the biggest factors."),
            ("How much of the sales cycle involves the SE?", "SEs are typically engaged from the first technical touchpoint (discovery) through the technical close. In a 6-month cycle, the SE might be actively involved for 3 to 4 months, with lighter involvement in the early qualification and late procurement stages."),
            ("How can SEs help shorten the sales cycle?", "Run thorough discovery so demos are targeted. Set tight POC timelines with clear success criteria. Address technical objections proactively instead of waiting for them to surface. Help the champion build the internal business case so procurement moves faster."),
        ],
        "related": ["discovery-call", "proof-of-concept", "technical-close", "mutual-action-plan", "buying-committee"],
    },
    {
        "term": "Buying Committee",
        "slug": "buying-committee",
        "definition": "The group of stakeholders at a prospect who collectively make the purchase decision, typically spanning technical, business, and procurement roles.",
        "body": """<p>Enterprise software purchases are rarely made by one person. The buying committee includes everyone with a voice in the decision: the <a href="/glossary/technical-decision-maker/">technical decision maker</a>, the <a href="/glossary/economic-buyer/">economic buyer</a>, end users who will work with the product daily, IT and security reviewers, and procurement. Research consistently shows enterprise buying committees average 6 to 10 people.</p>

<p>Each member of the buying committee has different concerns. The TDM cares about technical fit and integration complexity. The economic buyer cares about ROI and total cost of ownership. End users care about usability. Security cares about compliance. Procurement cares about terms and pricing. Selling to all of them requires different messages from the same product.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs interact with most of the buying committee. You present to the TDM during <a href="/glossary/technical-discovery/">technical discovery</a>. You demo to end users. You answer <a href="/glossary/security-questionnaire/">security questionnaires</a> for the security team. You may present the <a href="/glossary/solution-architecture/">solution architecture</a> to IT. Understanding who each person is and what they care about determines how you tailor each interaction.</p>

<p>The biggest risk is an unknown stakeholder who surfaces late in the process with a blocking objection. <a href="/glossary/stakeholder-mapping/">Stakeholder mapping</a> early in the deal helps SEs and AEs identify and engage every relevant person before they become a last-minute obstacle.</p>

<h2>How SEs Use This</h2>
<p>Map the buying committee with your AE after the first couple of calls. Identify each person's role, their influence level, their likely concerns, and their disposition toward your solution (supporter, neutral, or skeptic). Update the map as you learn more.</p>

<p>Build relationships with multiple committee members. If your only contact is one <a href="/glossary/champion/">champion</a> and that person leaves the company or changes roles, you lose the deal. Multi-threading across the committee protects against single points of failure and gives you a more complete picture of the decision dynamics.</p>""",
        "faq": [
            ("How many people are in a typical buying committee?", "Enterprise B2B buying committees average 6 to 10 people. Larger organizations and more complex purchases tend toward the higher end. Smaller companies may have 3 to 5 people involved."),
            ("How do you identify all buying committee members?", "Ask your champion directly. Use your discovery calls to ask who else will be involved in the evaluation and decision. Review the meeting invite lists. Ask the AE to confirm roles with their contacts. Update your map continuously throughout the deal."),
            ("What do you do when a new stakeholder appears late in the deal?", "Engage them immediately. Offer a dedicated briefing. Understand their concerns and address them directly. A new stakeholder who feels ignored or rushed is more likely to block the deal than one who feels heard."),
        ],
        "related": ["technical-decision-maker", "economic-buyer", "champion", "stakeholder-mapping", "meddpicc"],
    },
    {
        "term": "Technical Decision Maker (TDM)",
        "slug": "technical-decision-maker",
        "abbr": "TDM",
        "definition": "The person in the buying committee with authority over technical requirements and vendor selection, often a VP of Engineering, CTO, or IT Director.",
        "body": """<p>The TDM is the SE's primary audience. This is the person who decides whether your product is technically acceptable for their organization. Their approval is required for a <a href="/glossary/technical-win/">technical win</a>. Without it, the deal cannot proceed regardless of how much the end users or the <a href="/glossary/economic-buyer/">economic buyer</a> like you.</p>

<p>TDMs come in different flavors. Some are deeply technical and will challenge you on API design, database architecture, and scaling characteristics. Others are more managerial and focus on risk, vendor stability, and team impact. Your approach needs to match their style. A highly technical TDM wants to see the product in depth. A strategic TDM wants to see the business case and risk mitigation.</p>

<h2>Why It Matters for SEs</h2>
<p>Identifying the TDM early is critical. Many deals have someone who looks like the TDM but is not. The person attending your <a href="/glossary/discovery-call/">discovery calls</a> may be the evaluator, not the decision maker. SEs who build their entire strategy around the wrong person discover the real TDM only when the deal stalls.</p>

<p>Engaging the TDM requires earning technical respect. They have seen hundreds of vendor pitches and can spot hand-waving instantly. Come prepared with technical depth. Be honest about product limitations. TDMs trust SEs who say "we do not do that" more than those who claim to do everything.</p>

<h2>How SEs Use This</h2>
<p>Ask directly: "Who will make the final technical decision?" Then validate the answer by checking whether that person has the authority to approve vendors, allocate engineering resources for integration, and sign off on <a href="/glossary/security-questionnaire/">security reviews</a>. If the answer to any of those is no, keep looking.</p>

<p>Tailor your <a href="/glossary/custom-demo/">demo</a> and <a href="/glossary/solution-architecture/">architecture</a> presentations to the TDM's concerns. If they care about scalability, show load test results. If they care about security, lead with your compliance certifications. If they care about team productivity, demonstrate the developer experience. Let your <a href="/glossary/champion/">champion</a> brief you on the TDM's priorities before you present to them.</p>""",
        "faq": [
            ("How do you identify the technical decision maker?", "Ask your contacts directly who has final authority on technical vendor selection. Validate by checking whether that person can allocate engineering resources, approve security reviews, and veto vendor choices. Title alone is not enough, as org structures vary."),
            ("What is the difference between a TDM and an economic buyer?", "The TDM has authority over the technical evaluation and vendor approval. The economic buyer has budget authority. They can be the same person in smaller organizations, but in enterprise deals they are usually different people with different concerns."),
            ("What if the TDM is skeptical of your product?", "Address their specific concerns directly. Ask what would change their mind and work toward that. If they have a competing preference, understand why and position against it honestly. Never go around a skeptical TDM because they will find out and block you harder."),
        ],
        "related": ["buying-committee", "economic-buyer", "technical-win", "champion", "technical-close"],
    },
    {
        "term": "Demo Script",
        "slug": "demo-script",
        "definition": "A structured outline for a product demonstration that guides the SE through key flows, talking points, and transitions for a specific audience.",
        "body": """<p>A demo script is your flight plan. It outlines the features you will show, the order you will show them, the story connecting each section, and the talking points for each transition. Good demo scripts are not word-for-word transcripts. They are structured outlines that keep the demo focused while leaving room for the SE's natural delivery.</p>

<p>The best demo scripts are customized per prospect based on what you learned in <a href="/glossary/discovery-call/">discovery</a>. A generic "show everything" demo script bores prospects and buries the features they care about under features they do not. A targeted script that opens with their top pain point and shows exactly how your product solves it holds attention and builds conviction.</p>

<h2>Why It Matters for SEs</h2>
<p>Demo scripts prevent the two most common demo failures: going off-track and running long. Without a script, SEs tend to follow the prospect's questions down rabbit holes, lose the narrative thread, and run 15 minutes over time. Scripts keep the demo on message and on schedule.</p>

<p>Scripts also enable consistency across the SE team. When new SEs join, they can deliver a competent demo on day one by following the script. As they gain experience, they customize it. But the baseline ensures no critical feature or message is missed.</p>

<h2>How SEs Use This</h2>
<p>Build a library of demo scripts: one master script for the full product, plus modular scripts for specific use cases or personas. Before each <a href="/glossary/custom-demo/">custom demo</a>, pull the relevant modules and arrange them based on what <a href="/glossary/technical-discovery/">discovery</a> revealed about this prospect.</p>

<p>Practice transitions. The weakest moment in most demos is the gap between features. "Let me also show you..." is forgettable. "You mentioned your team spends 4 hours a week on this, so let me show you how that goes away" ties the demo to the prospect's reality. Scripts should include these transition hooks.</p>""",
        "faq": [
            ("Should demo scripts be word-for-word?", "No. Outline format with key talking points, feature sequences, and transition hooks. Word-for-word scripts sound rehearsed and make it hard to adapt when prospects ask questions. The script is a framework, not a teleprompter."),
            ("How often should demo scripts be updated?", "After every major product release and whenever win/loss analysis reveals messaging gaps. Review scripts quarterly at minimum. Stale scripts that reference old UI or missing features undermine credibility."),
            ("Who owns demo script creation?", "Typically SE leadership or presales operations create the master scripts. Individual SEs customize them per deal. The best orgs have a shared library that the team contributes to and iterates on collectively."),
        ],
        "related": ["custom-demo", "discovery-call", "demo-environment", "first-call-deck", "presales-operations"],
    },
    {
        "term": "Feature Matrix",
        "slug": "feature-matrix",
        "definition": "A comparison grid showing which features each vendor offers, used by both prospects and SEs to structure competitive evaluations.",
        "body": """<p>A feature matrix is a table with vendors across the top and features down the side. Each cell shows whether a vendor supports that feature, partially supports it, or does not have it. Prospects use feature matrices to structure their evaluation and compare vendors objectively. SEs both respond to prospect-generated matrices and build their own for competitive positioning.</p>

<p>Feature matrices can be your best friend or your worst enemy. If the matrix highlights your strengths, it works in your favor. If a competitor helped the prospect build the matrix (and stacked it with their differentiators), you are playing on their field. Recognizing a planted matrix is a critical SE skill.</p>

<h2>Why It Matters for SEs</h2>
<p>When a prospect sends you a feature matrix, they are telling you exactly what they plan to evaluate. Read it carefully. Which features are weighted? Which ones seem oddly specific (a sign that a competitor influenced the list)? The matrix is both an evaluation tool and competitive intelligence.</p>

<p>SEs who only respond to feature matrices reactively are at a disadvantage. Proactive SEs create their own matrices that frame the evaluation around their product's strengths. If your product excels at scalability and the prospect's matrix does not mention scalability, suggest adding it.</p>

<h2>How SEs Use This</h2>
<p>Maintain an updated <a href="/glossary/competitive-battlecard/">battlecard</a>-backed feature matrix for your top 3 to 5 competitors. When you receive a prospect matrix, compare it against your internal matrix to spot gaps and opportunities. Fill in your column honestly, including "partial" or "planned" where appropriate.</p>

<p>Never misrepresent capabilities in a feature matrix. Prospects verify claims during <a href="/glossary/proof-of-concept/">POCs</a>. Getting caught claiming a feature you do not have is an instant disqualification and damages your reputation with that prospect permanently. If a feature is on the roadmap, say so with a timeline. If it does not exist, say that and explain your alternative approach.</p>""",
        "faq": [
            ("How do you respond to a biased feature matrix?", "Identify features that seem oddly specific to a competitor's strengths. Request that evaluation criteria be expanded to include capabilities important to the prospect's actual use case. Suggest adding categories like scalability, support quality, or implementation speed."),
            ("Should SEs create their own feature matrices?", "Yes, proactively. Frame the comparison around your product's differentiators while including the features prospects expect. Share it early in the evaluation to influence how the prospect structures their assessment."),
            ("What do you do when your product lacks a feature on the matrix?", "Be honest. Say you do not have it and explain how customers accomplish that outcome with your product (workaround or integration). If it is on the roadmap, share the expected timeline. Never claim a capability you cannot demonstrate."),
        ],
        "related": ["competitive-battlecard", "request-for-proposal", "proof-of-concept", "technical-objection"],
    },
    {
        "term": "Competitive Battlecard",
        "slug": "competitive-battlecard",
        "definition": "An internal document that outlines how to position your product against a specific competitor, including strengths, weaknesses, and talk tracks.",
        "body": """<p>Battlecards are the SE's competitive playbook. Each card covers one competitor and includes: where you win (your advantages), where they win (their advantages), common objections and responses, positioning statements, and customer proof points. Good battlecards are 1 to 2 pages, not 20-page competitive intelligence reports that nobody reads.</p>

<p>The most useful battlecards are written by SEs who have competed against the vendor in real deals. Theoretical competitive analysis from marketing is a starting point, but SEs who have lost (and won) against a competitor know what matters in the room.</p>

<h2>Why It Matters for SEs</h2>
<p>Competitive deals are the norm, not the exception. In most enterprise evaluations, 2 to 4 vendors are on the shortlist. SEs who walk into a competitive demo without knowing the other vendor's strengths and weaknesses are unprepared. Battlecards provide that preparation in a format you can review in 10 minutes before a call.</p>

<p>Battlecards also prevent bad habits. Without them, SEs sometimes spread FUD (fear, uncertainty, doubt) about competitors based on outdated information or hearsay. Good battlecards are fact-checked and updated regularly, so your competitive claims are accurate.</p>

<h2>How SEs Use This</h2>
<p>Review the relevant battlecard before every competitive deal. Focus on the "where they win" section because that tells you what objections to expect. Prepare answers for those objections before the prospect raises them.</p>

<p>Contribute to battlecards after every deal. If you lost to a competitor, document why. If you won, document what worked. Share these notes with <a href="/glossary/presales-operations/">presales ops</a> so the battlecard stays current. The best battlecard programs include a quarterly review cycle where SEs validate and update the content based on recent deal experience.</p>

<p>Never share battlecards with prospects. They are internal documents. Use the talk tracks and positioning from the battlecard in your conversations, but the document itself stays inside the company.</p>""",
        "faq": [
            ("Who creates competitive battlecards?", "Product marketing or competitive intelligence teams create the initial version. SEs contribute real-deal insights and validate the content. The best battlecards are co-authored by marketing and experienced SEs who have competed head-to-head."),
            ("How often should battlecards be updated?", "Quarterly at minimum, or immediately after a major competitor product launch or pricing change. Stale battlecards with outdated feature claims or old pricing are worse than no battlecard because they create false confidence."),
            ("How long should a competitive battlecard be?", "One to two pages. If an SE cannot review it in 10 minutes before a call, it is too long. Focus on the top 5 differentiators, top 5 objection responses, and 2 to 3 customer proof points."),
        ],
        "related": ["feature-matrix", "technical-objection", "win-loss-analysis", "presales-operations"],
    },
    {
        "term": "SE-to-AE Ratio",
        "slug": "se-to-ae-ratio",
        "definition": "The number of Solutions Engineers per Account Executive on a sales team, typically ranging from 1:2 to 1:4, directly affecting workload, deal quality, and compensation.",
        "body": """<p>The SE-to-AE ratio determines how many deals each SE supports simultaneously. At 1:2 (one SE for every two AEs), each SE covers a manageable number of deals and can provide deep technical engagement. At 1:4, each SE is spread across more deals, requiring more efficient workflows and less customization per deal.</p>

<p>Industry averages cluster around 1:2 to 1:3 for enterprise sales. Companies selling to highly technical buyers or running complex evaluations need lower ratios. Companies with simpler products or self-serve evaluation paths can stretch to 1:4 or higher.</p>

<h2>Why It Matters for SEs</h2>
<p>The ratio directly impacts your quality of life. A 1:2 ratio means you are the dedicated technical partner for two AEs. You know their deals deeply, build strong working relationships, and have time for thorough <a href="/glossary/discovery-call/">discovery</a> and <a href="/glossary/custom-demo/">custom demos</a>. A 1:4 ratio means you are triaging, prioritizing the highest-value deals while giving lighter coverage to the rest.</p>

<p>The ratio also affects compensation models. Companies with lower ratios can tie SE comp more directly to deal outcomes because the SE's contribution is clearer. At higher ratios, comp tends to be more pooled or territory-based.</p>

<h2>How SEs Use This</h2>
<p>Ask about the ratio during interviews. It tells you more about your day-to-day experience than almost any other question. A company claiming "we value deep technical selling" but running a 1:5 ratio is asking SEs to do shallow work across too many deals.</p>

<p>If your current ratio is too high, build the case for change with data. Track your deals, time-per-deal, <a href="/glossary/technical-win/">technical win</a> rate, and <a href="/glossary/demo-to-close-rate/">demo-to-close rate</a>. Show leadership that deals with more SE engagement close at higher rates and shorter cycles. The math usually supports hiring more SEs, but only if you can prove it with your own team's numbers.</p>""",
        "faq": [
            ("What is the ideal SE-to-AE ratio?", "There is no universal answer. Enterprise sales with complex technical evaluations: 1:1 to 1:2. Mid-market with moderate complexity: 1:2 to 1:3. SMB or product-led motion: 1:3 to 1:5 or higher. The right ratio depends on deal complexity and SE involvement requirements."),
            ("How does the SE-to-AE ratio affect compensation?", "Lower ratios (more dedicated pairing) often come with deal-specific variable comp because the SE's contribution is traceable. Higher ratios tend toward team or territory-based variable comp because individual deal attribution is harder."),
            ("What happens when the ratio is too high?", "SEs cut corners. Discovery gets shallow, demos get generic, POCs lack attention, and technical win rates drop. High ratios also increase burnout because SEs are context-switching between too many deals simultaneously."),
        ],
        "related": ["overlay-se", "presales-operations", "demo-to-close-rate", "technical-win"],
    },
    {
        "term": "Technical Close",
        "slug": "technical-close",
        "definition": "The point in the sales cycle where all technical objections are resolved and the evaluation team has approved the solution for purchase.",
        "body": """<p>The technical close is the SE's version of "closing the deal." It happens when the <a href="/glossary/technical-decision-maker/">TDM</a> and the technical evaluation team confirm that your product meets their requirements. The deal then transitions to commercial negotiation, legal review, and procurement, which the AE leads.</p>

<p>A clean technical close requires no open <a href="/glossary/technical-objection/">technical objections</a>, positive <a href="/glossary/proof-of-concept/">POC</a> results (if applicable), satisfactory <a href="/glossary/security-questionnaire/">security review</a>, and confirmation that <a href="/glossary/integration-requirements/">integration requirements</a> are feasible. If any of these remain unresolved, the technical close is incomplete and the deal is at risk of stalling.</p>

<h2>Why It Matters for SEs</h2>
<p>The technical close is the clearest line between SE responsibility and AE responsibility. Before the technical close, the SE drives the deal. After it, the SE supports while the AE leads commercial discussions. SEs who do not explicitly close the technical evaluation leave ambiguity that slows the deal and blurs accountability.</p>

<p>Tracking your technical close rate is essential for performance measurement and comp discussions. If you achieve technical close on 75% of qualified opportunities but only 50% ultimately purchase, the gap is in commercial negotiation, not your technical work.</p>

<h2>How SEs Use This</h2>
<p>Drive toward the technical close explicitly. After the POC readout or final technical review, ask the TDM: "Based on what you have seen, are you comfortable recommending this solution to the broader team?" Get a definitive answer. If the answer is conditional, clarify what remains and address it immediately.</p>

<p>Document the <a href="/glossary/technical-win/">technical win</a> in writing. An email from the TDM confirming that the product meets their evaluation criteria is the gold standard. This documentation protects you if the deal stalls in procurement for months, prevents the evaluation from being reopened, and gives the AE a strong foundation for the commercial negotiation.</p>""",
        "faq": [
            ("How do you know when the technical close is complete?", "When the technical decision maker explicitly confirms that the product meets their requirements and they are recommending it for purchase. Get this in writing. If you have to guess whether the technical close happened, it has not."),
            ("What if the technical close stalls?", "Identify the specific unresolved objection. Is it a product gap, an integration concern, or a security issue? Address it directly. If the objection is valid and your product cannot resolve it, be transparent with the AE so they can decide whether to continue pursuing the deal."),
            ("Who is responsible for the technical close?", "The SE. While the AE manages the overall deal, the SE owns the technical evaluation and is responsible for resolving all technical concerns and securing the technical decision maker's approval."),
        ],
        "related": ["technical-win", "technical-objection", "technical-decision-maker", "proof-of-concept", "sales-cycle"],
    },
    {
        "term": "Overlay SE",
        "slug": "overlay-se",
        "definition": "A specialist SE who supports multiple AEs across a region or product line rather than being paired with a specific AE.",
        "body": """<p>Overlay SEs are the specialists. Instead of being dedicated to one or two AEs, they cover a broader territory and engage when a deal requires their specific expertise. Common overlay specializations include industry verticals (healthcare, financial services), product areas (security, data platform), or deal stages (POC management, RFP response).</p>

<p>The overlay model exists because not every deal needs every type of expertise. Pairing a security-specialist SE with an AE who sells to marketing teams wastes that specialization. The overlay model lets companies deploy deep expertise where it is needed without hiring specialists for every AE pair.</p>

<h2>Why It Matters for SEs</h2>
<p>Overlay roles offer depth over breadth. If you enjoy going deep on a specific technology area or industry, overlay positions let you focus. You become the go-to expert, which builds your reputation internally and externally. The tradeoff is less deal ownership. Overlay SEs influence outcomes but often share credit with the primary SE.</p>

<p>Comp models for overlay SEs differ from dedicated SEs. Since overlays touch more deals at a lighter level, they are often compensated on aggregate metrics (total revenue supported, technical win rate across deals) rather than individual deal attribution. This can be better or worse depending on team performance.</p>

<h2>How SEs Use This</h2>
<p>If you are an overlay SE, build a reputation for responsiveness and quality. Primary SEs and AEs choose whether to bring you in. If you are slow to respond, produce generic deliverables, or require too much context before contributing, teams will stop requesting you.</p>

<p>If you work with overlay SEs, bring them in early enough to be effective. An overlay SE looped in 48 hours before a <a href="/glossary/security-questionnaire/">security review</a> deadline cannot do their best work. Plan overlay involvement into your <a href="/glossary/mutual-action-plan/">mutual action plan</a> from the start of the deal.</p>""",
        "faq": [
            ("What is the difference between an overlay SE and a dedicated SE?", "A dedicated SE is paired with one or two AEs and works all their deals. An overlay SE supports multiple AEs across a region or product line, engaging only when their specialization is needed. Overlays go deeper on a specific area but cover more deals more lightly."),
            ("Is overlay SE a more senior role?", "Usually yes. Overlay roles require deep specialization in an industry or product area. Most overlay SEs have several years of dedicated SE experience before transitioning. Overlay roles can also be a step toward SE management or solutions architecture."),
            ("How are overlay SEs compensated?", "Typically on aggregate metrics like total supported revenue or territory-wide technical win rate, rather than individual deal attribution. Some companies use a pool model where overlay SEs share a variable comp pool based on team results."),
        ],
        "related": ["se-to-ae-ratio", "presales-operations", "solution-consulting", "technical-win"],
    },
    {
        "term": "POC Success Criteria",
        "slug": "poc-success-criteria",
        "definition": "The specific, measurable outcomes that a prospect and vendor agree a POC must demonstrate before it is considered successful.",
        "body": """<p>POC success criteria are the scorecard. Before the evaluation starts, both sides agree on exactly what the product must demonstrate and how success will be measured. Without defined criteria, a POC devolves into open-ended exploration where the prospect can always find one more thing to test, and the evaluation never reaches a conclusion.</p>

<p>Good success criteria are specific and measurable. "The product must be fast" is not a criterion. "The product must process 10,000 records in under 5 minutes" is. Each criterion should have a clear pass/fail threshold that both sides accept before the POC begins.</p>

<h2>Why It Matters for SEs</h2>
<p>Success criteria protect the SE's time and the company's resources. A <a href="/glossary/proof-of-concept/">POC</a> without criteria is an open commitment with no defined endpoint. SEs who start POCs without agreed criteria often find themselves running extra weeks of testing, adding new requirements mid-evaluation, and struggling to reach a <a href="/glossary/technical-win/">technical win</a> because the goalpost keeps moving.</p>

<p>Defined criteria also create accountability for the prospect. If the product meets every criterion and the prospect still will not commit, something else is going on (budget, competing priorities, or a competitor they prefer). That clarity helps you and the AE decide whether to keep investing or move on.</p>

<h2>How SEs Use This</h2>
<p>Draft the success criteria collaboratively with the <a href="/glossary/technical-decision-maker/">TDM</a>. Start with their top 3 to 5 requirements from <a href="/glossary/technical-discovery/">technical discovery</a> and translate each into a measurable criterion. Get sign-off (email or document) before provisioning the POC environment.</p>

<p>During the POC, track progress against each criterion. Provide weekly updates showing which criteria have been met, which are in progress, and which are at risk. At the POC readout, walk through every criterion with a clear pass/fail result. If all criteria pass, ask for the technical win on the spot. Do not let the conversation drift to "we need to think about it."</p>""",
        "faq": [
            ("How many success criteria should a POC have?", "Three to seven is the sweet spot. Fewer than three suggests the evaluation is not rigorous enough. More than seven creates too many variables and makes the POC harder to manage. Focus on the requirements that influence the buying decision."),
            ("What happens if a POC fails a success criterion?", "It depends on which one and why. A minor criterion failing may not block the deal if you can demonstrate a workaround or timeline for resolution. A core criterion failing usually means the deal is lost or the POC needs to be extended to address the gap."),
            ("Should success criteria be weighted?", "Yes. Not all criteria are equally important. Work with the TDM to assign priority levels (must-have vs. nice-to-have). A POC that passes all must-have criteria and most nice-to-haves is a technical win even if one low-priority item falls short."),
        ],
        "related": ["proof-of-concept", "technical-win", "technical-decision-maker", "proof-of-value", "mutual-action-plan"],
    },
    {
        "term": "Deal Desk",
        "slug": "deal-desk",
        "definition": "The internal function that handles non-standard pricing, discounting, contract terms, and configuration approvals that fall outside standard guidelines.",
        "body": """<p>Deal desk sits between the sales team and finance/legal. When a deal requires custom pricing, non-standard contract terms, multi-year commitments, or bundled configurations, the AE submits a request to deal desk for approval. Deal desk evaluates the request against company guidelines and approves, modifies, or rejects it.</p>

<p>For straightforward deals with standard pricing, deal desk is invisible. For complex enterprise deals with custom terms, deal desk involvement can add days or weeks to the <a href="/glossary/sales-cycle/">sales cycle</a>. Fast deal desk turnaround is a competitive advantage. Slow deal desk is a deal killer.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs interact with deal desk when deals involve complex product configurations. If a prospect needs a custom implementation, a non-standard integration, or a unique deployment model, the SE provides the technical context that deal desk needs to price the deal accurately. Without SE input, deal desk may overprice the implementation (losing the deal) or underprice it (creating a professional services nightmare).</p>

<p>SEs also get involved when prospects request technical concessions in the contract, such as uptime SLAs, performance guarantees, or specific integration commitments. The SE validates whether those commitments are realistic before the company agrees to them.</p>

<h2>How SEs Use This</h2>
<p>Build a working relationship with your deal desk team. Understand their approval thresholds and turnaround times. When you know a deal will need non-standard terms, flag it early so deal desk can start processing in parallel with the <a href="/glossary/proof-of-concept/">technical evaluation</a> rather than sequentially after it.</p>

<p>Provide clear, concise technical summaries for deal desk requests. "The customer needs X integration which requires Y engineering hours and Z infrastructure" is actionable. "Complex deal, needs custom pricing" is not. The better your technical documentation, the faster deal desk can respond.</p>""",
        "faq": [
            ("When does an SE need to involve deal desk?", "When the deal requires non-standard pricing, custom implementation scope, special contract terms (SLAs, performance guarantees), multi-product bundles, or significant discounting beyond the AE's approval authority."),
            ("How does deal desk affect the sales cycle?", "Deal desk adds review time, typically 2 to 5 business days for standard requests and longer for complex ones. Fast deal desk processes are a competitive advantage. SEs can help by submitting clear, complete technical documentation that reduces back-and-forth."),
            ("Is deal desk the same as sales operations?", "No. Sales ops handles pipeline management, forecasting, territory planning, and process optimization. Deal desk specifically handles non-standard deal approvals, pricing, and contract terms. They often sit within or alongside the sales ops function."),
        ],
        "related": ["sales-cycle", "mutual-action-plan", "economic-buyer", "integration-requirements"],
    },
    {
        "term": "White Space Analysis",
        "slug": "white-space-analysis",
        "definition": "The process of identifying unmet needs or expansion opportunities within an existing customer account, used by both SEs and customer success teams.",
        "body": """<p>White space analysis maps what a customer currently uses against what they could use. The "white space" is the gap between their current product adoption and the full potential of your platform. For SEs, this is relevant in two contexts: during the initial sale (identifying all the problems you can solve) and during expansion plays on existing accounts.</p>

<p>The analysis typically involves mapping the customer's departments, use cases, and workflows against your product's capabilities. A customer using your product in one department has white space in every other department that could benefit. A customer using three of your ten features has white space in the seven unused features.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs who identify white space during the initial sale can expand deal size before the first contract is signed. If <a href="/glossary/discovery-call/">discovery</a> reveals that three departments have the same problem, the SE can architect a solution that covers all three, tripling the deal value. This requires asking broader questions during discovery rather than focusing narrowly on the requesting department.</p>

<p>For existing accounts, SEs support expansion deals by providing the technical credibility needed to sell into new departments or use cases. The customer already trusts the product. The SE's job is to show how it applies to the new context and handle any new <a href="/glossary/technical-objection/">technical objections</a> or <a href="/glossary/integration-requirements/">integration needs</a>.</p>

<h2>How SEs Use This</h2>
<p>During initial discovery, ask about adjacent teams and workflows. "Is this challenge unique to your team, or do other departments face it too?" and "What other tools are you evaluating or planning to replace in the next 12 months?" These questions open white space conversations naturally.</p>

<p>For expansion, partner with the CSM or account manager to review product usage data. Low adoption of certain features may indicate a training gap (fixable) or a poor fit (not worth pursuing). Focus expansion efforts on use cases where the product already demonstrates value, because those are the easiest internal sells.</p>""",
        "faq": [
            ("When should white space analysis happen?", "During the initial discovery to maximize first-deal value, and continuously for existing accounts. Many companies run formal white space reviews quarterly for their top accounts."),
            ("Who owns white space analysis?", "For new deals, the AE and SE collaborate. For existing accounts, the CSM or account manager leads with SE support for technical expansion opportunities. In some orgs, a dedicated expansion team handles this."),
            ("How do you prioritize white space opportunities?", "Rank by revenue potential, implementation complexity, and likelihood of success. The best expansion targets are use cases where the customer already has a pain point and your product has proven capabilities. Avoid pushing into areas where the product is weak."),
        ],
        "related": ["discovery-call", "stakeholder-mapping", "value-selling", "technical-discovery"],
    },
    {
        "term": "Mutual Action Plan (MAP)",
        "slug": "mutual-action-plan",
        "abbr": "MAP",
        "definition": "A shared document between vendor and prospect that outlines the steps, owners, and timeline required to reach a purchase decision.",
        "body": """<p>A mutual action plan is a project plan for the deal. It lists every step from the current stage to contract signature: technical evaluation, security review, executive briefing, procurement, legal review, and final approval. Each step has an owner (vendor side or prospect side) and a target date. Both parties agree to the plan and track progress together.</p>

<p>MAPs work because they create shared accountability. When the prospect agrees to a timeline that includes "TDM provides technical approval by March 15" and "Procurement sends contract for review by March 22," there is a clear commitment on both sides. Without a MAP, deals drift because nobody owns the next step.</p>

<h2>Why It Matters for SEs</h2>
<p>MAPs give SEs predictability. Instead of wondering when the <a href="/glossary/proof-of-concept/">POC</a> will wrap up or when the <a href="/glossary/security-questionnaire/">security review</a> will start, the MAP shows the timeline. This helps SEs plan their workload across deals and avoid the crunch of multiple POC deadlines hitting simultaneously.</p>

<p>MAPs also reveal deal health. If the prospect is not willing to commit to dates and owners for next steps, the deal may not be as far along as the AE thinks. A prospect who agrees to a detailed MAP is demonstrating genuine buying intent.</p>

<h2>How SEs Use This</h2>
<p>Propose the MAP after the initial <a href="/glossary/discovery-call/">discovery call</a> or <a href="/glossary/technical-discovery/">technical discovery</a>. Frame it as a joint project plan. "To make sure we are efficient with everyone's time, can we map out the evaluation process together?" Include every step where SE involvement is needed: demo, technical deep-dive, POC setup, POC review, <a href="/glossary/technical-close/">technical close</a>, and executive presentation.</p>

<p>Update the MAP weekly and share it with the prospect. Flag any steps that are behind schedule. The MAP is your tool for keeping the deal on track without nagging. Instead of "when will you get back to us on the security review?" you say "our MAP shows the security review completing this week. Are we still on track?"</p>""",
        "faq": [
            ("When should you introduce a mutual action plan?", "After the first or second meeting, once the prospect has shown genuine interest and the evaluation process is taking shape. Introducing it too early (before they are engaged) feels pushy. Introducing it too late (mid-POC) means you have already lost scheduling control."),
            ("What if the prospect will not commit to a MAP?", "That is a qualification signal. Prospects who are serious about buying are willing to plan the process. If they refuse to commit to dates or assign owners, the deal may lack urgency, budget, or internal support. Discuss this signal with the AE."),
            ("What tools are used for mutual action plans?", "Dedicated tools like Accord and Recapped exist for this purpose. Many SEs use shared Google Docs or spreadsheets. The tool matters less than the habit of creating the plan, sharing it, and tracking it weekly."),
        ],
        "related": ["sales-cycle", "proof-of-concept", "technical-close", "discovery-call", "buying-committee"],
    },
    {
        "term": "Economic Buyer",
        "slug": "economic-buyer",
        "definition": "The person with budget authority for the purchase who can approve or reject the spending, regardless of the technical evaluation outcome.",
        "body": """<p>The economic buyer controls the money. They might be a VP, a C-level executive, or a department head with discretionary budget. Their primary concern is ROI: what does the product cost, what does it save or generate, and does it justify the investment? They may or may not be involved in the technical evaluation, but their approval is required to close the deal.</p>

<p>In some organizations, the economic buyer and the <a href="/glossary/technical-decision-maker/">TDM</a> are the same person. In larger enterprises, they are different people with different priorities. A CTO who is the TDM might love your product technically while the CFO (economic buyer) blocks the purchase because the budget is allocated elsewhere.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs rarely sell directly to the economic buyer, but they heavily influence the materials the economic buyer sees. The <a href="/glossary/value-selling/">value</a> calculation, the ROI analysis, the business case document: these often contain technical data that only the SE can provide. An SE who can quantify business impact gives the AE and <a href="/glossary/champion/">champion</a> the ammunition they need for the budget conversation.</p>

<p>Understanding the economic buyer's priorities also shapes how the SE frames the <a href="/glossary/custom-demo/">demo</a>. If the economic buyer will attend, the SE should lead with business outcomes, not technical architecture. Executive demos that start with API documentation instead of revenue impact lose the room in 30 seconds.</p>

<h2>How SEs Use This</h2>
<p>Ask your champion and AE: "Who signs the check?" Then learn what that person cares about. Build a one-page executive summary that connects your product to their business priorities. Frame everything in terms of outcomes: revenue gained, costs reduced, risk mitigated, time recovered.</p>

<p>If you get a meeting with the economic buyer (which is not guaranteed), prepare differently than you would for a technical audience. Keep it high-level, focus on business value, and be ready to answer "why this, why now, why this much?" The economic buyer does not care about your API design. They care about what it is worth.</p>""",
        "faq": [
            ("How do you identify the economic buyer?", "Ask your contacts directly: who approves the budget for this purchase? Validate by checking whether that person has authorized similar purchases before. In large enterprises, economic buyers are often one or two levels above the day-to-day evaluation team."),
            ("Should the SE meet with the economic buyer?", "If possible, yes, but the AE typically leads that meeting. The SE supports with value quantification, business case materials, and answers to technical questions the economic buyer may have about risk or implementation."),
            ("What if the economic buyer is not engaged?", "This is a red flag in MEDDPICC. Without economic buyer engagement, the deal can stall after the technical win because nobody with budget authority has bought in. Work with the AE and champion to create an opportunity for the economic buyer to engage."),
        ],
        "related": ["buying-committee", "technical-decision-maker", "value-selling", "champion", "meddpicc"],
    },
    {
        "term": "MEDDPICC",
        "slug": "meddpicc",
        "definition": "A deal qualification methodology standing for Metrics, Economic Buyer, Decision Criteria, Decision Process, Paper Process, Identify Pain, Champion, and Competition.",
        "body": """<p>MEDDPICC is a framework for evaluating whether a deal is real and winnable. Each letter represents a qualification criterion. Metrics: can you quantify the business impact? <a href="/glossary/economic-buyer/">Economic Buyer</a>: have you identified and engaged the budget holder? Decision Criteria: do you know how they will evaluate vendors? Decision Process: do you understand the steps to get from evaluation to signed contract?</p>

<p>Paper Process covers procurement and legal workflows. Identify Pain ensures you have found a genuine business problem (not just interest). <a href="/glossary/champion/">Champion</a> confirms you have an internal advocate. Competition asks who else is in the running and how you compare. A deal with gaps in multiple MEDDPICC elements is at high risk of stalling or losing.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs contribute to most MEDDPICC criteria. <a href="/glossary/discovery-call/">Discovery</a> uncovers the pain and decision criteria. <a href="/glossary/value-selling/">Value selling</a> provides the metrics. Technical evaluation builds the champion relationship. Security and integration work reveals the paper process. SEs who understand MEDDPICC can proactively fill gaps in the deal qualification rather than just responding to AE requests.</p>

<p>MEDDPICC also helps SEs prioritize their time. A deal with no identified economic buyer, no champion, and unknown competition is a long shot. An SE who spends 30 hours prepping a POC for that deal is making a bad investment. MEDDPICC gives SEs the vocabulary to push back on AEs who are overly optimistic about unqualified deals.</p>

<h2>How SEs Use This</h2>
<p>Use MEDDPICC as a deal review framework with your AE. Before investing significant SE time (custom demo, POC), review each criterion. Where are the gaps? What do you need to learn? A quick MEDDPICC check takes 15 minutes and can save you 40 hours on a dead deal.</p>

<p>In deal reviews with SE leadership, frame your assessment using MEDDPICC language. "We have strong champion and clear decision criteria, but we have not engaged the economic buyer and the paper process is unknown" is a precise, actionable assessment that leadership can act on.</p>""",
        "faq": [
            ("What is the difference between MEDDIC and MEDDPICC?", "MEDDIC is the original framework with six criteria. MEDDPICC adds Paper Process (procurement/legal workflow) and Competition. The extra two criteria reflect the realities of modern enterprise sales where procurement and competitive dynamics significantly affect outcomes."),
            ("Do all SE teams use MEDDPICC?", "No. MEDDPICC is most common in enterprise sales orgs. Other popular frameworks include BANT (Budget, Authority, Need, Timeline), SPICED, and MEDDIC. The specific framework matters less than having a systematic way to qualify deals."),
            ("How does MEDDPICC affect SE compensation?", "MEDDPICC itself does not directly affect comp, but it influences which deals get resources. In orgs that use MEDDPICC rigorously, SEs spend more time on qualified deals and less on long shots, which tends to improve win rates and therefore variable comp payouts."),
        ],
        "related": ["champion", "economic-buyer", "discovery-call", "technical-decision-maker", "value-selling"],
    },
    {
        "term": "Solution Consulting",
        "slug": "solution-consulting",
        "definition": "An alternative title for the SE function, commonly used at Salesforce and other large enterprise software vendors.",
        "body": """<p>Solution Consulting is the same role as Solutions Engineering, just with a different name. Solution Consultants (SCs) run demos, manage POCs, respond to RFPs, and serve as the technical bridge between the sales team and the customer's technical requirements. Salesforce is the most prominent company using this title, and many Salesforce alumni carry it to other organizations.</p>

<p>The title difference occasionally signals a style difference. "Solution Consultant" tends to emphasize the advisory and consultative aspects of the role: understanding the customer's business, designing solutions, and presenting recommendations. "Solutions Engineer" tends to emphasize the technical depth: integrations, architecture, and product expertise. In practice, both titles do the same work.</p>

<h2>Why It Matters for SEs</h2>
<p>Title awareness matters for job searches and career navigation. If you search only for "Solutions Engineer" openings, you miss every company that calls the same role "Solution Consultant," "Pre-Sales Consultant," "Technical Consultant," or "Sales Engineer." The function is identical. The title varies by company culture.</p>

<p>The title can also affect how internal teams perceive you. "Consultant" carries connotations of advisory and strategy. "Engineer" carries connotations of technical depth. Neither is wrong. Knowing how your title is perceived helps you frame your contributions in language that lands with leadership.</p>

<h2>How SEs Use This</h2>
<p>When job searching, search for all common title variants: Solutions Engineer, Solution Consultant, Sales Engineer, Pre-Sales Engineer, Pre-Sales Consultant, Technical Consultant, and <a href="/glossary/pre-sales/">Pre-Sales</a> Specialist. Set up alerts for all of them. The company you want may use a title you are not searching for.</p>

<p>On your resume and LinkedIn, include the most common variant (Solutions Engineer) as a secondary title or in your summary, even if your official title is different. This ensures recruiters searching for either term find your profile. The <a href="/glossary/pre-sales/">pre-sales</a> community is small enough that everyone understands the title equivalence.</p>""",
        "faq": [
            ("Is Solution Consultant the same as Solutions Engineer?", "Yes. The job function is identical: pre-sales technical selling including demos, POCs, RFPs, and technical close. Salesforce and several enterprise vendors prefer 'Solution Consultant.' Most other companies use 'Solutions Engineer' or 'Sales Engineer.'"),
            ("Does the title affect compensation?", "Not directly. Compensation is driven by the company, the market, and the deal complexity, not the title. A Solution Consultant at Salesforce and a Solutions Engineer at a similar-sized company earn comparable compensation for comparable work."),
            ("Which title should I use on LinkedIn?", "Use whatever your company calls the role, but include 'Solutions Engineer' in your headline or summary since it is the most widely searched variant. This ensures both recruiters and peers can find your profile."),
        ],
        "related": ["pre-sales", "overlay-se", "presales-operations", "se-to-ae-ratio"],
    },
    {
        "term": "Demo-to-Close Rate",
        "slug": "demo-to-close-rate",
        "definition": "The percentage of qualified demos that result in a closed-won deal, serving as a key metric for measuring SE and sales team effectiveness.",
        "body": """<p>Demo-to-close rate answers a fundamental question: when we show the product, how often does it lead to a sale? If an SE delivers 40 qualified demos in a quarter and 12 result in closed deals, the demo-to-close rate is 30%. This metric captures the combined effectiveness of the SE's demo skills, the AE's closing ability, and the overall deal qualification process.</p>

<p>Benchmarks vary by market segment and deal complexity. Enterprise deals with long sales cycles and competitive evaluations typically see 20-30% demo-to-close rates. Mid-market and SMB deals with shorter cycles can run 30-50%. Anything below 15% suggests a qualification problem: too many unqualified prospects are getting demos.</p>

<h2>Why It Matters for SEs</h2>
<p>Demo-to-close rate is one of the few metrics that quantifies SE impact on revenue. A high rate means the SE is delivering compelling, well-targeted demos to qualified prospects. A low rate could mean several things: weak demos, poor qualification, strong competition, or pricing misalignment. The metric alone does not diagnose the problem, but it signals that one exists.</p>

<p>Tracking this metric over time also shows improvement. An SE whose demo-to-close rate increases from 20% to 35% over a year has demonstrably improved their craft. That data point is valuable in performance reviews and comp negotiations.</p>

<h2>How SEs Use This</h2>
<p>Track your personal demo-to-close rate in addition to the team average. If your rate is significantly below the team average, examine your demos: are they customized enough? Is your <a href="/glossary/discovery-call/">discovery</a> surfacing the right pain points? Are you demoing to the right stakeholders? If your rate is above the team average, share what is working.</p>

<p>Segment the metric. Your demo-to-close rate for <a href="/glossary/custom-demo/">custom demos</a> should be higher than for generic demos. Your rate for deals where you ran a <a href="/glossary/proof-of-concept/">POC</a> should be higher than demos-only. These segments show where your process is strongest and where it needs work.</p>""",
        "faq": [
            ("What is a good demo-to-close rate?", "Enterprise: 20-30%. Mid-market: 30-40%. SMB: 35-50%. These benchmarks vary by product complexity, competitive dynamics, and deal size. Compare your rate against your team average rather than generic benchmarks."),
            ("How do you improve demo-to-close rate?", "Better qualification (demo only to serious buyers), stronger discovery (customize every demo), tighter follow-up (never let momentum die after a demo), and continuous improvement based on win/loss analysis."),
            ("Is demo-to-close rate an SE metric or a sales metric?", "Both. The SE controls demo quality and technical conviction. The AE controls qualification, pricing, and commercial close. The rate reflects the combined performance. SEs should track their own rate but recognize that factors outside their control affect it."),
        ],
        "related": ["custom-demo", "technical-win", "se-to-ae-ratio", "win-loss-analysis", "discovery-call"],
    },
    {
        "term": "Sandbox Provisioning",
        "slug": "sandbox-provisioning",
        "definition": "The process of creating and configuring demo or POC environments for prospects and SEs, ranging from fully automated to entirely manual.",
        "body": """<p>Sandbox provisioning is the plumbing behind every <a href="/glossary/demo-environment/">demo environment</a> and <a href="/glossary/proof-of-concept/">POC</a>. It covers everything from spinning up the infrastructure to loading sample data, configuring integrations, and setting access credentials. How fast and reliable this process is directly affects how quickly SEs can start evaluations.</p>

<p>Provisioning ranges from fully automated (click a button, get an environment in minutes) to entirely manual (file a ticket, wait 3 days for DevOps to set it up). The maturity of your provisioning process is a competitive factor. Vendors who can start a POC same-day have an advantage over those who need a week to set up the environment.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs lose time and deals to slow provisioning. If a prospect is excited after a great <a href="/glossary/custom-demo/">demo</a> and ready to start a POC, a 5-day wait for the environment kills momentum. Competitors who provision faster capture that energy. SEs at companies with slow provisioning learn to start the provisioning process before the prospect even asks, just to have environments ready.</p>

<p>Provisioning quality matters too. An environment that is missing features, loaded with broken data, or configured incorrectly requires SE debugging time that should go toward deal work. <a href="/glossary/presales-operations/">Presales ops</a> teams that invest in provisioning reliability free SEs to focus on customers.</p>

<h2>How SEs Use This</h2>
<p>If provisioning is automated at your company, learn the system well enough to troubleshoot common issues. If it is manual, build a relationship with the team that handles it and give them advance notice when a POC is coming. In either case, always verify the environment before handing it to a prospect. Nothing undermines credibility faster than a broken sandbox on day one.</p>

<p>Advocate for provisioning improvements internally. Track the time from "POC approved" to "environment ready" and present that data to engineering or IT leadership. If the average is 4 days and competitors do it in hours, that is a measurable competitive disadvantage worth fixing.</p>""",
        "faq": [
            ("How long should sandbox provisioning take?", "Ideally under an hour for standard configurations. Many mature products offer same-day provisioning. If your provisioning takes more than 2 business days, it is a competitive disadvantage worth escalating to engineering leadership."),
            ("Who is responsible for sandbox provisioning?", "It varies. In some companies, SEs self-serve through an internal tool. In others, DevOps or IT handles it via ticket. Mature orgs have presales operations or a demo engineering team dedicated to provisioning and maintaining demo infrastructure."),
            ("Should sandbox provisioning be automated?", "Yes, to the extent possible. Automated provisioning reduces wait times, eliminates configuration errors, and lets SEs focus on customers instead of infrastructure. Even partial automation (templated configurations, pre-loaded data sets) provides significant improvement over fully manual processes."),
        ],
        "related": ["sandbox", "demo-environment", "proof-of-concept", "presales-operations", "custom-demo"],
    },
    {
        "term": "Technical Objection",
        "slug": "technical-objection",
        "definition": "A concern raised by a prospect about product capabilities, integrations, security, scalability, or compliance during the sales process that the SE must address.",
        "body": """<p>Technical objections are the reasons prospects hesitate. "Does it integrate with our legacy system?" "Can it handle our data volume?" "Is it SOC 2 certified?" "What happens if the API goes down?" Each objection is a question that, if unanswered, blocks the deal. SEs exist to answer these questions credibly and completely.</p>

<p>Objections are not the same as rejections. A prospect raising technical concerns is engaged and evaluating seriously. A prospect who says nothing and goes dark is the one you should worry about. Objections are opportunities to demonstrate depth and build trust.</p>

<h2>Why It Matters for SEs</h2>
<p>Every unresolved technical objection is a risk to the <a href="/glossary/technical-win/">technical win</a>. SEs who dismiss or deflect objections lose credibility. SEs who address them directly, with evidence, build the trust that leads to technical close. The best SEs welcome objections because each one they resolve removes a barrier to the sale.</p>

<p>Objections also provide product intelligence. If every prospect in a vertical raises the same integration concern, that is a signal for the product team. SEs who track and aggregate objections become a valuable feedback channel between the market and engineering.</p>

<h2>How SEs Use This</h2>
<p>Maintain a personal library of the 10 most common objections and your best responses. Prepare these before every <a href="/glossary/custom-demo/">demo</a> and <a href="/glossary/proof-of-concept/">POC</a>. When an objection comes up, you should not be hearing it for the first time. You should have a practiced, evidence-backed response ready.</p>

<p>For objections you cannot immediately answer, acknowledge them and commit to a response timeline. "That is a great question. Let me get you a detailed answer by tomorrow" is infinitely better than guessing or deflecting. Follow through on that commitment. SEs who consistently deliver on follow-up answers build a reputation for reliability that carries the deal forward.</p>""",
        "faq": [
            ("What are the most common technical objections?", "Integration with existing systems, security and compliance certifications, scalability under load, data migration complexity, and vendor lock-in risk. The specific objections vary by product category, but these five appear in most enterprise evaluations."),
            ("How should an SE handle an objection they cannot answer?", "Acknowledge the concern, commit to a specific response timeline, involve the right internal expert (product, engineering, security), and deliver the answer on time. Never guess or bluff. Getting caught with an inaccurate answer is worse than admitting you need to check."),
            ("Are technical objections a bad sign for the deal?", "No. Objections indicate engagement. A prospect who asks hard technical questions is evaluating seriously. A prospect who asks nothing may not be invested in the evaluation. Objections are opportunities to demonstrate expertise and build trust."),
        ],
        "related": ["technical-win", "technical-close", "security-questionnaire", "integration-requirements", "feature-matrix"],
    },
    {
        "term": "Reference Call",
        "slug": "reference-call",
        "definition": "A call arranged between a prospect and an existing customer to validate the vendor's claims, where SEs typically prep the reference customer beforehand.",
        "body": """<p>Reference calls are the trust verification step. The prospect talks directly to someone who already uses your product. They ask about implementation experience, product strengths and weaknesses, support quality, and whether the vendor delivered on their promises. A strong reference call can close a deal. A weak one can kill it.</p>

<p>Most enterprise deals include at least one reference call, usually late in the <a href="/glossary/sales-cycle/">sales cycle</a> after the <a href="/glossary/proof-of-concept/">POC</a> or <a href="/glossary/custom-demo/">demo</a> phase. The prospect wants to hear from a peer, not from sales. The reference customer's credibility is more persuasive than any <a href="/glossary/competitive-battlecard/">battlecard</a> or feature comparison.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs are often the ones who built the relationship with the reference customer during implementation or ongoing engagement. You know which customers had great experiences and which had rocky ones. You also know which customers are most relevant to the current prospect's industry, use case, and technical environment.</p>

<p>Matching the right reference to the right prospect is an underrated SE skill. A healthcare prospect talking to a healthcare customer is powerful. That same prospect talking to a customer in a completely different industry is less convincing. SEs who maintain a mental (or documented) map of their best references by industry and use case can deploy the right reference at the right time.</p>

<h2>How SEs Use This</h2>
<p>Prep the reference customer before the call. Brief them on the prospect, what the prospect cares about, and which aspects of their experience would be most relevant to highlight. Reference customers want to help (they would not have agreed to the call otherwise), but they do their best job when they know what questions to expect.</p>

<p>After the reference call, follow up with the prospect to ask what they heard and whether any concerns remain. Reference calls sometimes surface new questions that the SE needs to address. Closing the loop shows attentiveness and prevents the reference call from creating unresolved doubts instead of eliminating them.</p>""",
        "faq": [
            ("When should a reference call happen in the sales cycle?", "Typically after the demo or POC phase and before the final purchase decision. Placing it too early wastes the reference customer's time on a deal that may not be serious. Placing it too late delays the close."),
            ("How many reference calls should a deal include?", "One to two is standard. More than two suggests the prospect has concerns that a reference call alone will not resolve. If a prospect asks for five references, dig into what specific concern they are trying to validate."),
            ("What makes a bad reference call?", "An unprepared reference customer, a mismatch between the reference's industry/use case and the prospect's needs, or a reference who had a negative experience that was not fully resolved. SEs should vet references before offering them."),
        ],
        "related": ["proof-of-concept", "technical-win", "champion", "win-loss-analysis", "sales-cycle"],
    },
    {
        "term": "Security Questionnaire",
        "slug": "security-questionnaire",
        "definition": "A formal document where prospects ask vendors about security practices, certifications, data handling, and compliance, typically completed by SEs or security teams.",
        "body": """<p>Security questionnaires are the compliance checkpoint in enterprise sales. The prospect's security or IT team sends a document (sometimes hundreds of questions) covering encryption, access controls, data residency, incident response, SOC 2 compliance, GDPR, HIPAA, and more. Your answers determine whether the security team will approve the vendor for use.</p>

<p>Questionnaires come in many formats: SIG (Standardized Information Gathering), CAIQ (Consensus Assessment Initiative Questionnaire), custom spreadsheets, or third-party platforms like OneTrust or Whistic. The format varies, but the substance is similar: prove that your product will not create security or compliance risk for the prospect.</p>

<h2>Why It Matters for SEs</h2>
<p>Security questionnaires can block or delay deals for weeks. A prospect's security team that does not approve the vendor stops the deal regardless of how strong the <a href="/glossary/technical-win/">technical win</a> is. SEs who can complete questionnaires quickly and accurately remove this bottleneck.</p>

<p>In many SE orgs, security questionnaire completion is a shared responsibility. The SE handles product-specific questions (how does the product handle authentication, what APIs are exposed) while a security or compliance team handles company-level questions (SOC 2 report availability, insurance coverage). Knowing which questions are yours and routing the rest quickly keeps the process moving.</p>

<h2>How SEs Use This</h2>
<p>Build a security response library. Most questions repeat across questionnaires with minor wording variations. A well-maintained library with pre-approved answers can cut completion time from days to hours. Update the library every time your product ships a security-relevant change.</p>

<p>Start the questionnaire process early. Do not wait until the prospect asks. If you know the prospect has a security team (and every enterprise does), proactively offer your SOC 2 report, security whitepaper, or pre-filled SIG during <a href="/glossary/technical-discovery/">technical discovery</a>. This signals confidence and often shortens the review cycle.</p>""",
        "faq": [
            ("How long does a security questionnaire take to complete?", "With a response library: 2 to 8 hours depending on length and complexity. Without one: 2 to 5 days. Investing in a maintained response library is one of the highest-ROI activities for presales operations."),
            ("Who is responsible for security questionnaires?", "Typically shared between the SE (product-specific questions) and the security or compliance team (company-level questions). In smaller companies without a dedicated security team, the SE may own the entire questionnaire."),
            ("What certifications do prospects ask about most?", "SOC 2 Type II is the most common. HIPAA for healthcare, GDPR for companies handling EU data, FedRAMP for government, and PCI DSS for companies processing payments. Having these certifications and documentation ready saves significant deal cycle time."),
        ],
        "related": ["technical-discovery", "integration-requirements", "technical-objection", "buying-committee", "technical-close"],
    },
    {
        "term": "Integration Requirements",
        "slug": "integration-requirements",
        "definition": "The technical specifications for connecting your product with the prospect's existing systems, covering APIs, data formats, authentication methods, and data flow.",
        "body": """<p>Integration requirements define how your product talks to everything else in the prospect's stack. Which systems need to connect? What APIs are involved? What data moves between systems and in which direction? What authentication method is required (OAuth, SAML, API keys)? How often does data sync? What happens when the integration fails?</p>

<p>These questions come up in every enterprise deal. Buyers almost never purchase a product that operates in isolation. Your product needs to integrate with their CRM, data warehouse, identity provider, ticketing system, or some combination. The complexity of those integrations often determines both the deal timeline and the implementation cost.</p>

<h2>Why It Matters for SEs</h2>
<p>Integration complexity is one of the top reasons enterprise deals stall or die. A prospect who discovers during the <a href="/glossary/proof-of-concept/">POC</a> that a critical integration does not work will walk away regardless of everything else your product does well. SEs who surface and validate integration requirements during <a href="/glossary/technical-discovery/">technical discovery</a> prevent this.</p>

<p>Integration requirements also feed directly into the <a href="/glossary/solution-architecture/">solution architecture</a>. The SE maps the integration points, identifies gaps between what exists natively and what requires custom development, and communicates the effort level honestly. Underestimating integration work during the sales process creates implementation nightmares after the deal closes.</p>

<h2>How SEs Use This</h2>
<p>Maintain a deep understanding of your product's native integrations, API capabilities, and known limitations. During <a href="/glossary/technical-discovery/">technical discovery</a>, ask specifically about every system the prospect expects to connect. Do not assume. A prospect who mentions "Salesforce integration" might mean real-time bi-directional sync or a nightly CSV export. The details matter enormously.</p>

<p>For each integration, document: the source and destination systems, data direction, sync frequency, authentication method, expected data volume, and error handling requirements. Share this documentation with the prospect and your post-sales team. Clear integration specs set up both the deal and the implementation for success.</p>""",
        "faq": [
            ("When should integration requirements be discussed?", "During technical discovery, before the POC. Discovering a critical integration gap during the POC wastes time and damages credibility. Identify all required integrations early and validate feasibility before committing to an evaluation."),
            ("What if the prospect needs an integration your product does not support?", "Be transparent. Explain what is available natively, what can be built via API, and what would require a partner or custom development. Provide a realistic effort estimate. Hiding gaps only creates bigger problems later."),
            ("Who handles integrations during implementation?", "The SE defines the integration requirements during the sale. Professional services or the customer's engineering team builds them during implementation. A clear handoff document from the SE prevents the post-sales team from re-discovering requirements."),
        ],
        "related": ["technical-discovery", "solution-architecture", "security-questionnaire", "proof-of-concept", "technical-objection"],
    },
    {
        "term": "Stakeholder Mapping",
        "slug": "stakeholder-mapping",
        "definition": "The process of identifying and documenting every person involved in a purchase decision, including their role, influence level, and disposition toward your solution.",
        "body": """<p>Stakeholder mapping is the SE's intelligence map for the deal. It documents who is involved in the <a href="/glossary/buying-committee/">buying committee</a>, what each person cares about, how much influence they have, and whether they support, oppose, or are neutral toward your solution. A complete stakeholder map prevents surprises and ensures every key person is engaged appropriately.</p>

<p>The map typically includes: name, title, functional role in the evaluation (technical evaluator, budget holder, end user, gatekeeper), influence level (high, medium, low), disposition (supporter, neutral, skeptic), and key concerns. It is a living document that gets updated as the deal progresses and you learn more.</p>

<h2>Why It Matters for SEs</h2>
<p>Deals fail when key stakeholders are ignored or unknown. A security architect who surfaces in week 10 with a blocking compliance concern could have been addressed in week 2 if anyone had mapped the <a href="/glossary/buying-committee/">buying committee</a> properly. Stakeholder mapping catches these gaps early.</p>

<p>It also helps SEs tailor their engagement. A skeptical <a href="/glossary/technical-decision-maker/">TDM</a> needs a different approach than a supportive end user. Knowing the disposition of each stakeholder before you interact with them lets you prepare the right message, the right level of detail, and the right proof points.</p>

<h2>How SEs Use This</h2>
<p>Start the map after the first <a href="/glossary/discovery-call/">discovery call</a>. Ask your initial contacts: "Who else will be involved in evaluating and deciding on this?" Add every name mentioned. With your AE, assign roles and estimate influence levels based on what you know.</p>

<p>Update the map after every interaction. Did a new name appear on a call? Add them. Did someone express skepticism? Note it. Did your <a href="/glossary/champion/">champion</a> mention that the CFO is cautious about new spending? That is critical intelligence. Share the map with your AE and align on a plan to engage each stakeholder appropriately.</p>""",
        "faq": [
            ("When should stakeholder mapping start?", "After the first or second meeting. The earlier you map the buying committee, the more time you have to engage each stakeholder. Waiting until late in the cycle means you are reacting to unknown stakeholders rather than proactively engaging them."),
            ("What tools are used for stakeholder mapping?", "Lucidchart and Miro for visual maps, CRM fields for structured data, or a simple spreadsheet. The format matters less than the habit of mapping and updating consistently. Some MEDDPICC platforms have built-in stakeholder mapping features."),
            ("How do you engage a skeptical stakeholder?", "Address their specific concerns directly. Ask what evidence would change their mind. Offer a dedicated session focused on their concerns rather than a generic group demo. If they have a competing preference, understand why and position accordingly without being dismissive."),
        ],
        "related": ["buying-committee", "champion", "technical-decision-maker", "economic-buyer", "meddpicc"],
    },
    {
        "term": "Custom Demo",
        "slug": "custom-demo",
        "definition": "A product demonstration tailored to a specific prospect's use case, data, industry, and pain points, as opposed to a generic or canned demo.",
        "body": """<p>A custom demo shows the prospect their future with your product. Instead of clicking through generic features, you walk them through a scenario that mirrors their actual workflow, uses data that looks like theirs, and solves the specific problem they described in <a href="/glossary/discovery-call/">discovery</a>. Custom demos close at significantly higher rates than generic ones because the prospect can see themselves using the product.</p>

<p>The preparation investment is real. A strong custom demo requires 2 to 4 hours of setup: configuring the <a href="/glossary/demo-environment/">demo environment</a>, loading relevant data, building a <a href="/glossary/demo-script/">demo script</a> around the prospect's use case, and rehearsing the flow. That investment pays off when the prospect says "this is exactly what we need" instead of "how would that work for us?"</p>

<h2>Why It Matters for SEs</h2>
<p>Custom demos are the SE's highest-impact activity. A well-targeted 30-minute custom demo can accomplish more than a 60-minute generic demo because every minute addresses something the prospect cares about. SEs who invest in customization win more <a href="/glossary/technical-win/">technical wins</a> than those who default to the standard demo.</p>

<p>The customization also signals effort and respect. The prospect sees that you listened during discovery, understood their problems, and prepared specifically for them. That effort builds the trust and credibility that carry the deal through the evaluation.</p>

<h2>How SEs Use This</h2>
<p>After <a href="/glossary/discovery-call/">discovery</a>, identify the 3 most important pain points and build your demo around solving them. Lead with the biggest pain point. Show the product handling their specific scenario. Pause after each section and confirm it matches their expectation before moving on.</p>

<p>Customize the data visible in the demo. If you are selling to a healthcare company, the demo should show healthcare data. If the prospect manages 500 users, the demo should show a 500-user environment. These details seem minor but they make the difference between "I can imagine using this" and "I wonder if this works for companies like ours."</p>""",
        "faq": [
            ("How much time should custom demo prep take?", "Two to four hours for a well-customized demo. This includes data configuration, script preparation, environment verification, and rehearsal. The payoff in higher close rates justifies the investment for qualified opportunities."),
            ("Should every demo be customized?", "For qualified enterprise deals, yes. For early-stage qualification calls or high-volume SMB demos, a semi-custom approach (standard demo with a few personalized data points and talking points) is a reasonable tradeoff between effort and impact."),
            ("What if the prospect's use case is unusual?", "Even better. A custom demo for an unusual use case shows that your product is flexible and that your SE team understands edge cases. These are the demos that create the strongest champions because the prospect sees that you took their specific situation seriously."),
        ],
        "related": ["demo-environment", "demo-script", "discovery-call", "technical-win", "demo-to-close-rate"],
    },
    {
        "term": "First Call Deck",
        "slug": "first-call-deck",
        "definition": "A presentation used in the initial meeting with a prospect that covers company overview, relevant use cases, and sets the agenda for next steps.",
        "body": """<p>The first call deck is your opening act. It introduces your company, establishes credibility, highlights relevant use cases for this prospect's industry, and sets the stage for the rest of the <a href="/glossary/sales-cycle/">sales cycle</a>. It should be concise (10 to 15 slides), visually clean, and leave more time for conversation than presentation.</p>

<p>A good first call deck is not a product feature tour. It is a conversation starter. The slides frame the problems your product solves, show evidence that you solve them well (customer logos, metrics, case studies), and create natural openings for <a href="/glossary/discovery-call/">discovery</a> questions. The prospect should talk more than you do.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs often join the first call alongside the AE. The SE's section of the first call deck typically covers a high-level architecture overview, a quick product preview, and relevant technical differentiation. Getting this right sets the tone for the entire engagement. A first call that impresses the technical attendees earns you a follow-up for <a href="/glossary/technical-discovery/">technical discovery</a>.</p>

<p>The first call deck also helps you read the room. Watch which slides generate questions and which ones get blank stares. The topics that spark engagement are the ones to double down on in the <a href="/glossary/custom-demo/">custom demo</a>.</p>

<h2>How SEs Use This</h2>
<p>Customize 2 to 3 slides per prospect. At minimum, include their industry in the use case examples and swap in relevant customer logos. If you have a case study from a similar company, lead with it. The standard company overview slides can stay generic, but the "why this matters for you" section must feel specific.</p>

<p>Keep a strict time budget. The first call deck should take no more than 15 minutes to present, leaving 30 minutes for discussion and discovery. SEs who spend the entire meeting presenting learn nothing about the prospect and waste the opportunity to qualify the deal. Present less, ask more.</p>""",
        "faq": [
            ("How many slides should a first call deck have?", "Ten to 15 slides maximum. You should be able to present the core deck in 15 minutes. More slides means more talking and less listening. The goal is to start a conversation, not deliver a lecture."),
            ("Should the first call deck include a product demo?", "A brief product preview (2 to 3 minutes of the most compelling feature) can work, but save the full demo for a dedicated follow-up. Cramming a demo into the first call reduces time for discovery and often shows features the prospect does not care about."),
            ("Who presents the first call deck?", "The AE typically handles the company overview and business value sections. The SE covers the technical overview and product preview. Coordinate in advance so the handoff is clean and both parties know their sections."),
        ],
        "related": ["discovery-call", "custom-demo", "demo-script", "sales-cycle", "stakeholder-mapping"],
    },
    {
        "term": "Win/Loss Analysis",
        "slug": "win-loss-analysis",
        "definition": "A post-deal review examining why deals were won or lost, where SEs contribute the technical perspective on what influenced the outcome.",
        "body": """<p>Win/loss analysis is the retrospective. After a deal closes (or dies), the team examines what happened and why. What did the prospect say about the evaluation? Where did competitors beat you or fall short? What worked in the demo or POC? What objections were unresolved? The goal is to extract actionable insights that improve future deal execution.</p>

<p>The best win/loss programs include prospect interviews conducted by a neutral party (not the AE or SE who worked the deal). Prospects are more candid with someone who was not involved. Internal-only reviews miss the prospect's actual reasoning, which is often different from what the team assumes.</p>

<h2>Why It Matters for SEs</h2>
<p>SEs learn more from losses than wins. A lost deal where the competitor's <a href="/glossary/proof-of-concept/">POC</a> was better, or where an unresolved <a href="/glossary/technical-objection/">technical objection</a> killed the deal, provides specific, actionable feedback. SEs who study their losses systematically improve faster than those who move on without reflection.</p>

<p>Win/loss data also feeds back into <a href="/glossary/competitive-battlecard/">battlecards</a>, <a href="/glossary/demo-script/">demo scripts</a>, and product feedback. If three deals are lost because of the same integration gap, that is a product team conversation. If two deals are won because of a specific POC approach, that approach should be standardized.</p>

<h2>How SEs Use This</h2>
<p>Participate in every win/loss review for deals you worked. Share your technical perspective honestly: what went well in the evaluation, what did not, and what you would do differently. Avoid defensiveness. The point is learning, not blame.</p>

<p>Track patterns across your personal win/loss data. If you consistently win deals where you run thorough <a href="/glossary/technical-discovery/">technical discovery</a> but lose deals where discovery was shallow, that pattern tells you exactly where to improve. Aggregate this data quarterly and use it in career development conversations with your manager.</p>""",
        "faq": [
            ("How soon after a deal should win/loss analysis happen?", "Within two weeks of the deal closing or dying. Memories fade quickly, and the prospect's willingness to provide feedback decreases with time. For prospect interviews, schedule them within one week of the decision."),
            ("Who should participate in win/loss reviews?", "The AE, SE, SE manager, and ideally a product marketing or competitive intelligence representative. For prospect interviews, use a neutral party such as product marketing or an external consultant."),
            ("What is the most common reason for losing enterprise deals?", "Competitive displacement (a competitor offered a better fit or better price) and lack of urgency (the prospect decided to do nothing). Technical gaps and poor execution are less common but more actionable. Win/loss analysis helps distinguish between these causes."),
        ],
        "related": ["competitive-battlecard", "demo-to-close-rate", "technical-objection", "presales-operations"],
    },
    {
        "term": "Presales Operations",
        "slug": "presales-operations",
        "definition": "The function that supports SE teams with tools, content, reporting, training, and process optimization, similar to sales ops but focused on the SE org.",
        "body": """<p>Presales operations is the back-office engine that makes SE teams efficient. It covers <a href="/glossary/demo-environment/">demo environment</a> management, <a href="/glossary/competitive-battlecard/">battlecard</a> maintenance, SE reporting and analytics, training programs, <a href="/glossary/sandbox-provisioning/">sandbox provisioning</a>, RFP response libraries, and process standardization. In mature orgs, presales ops is a dedicated team. In smaller companies, these responsibilities are shared among SE leadership and individual contributors.</p>

<p>The presales ops function has grown significantly in recent years as companies recognize that SE productivity is a revenue lever. Every hour an SE spends on administrative tasks, broken <a href="/glossary/demo-environment/">demo environments</a>, or searching for <a href="/glossary/competitive-battlecard/">battlecard</a> content is an hour not spent with customers. Presales ops removes that friction.</p>

<h2>Why It Matters for SEs</h2>
<p>Good presales ops makes SEs better at their jobs. When demo environments are reliable, response libraries are current, and reporting is automated, SEs can focus on the work that directly drives revenue: <a href="/glossary/discovery-call/">discovery</a>, <a href="/glossary/custom-demo/">demos</a>, <a href="/glossary/proof-of-concept/">POCs</a>, and <a href="/glossary/technical-close/">technical close</a>.</p>

<p>For SE leaders, presales ops provides the data needed to manage the team effectively. Metrics like <a href="/glossary/demo-to-close-rate/">demo-to-close rate</a>, average POC duration, <a href="/glossary/se-to-ae-ratio/">SE-to-AE ratio</a> performance, and technical win rate become trackable and actionable when presales ops builds the reporting infrastructure.</p>

<h2>How SEs Use This</h2>
<p>If your company has a presales ops team, engage with them. Report issues with demo environments, contribute to the response library, and provide feedback on tools and processes. The more input presales ops gets from the SE team, the better they can optimize the systems that support you.</p>

<p>If your company does not have dedicated presales ops, recognize that someone (probably you) is doing this work informally. Building the case for a dedicated presales ops hire or function starts with documenting the time SEs spend on non-customer-facing tasks. A presales ops person who saves 10 SEs five hours per week each creates more capacity than hiring another SE.</p>""",
        "faq": [
            ("When should a company invest in presales operations?", "When the SE team reaches 8 to 10 people. Below that size, SE leadership handles ops tasks. Above it, the administrative burden justifies a dedicated presales ops hire. The first hire typically focuses on demo environment management and content operations."),
            ("What tools does presales operations manage?", "Demo platforms and environments, RFP response tools (Loopio, Responsive), competitive intelligence platforms, SE analytics dashboards, sandbox provisioning systems, and internal knowledge bases for the SE team."),
            ("Is presales operations a good career path?", "Yes. Presales ops is a growing function with increasing demand. It combines technical knowledge, analytical skills, and operational expertise. Career progression leads to Director of Presales Operations, VP of Sales Operations, or Chief Revenue Officer depending on the path."),
        ],
        "related": ["se-to-ae-ratio", "demo-environment", "competitive-battlecard", "sandbox-provisioning", "demo-to-close-rate"],
    },
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_related_terms_html(current_slug, related_slugs):
    """Build related terms HTML section."""
    links = []
    for slug in related_slugs:
        for t in GLOSSARY_TERMS:
            if t["slug"] == slug:
                links.append(f'<a href="/glossary/{slug}/" class="related-link-card">{t["term"]}</a>')
                break
    if not links:
        return ""
    return f'''<section class="related-links">
    <h2>Related SE Terms</h2>
    <div class="related-links-grid">{"".join(links)}</div>
</section>'''


def _letter_groups():
    """Group terms by first letter for the index page."""
    groups = {}
    for t in GLOSSARY_TERMS:
        letter = t["term"][0].upper()
        if letter not in groups:
            groups[letter] = []
        groups[letter].append(t)
    return dict(sorted(groups.items()))


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------

def build_glossary_index():
    """Generate /glossary/ index page with all terms grouped alphabetically and by category."""
    title = "PreSales Glossary - 40 SE Terms Defined"
    description = (
        "A practitioner glossary of pre-sales terms. Clear definitions for POC, technical win,"
        " MEDDPICC, discovery calls, and 36 more concepts every SE should know."
    )

    crumbs = [("Home", "/"), ("Glossary", None)]
    groups = _letter_groups()

    # Build slug-to-term lookup
    slug_lookup = {t["slug"]: t for t in GLOSSARY_TERMS}

    # Category sections
    category_html = '<div class="glossary-categories">'
    category_html += '<h2>Browse by Category</h2>'
    category_html += '<div class="glossary-category-grid">'
    for cat_name, cat_slugs in GLOSSARY_CATEGORIES.items():
        links = ""
        for slug in cat_slugs:
            if slug in slug_lookup:
                t = slug_lookup[slug]
                links += f'<li><a href="/glossary/{slug}/">{t["term"]}</a></li>\n'
        category_html += f'''<div class="glossary-category-card">
    <h3>{cat_name}</h3>
    <ul>{links}</ul>
</div>
'''
    category_html += '</div></div>'

    # Letter nav
    letter_nav = '<div class="glossary-letter-nav">'
    for letter in groups:
        letter_nav += f'<a href="#letter-{letter}">{letter}</a>'
    letter_nav += '</div>'

    # Term list by letter
    term_list = ''
    for letter, terms in groups.items():
        term_list += f'<div class="glossary-letter-group" id="letter-{letter}">'
        term_list += f'<h2 class="glossary-letter-heading">{letter}</h2>'
        term_list += '<div class="glossary-term-list">'
        for t in sorted(terms, key=lambda x: x["term"]):
            term_list += f'''<a href="/glossary/{t["slug"]}/" class="glossary-term-card">
    <h3>{t["term"]}</h3>
    <p>{t["definition"][:120]}{"..." if len(t["definition"]) > 120 else ""}</p>
</a>
'''
        term_list += '</div></div>'

    body = f'''<div class="salary-content">
    {breadcrumb_html(crumbs)}
    <h1>PreSales Glossary for Solutions Engineers</h1>
    <p class="lead">Clear, practical definitions for 40 pre-sales terms. Written by SEs, for SEs. No buzzword soup.</p>
    {category_html}
    <h2>All Terms A-Z</h2>
    {letter_nav}
    {term_list}
    <section class="related-links">
        <h2>Explore More</h2>
        <div class="related-links-grid">
            <a href="/careers/" class="related-link-card">Career Guides</a>
            <a href="/tools/" class="related-link-card">SE Tool Reviews</a>
            <a href="/salary/" class="related-link-card">SE Salary Data</a>
            <a href="/companies/" class="related-link-card">Companies Hiring SEs</a>
        </div>
    </section>
</div>
'''
    body += newsletter_cta_html("Stay sharp on SE terminology and trends.")

    schema = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(
        title=title,
        description=description,
        canonical_path="/glossary/",
        body_content=body,
        active_path="/glossary/",
        extra_head=schema,
    )
    write_page("glossary/index.html", page)
    print(f"  Built: glossary/index.html")


# ---------------------------------------------------------------------------
# Individual term pages
# ---------------------------------------------------------------------------

def build_glossary_term(t):
    """Generate a single glossary term page."""
    term = t["term"]
    slug = t["slug"]
    definition = t["definition"]
    body_content = t["body"]
    faq_pairs = t["faq"]
    related = t.get("related", [])

    title = f"What Is {term}? Definition for SEs"
    # Truncate title to ~60 chars if needed
    if len(title) > 62:
        title = f"{term} - SE Definition and Guide"
    if len(title) > 62:
        title = f"{term} - SE Glossary"

    description = definition[:155].rstrip('.') + '.' if len(definition) > 155 else definition

    crumbs = [("Home", "/"), ("Glossary", "/glossary/"), (term, None)]

    # Build body
    body = f'''<div class="salary-content">
    {breadcrumb_html(crumbs)}
    <h1>What Is {term}?</h1>
    <p class="lead">{definition}</p>
    {body_content}
    {faq_html(faq_pairs)}
    {_get_related_terms_html(slug, related)}
</div>
'''
    body += newsletter_cta_html(f"Get weekly SE intelligence on {term.split('(')[0].strip().lower()} and more.")

    # Schema: breadcrumb + FAQ
    schema = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title,
        description=description,
        canonical_path=f"/glossary/{slug}/",
        body_content=body,
        active_path="/glossary/",
        extra_head=schema,
    )
    write_page(f"glossary/{slug}/index.html", page)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_all_glossary():
    """Build glossary index + all term pages. Returns count."""
    print(f"\n  Building glossary pages ({len(GLOSSARY_TERMS)} terms)...")
    build_glossary_index()
    for t in GLOSSARY_TERMS:
        build_glossary_term(t)
    print(f"  Built: {len(GLOSSARY_TERMS)} glossary term pages")
    return len(GLOSSARY_TERMS) + 1  # terms + index
