# scripts/build.py
# Main build pipeline: generates all pages, sitemap, robots, CNAME.
# Data + page generators live here. HTML shell lives in templates.py.
# Site constants live in nav_config.py.

import os
import sys
import re
import shutil
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav_config import *
import templates
from templates import (get_page_wrapper, write_page, get_homepage_schema,
                       get_breadcrumb_schema, get_faq_schema,
                       get_software_application_schema, get_article_schema,
                       breadcrumb_html, newsletter_cta_html, faq_html, ALL_PAGES)
from generate_og_images import generate_og_images, og_filename_from_path, og_template_for_path
from tools_pages import build_all_tools
from careers_pages import build_all_careers
from glossary_pages import build_all_glossary
from extras_pages import build_all_extras

# OG image generation state
OG_PAGES = []
SKIP_OG = "--skip-og" in sys.argv


def register_og(rel_path, title, subtitle=""):
    """Register a page for OG image generation."""
    OG_PAGES.append({
        "rel_path": rel_path,
        "title": title,
        "subtitle": subtitle,
        "template": og_template_for_path(rel_path),
        "og_filename": og_filename_from_path(rel_path),
    })


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
BUILD_DATE = datetime.now().strftime("%Y-%m-%d")

# Wire up templates module
templates.OUTPUT_DIR = OUTPUT_DIR
templates.SKIP_OG = SKIP_OG


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------

def load_data(filename):
    """Load JSON from data/ directory."""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fmt_salary(n):
    """Format salary number: 155000 -> '$155K'"""
    return f"${n // 1000}K"


REPORT_CITATION = "PreSales Pulse Market Analysis 2026 (n=327)"


def source_citation_html():
    """Visible source citation block for salary pages."""
    return f'''<div class="source-citation">
    <p><strong>Source:</strong> {REPORT_CITATION}. Salary data combines analysis of 4,250+ Solutions Engineer job postings with compensation survey data from verified SE professionals across 15 US markets. Cross-referenced with data from <a href="https://www.bls.gov/oes/" target="_blank" rel="noopener">Bureau of Labor Statistics</a> and <a href="https://www.levels.fyi" target="_blank" rel="noopener">Levels.fyi</a>.</p>
</div>'''


def pad_description(desc, target_min=150, target_max=158):
    """Ensure description is within 150-158 chars by appending filler."""
    suffixes = [
        " Updated weekly.", " Independent.", " Data from 4,250+ job postings.",
        " Based on 327 verified SE professionals.", " Free.", " No ads.",
        " No paywall.", " Practitioner-written.",
    ]
    used = set()
    for suffix in suffixes:
        if target_min <= len(desc) <= target_max:
            return desc
        if suffix in used:
            continue
        new = desc + suffix
        if len(new) <= target_max:
            desc = new
            used.add(suffix)
    if len(desc) > target_max:
        desc = desc[:target_max - 1].rstrip() + "."
    return desc


# ---------------------------------------------------------------------------
# Salary data structures
# ---------------------------------------------------------------------------

SALARY_BY_SENIORITY = {
    "junior": {
        "label": "Junior SE",
        "slug": "junior",
        "min": 95000, "max": 135000, "median": 115000,
        "sample": 42,
        "context": [
            "Junior Solutions Engineers typically have 0 to 2 years of experience in pre-sales or technical roles. Many come from SDR, support engineering, or customer success backgrounds and transition into SE work because they want to combine technical skills with customer-facing responsibilities. At this level, you're running segments of discovery calls, building basic demo environments, and shadowing senior SEs on larger deals. The learning curve is steep, but companies invest in ramp programs because hiring experienced SEs is expensive and competitive.",
            "Compensation for junior SEs sits in the $95K to $135K range, with a $115K median. That's strong for an entry-level technical sales role, and it reflects the fact that even junior SEs need to understand product architecture, speak credibly about integrations, and handle live technical questions from prospects. Companies that hire junior SEs at the lower end of the range typically offer structured mentorship and expect 6 to 12 months before full productivity. Those paying at the top of the range usually want someone who can carry smaller deals independently from day one.",
            "The variable compensation at this level is modest. Most junior SEs receive 80/20 or 90/10 base-to-variable splits, with the variable tied to team quota or individual deal support metrics. Equity is uncommon unless you join an early-stage startup. The real financial upside at the junior level is speed of advancement: SEs who demonstrate strong demo skills, product knowledge, and deal sense can move to mid-level in 18 to 24 months, which comes with a significant pay bump.",
        ],
        "drivers": [
            "Prior technical experience (support engineering, implementation, or development) commands a $5K to $15K premium over pure sales backgrounds",
            "Location matters significantly: SF and NYC junior SEs earn $120K to $135K while remote roles cluster around $95K to $110K",
            "Industry vertical drives pay, with cybersecurity and infrastructure software paying 10 to 15% above median for junior SEs",
            "Demo platform proficiency (Consensus, Navattic, or vendor-specific demo environments) signals readiness and reduces ramp time",
            "Company stage affects structure: startups offer lower base but more equity and faster advancement, while enterprise companies offer higher base with slower promotion cycles",
        ],
        "total_comp": "Total compensation for junior SEs ranges from $95K to $150K when you factor in variable pay and signing bonuses. Base salary makes up 80 to 90% of total comp at this level. Signing bonuses of $5K to $15K are common at enterprise companies trying to compete for technical talent. Equity is rare outside of seed and Series A startups, where grants of 0.01% to 0.05% are typical. Benefits packages (health, 401k match, learning stipends) add $10K to $20K in effective value but aren't reflected in cash comp figures.",
    },
    "mid": {
        "label": "Mid-Level SE",
        "slug": "mid-level",
        "min": 130000, "max": 175000, "median": 155000,
        "sample": 86,
        "context": [
            "Mid-level Solutions Engineers have 2 to 5 years of experience and carry their own deals. You're running full discovery calls, building custom demo environments tailored to prospect use cases, and managing the technical side of the sales cycle from first meeting through POC to close. At this level, you're expected to handle complex technical objections, create competitive battlecards, and partner effectively with Account Executives to move deals forward. The best mid-level SEs develop specializations in specific verticals or technical domains that make them the go-to person for certain deal types.",
            "The compensation range widens at mid-level: $130K to $175K base with a $155K median. This spread reflects the difference between SEs at companies where the role is well-defined versus those where you're building the SE function from scratch. Companies paying at the top of the range typically sell complex, technical products (infrastructure, security, data platforms) where the SE carries significant deal influence. Companies paying at the lower end often have simpler products with shorter sales cycles where the SE role is more demo-and-go.",
            "This is where career strategy starts to matter. Mid-level SEs who invest in vertical expertise (healthcare, financial services, government) command premiums because they can speak the prospect's language from day one. SEs who build strong relationships with their AE partners and develop a reputation for winning competitive deals advance faster. The difference between a $130K mid-level SE and a $175K one is often specialization, deal complexity, and track record, not just years of experience.",
        ],
        "drivers": [
            "Vertical specialization in high-value industries (healthcare, financial services, government) adds $10K to $20K over generalist peers",
            "Technical depth with the product stack, including the ability to build custom integrations during POCs, pushes compensation toward the top of range",
            "Win rate on competitive deals is the most visible performance metric and directly affects promotion timing and variable pay",
            "Company revenue stage: Series B through growth-stage companies offer the strongest total comp packages for mid-level SEs",
            "Geography still plays a role, with coastal metro areas paying 15 to 20% more than remote or secondary markets",
        ],
        "total_comp": "Total comp for mid-level SEs ranges from $145K to $220K. Variable compensation represents 15 to 25% of base, typically tied to team or individual quota attainment. Accelerators kick in above 100% quota, making the variable component potentially much larger in strong years. Equity becomes more common at this level: growth-stage companies offer RSU grants of $20K to $60K vesting over 4 years. Enterprise companies offer structured bonus plans that can add $20K to $40K annually. The most impactful compensation lever at mid-level is moving to a higher-ACV product, where deal values directly influence variable pay.",
    },
    "senior": {
        "label": "Senior SE",
        "slug": "senior",
        "min": 160000, "max": 210000, "median": 185000,
        "sample": 94,
        "context": [
            "Senior Solutions Engineers are the backbone of enterprise sales teams. With 5 to 8 years of experience, you're handling the largest, most complex deals in the pipeline. That means multi-stakeholder technical evaluations, extended POCs with custom infrastructure, competitive bake-offs against incumbent vendors, and deep integration architecture discussions with the prospect's engineering team. You're also mentoring junior SEs, contributing to product feedback loops, and often serving as the technical authority in executive briefings.",
            "The $160K to $210K salary range with a $185K median reflects the market value of an SE who can independently run enterprise deals. At this level, you're expected to walk into a room full of CTOs and VPs of Engineering and hold your own. You know the competitive field cold. You can whiteboard a solution architecture on the spot. You've seen enough failed POCs to know how to structure one that proves value. These aren't skills you learn from training programs; they come from hundreds of deals and years of pattern recognition.",
            "Senior SEs face a fork in the road: stay on the individual contributor track (which leads to Principal/Staff SE) or move into management. Both paths have comparable compensation, but the work is fundamentally different. IC seniors spend most of their time on deals and technical strategy. Managers spend most of their time on team building, forecasting, and cross-functional alignment. The right choice depends on whether you get more energy from solving technical problems or from developing people. There's no wrong answer, but you should make the choice deliberately rather than defaulting into management because it seems like the expected next step.",
        ],
        "drivers": [
            "Enterprise deal experience with $250K+ ACV products is the single biggest driver of senior SE compensation",
            "Industry specialization becomes a major differentiator: senior SEs with deep government (FedRAMP), healthcare (HIPAA), or financial services (SOC2/PCI) expertise earn 15 to 20% premiums",
            "Leadership scope matters: SEs who mentor a pod of 2 to 3 junior/mid SEs demonstrate readiness for the next level",
            "Technical architecture skills, particularly the ability to design integration solutions during the sales cycle, correlate with higher close rates and higher comp",
            "Competitive win rate: senior SEs with documented records of winning against specific competitors are in high demand",
        ],
        "total_comp": "Senior SE total comp ranges from $200K to $300K. Variable compensation represents 20 to 30% of base and is typically tied to individual deal outcomes or overlay quota. At enterprise software companies, accelerators can push variable pay to 150 to 200% of target in strong years. RSU grants at public companies range from $30K to $80K per year. Pre-IPO companies offer larger percentage grants with higher risk and higher potential upside. The biggest total comp packages at this level go to senior SEs at high-growth companies selling $500K+ ACV products to Fortune 500 accounts.",
    },
    "principal": {
        "label": "Principal/Staff SE",
        "slug": "principal-staff",
        "min": 190000, "max": 250000, "median": 220000,
        "sample": 38,
        "context": [
            "Principal and Staff SEs are the top of the individual contributor track. Fewer than 10% of SE organizations have this level, and the role varies significantly by company. At some organizations, Principal SEs own the most strategic deals (the ones where the CEO is involved and the deal outcome materially affects the quarter). At others, they operate as internal technical consultants who support multiple SE teams across regions or product lines. In both cases, the defining characteristic is influence without direct authority: you shape how deals are run, how products are positioned, and how the SE team develops its skills.",
            "The $190K to $250K salary range reflects scarcity. Companies that create Principal/Staff SE roles do so because they've identified specific individuals whose technical depth and deal influence justify the investment. These aren't roles you apply to on LinkedIn; they're created for people who've already demonstrated the impact. The median of $220K sits between senior SE comp and SE Manager comp, which makes sense: Principal SEs carry fewer deals but have outsized impact on the ones they touch.",
            "At this level, your scope extends well beyond individual deals. You're defining the POC methodology that the entire SE team follows. You're building the competitive intelligence framework. You're the person product teams call when they need real customer feedback on a new feature. You're presenting at industry conferences and building the company's technical reputation. The work is more varied and more strategic than at any other SE level, which is why many SEs who reach this tier choose to stay rather than move into management.",
        ],
        "drivers": [
            "Strategic deal ownership: carrying the largest, most complex deals in the company's pipeline",
            "Cross-team influence: serving as a technical resource for SEs across multiple regions or product lines",
            "Product strategy contributions: directly influencing the product roadmap based on field experience",
            "Industry thought leadership: conference presentations, published content, and external reputation",
            "Custom tooling and process innovation: building internal tools, demo frameworks, or competitive analysis systems that scale the entire SE org",
        ],
        "total_comp": "Principal/Staff SE total comp ranges from $250K to $380K. These roles carry significant equity components: RSU grants at public companies can reach $100K to $150K annually. Variable compensation is typically 20 to 25% of base but may be structured differently than standard SE comp plans (strategic bonus pools, president's club eligibility, or project-based incentives). At pre-IPO companies, the equity component can represent the majority of total expected comp over a 4-year vest. Benefits at this level often include additional perks: higher conference budgets, executive health plans, and sabbatical eligibility.",
    },
    "manager": {
        "label": "SE Manager",
        "slug": "manager",
        "min": 170000, "max": 230000, "median": 200000,
        "sample": 45,
        "context": [
            "SE Managers lead teams of 4 to 10 Solutions Engineers and sit at the intersection of sales leadership and technical strategy. The job is fundamentally different from being an individual contributor SE. You're responsible for hiring, coaching, forecasting SE capacity, managing deal assignments, running team meetings, and coordinating with sales leadership on pipeline strategy. The best SE Managers spend 30 to 40% of their time on active deals (coaching SEs through complex situations) and 60 to 70% on team operations and development.",
            "Compensation for SE Managers sits at $170K to $230K base with a $200K median. The range is wider than senior SE comp because management roles vary enormously by company. A manager running a team of 4 SEs at a mid-market company is doing very different work than one managing 10 SEs across multiple product lines at an enterprise vendor. The pay reflects that scope difference. Companies that value the SE function and give managers real authority (hiring, firing, comp decisions, deal strategy) pay at the top of the range. Companies where the SE Manager is essentially a team lead with limited authority pay at the lower end.",
            "The transition from senior SE to SE Manager is the most common career move at the 5 to 8 year mark, but it's not always the right one. Managers who succeed are those who find real satisfaction in developing other people's careers, who can delegate deals they'd rather run themselves, and who find satisfaction in team metrics rather than individual wins. The ones who struggle are strong individual contributors who took the promotion for the title and comp bump but miss the deal-level work. If you're considering the move, shadow an SE Manager for a quarter before committing. The job is less glamorous and more operational than most people expect.",
        ],
        "drivers": [
            "Team size directly correlates with comp: managers of 8 to 10 SEs earn 10 to 15% more than those managing 4 to 5",
            "Revenue responsibility: managers whose teams cover $20M+ in pipeline command premium compensation",
            "Hiring track record: managers who've built successful SE teams from scratch are in high demand",
            "Second-line management potential: companies pay more for managers they see growing into Director roles within 2 to 3 years",
            "Technical credibility: managers who can still step into deals and contribute technically (not just coach) are more valuable than pure people managers",
        ],
        "total_comp": "SE Manager total comp ranges from $220K to $320K. Variable compensation is typically 20 to 30% of base and tied to team quota attainment rather than individual deals. This creates interesting dynamics: your variable pay depends on how well you've hired, coached, and deployed your team. RSU grants at public companies range from $40K to $100K annually. Management bonuses (for hiring, team performance, cross-functional initiatives) can add another $10K to $25K. The best packages go to managers at enterprise companies with large teams and clear paths to Director promotion.",
    },
    "director": {
        "label": "Director of SE",
        "slug": "director",
        "min": 210000, "max": 300000, "median": 255000,
        "sample": 22,
        "context": [
            "Directors of Solutions Engineering lead the entire SE function for a region, product line, or (at smaller companies) the whole organization. You're managing SE Managers, setting the technical go-to-market strategy, defining the SE hiring profile, building the POC and demo methodology, and reporting to the VP of Sales or CRO. The role is equal parts strategy and execution. You need to understand the competitive field at a technical level while also managing budgets, headcount plans, and cross-functional relationships with product, marketing, and customer success.",
            "The $210K to $300K salary range reflects the seniority and scope of the role. Directors at enterprise software companies with 20+ SEs reporting through them earn at the top of the range. Directors at growth-stage companies building the SE function from scratch earn at the lower end but often receive larger equity grants. The $255K median includes significant variation: a Director at a public company in San Francisco earns very differently from one at a Series B startup in Denver. The key differentiator is whether you're maintaining an established SE org or building one, and both are valued differently by different companies.",
            "Getting to Director typically requires 8 to 15 years of SE experience, including at least 2 to 3 years as an SE Manager. The skills that matter at this level are strategic thinking, executive communication, organizational design, and the ability to hire and develop managers (not just individual contributors). The best Directors of SE are people who can articulate the value of the SE function in revenue terms: pipeline influenced, competitive win rate, deal acceleration, and expansion revenue. If you can walk into a board meeting and explain why investing in 5 more SEs will generate $20M in incremental pipeline, you'll do well at this level.",
        ],
        "drivers": [
            "Organizational scope: Directors managing 15+ SEs across multiple teams earn significantly more than those with smaller orgs",
            "Revenue influence: the ability to quantify SE team impact on pipeline, win rate, and deal size is the strongest negotiation lever",
            "Executive presence: Directors who present regularly to the C-suite and board command premium compensation",
            "Geographic coverage: Directors responsible for multiple regions (Americas, EMEA) earn more than single-region leaders",
            "Track record of building: Directors who've scaled SE teams from 5 to 20+ during company growth phases are rare and highly valued",
        ],
        "total_comp": "Director of SE total comp ranges from $300K to $450K+. Base salary is the foundation, but equity and variable comp are substantial. RSU grants at public companies range from $80K to $200K annually. Variable compensation is 25 to 35% of base and tied to org-level metrics: team quota, win rate, SE utilization, and strategic initiative completion. Executive bonuses and long-term incentive plans can add another $25K to $75K. At pre-IPO companies, Directors often negotiate for board observer rights or advisory equity in addition to standard grants. The total expected comp over a 4-year period at a successful growth company can exceed $2M.",
    },
}


SALARY_BY_LOCATION = {
    "san-francisco": {
        "label": "San Francisco",
        "slug": "san-francisco",
        "min": 165000, "max": 245000, "median": 195000,
        "sample": 58,
        "context": [
            "San Francisco remains the highest-paying market for Solutions Engineers in the US. The concentration of enterprise software companies (Salesforce, Datadog, Palo Alto Networks, CrowdStrike) creates intense competition for SE talent, and compensation reflects that. A mid-level SE in SF earns what a senior SE earns in most other markets. The trade-off is obvious: housing costs are brutal, and a $195K salary in SF has roughly the same purchasing power as $140K in Austin or $130K in Atlanta.",
            "The SF market has a few distinctive characteristics for SEs. First, the density of technical buyers means prospects are sophisticated. You'll demo to CTOs who've seen every competitive product and engineers who'll challenge your architecture claims in real time. That raises the bar for SE quality, which in turn raises comp. Second, the network effects are strong. SF-based SEs get more exposure to industry events, peer communities (like PreSales Collective meetups), and career opportunities through proximity alone.",
            "Remote work has changed the SF SE market, but not as much as some predicted. Many SF-based companies still pay SF rates to remote SEs, especially for enterprise roles where occasional on-site presence is expected. Others have adopted geo-adjusted pay bands that reduce remote SE comp by 10 to 20% compared to SF on-site rates. If you're evaluating an SF offer versus a remote offer, do the after-tax, after-housing math carefully. A $195K offer in SF may not beat a $168K remote offer when you account for California state income tax and Bay Area rent.",
        ],
        "drivers": [
            "Enterprise software companies headquartered in SF consistently pay at the top of the market for SEs at all levels",
            "California state income tax (9 to 13%) meaningfully reduces take-home pay compared to states like Texas, Florida, or Washington",
            "On-site SE roles in SF still pay 5 to 10% more than equivalent remote roles at the same company",
            "Cybersecurity and infrastructure software companies in the Bay Area pay the highest SE salaries across all verticals",
            "Signing bonuses of $15K to $30K are common for mid-to-senior SEs relocating to or accepting roles in SF",
        ],
        "cost_of_living": "San Francisco's cost of living is approximately 80% higher than the US average. A $195K salary in SF provides roughly equivalent purchasing power to $108K in the median US metro. Housing is the primary driver: median rent for a 1-bedroom apartment exceeds $3,200/month. Many SEs mitigate this by living in the East Bay or South Bay, which reduces housing costs 15 to 30% while still providing access to SF-based offices.",
    },
    "new-york": {
        "label": "New York City",
        "slug": "new-york",
        "min": 155000, "max": 235000, "median": 185000,
        "sample": 52,
        "context": [
            "New York City is the second-highest paying market for SEs and has a distinctly different character than SF. The NYC SE market is driven by fintech (Stripe, Plaid, Brex), enterprise SaaS companies with East Coast headquarters, and the financial services industry's demand for vendor-side technical sales. SEs selling into Wall Street banks, hedge funds, and insurance companies need specialized knowledge of compliance frameworks (SOC2, SOX, PCI-DSS) that commands a premium.",
            "The NYC SE market also benefits from the density of major enterprise buyers. A significant number of Fortune 500 companies have their headquarters or major offices in the metro area, which means NYC-based SEs can run in-person meetings and demos without travel. That proximity to buyers is valuable and keeps demand for NYC-based SEs high even as remote work becomes more common for other markets.",
            "Compensation in NYC is strong but slightly below SF at every level. The $185K median reflects a market where competition for SE talent is real but not as frenzied as the Bay Area. NYC also has a meaningful pool of SEs who've transitioned from finance or consulting backgrounds, bringing domain expertise that commands premium compensation. If you have prior experience at a bank, consulting firm, or financial technology company, the NYC SE market will value that background more than almost any other geography.",
        ],
        "drivers": [
            "Financial services domain expertise (SOC2, SOX, PCI-DSS, FIX protocol) adds $15K to $25K over generalist SEs",
            "Enterprise companies with NYC headquarters pay full NYC rates even for hybrid roles requiring 2 to 3 days in-office",
            "New York state plus city income tax (combined 10 to 14%) significantly affects take-home pay",
            "Fintech and regtech companies are the fastest-growing SE hiring segment in NYC",
            "Consulting or banking background translates directly to higher starting comp for SE roles in NYC",
        ],
        "cost_of_living": "NYC cost of living runs approximately 75% above the US average, driven primarily by housing. Median 1-bedroom rent in Manhattan exceeds $3,500/month. Brooklyn and Queens offer 15 to 25% savings. Combined state and city income tax rates of 10 to 14% further reduce take-home pay. A $185K salary in NYC has roughly equivalent purchasing power to $106K in the median US metro.",
    },
    "austin": {
        "label": "Austin",
        "slug": "austin",
        "min": 135000, "max": 200000, "median": 165000,
        "sample": 34,
        "context": [
            "Austin has become one of the strongest secondary markets for SEs, driven by the wave of tech companies opening offices or relocating there. Oracle, Dell, Indeed, and dozens of growth-stage SaaS companies have established Austin operations. No state income tax means a $165K salary in Austin provides more take-home pay than $185K in NYC or $195K in SF. That math has attracted a growing population of experienced SEs who want strong comp without coastal living costs.",
            "The Austin SE market is particularly strong for SEs selling cybersecurity, DevOps, and cloud infrastructure products. The city's tech talent density creates a pool of technical buyers, which means SEs working Austin-territory deals face sophisticated evaluations. That keeps the skill bar high and compensation competitive. Austin-based SEs also benefit from the city's growing conference and event scene, with South by Southwest and a growing number of B2B tech events creating networking opportunities.",
            "One caveat: Austin's cost of living has risen sharply over the past 5 years. It's no longer the bargain it was in 2020. Housing costs have increased 40 to 50% in that period, and the city's infrastructure hasn't kept pace with population growth. Still, compared to SF or NYC, Austin remains 30 to 40% cheaper for comparable quality of life. The SE talent pool is growing fast here, which could put downward pressure on comp premiums as supply catches up with demand.",
        ],
        "drivers": [
            "No state income tax adds 5 to 8% to effective take-home pay compared to California or New York roles",
            "Oracle and Dell presence anchors the enterprise SE market, with both companies hiring aggressively for pre-sales roles",
            "Growth-stage SaaS companies (Series B through D) based in Austin offer the strongest total comp packages when equity is included",
            "Cybersecurity and infrastructure companies pay at the top of the Austin range",
            "Remote SE roles benchmarked to Austin pay provide strong value since Austin rates have risen to near-coastal levels for senior roles",
        ],
        "cost_of_living": "Austin's cost of living sits approximately 15% above the US average, driven primarily by housing appreciation over the past 5 years. Median 1-bedroom rent is around $1,600/month, roughly half of SF or NYC. No state income tax adds meaningful effective income. A $165K salary in Austin provides equivalent purchasing power to roughly $200K in SF or $195K in NYC when you account for taxes and housing.",
    },
    "seattle": {
        "label": "Seattle",
        "slug": "seattle",
        "min": 160000, "max": 240000, "median": 190000,
        "sample": 41,
        "context": [
            "Seattle is the third-highest paying market for SEs, driven by the massive presence of Microsoft, Amazon, and a growing cluster of enterprise SaaS companies. The city's SE market has a distinctly enterprise flavor: most SE roles here involve selling to large organizations with complex procurement processes. That creates demand for SEs who can navigate multi-stakeholder evaluations, manage extended POC timelines, and build relationships at the executive level.",
            "Washington state has no income tax, which makes Seattle's $190K median effectively higher than NYC's $185K for take-home pay. Combine that with a cost of living 25 to 30% below SF, and Seattle becomes one of the best value propositions for SE compensation in the country. The city also has strong quality of life factors (proximity to outdoor recreation, growing food and arts scenes) that attract experienced SEs from other markets.",
            "The Seattle SE market is competitive for both employers and candidates. Amazon and Microsoft absorb a large share of available SE talent, and their compensation packages (strong base plus significant RSU grants) set the bar high. Smaller companies in the area need to offer competitive total comp to attract SEs away from those two giants. That dynamic pushes salaries up across the market, benefiting SEs at companies of all sizes in the metro area.",
        ],
        "drivers": [
            "No state income tax provides 5 to 9% higher take-home pay versus California or New York",
            "Microsoft and Amazon's SE compensation sets the local market floor for mid-level and senior roles",
            "Cloud and infrastructure software companies in Seattle pay the highest premiums for SEs with AWS, Azure, or GCP expertise",
            "Enterprise deal experience is particularly valued in Seattle given the concentration of large-company HQs",
            "RSU packages at Seattle's large tech companies can add $40K to $100K annually to total comp",
        ],
        "cost_of_living": "Seattle's cost of living runs approximately 50% above the US average. Median 1-bedroom rent is around $2,200/month. The absence of state income tax partially offsets the housing premium. A $190K salary in Seattle provides roughly equivalent purchasing power to $175K in Austin (accounting for Austin's lower housing costs but similar tax treatment).",
    },
    "boston": {
        "label": "Boston",
        "slug": "boston",
        "min": 150000, "max": 225000, "median": 180000,
        "sample": 29,
        "context": [
            "Boston's SE market is shaped by its concentration of enterprise SaaS, biotech, and healthcare IT companies. HubSpot's headquarters drives a significant share of mid-market SE hiring, while companies like Datadog, Toast, and DraftKings have expanded the city's tech employment base. The biotech corridor (Cambridge, Kendall Square) creates specialized demand for SEs who can sell data platforms, lab informatics, and research tools to scientific buyers.",
            "SEs in Boston benefit from the city's deep pool of technical talent from MIT and the broader university ecosystem. That cuts both ways: the talent pool means more competition for SE roles, but it also means Boston-based prospects tend to be highly technical, which keeps the bar high for SEs and supports premium compensation. SEs with graduate degrees or prior research experience command meaningful premiums when selling to biotech and healthcare companies.",
            "Boston's cost of living is high but not as extreme as SF or Manhattan. Housing has risen sharply, with median 1-bedroom rents around $2,600/month in the city proper. The surrounding suburbs (Waltham, Burlington, Cambridge) offer modestly lower costs while remaining accessible to Boston offices. Massachusetts state income tax is a flat 5%, which is significantly lower than California or NYC's combined rates.",
        ],
        "drivers": [
            "Healthcare IT and biotech domain expertise commands a $10K to $20K premium for SEs selling into those verticals",
            "HubSpot's presence has created a strong pipeline of mid-market SE talent that other companies recruit from",
            "Massachusetts flat 5% income tax is favorable compared to CA (9 to 13%) and NYC (10 to 14% combined)",
            "Enterprise companies in the Route 128 corridor pay full Boston-metro rates for hybrid roles",
            "Graduate degrees from local universities (MIT, Harvard, BU) provide measurable comp premiums for technical SE roles",
        ],
        "cost_of_living": "Boston's cost of living is approximately 50% above the US average. Median 1-bedroom rent in the city runs around $2,600/month, with Cambridge and Somerville slightly higher. Suburbs like Waltham and Burlington offer 15 to 20% savings. Massachusetts's 5% flat income tax is lower than most coastal states. A $180K salary in Boston provides roughly equivalent purchasing power to $155K in Austin or $135K in Atlanta.",
    },
    "denver": {
        "label": "Denver",
        "slug": "denver",
        "min": 140000, "max": 205000, "median": 170000,
        "sample": 25,
        "context": [
            "Denver has grown into a solid secondary market for SEs, attracting both companies and talent who want a mountain-west lifestyle without giving up competitive compensation. The city's tech sector is anchored by a mix of enterprise companies (Arrow Electronics, Oracle's Denver office, Ping Identity) and a growing cluster of growth-stage SaaS companies. The outdoor lifestyle is a genuine draw for SEs relocating from coastal markets, and companies in Denver lean into that as a recruiting advantage.",
            "SE compensation in Denver sits in the $140K to $205K range, which is 10 to 15% below equivalent roles in SF or Seattle. Colorado's state income tax (4.4% flat) is moderate, and the cost of living, while rising, remains meaningfully below coastal cities. For SEs doing the math, a $170K offer in Denver often provides comparable or better quality of life than $195K in SF, especially for those with families or those who value outdoor recreation access.",
            "The Denver market is still developing its SE talent density. Companies hiring SEs in Denver sometimes struggle to find experienced candidates locally and end up recruiting from SF, NYC, or Seattle. That scarcity dynamic benefits candidates: if you're an experienced SE willing to relocate to Denver, you have negotiating leverage that wouldn't exist in more saturated markets.",
        ],
        "drivers": [
            "Colorado's 4.4% flat income tax is favorable compared to coastal states",
            "Enterprise companies with Denver offices pay competitive rates to attract talent from coastal markets",
            "Cybersecurity companies (Ping Identity, SomaLogic) pay at the top of the Denver range for experienced SEs",
            "Quality of life is a genuine negotiation factor: companies compete on flexibility and outdoor lifestyle as much as comp",
            "Remote SE roles benchmarked to Denver pay provide good value given the city's moderate cost of living",
        ],
        "cost_of_living": "Denver's cost of living is approximately 15 to 20% above the US average. Median 1-bedroom rent runs around $1,700/month. The surrounding suburbs (Lakewood, Arvada, Golden) offer 10 to 15% savings. Colorado's 4.4% flat income tax is moderate. A $170K salary in Denver provides solid purchasing power, roughly equivalent to $200K in SF after adjusting for taxes and housing.",
    },
    "chicago": {
        "label": "Chicago",
        "slug": "chicago",
        "min": 140000, "max": 210000, "median": 170000,
        "sample": 31,
        "context": [
            "Chicago's SE market is anchored by a mix of enterprise tech companies and a growing SaaS startup ecosystem. Salesforce, ServiceNow, and Grubhub maintain significant Chicago offices, while companies like G2, ActiveCampaign, and Sprout Social are headquartered there. The city's SE market benefits from a strong talent pipeline (Northwestern, University of Chicago, Illinois Tech) and a cost of living that's meaningfully lower than coastal cities.",
            "SEs in Chicago often work territories that cover the broader Midwest, which means travel is part of the job for enterprise roles. The flip side is that Chicago-based SEs get exposure to a wide range of industries (manufacturing, finance, logistics, healthcare) that coastal SEs rarely see. That industry breadth builds versatile SE skills and opens career paths into vertical specialization that can command premium compensation later.",
            "The Chicago market pays comparably to Denver and Austin at the mid-level but offers more upside at the senior and Director levels, driven by the concentration of enterprise companies with large SE orgs. If you're a senior SE or SE Manager, Chicago offers strong comp, moderate costs, and a deep pool of enterprise prospects to sell into.",
        ],
        "drivers": [
            "Enterprise companies with Chicago offices (Salesforce, ServiceNow) set the local comp benchmark for senior SE roles",
            "Illinois state income tax is a flat 4.95%, moderate compared to coastal states",
            "Industry diversity (finance, healthcare, manufacturing) creates demand for SEs with vertical specialization",
            "Travel willingness: SEs covering Midwest territory may earn travel premiums or per-diems on top of base comp",
            "G2 and ActiveCampaign headquarters create a strong local pipeline of SaaS-experienced SE talent",
        ],
        "cost_of_living": "Chicago's cost of living is approximately 20% above the US average. Median 1-bedroom rent in the city proper runs around $1,800/month, with neighborhoods like Lincoln Park and Wicker Park higher. Suburban options (Evanston, Naperville) offer meaningful savings. Illinois's 4.95% flat income tax is moderate. A $170K salary in Chicago provides purchasing power comparable to $195K in SF or $190K in NYC.",
    },
    "los-angeles": {
        "label": "Los Angeles",
        "slug": "los-angeles",
        "min": 150000, "max": 230000, "median": 180000,
        "sample": 36,
        "context": [
            "Los Angeles has a growing but still developing SE market. The city's tech ecosystem spans entertainment tech (Snap, Hulu, Riot Games), e-commerce (TikTok Shop, Honey), and a growing cluster of B2B SaaS companies. SE roles in LA are less concentrated than in SF or NYC, which means the market is more dispersed and harder to navigate. That said, the companies that do hire SEs in LA often pay well because they're competing with SF-based companies for Southern California talent.",
            "LA-based SEs benefit from California's large economy and the presence of major enterprise buyers across entertainment, aerospace, healthcare, and manufacturing. The diversity of industries means SEs in LA develop broad selling experience that transfers well across verticals. The downside is California's high state income tax (9 to 13%), which reduces take-home pay meaningfully compared to Texas, Florida, or Washington-based roles.",
            "For SEs who prefer warm weather and are willing to deal with California taxes and LA traffic, the market offers solid mid-to-senior opportunities. The $180K median is competitive for the cost of living in LA's more affordable neighborhoods (Long Beach, Pasadena, Burbank), though living on the Westside or in Santa Monica pushes housing costs close to SF levels.",
        ],
        "drivers": [
            "Entertainment and media tech companies pay premiums for SEs who understand content delivery, streaming, and digital media workflows",
            "California state income tax (9 to 13%) is the biggest drag on take-home pay for LA-based SEs",
            "Aerospace and defense companies in the LA area pay well for SEs with security clearances or government experience",
            "E-commerce and retail tech are growing SE hiring segments in LA",
            "Remote roles benchmarked to LA pay provide good value if you live in a more affordable part of Southern California",
        ],
        "cost_of_living": "LA's cost of living is approximately 45% above the US average. Median 1-bedroom rent ranges from $1,800 in more affordable neighborhoods to $3,000+ on the Westside. California's high state income tax further reduces effective earnings. A $180K salary in LA provides roughly equivalent purchasing power to $165K in Austin or $155K in Atlanta.",
    },
    "miami": {
        "label": "Miami",
        "slug": "miami",
        "min": 130000, "max": 195000, "median": 160000,
        "sample": 18,
        "context": [
            "Miami's tech scene has expanded rapidly since 2021, but the SE market is still relatively small compared to established hubs. The city's strengths are in fintech (MoonPay, Pipe, several crypto companies), Latin American market coverage, and a growing cluster of companies attracted by Florida's business-friendly environment. No state income tax makes Miami's $160K median more competitive than it appears on paper, especially compared to NYC or SF.",
            "SEs based in Miami often cover Latin American territories in addition to domestic accounts. Spanish fluency is a genuine differentiator that commands a $10K to $15K premium for SE roles with LatAm coverage. The city's time zone (Eastern) and proximity to Latin American business hubs make it a natural base for companies expanding into Central and South American markets.",
            "The Miami SE market is young, which creates both opportunity and risk. On the upside, there's less competition for senior SE roles, and companies relocating to Miami often bring coastal-level compensation packages. On the downside, the talent pool is thinner, career progression options are more limited, and the SE community is smaller than in more established markets. If you're an experienced SE who values warm weather, no state income tax, and the ability to stand out in a smaller market, Miami is worth considering.",
        ],
        "drivers": [
            "No state income tax adds 5 to 9% to effective take-home pay compared to California or New York",
            "Spanish fluency commands a $10K to $15K premium for roles covering Latin American markets",
            "Fintech and crypto companies drive the highest SE salaries in Miami",
            "Companies relocating from SF or NYC often bring coastal comp benchmarks to Miami offices",
            "The smaller SE talent pool gives experienced candidates stronger negotiating leverage",
        ],
        "cost_of_living": "Miami's cost of living is approximately 25% above the US average, driven by rapidly rising housing costs. Median 1-bedroom rent in the city runs around $2,200/month. No state income tax partially offsets the housing premium. A $160K salary in Miami provides roughly equivalent purchasing power to $175K in NYC or $185K in SF after accounting for taxes and housing.",
    },
    "atlanta": {
        "label": "Atlanta",
        "slug": "atlanta",
        "min": 130000, "max": 200000, "median": 162000,
        "sample": 22,
        "context": [
            "Atlanta offers one of the best value propositions for SEs who want competitive compensation in a lower-cost market. The city's tech sector is anchored by Salesforce's southeastern hub, NCR, and a growing cluster of SaaS companies (Mailchimp/Intuit, SalesLoft, Calendly). Georgia's state income tax is moderate (5.49% flat), and the cost of living is 25 to 35% below coastal cities for comparable quality of life.",
            "The Atlanta SE market benefits from the city's role as a regional hub for the southeastern US. SEs based in Atlanta often cover territory across the Southeast, which includes a wide range of industries: healthcare (Emory, CDC corridor), logistics (UPS, Delta), fintech (NCR, Fiserv presence), and a growing manufacturing tech segment. That industry diversity builds well-rounded SE skills.",
            "For SEs relocating from coastal markets, Atlanta provides a meaningful quality-of-life upgrade. A $162K salary in Atlanta buys substantially more housing, shorter commutes, and lower overall costs than equivalent comp in SF, NYC, or LA. The trade-off is a smaller SE community and fewer local tech events compared to top-tier markets. The rapid growth of Atlanta's tech sector is closing that gap, and the city should be a top-5 SE market within the next 3 to 5 years.",
        ],
        "drivers": [
            "Cost of living 25 to 35% below coastal cities makes Atlanta comp highly competitive on a purchasing power basis",
            "Georgia's 5.49% flat income tax is moderate and straightforward",
            "Salesforce's southeastern hub and SalesLoft's HQ anchor the local SE hiring market",
            "Healthcare IT and fintech companies in the metro area pay at the top of the Atlanta range",
            "Relocation packages from coastal companies often include $10K to $20K signing bonuses for Atlanta-based roles",
        ],
        "cost_of_living": "Atlanta's cost of living is approximately 5 to 10% above the US average. Median 1-bedroom rent runs around $1,500/month in the city, with suburbs like Buckhead, Decatur, and Roswell offering comparable rates. Georgia's 5.49% income tax is moderate. A $162K salary in Atlanta provides purchasing power roughly equivalent to $215K in SF or $200K in NYC.",
    },
    "portland": {
        "label": "Portland",
        "slug": "portland",
        "min": 135000, "max": 200000, "median": 165000,
        "sample": 15,
        "context": [
            "Portland's SE market is small but punches above its weight for a city its size. The tech sector is anchored by Intel, Nike's digital division, and a cluster of mid-stage SaaS companies. Oregon has no sales tax, which doesn't directly affect SE compensation but contributes to the city's overall cost of living advantage. The SE talent pool is limited, which means companies hiring in Portland often need to recruit from Seattle or SF, and that scarcity works in candidates' favor.",
            "Most SE roles in Portland are remote-friendly, with local companies understanding that the talent pool isn't deep enough to require in-office presence. That flexibility, combined with Oregon's moderate state income tax (9 to 9.9% at higher brackets), makes Portland a solid option for SEs who want Pacific time zone coverage without SF or Seattle living costs. The city's outdoor access and cultural scene are genuine quality-of-life advantages that attract SEs from larger, more expensive markets.",
            "The downside of Portland's SE market is its size. Career advancement opportunities are limited locally, and the SE community is small enough that networking requires deliberate effort. Most Portland-based SEs work for companies headquartered elsewhere (SF, Seattle, NYC) and contribute remotely. If you're comfortable with that arrangement and value the lifestyle, Portland offers a good balance.",
        ],
        "drivers": [
            "Oregon state income tax (9 to 9.9%) is on the higher side, partially offsetting the cost-of-living advantage",
            "Limited local talent pool gives experienced candidates strong negotiating leverage",
            "Remote-friendly culture means most Portland SE roles offer full flexibility",
            "Intel and Nike's digital operations anchor the enterprise SE market locally",
            "Quality of life (outdoor access, food scene, moderate housing costs) is a genuine recruiting tool for Portland-based companies",
        ],
        "cost_of_living": "Portland's cost of living is approximately 20% above the US average. Median 1-bedroom rent runs around $1,600/month. Oregon's income tax (9 to 9.9% at higher brackets) partially offsets the housing savings compared to Washington state. A $165K salary in Portland provides purchasing power roughly equivalent to $190K in SF after taxes and housing adjustments.",
    },
    "washington-dc": {
        "label": "Washington DC",
        "slug": "washington-dc",
        "min": 150000, "max": 225000, "median": 182000,
        "sample": 27,
        "context": [
            "Washington DC's SE market is unique because of the federal government's influence on tech buying. SEs selling into government agencies (directly or through systems integrators like Deloitte, Booz Allen, SAIC) need specialized knowledge of FedRAMP, FISMA, IL4/IL5, and federal procurement processes. That expertise commands a significant premium: government-specialized SEs earn 15 to 25% more than generalist SEs at equivalent seniority levels.",
            "The DC metro area (including Northern Virginia and Maryland) is home to a massive concentration of cybersecurity, cloud infrastructure, and defense tech companies. AWS's East Coast hub is in Arlington. Palantir, Crowdstrike, and dozens of smaller security companies have significant DC-area operations. For SEs who want to build deep expertise in security, compliance, and government technology, DC is the best market in the country.",
            "Compensation in DC is strong: the $182K median reflects the premium that government and security specialization commands. The cost of living is high (comparable to Boston or slightly below NYC), and the local tax situation is complex (DC, Virginia, and Maryland each have different rates). SEs living in Virginia benefit from the state's moderate income tax (5.75%), while those in DC proper face a 8.5 to 10.75% rate. Geography within the metro area matters more for tax purposes in DC than in almost any other market.",
        ],
        "drivers": [
            "Security clearance (Secret, Top Secret, TS/SCI) commands $20K to $40K premiums for SEs at cleared companies",
            "FedRAMP and government procurement expertise is the single biggest comp driver in the DC market",
            "Cybersecurity companies in Northern Virginia pay at the top of the DC-metro range",
            "Tax jurisdiction matters: Virginia (5.75%) is more favorable than DC (8.5 to 10.75%) or Maryland (5.75% plus county)",
            "Systems integrator experience (Deloitte, SAIC, Booz Allen) translates to higher starting comp at vendor-side SE roles",
        ],
        "cost_of_living": "DC metro cost of living is approximately 45% above the US average. Median 1-bedroom rent ranges from $2,000 in outer suburbs to $2,800 in the city proper. Tax rates vary significantly by jurisdiction. A $182K salary in DC provides purchasing power roughly equivalent to $155K in Austin or $140K in Atlanta.",
    },
    "dallas": {
        "label": "Dallas",
        "slug": "dallas",
        "min": 135000, "max": 205000, "median": 168000,
        "sample": 20,
        "context": [
            "Dallas-Fort Worth is a growing SE market anchored by a mix of enterprise tech companies and the financial and healthcare industries. AT&T, Texas Instruments, and a wave of tech companies opening DFW offices create steady demand for SEs. No state income tax gives Dallas a meaningful take-home pay advantage over coastal markets, and the cost of living is moderate for a major metro area.",
            "SEs in Dallas often cover broad territories across Texas and the broader South/Southwest region. The travel can be significant for enterprise roles, but the upside is exposure to a diverse set of industries: oil and gas tech, healthcare (large hospital systems), financial services, and logistics. That industry breadth builds versatile SE skills that translate to higher comp as you specialize.",
            "The DFW tech talent pool is growing rapidly, driven partly by corporate relocations (Charles Schwab, McKesson, several fintech firms) and partly by the quality-of-life arbitrage that draws experienced professionals from coastal cities. The SE market here is still catching up to Austin's, but the larger metro population and broader industry base give Dallas long-term upside as a secondary SE hub.",
        ],
        "drivers": [
            "No state income tax adds 5 to 8% effective take-home pay versus California or New York roles",
            "Enterprise companies with DFW operations (AT&T, Texas Instruments, McKesson) anchor the local SE comp benchmark",
            "Healthcare IT companies pay at the top of the Dallas range for SEs with HIPAA and health data expertise",
            "Corporate relocations from coastal cities are importing higher comp expectations to the DFW market",
            "Cost of living in DFW is 10 to 15% below Austin and 35 to 45% below SF for comparable housing",
        ],
        "cost_of_living": "Dallas-Fort Worth cost of living is approximately 5 to 10% above the US average. Median 1-bedroom rent runs around $1,400/month, well below most other major SE markets. No state income tax further improves purchasing power. A $168K salary in Dallas provides purchasing power roughly equivalent to $220K in SF or $210K in NYC.",
    },
    "san-diego": {
        "label": "San Diego",
        "slug": "san-diego",
        "min": 145000, "max": 215000, "median": 175000,
        "sample": 16,
        "context": [
            "San Diego offers a California tech market experience at a lower price point than SF or LA. The city's SE market is driven by biotech/life sciences (Illumina, Dexcom, dozens of smaller firms), defense tech (Qualcomm, SAIC, BAE Systems), and a growing cluster of SaaS companies. For SEs who want to live in Southern California and work in specialized verticals, San Diego is an attractive option.",
            "The biotech concentration creates demand for SEs who can sell data platforms, lab informatics, and research tools to scientific buyers. These roles require a combination of technical depth and the ability to communicate with PhD-level researchers, which is a rare skill set that commands premium compensation. Defense and aerospace companies in the area also pay well for SEs with security clearances.",
            "San Diego's SE market is smaller than LA's, with fewer companies and fewer open roles at any given time. The trade-off is less competition for positions and a tight-knit SE community that provides strong networking opportunities. California's state income tax applies here too, which reduces the take-home pay advantage compared to Texas or Florida. For SEs who prioritize quality of life and vertical specialization in biotech or defense, San Diego is hard to beat.",
        ],
        "drivers": [
            "Biotech and life sciences expertise commands a $10K to $20K premium for SEs selling into research and clinical organizations",
            "Defense and aerospace companies pay well for SEs with active security clearances",
            "California state income tax (9 to 13%) reduces take-home pay compared to zero-tax states",
            "Qualcomm and Illumina set the local enterprise SE comp benchmark",
            "Smaller market means less competition for senior SE roles, giving candidates more leverage",
        ],
        "cost_of_living": "San Diego's cost of living is approximately 40% above the US average. Median 1-bedroom rent runs around $2,100/month, roughly 30% below SF. California state income tax applies at the same rates as SF and LA. A $175K salary in San Diego provides roughly equivalent purchasing power to $150K in Austin or $145K in Atlanta.",
    },
    "remote": {
        "label": "Remote",
        "slug": "remote",
        "min": 130000, "max": 210000, "median": 168000,
        "sample": 72,
        "context": [
            "Remote SE roles represent the fastest-growing segment of the SE job market. Approximately 34% of SE job postings now offer fully remote work, and that number has increased steadily since 2022. The $130K to $210K range is wide because it encompasses everything from SF-benchmarked remote roles ($190K to $210K) to geo-adjusted positions benchmarked to lower-cost markets ($130K to $150K). Understanding how a specific company handles remote comp is critical before evaluating any offer.",
            "The remote SE market has matured significantly. In 2022, many companies hired remote SEs for the first time and experimented with compensation structures. By 2026, clear patterns have emerged. Tier 1 companies (Salesforce, Datadog, CrowdStrike) pay a single national rate regardless of location. Tier 2 companies use 3 to 5 geographic tiers. Tier 3 companies geo-adjust to local market rates, which can mean a 20 to 30% difference between an SE living in SF versus one in Birmingham. Always ask about the geo-adjustment policy before engaging with a remote SE opportunity.",
            "Remote SEs face unique challenges that in-office SEs don't. Demo delivery over video is different from in-person demos. Building relationships with AE partners requires more deliberate effort. Getting visibility for promotion is harder when leadership doesn't see you daily. The SEs who succeed remotely are disciplined about communication, proactive about internal networking, and excellent at asynchronous collaboration. If you thrive in that environment, remote SE roles offer outstanding flexibility and, at the top of the range, compensation that matches or exceeds most local markets.",
        ],
        "drivers": [
            "Geo-adjustment policy is the single biggest factor: SF-benchmarked remote roles pay $190K+ while geo-adjusted roles may drop to $130K for lower-cost locations",
            "Enterprise deal experience matters more for remote SEs because travel to prospect sites is less frequent, putting more weight on virtual selling skills",
            "Demo delivery skills over video are table stakes: remote SEs who run polished, engaging virtual demos earn more and advance faster",
            "Time zone coverage preferences affect comp: SEs willing to cover West Coast hours from East Coast locations (or vice versa) have more options",
            "Company maturity with remote SE teams: companies that have had remote SEs for 3+ years typically pay better and have more defined career paths than those just starting",
        ],
        "cost_of_living": "Remote SE compensation varies based on where you live and the employer's geo-adjustment policy. The most favorable arrangement is a SF-benchmarked salary while living in a lower-cost area (Austin, Denver, Atlanta). The $168K remote median represents the middle ground across all geo-adjustment tiers. Your effective purchasing power depends entirely on your location.",
    },
}


SALARY_BY_STAGE = {
    "seed": {
        "label": "Seed Stage",
        "slug": "seed",
        "min": 100000, "max": 155000, "median": 125000,
        "sample": 18,
        "context": [
            "Seed-stage companies hire SEs when founder-led sales starts hitting a wall on technical deals. You're typically the first SE, which means you're building everything from scratch: demo environments, POC processes, competitive battlecards, and the technical narrative for the product. The pay range of $100K to $155K reflects the reality that seed companies have limited cash, but they compensate with equity that can be worth multiples of your salary if the company succeeds. Most seed SEs join because they believe in the product and want the experience of building a pre-sales function from zero.",
            "Working as an SE at a seed company is a fundamentally different job than at an enterprise vendor. You're not running polished demo scripts on a mature platform. You're figuring out what the demo should be, working with engineering to build features that close specific deals, and often doing customer success work alongside pre-sales because the team is too small to separate those functions. The upside is enormous learning velocity. The downside is that the product may not be ready for the technical evaluations you're being asked to run, which means creative problem-solving is a daily requirement.",
            "SE hiring at seed stage is relatively rare (only 18 data points in our sample), which means the range is less well-defined than later stages. The companies that hire SEs this early tend to be selling technical products to technical buyers (developer tools, infrastructure, security) where having a credible technical voice in the sales process is essential from day one. If you're considering a seed-stage SE role, evaluate the founders' technical credibility, the product's competitive position, and the equity grant carefully. The cash comp will be the lowest of your SE career, but the equity upside and experience value can be significant.",
        ],
        "drivers": [
            "Equity grants at seed stage typically range from 0.1% to 0.5%, which can be worth $100K to $500K+ at a successful Series B or later",
            "Cash compensation is constrained by runway: seed companies typically have 12 to 24 months of cash and need to be disciplined about burn",
            "Prior startup experience significantly increases starting comp because seed companies can't afford a long ramp",
            "Product-market fit uncertainty means your demo and competitive positioning skills need to be adaptable as the product evolves",
            "Geographic flexibility: most seed-stage SE roles are remote, which means your local cost of living determines effective compensation",
        ],
        "equity_note": "Equity at seed stage is the primary upside. Typical SE grants range from 0.1% to 0.5% with standard 4-year vesting and 1-year cliff. The expected value is highly uncertain: most seed companies fail, but the ones that succeed can make early SE equity worth $200K to $1M+ over the vesting period. Negotiate for the largest grant possible, since dilution from future funding rounds will reduce your percentage. Ask about the current valuation, shares outstanding, and the most recent 409A to understand what your grant is worth today.",
    },
    "series-a": {
        "label": "Series A",
        "slug": "series-a",
        "min": 120000, "max": 175000, "median": 145000,
        "sample": 32,
        "context": [
            "Series A is where SE hiring accelerates. The company has proven product-market fit and needs to scale the sales process beyond founder-led deals. You're building the repeatable demo flow, documenting the competitive landscape, and working closely with the first AEs to figure out which deals need SE involvement and which don't. The $120K to $175K range reflects more mature compensation structures than seed stage, with proper variable comp plans and equity grants that, while smaller in percentage terms, come with better-defined valuations.",
            "At Series A, the SE function is still being defined. You'll have input into the SE hiring profile, the tools the team uses, and the POC methodology. That influence is valuable for your career development because it gives you experience building processes, not just executing them. The best Series A SEs are generalists who can handle discovery, demos, POCs, and technical objections across a wide range of prospect types. Specialization comes later as the team grows.",
            "Compensation at Series A is competitive enough to attract experienced SEs from larger companies, especially when you factor in equity. Companies at this stage typically offer SE equity grants of 0.05% to 0.2%, which is smaller than seed but with lower risk since the company has raised meaningful capital and validated its market. The cash comp improvement over seed stage ($20K to $30K higher median) reflects both the company's better funding position and the higher expectations for immediate impact.",
        ],
        "drivers": [
            "Prior experience as a first or second SE at a startup commands a meaningful premium because Series A companies need someone who can build processes",
            "Technical product expertise in the company's domain (security, data, infrastructure) drives starting comp toward the top of the range",
            "Equity grants at Series A typically range from 0.05% to 0.2% with 4-year vesting",
            "Variable comp plans at Series A are more structured than seed: expect 80/20 or 85/15 base-to-variable splits",
            "Location matters less at Series A since most roles are remote, but companies may geo-adjust comp based on your location",
        ],
        "equity_note": "Series A equity grants for SEs typically range from 0.05% to 0.2%. The company has a post-money valuation ($15M to $50M typically), so you can estimate the current paper value of your grant. Expected dilution from future rounds will reduce your percentage by 20 to 30% per round. The key question is the company's growth trajectory: a 0.1% grant at a company that reaches a $500M valuation is worth $500K before dilution. Ask about the option strike price, exercise window (90 days is standard, but some companies offer extended windows), and any acceleration provisions.",
    },
    "series-b": {
        "label": "Series B",
        "slug": "series-b",
        "min": 140000, "max": 200000, "median": 168000,
        "sample": 45,
        "context": [
            "Series B is the sweet spot for SE compensation when you balance cash, equity, risk, and growth opportunity. The company has a working sales motion, a growing customer base, and enough funding ($30M to $80M+ raised) to pay competitive salaries. SE teams at Series B companies typically grow from 2 to 3 people to 5 to 8, which means you're joining a team that has some structure but still offers room to influence the direction of the function.",
            "The $140K to $200K range with a $168K median represents a meaningful step up from Series A compensation. Variable comp is well-defined (15 to 25% of base tied to quota), equity grants come with clearer valuations, and benefits packages start to resemble enterprise-quality offerings. Series B companies compete directly with enterprise companies for SE talent, which pushes them to offer total comp packages that are competitive on a cash basis, not just on an equity-upside basis.",
            "For SEs evaluating Series B opportunities, the key factors to assess are the SE-to-AE ratio (which affects workload), the company's competitive position (how much deal-level work is competitive versus net-new category creation), and the product's technical depth (which determines how much of your time is spent on genuine technical selling versus demo-and-go). Companies where the SE function is strategically valued and where AE-SE partnerships are strong tend to pay at the top of the range and promote faster.",
        ],
        "drivers": [
            "Company growth rate: Series B companies growing 100%+ year-over-year pay more aggressively for SE talent because unfilled SE seats directly constrain pipeline",
            "Product complexity: companies selling technical products to technical buyers pay $15K to $25K more than those with simpler, broader products",
            "SE-to-AE ratio: companies with 1:3 or better ratios provide better workload balance and tend to have higher SE satisfaction and retention",
            "Equity grants at Series B typically range from 0.02% to 0.1%, with RSUs becoming more common than options at later-stage Series B companies",
            "Signing bonuses of $10K to $25K are common at Series B companies competing with enterprise companies for experienced SEs",
        ],
        "equity_note": "Series B equity grants for SEs typically range from 0.02% to 0.1%. Post-money valuations at this stage are usually $100M to $400M, giving grants a more tangible current value. Some later-stage Series B companies have transitioned from stock options to RSUs, which means no strike price risk. The equity is less speculative than seed or Series A: the company has proven revenue, growing customers, and a clear path to the next funding round. Ask about secondary sale opportunities (some Series B companies allow partial equity liquidation) and the expected timeline to IPO or acquisition.",
    },
    "growth": {
        "label": "Growth Stage",
        "slug": "growth",
        "min": 155000, "max": 225000, "median": 185000,
        "sample": 64,
        "context": [
            "Growth-stage companies (Series C and beyond, $100M+ ARR) offer the highest total compensation packages for SEs when you combine base salary, variable comp, and equity. The $155K to $225K base range is competitive with enterprise companies, and the equity component (RSUs at defined valuations, often with secondary sale opportunities) adds meaningful value without the binary risk of early-stage equity. SE teams at growth-stage companies are typically 10 to 30 people, with formal management structures, specialized roles, and established processes.",
            "Working as an SE at a growth-stage company combines the best of both worlds for many professionals. You get startup-level growth opportunities (rapid product development, new market expansion, evolving competitive dynamics) with enterprise-level compensation and infrastructure (established demo environments, dedicated SE tooling, structured onboarding). The trade-off is that you have less influence over the SE function's direction compared to earlier stages: the playbook is largely written, and your job is to execute it at a high level.",
            "Growth-stage companies are where SE career paths become most clearly defined. Individual contributor tracks (Senior to Principal/Staff), management tracks (SE Manager to Director), and specialist tracks (industry vertical experts, overlay SEs for specific product lines) all exist with explicit promotion criteria and compensation bands. For SEs who value clarity about their career trajectory and competitive compensation, growth-stage companies are hard to beat.",
        ],
        "drivers": [
            "RSU grants with defined valuations add $40K to $100K annually in expected equity comp",
            "Variable compensation plans are mature: 80/20 base-to-variable splits with quarterly accelerators that can push variable to 150% of target",
            "Product line complexity: growth-stage companies with multiple products pay premiums for SEs who can sell across the portfolio",
            "Geographic territory: SEs covering major metros (SF, NYC, Chicago) earn more than those covering secondary or tertiary markets",
            "Pre-IPO companies with clear public offering timelines offer the best equity upside at the growth stage",
        ],
        "equity_note": "Growth-stage equity for SEs is typically structured as RSUs with 4-year vesting. Annual grant values range from $40K to $100K depending on seniority and company valuation. The key advantage over earlier stages is liquidity: many growth companies offer secondary sale opportunities (Carta, EquityBee, direct tender offers) that let you convert some equity to cash before an IPO. Ask about secondary sale policies, lockup periods, and the company's stated timeline for a liquidity event. Growth-stage equity is less speculative but offers less dramatic upside than early-stage grants.",
    },
    "enterprise": {
        "label": "Enterprise",
        "slug": "enterprise",
        "min": 160000, "max": 240000, "median": 195000,
        "sample": 89,
        "context": [
            "Enterprise companies (public companies, late-stage private companies with $500M+ valuations) offer the highest base salaries and most predictable compensation for SEs. The $160K to $240K base range with a $195K median reflects mature comp structures with annual review cycles, merit increases, and defined pay bands. RSU packages at public companies provide liquid equity that you can sell on a regular vesting schedule, eliminating the lottery-ticket dynamics of startup equity.",
            "SE roles at enterprise companies are well-defined and specialized. You'll typically focus on a specific product line, industry vertical, or deal size tier. The demo environments are mature, the competitive battlecards are maintained, and the POC processes are documented. That structure reduces the ambiguity of the role but also means less flexibility to shape the function. Enterprise SEs who thrive are those who enjoy going deep on complex deals and building long-term relationships with named accounts, not those who want to build processes from scratch.",
            "The trade-off with enterprise SE roles is clear: highest cash comp and most stability, but slower career progression and less equity upside compared to growth-stage companies. Promotion cycles at enterprise companies typically run 18 to 36 months, and advancement often requires geographic moves or product line changes. The SEs who earn at the top of the enterprise range are those with deep vertical expertise (government, healthcare, financial services), strong competitive win rates, and the ability to influence deals at the executive level.",
        ],
        "drivers": [
            "RSU packages at public companies add $50K to $150K annually in liquid equity",
            "Deal size specialization: SEs handling $1M+ ACV deals earn at the top of the range",
            "Industry vertical expertise (government/FedRAMP, healthcare/HIPAA, financial services/SOX) commands 15 to 20% premiums",
            "Public company benefits packages (401k match, ESPP, wellness programs) add $15K to $30K in effective total comp value",
            "President's Club and other recognition programs provide additional variable comp of $10K to $25K for top performers",
        ],
        "equity_note": "Enterprise/public company equity is structured as RSUs that vest on a regular schedule (monthly or quarterly after a 1-year cliff is common). Annual grant values range from $50K to $150K for mid-to-senior SEs, with refresh grants provided at annual reviews. The key advantage is liquidity: you can sell vested shares immediately at market price. ESPP (Employee Stock Purchase Plan) programs offer an additional 5 to 15% discount on share purchases. The downside compared to pre-IPO equity is limited upside: you're buying shares at market price rather than at a strike price from years earlier.",
    },
}


SALARY_COMPARISONS = {
    "se-vs-ae": {
        "slug": "se-vs-ae",
        "role_a": "Solutions Engineer",
        "role_b": "Account Executive",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 80000, "max": 350000, "median": 145000},
        "context": [
            "Solutions Engineers and Account Executives work side by side on every deal, but their compensation structures look completely different. AEs live on variable comp: a 50/50 or 60/40 base-to-OTE split is standard, which means a $145K median OTE translates to roughly $75K to $85K in base salary. SEs, by contrast, have 80/20 or 85/15 splits, with the $155K median representing a much higher base salary. In a great year, a top AE can out-earn any SE. In a mediocre year, the SE's paycheck barely changes while the AE's drops dramatically.",
            "The relationship between SEs and AEs is the defining dynamic of pre-sales work. Great AE-SE partnerships are force multipliers: the AE handles business relationships and commercial negotiations while the SE builds technical credibility and manages the evaluation process. Poor partnerships (where the AE overpromises, the SE is brought in too late, or territory alignment creates conflicts) are the number one source of SE job dissatisfaction. When evaluating an SE role, the quality of the AE team matters as much as the comp package.",
            "Career crossover between the two roles is uncommon but not unheard of. Some SEs move to AE roles because they want the uncapped earning potential of variable comp. Some AEs move to SE roles because they prefer the technical work and more predictable income. The skills don't transfer as cleanly as people assume: AEs who become SEs often struggle with the technical depth required, and SEs who become AEs often struggle with the relentless pipeline generation and closing pressure that defines the AE job.",
        ],
        "key_differences": [
            "Comp structure: SEs earn 80 to 85% base with predictable income. AEs earn 50 to 60% base with uncapped variable, creating wider income variance.",
            "Day-to-day work: SEs run discovery, demos, POCs, and technical evaluations. AEs run pipeline generation, business conversations, contract negotiations, and closing.",
            "Stress profile: SEs face technical pressure (live demos, difficult questions, POC timelines). AEs face quota pressure (monthly/quarterly targets, pipeline coverage, forecast accuracy).",
            "Career trajectory: SE path leads to Principal SE, SE Manager, or Director of SE. AE path leads to Enterprise AE, Sales Manager, or VP of Sales. Both paths reach VP level with $300K+ total comp.",
            "Skill emphasis: SEs need deep product knowledge, competitive intelligence, and the ability to build trust with technical buyers. AEs need prospecting skills, negotiation ability, and the ability to build executive-level relationships.",
        ],
        "faq": [
            ("Do Solutions Engineers or Account Executives earn more?", "It depends on performance. The SE median ($155K) is higher than the AE median ($145K), but top AEs clearing quota can earn $250K to $350K+ in strong years. SE comp is more predictable; AE comp has higher upside but more downside risk."),
            ("Can a Solutions Engineer become an Account Executive?", "Yes, though the transition requires developing pipeline generation and closing skills that aren't part of the typical SE job. SEs who make the switch usually do so because they want uncapped earning potential. The technical knowledge transfers well, but the quota pressure and business development skills take 6 to 12 months to develop."),
            ("What is the SE-to-AE ratio and why does it matter?", "The typical SE-to-AE ratio is 1:2 to 1:4, meaning each SE supports 2 to 4 AEs. Lower ratios (1:2) mean less deal volume per SE, deeper deal involvement, and generally higher SE satisfaction. Higher ratios (1:4+) mean more deals but shallower involvement and higher burnout risk."),
        ],
    },
    "se-vs-gtm-engineer": {
        "slug": "se-vs-gtm-engineer",
        "role_a": "Solutions Engineer",
        "role_b": "GTM Engineer",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 90000, "max": 250000, "median": 135000},
        "context": [
            "Solutions Engineers and GTM Engineers both sit at the intersection of sales and technology, but they work on fundamentally different parts of the funnel. SEs work the middle and bottom of the funnel: discovery calls, demos, POCs, and technical evaluations for qualified prospects. GTM Engineers work the top of the funnel: building automated outbound systems, enrichment pipelines, and data infrastructure that generate the qualified leads SEs eventually work. They're complementary roles, not competing ones.",
            "The $20K median gap ($155K for SEs versus $135K for GTM Engineers) reflects two things. First, the SE role is more established, with decades of history and well-defined career paths. GTM Engineering emerged in 2023 to 2024 and is still defining its compensation norms. Second, SEs directly influence deal outcomes (technical wins, POC successes, competitive victories), which gives them clearer revenue attribution and stronger negotiation leverage. GTM Engineers generate pipeline at scale, but the revenue attribution is less direct.",
            "Skills overlap between the two roles is increasing. Both need API literacy, CRM expertise, and the ability to translate between technical and business contexts. SEs who learn automation tools (Clay, Make, n8n) and data enrichment become more valuable because they can support deal-level personalization. GTM Engineers who understand the SE's needs (what makes a qualified prospect, which technical signals matter) build better pipeline. Companies that integrate the two functions outperform those that silo them.",
        ],
        "key_differences": [
            "Funnel position: SEs work qualified opportunities (demos, POCs, evaluations). GTM Engineers build the systems that generate those opportunities.",
            "Skills emphasis: SEs need deep product knowledge, demo skills, and live communication ability. GTM Engineers need data engineering, automation tools (Clay, Make), and pipeline architecture.",
            "Revenue attribution: SEs have direct deal influence (win/loss attribution). GTM Engineers have pipeline generation attribution (meetings booked, contacts enriched).",
            "Team structure: SEs report to sales leadership and partner with AEs. GTM Engineers may report to sales, marketing, or revenue operations depending on the company.",
            "Growth trajectory: SE career path is well-established (to Principal, Manager, Director). GTM Engineer path is emerging (to Lead GTM Engineer, Head of GTM Engineering).",
        ],
        "faq": [
            ("Should I become a Solutions Engineer or GTM Engineer?", "If you enjoy customer-facing work, live demos, and solving complex technical problems deal-by-deal, SE is the better fit. If you prefer building systems, automating workflows, and working with data at scale, GTM Engineering is the better fit. SEs are deal-focused; GTM Engineers are system-focused."),
            ("Do GTM Engineers replace Solutions Engineers?", "No. They serve different parts of the funnel. GTM Engineers automate top-of-funnel pipeline generation (outbound data, enrichment, sequencing). SEs handle the technical evaluation once a prospect is qualified. Companies need both: GTM Engineers to fill the pipeline and SEs to convert it."),
            ("Which role pays more long-term?", "SEs currently have higher median comp ($155K versus $135K) and more established senior-level roles ($220K to $300K+ for Principal/Director). GTM Engineering is newer with faster growth (205% YoY job posting increase). The ceiling for both roles is likely $250K to $300K+ at senior levels within 3 to 5 years."),
        ],
    },
    "se-vs-sales-engineer": {
        "slug": "se-vs-sales-engineer",
        "role_a": "Solutions Engineer",
        "role_b": "Sales Engineer",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 100000, "max": 280000, "median": 158000},
        "context": [
            "Solutions Engineer and Sales Engineer are, in most companies, the same job with a different title. The distinction is purely linguistic and driven by company preference rather than any meaningful difference in responsibilities. Both roles involve technical discovery, demos, POC management, and technical objection handling. The median salaries ($155K for SE, $158K for Sales Engineer) are close enough to be within the margin of error for our data set.",
            "Where titles do matter is in how companies signal their culture. Companies that use 'Solutions Engineer' tend to position the role as more consultative, with emphasis on understanding the prospect's business problems and designing solutions. Companies that use 'Sales Engineer' tend to lean more into the deal support aspect, with the SE serving as the technical arm of the sales team. In practice, both titles do both things. The difference is emphasis, not substance.",
            "For job seekers, the title distinction is worth understanding during your search. If you search only for 'Solutions Engineer' openings, you'll miss identical roles posted as 'Sales Engineer,' 'Solutions Consultant,' or 'Pre-Sales Engineer.' All four titles describe the same core function. The compensation data we've collected combines all four titles (normalized to the common role definition) and shows no statistically significant pay difference between them.",
        ],
        "key_differences": [
            "Title preference: 'Solutions Engineer' is more common at SaaS companies. 'Sales Engineer' is more common in infrastructure, networking, and traditional enterprise tech.",
            "Cultural signal: 'Solutions' implies consultative selling emphasis. 'Sales' implies deal support emphasis. Both roles do both things.",
            "Industry prevalence: cybersecurity and networking companies tend to use 'Sales Engineer.' Cloud and SaaS companies tend to use 'Solutions Engineer.'",
            "Compensation: no meaningful difference. The $3K median gap ($155K vs $158K) is within normal data variance and should not influence job decisions.",
        ],
        "faq": [
            ("Is there a difference between Solutions Engineer and Sales Engineer?", "In most companies, no. The titles describe the same pre-sales technical role: running discovery, building demos, managing POCs, and handling technical objections. The title preference varies by industry and company culture, but the job responsibilities are interchangeable."),
            ("Which title is better for my career?", "Neither title has inherent career advantages. What matters is the company, the products you sell, the deals you close, and the skills you develop. Both titles are recognized and respected across the industry. Use whichever title your employer uses and focus on building strong SE skills rather than optimizing your title."),
            ("Do companies pay differently for Solutions Engineers vs Sales Engineers?", "Our data shows no statistically significant pay difference. The $155K SE median and $158K Sales Engineer median are within normal variance. Compensation is driven by seniority, location, company stage, and individual performance, not by which of these two titles appears on your offer letter."),
        ],
    },
    "se-vs-csm": {
        "slug": "se-vs-csm",
        "role_a": "Solutions Engineer",
        "role_b": "Customer Success Manager",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 75000, "max": 180000, "median": 115000},
        "context": [
            "Solutions Engineers and Customer Success Managers occupy opposite sides of the sales cycle. SEs are pre-sale: they help prospects evaluate and buy the product. CSMs are post-sale: they help customers adopt, use, and renew the product. The $40K median gap ($155K versus $115K) reflects the revenue attribution difference. SEs directly influence new revenue (deal wins). CSMs influence retention and expansion revenue, which is valuable but attributed differently in most organizations.",
            "The skills overlap is larger than the comp gap suggests. Both SEs and CSMs need product expertise, communication skills, and the ability to build trust with technical and business stakeholders. Both roles require understanding the customer's use case and mapping the product's capabilities to their needs. The key difference is context: SEs do this in a competitive evaluation where the customer hasn't committed yet, while CSMs do it with an existing customer who has already bought.",
            "Career crossover between SE and CSM is common in both directions. CSMs who want higher comp and enjoy competitive selling often move to SE roles, bringing valuable product expertise and customer empathy. SEs who are tired of the sales cycle pressure and want more strategic, relationship-focused work sometimes move to CSM, accepting lower comp for a different work dynamic. The CSM-to-SE transition typically comes with a $20K to $40K pay increase; the SE-to-CSM transition usually involves a comp decrease unless you're moving into a senior CSM or CS leadership role.",
        ],
        "key_differences": [
            "Sales cycle position: SEs are pre-sale (evaluation and purchase). CSMs are post-sale (adoption, renewal, expansion).",
            "Revenue attribution: SEs are measured on new logo wins and pipeline influence. CSMs are measured on net retention rate, churn, and expansion revenue.",
            "Compensation structure: SEs have higher base and variable tied to new deals. CSMs have lower base and variable tied to retention and expansion metrics.",
            "Technical depth: SEs need to go deeper on product architecture and competitive positioning. CSMs need broader product knowledge focused on adoption and best practices.",
            "Career ceiling: SE path reaches $250K to $300K+ at Director level. CSM path reaches $180K to $230K at VP of CS level.",
        ],
        "faq": [
            ("Should I become a Solutions Engineer or Customer Success Manager?", "If you enjoy competitive selling, live demos, and influencing purchase decisions, choose SE. If you prefer building long-term customer relationships, driving adoption, and working on retention strategy, choose CSM. SEs earn more ($155K vs $115K median) but face more sales pressure."),
            ("Can a CSM transition to a Solutions Engineer role?", "Yes, and the product expertise transfers directly. You'll need to develop demo skills, competitive positioning knowledge, and comfort with the evaluation/POC process. Most CSM-to-SE transitions take 3 to 6 months of ramping. Expect a $20K to $40K pay increase."),
            ("Which role has better long-term earning potential?", "SE compensation ceiling is higher ($250K to $300K+ at Director/Principal level versus $180K to $230K for VP of CS). However, CS leadership roles are more plentiful because every SaaS company needs a CS function, while not all have large SE teams."),
        ],
    },
    "se-vs-product-manager": {
        "slug": "se-vs-product-manager",
        "role_a": "Solutions Engineer",
        "role_b": "Product Manager",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 100000, "max": 280000, "median": 160000},
        "context": [
            "Solutions Engineers and Product Managers operate in different parts of the organization but share a critical skill: the ability to translate between technical and business contexts. SEs translate product capabilities into customer value during the sales process. PMs translate customer needs into product requirements during the development process. The compensation is nearly identical ($155K versus $160K median), reflecting comparable skill requirements and organizational seniority.",
            "The SE-to-PM transition is one of the most well-trodden career paths in B2B SaaS. SEs accumulate deep knowledge of how customers use the product, what competitors do differently, and where the product falls short. That knowledge is exactly what PM teams need. The transition requires developing prioritization frameworks, roadmap communication skills, and the ability to influence engineering teams without authority. Most SE-to-PM transitions happen at the same company, where the SE's field knowledge is already known and valued.",
            "For people choosing between the two paths, the daily work is the differentiator. SEs spend their time on external-facing work: customer calls, demos, competitive evaluations, and deal strategy. PMs spend their time on internal-facing work: defining requirements, prioritizing backlogs, coordinating releases, and analyzing usage data. Both are cross-functional and require strong communication skills, but the audience is different. SEs face outward; PMs face inward.",
        ],
        "key_differences": [
            "Primary audience: SEs work with prospects and customers. PMs work with engineering, design, and internal stakeholders.",
            "Success metrics: SEs are measured on deal outcomes, win rate, and pipeline influence. PMs are measured on feature adoption, product metrics, and release velocity.",
            "Technical depth: SEs need enough technical knowledge to demo and discuss architecture. PMs need enough to write requirements and evaluate tradeoffs with engineering.",
            "Compensation: nearly identical. The $5K median gap is within normal data variance.",
            "Career path: SE leads to Principal/Director of SE. PM leads to Director/VP of Product. Both have $300K+ ceilings at the highest levels.",
        ],
        "faq": [
            ("Do Solutions Engineers or Product Managers earn more?", "Compensation is nearly identical: $155K SE median versus $160K PM median. The gap is not statistically significant. Comp at senior levels ($250K to $300K+) is comparable for both paths. Choose based on work preference, not comp."),
            ("How do Solutions Engineers transition to Product Management?", "Use your customer knowledge: SEs hear feature requests, competitive shortcomings, and use case requirements every day. Build a track record of providing product feedback that gets prioritized. Develop skills in requirement writing, data analysis, and prioritization frameworks. Most SE-to-PM transitions happen internally at the same company."),
            ("Which role has more job openings?", "Product Management has roughly 3x more open positions than Solutions Engineering at any given time. However, PM roles also attract significantly more applicants (200+ per role versus 30 to 50 for SE roles). The competition-per-opening is comparable for both roles."),
        ],
    },
    "se-vs-tam": {
        "slug": "se-vs-tam",
        "role_a": "Solutions Engineer",
        "role_b": "Technical Account Manager",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 100000, "max": 200000, "median": 135000},
        "context": [
            "Solutions Engineers and Technical Account Managers share technical skills but face opposite directions. SEs handle pre-sale technical evaluations for prospects who haven't bought yet. TAMs manage post-sale technical relationships with existing customers, ensuring they get value from the product and expand their usage. The $20K median gap ($155K versus $135K) reflects the revenue attribution difference: SEs influence new deal closure while TAMs influence retention and expansion.",
            "TAM roles are common at enterprise software companies where the product is technically complex and ongoing support requires deep product expertise. TAMs troubleshoot integrations, advise on best practices, coordinate with engineering on customer-specific issues, and identify expansion opportunities. The best TAMs are proactive rather than reactive: they spot risks before customers escalate and identify expansion signals before renewal conversations.",
            "The SE-to-TAM transition is common but usually involves a pay decrease. SEs who make this move typically do so because they prefer deeper, longer-term customer relationships over the deal-to-deal cycle of pre-sales. The TAM-to-SE transition offers a pay increase and is attractive to TAMs who want higher comp and enjoy competitive selling. Both transitions are smoothed by the shared technical foundation and customer-facing skills.",
        ],
        "key_differences": [
            "Sales cycle position: SEs are pre-sale (evaluation, POC, technical win). TAMs are post-sale (adoption, support, expansion).",
            "Customer relationship: SEs have short-term, deal-focused relationships (weeks to months). TAMs have long-term, ongoing relationships (years).",
            "Revenue attribution: SEs influence new logo revenue. TAMs influence net retention and expansion revenue.",
            "Technical scope: SEs need competitive positioning and evaluation expertise. TAMs need deep product troubleshooting and integration expertise.",
            "Compensation: SEs earn $20K more at median. TAM comp is more stable but has a lower ceiling.",
        ],
        "faq": [
            ("What's the difference between a Solutions Engineer and a Technical Account Manager?", "SEs handle pre-sale technical work: discovery, demos, POCs, and competitive evaluations. TAMs handle post-sale technical work: onboarding, integration support, issue resolution, and expansion guidance. SEs sell the product; TAMs ensure customers succeed with it."),
            ("Do Solutions Engineers or TAMs earn more?", "SEs earn more at every level. The median gap is $20K ($155K vs $135K). The career ceiling for SEs ($250K to $300K+ at Director) is also higher than the TAM ceiling ($180K to $220K at senior/principal TAM level)."),
            ("Can TAMs become Solutions Engineers?", "Yes, and the technical skills transfer directly. TAMs need to develop competitive positioning, demo delivery, and evaluation management skills. The customer empathy and product depth from the TAM role are genuine advantages in SE interviews. Most TAM-to-SE transitions come with a $15K to $25K pay increase."),
        ],
    },
    "se-vs-implementation-manager": {
        "slug": "se-vs-implementation-manager",
        "role_a": "Solutions Engineer",
        "role_b": "Implementation Manager",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 85000, "max": 160000, "median": 118000},
        "context": [
            "Solutions Engineers and Implementation Managers are the pre-sale and post-sale mirror images of each other. SEs convince prospects the product will work for their use case. Implementation Managers make it work after the deal closes. The $37K median gap ($155K versus $118K) is one of the largest in this comparison set and reflects the fundamental difference between revenue generation (SE) and service delivery (Implementation).",
            "Implementation Managers own the post-sale deployment: onboarding projects, data migration, integration configuration, user training, and time-to-value tracking. The work requires project management skills, technical understanding, and the ability to manage customer expectations when things don't go perfectly (which they never do). Many Implementation Managers come from consulting backgrounds, where the project-based work structure is similar.",
            "The SE and Implementation Manager roles share an important dynamic: what the SE promises during the sales cycle directly affects what the Implementation Manager has to deliver. In well-run organizations, SEs and Implementation Managers have regular syncs to ensure pre-sale commitments are realistic. In poorly-run organizations, Implementation Managers are left cleaning up over-promises, which creates friction and churn risk. If you're evaluating either role at a company, ask about the SE-to-Implementation handoff process. It tells you a lot about the organization's maturity.",
        ],
        "key_differences": [
            "Revenue attribution: SEs generate new revenue. Implementation is a cost center (professional services). This drives the comp gap.",
            "Day-to-day work: SEs do discovery, demos, and competitive evaluations. Implementation Managers run deployment projects, configure integrations, and manage timelines.",
            "Skill emphasis: SEs need selling and competitive positioning skills. Implementation Managers need project management, configuration, and stakeholder management skills.",
            "Customer relationship: SEs have pre-sale relationships (weeks to months). Implementation Managers have deployment-phase relationships (months), then hand off to CSM/TAM.",
            "Career ceiling: SE path reaches $250K to $300K+. Implementation path reaches $160K to $200K at Director of Professional Services level.",
        ],
        "faq": [
            ("Why do Solutions Engineers earn more than Implementation Managers?", "The $37K median gap reflects organizational economics. SEs are tied to revenue generation (new deals), which companies value at a premium. Implementation Managers operate in professional services, which is typically a cost center or break-even function. The closer you are to revenue creation, the more you earn."),
            ("Can Implementation Managers transition to SE roles?", "Yes, and the transition is smoother than many people expect. Implementation Managers already know the product deeply, understand customer workflows, and have experience managing technical stakeholders. The gaps are competitive positioning, demo delivery, and evaluation management. Most transitions happen within 6 to 9 months of focused development."),
            ("Which role has better work-life balance?", "Implementation Manager roles tend to have more predictable schedules since projects follow defined timelines. SE roles have more variability: end-of-quarter deal rushes, last-minute demo requests, and POC timelines driven by prospect schedules. Both roles involve customer-facing pressure, but the nature of that pressure differs."),
        ],
    },
    "se-vs-devrel": {
        "slug": "se-vs-devrel",
        "role_a": "Solutions Engineer",
        "role_b": "Developer Relations",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 110000, "max": 250000, "median": 150000},
        "context": [
            "Solutions Engineers and Developer Relations (DevRel) professionals both need deep technical knowledge and strong communication skills, but they apply them in very different ways. SEs use technical expertise in 1-to-1 deal settings: running demos, answering architecture questions, and guiding evaluations for specific prospects. DevRel uses technical expertise in 1-to-many settings: writing documentation, creating tutorials, speaking at conferences, and building developer communities. The $5K median gap ($155K versus $150K) reflects comparable skill requirements with different organizational functions.",
            "DevRel sits at the intersection of engineering, marketing, and product. DevRel professionals build sample applications, write technical blog posts, maintain SDKs, staff conference booths, and engage with developer communities on forums, Discord, and social media. The work is more creative and public-facing than SE work, with less direct revenue attribution. Companies with developer-facing products (APIs, platforms, infrastructure) invest heavily in DevRel because developer adoption drives revenue.",
            "The SE-to-DevRel transition is attractive to SEs who enjoy the technical content creation aspects of their role (building demos, writing technical documentation) and want to move away from direct deal involvement. DevRel roles offer more creative freedom and public visibility but less predictable compensation structures. The DevRel-to-SE transition is attractive to DevRel professionals who want higher, more direct compensation and enjoy the intensity of deal-level technical work.",
        ],
        "key_differences": [
            "Audience scale: SEs work 1-to-1 with prospects. DevRel works 1-to-many with developer communities.",
            "Revenue attribution: SEs have direct deal attribution. DevRel has indirect attribution (developer adoption, content engagement, community growth).",
            "Content creation: SEs build deal-specific demos. DevRel creates scalable content (docs, tutorials, videos, conference talks).",
            "Visibility: DevRel professionals build public personal brands. SEs work largely behind the scenes on individual deals.",
            "Travel: DevRel involves conference travel (20 to 40%). SE travel depends on the deal, ranging from 0% (remote) to 50% (enterprise field SE).",
        ],
        "faq": [
            ("What's the difference between a Solutions Engineer and Developer Relations?", "SEs do pre-sale technical work for specific deals: discovery, demos, POCs. DevRel does community-scale technical work: documentation, tutorials, conference talks, developer community engagement. SEs drive individual deal outcomes. DevRel drives developer adoption across the market."),
            ("Do SEs or DevRel earn more?", "Compensation is nearly identical. SE median is $155K; DevRel median is $150K. The gap is within normal variance. SE comp has more variable tied to deals. DevRel comp is typically 90 to 100% base salary with minimal variable."),
            ("Can a Solutions Engineer move into Developer Relations?", "Yes, and SEs bring strong product knowledge and customer empathy. You'll need to develop content creation skills (writing, video, public speaking) and community management abilities. Building a public presence (blog, social media, conference talks) before making the switch strengthens your candidacy."),
        ],
    },
    "se-vs-solutions-architect": {
        "slug": "se-vs-solutions-architect",
        "role_a": "Solutions Engineer",
        "role_b": "Solutions Architect",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 120000, "max": 280000, "median": 170000},
        "context": [
            "Solutions Engineer and Solutions Architect share similar titles and overlapping skills, but the roles differ in scope and technical depth. SEs run the full pre-sale technical process: discovery, demos, POCs, and deal support. Solutions Architects typically focus on the technical design aspect: integration architecture, deployment planning, and solution design for complex enterprise deals. SAs are often brought in for the most technically demanding deals, where the customer's environment requires custom architecture work.",
            "The $15K median gap ($155K versus $170K) reflects the deeper technical requirements for SA roles. Solutions Architects at enterprise software companies often have engineering backgrounds and can design complex multi-system architectures. They're the people who whiteboard integration diagrams, review API documentation with the customer's engineering team, and produce technical design documents that go into the customer's procurement package. SEs do some of this work, but SAs do it at a deeper and more specialized level.",
            "In some companies, SE and SA are the same role (just different titles). In others, SAs are a more senior technical role that SEs escalate to for complex deals. And in some organizations, SAs sit in professional services rather than sales, which changes the compensation structure and career path. When evaluating an SA opportunity, understand where it sits organizationally: a sales-aligned SA is compensated like an SE with a technical premium, while a services-aligned SA is compensated like a senior consultant.",
        ],
        "key_differences": [
            "Technical depth: SAs go deeper on integration architecture, deployment design, and technical specifications. SEs cover a broader range of pre-sale activities.",
            "Deal involvement: SEs manage the full pre-sale technical cycle. SAs are often brought in for specific technical deep-dives on the most complex deals.",
            "Organizational placement: SEs sit in sales. SAs may sit in sales, pre-sales, or professional services depending on the company.",
            "Compensation: SAs earn a $15K premium at median, reflecting the deeper technical requirements.",
            "Career path: SE leads to SE Manager/Director. SA leads to Principal SA, Chief Architect, or (less commonly) VP of Solutions.",
        ],
        "faq": [
            ("Is a Solutions Architect the same as a Solutions Engineer?", "It depends on the company. At some organizations, the titles are interchangeable. At others, SA is a more technically specialized role focused on architecture and design, while SE covers the full pre-sale technical cycle. Ask about the specific responsibilities when evaluating a role with either title."),
            ("Do Solutions Architects earn more than Solutions Engineers?", "On average, yes. The median SA salary ($170K) is $15K higher than the SE median ($155K), reflecting deeper technical requirements. At the senior and principal levels, SAs who can design complex enterprise architectures earn $200K to $280K."),
            ("Should I aim for a Solutions Architect role?", "If you enjoy technical design work (integration architecture, deployment planning, system design) more than the full pre-sale process (demos, competitive positioning, deal management), the SA path may be a better fit. SA roles are fewer in number but command premium comp."),
        ],
    },
    "se-vs-presales-consultant": {
        "slug": "se-vs-presales-consultant",
        "role_a": "Solutions Engineer",
        "role_b": "PreSales Consultant",
        "role_a_salary": {"min": 95000, "max": 300000, "median": 155000},
        "role_b_salary": {"min": 90000, "max": 260000, "median": 148000},
        "context": [
            "Solutions Engineer and PreSales Consultant are functionally the same role in most organizations. Like the SE/Sales Engineer distinction, the title difference is driven by company preference rather than job content. Both roles involve discovery, demos, POCs, competitive evaluations, and technical objection handling. The $7K median gap ($155K versus $148K) is within normal data variance and should not drive career decisions.",
            "The 'Consultant' title is more common in certain contexts. Companies that sell complex enterprise solutions (ERP, supply chain, healthcare IT) tend to use 'PreSales Consultant' or 'Solutions Consultant' because the role involves significant advisory work beyond product demonstration. These SEs spend as much time understanding the customer's business processes as they do showing the product. The consulting framing signals that the role is about solving business problems, not just running feature demos.",
            "For job seekers, always search for all variants of the title: Solutions Engineer, Sales Engineer, Solutions Consultant, PreSales Consultant, PreSales Engineer. The roles are interchangeable across the industry, and limiting your search to one title will cause you to miss relevant opportunities. When interviewing, the title matters far less than the actual deal dynamics, product complexity, and team structure.",
        ],
        "key_differences": [
            "Title convention: 'Consultant' is more common in enterprise/ERP/complex solution companies. 'Engineer' is more common in SaaS and cloud.",
            "Cultural signal: 'Consultant' emphasizes advisory and business process expertise. 'Engineer' emphasizes technical depth and product architecture.",
            "Industry prevalence: SAP, Oracle, ServiceNow, and similar enterprise vendors use 'Consultant.' Datadog, Snowflake, CrowdStrike use 'Engineer.'",
            "Compensation: no meaningful difference. The $7K median gap is within normal data variance.",
        ],
        "faq": [
            ("Is a PreSales Consultant the same as a Solutions Engineer?", "In most companies, yes. The titles describe the same pre-sales technical role with different naming conventions. 'Consultant' is more common at enterprise solution vendors; 'Engineer' is more common at SaaS and cloud companies. Responsibilities, compensation, and career paths are interchangeable."),
            ("Which title should I use on my resume?", "Use whichever title your employer uses. When job searching, search for all variants (Solutions Engineer, Sales Engineer, Solutions Consultant, PreSales Consultant, PreSales Engineer) to avoid missing relevant opportunities. Recruiters and hiring managers recognize all variants."),
            ("Does the Consultant title affect compensation?", "No. Our data shows a $7K median gap between the two titles, which is within normal variance and not statistically significant. Compensation is driven by seniority, location, company stage, and individual performance, not by title naming conventions."),
        ],
    },
}


# ---------------------------------------------------------------------------
# Salary page helpers
# ---------------------------------------------------------------------------

def salary_stats_html(data):
    """Generate 3-card stats grid for salary pages."""
    return f'''<div class="salary-stats">
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(data["min"])}&#8209;{fmt_salary(data["max"])}</span>
        <span class="stat-label">Salary Range</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(data["median"])}</span>
        <span class="stat-label">Median Salary</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{data["sample"]:,}</span>
        <span class="stat-label">Sample Size</span>
    </div>
</div>'''


def salary_range_bar_html(data):
    """Visual range bar showing min-max."""
    scale_min, scale_max = 50000, 350000
    left_pct = max(0, (data["min"] - scale_min) / (scale_max - scale_min) * 100)
    width_pct = max(5, (data["max"] - data["min"]) / (scale_max - scale_min) * 100)
    return f'''<div class="salary-range-bar">
    <div class="range-bar-labels">
        <span>{fmt_salary(data["min"])}</span>
        <span>Median: {fmt_salary(data["median"])}</span>
        <span>{fmt_salary(data["max"])}</span>
    </div>
    <div class="range-bar-track">
        <div class="range-bar-fill" style="left:{left_pct:.0f}%;width:{width_pct:.0f}%"></div>
    </div>
</div>'''


def calculator_cta_html():
    """Inline CTA linking to the salary calculator from salary detail pages."""
    return '''<div class="calculator-cta" style="background: var(--psp-accent-subtle); padding: var(--psp-space-6); border-radius: var(--psp-radius-lg); margin: var(--psp-space-8) 0; text-align: center;">
    <h3>Calculate Your Market Rate</h3>
    <p>See how your compensation compares to the market based on your seniority, location, and company stage.</p>
    <a href="/salary/calculator/" class="btn btn--primary">Calculate My Market Rate</a>
</div>'''


def salary_related_links(current_slug, current_type):
    """Generate related salary page links."""
    # Add calculator CTA above related links (skip on the calculator page itself)
    calc_cta = calculator_cta_html() if current_slug != "calculator" else ""

    links = []
    if current_slug != "index":
        links.append(("/salary/", "Salary Index"))
    if current_slug != "calculator":
        links.append(("/salary/calculator/", "Salary Calculator"))
    links.append(("/salary/methodology/", "Data Methodology"))

    if current_type != "seniority":
        for key in ["senior", "principal", "director"]:
            data = SALARY_BY_SENIORITY[key]
            links.append((f"/salary/by-seniority/{data['slug']}/", f"{data['label']} Salary"))
    if current_type != "location":
        for key in ["san-francisco", "new-york", "remote"]:
            data = SALARY_BY_LOCATION[key]
            links.append((f"/salary/by-location/{data['slug']}/", f"{data['label']} Salary"))
    if current_type != "stage":
        for key in ["growth", "enterprise"]:
            data = SALARY_BY_STAGE[key]
            links.append((f"/salary/by-company-stage/{data['slug']}/", f"{data['label']} Salary"))
    if current_type != "comparison":
        links.append(("/salary/comparisons/se-vs-ae/", "SE vs AE"))
        links.append(("/salary/comparisons/se-vs-solutions-architect/", "SE vs SA"))
    if current_type != "analysis":
        links.append(("/salary/compensation-structure/", "Comp Structure Analysis"))
        links.append(("/salary/se-to-ae-ratio/", "SE-to-AE Ratio Impact"))

    links = links[:8]
    items = ""
    for href, label in links:
        items += f'<a href="{href}" class="related-link-card">{label}</a>\n'

    return f'''{calc_cta}
<section class="related-links">
    <h2>Related Salary Data</h2>
    <div class="related-links-grid">
        {items}
    </div>
</section>'''


def salary_section_related_links(current_section):
    """Generate 'More Salary Data' related links for salary index/hub pages."""
    sections = [
        ("/salary/", "Salary Index"),
        ("/salary/by-seniority/", "By Seniority"),
        ("/salary/by-location/", "By Location"),
        ("/salary/by-company-stage/", "By Company Stage"),
        ("/salary/comparisons/", "Role Comparisons"),
        ("/salary/calculator/", "Salary Calculator"),
        ("/salary/compensation-structure/", "Comp Structure"),
        ("/salary/se-to-ae-ratio/", "SE-to-AE Ratio"),
        ("/salary/methodology/", "Methodology"),
    ]
    items = ""
    for href, label in sections:
        if href.strip("/").endswith(current_section.strip("/")):
            continue
        items += f'<a href="{href}" class="related-link-card">{label}</a>\n'
    return f'''<section class="related-links">
    <h2>More Salary Data</h2>
    <div class="related-links-grid">
        {items}
    </div>
</section>'''


# ---------------------------------------------------------------------------
# Page generators: Homepage
# ---------------------------------------------------------------------------

def build_homepage(market_data, comp_data):
    """Generate the homepage with Organization+WebSite schema."""
    title = "SE Salary Data, Tool Reviews, and Career Intel"
    description = (
        "SE salary data by seniority, location, and company stage. Independent tool reviews"
        " and career guides for Solutions Engineers. Updated weekly. Free."
    )

    body = '''<section class="hero">
    <div class="hero-inner">
        <h1>SE Salary Data, Tool Reviews, and Career Intel</h1>
        <p class="hero-subtitle">Salary data, tool reviews, career paths, and job market analysis for Solutions Engineers, Sales Engineers, and PreSales Consultants.</p>
        <div class="stat-grid">
            <div class="stat-block">
                <span class="stat-value">$155K</span>
                <span class="stat-label">Median SE Salary</span>
            </div>
            <div class="stat-block">
                <span class="stat-value">4,250+</span>
                <span class="stat-label">Jobs Tracked</span>
            </div>
            <div class="stat-block">
                <span class="stat-value">30</span>
                <span class="stat-label">Tools Reviewed</span>
            </div>
            <div class="stat-block">
                <span class="stat-value">15</span>
                <span class="stat-label">Cities Tracked</span>
            </div>
        </div>
        <p class="signup-proof">Join 500+ solutions engineers getting weekly data</p>
        <form class="hero-signup" onsubmit="return false;">
            <input type="email" placeholder="Your email" aria-label="Email address" required>
            <button type="submit" class="btn btn--primary">Get the Weekly Pulse</button>
        </form>
    </div>
</section>

<section class="logo-strip">
    <p class="logo-strip-label">Tracking hiring data from companies like</p>
    <div class="logo-strip-row">
        <img class="logo-icon" src="/assets/logos/companies/salesforce.png" alt="Salesforce" width="128" height="128">
        <img class="logo-icon" src="/assets/logos/companies/servicenow.png" alt="ServiceNow" width="128" height="128">
        <img class="logo-icon" src="/assets/logos/companies/datadog.png" alt="Datadog" width="128" height="128">
        <img class="logo-icon" src="/assets/logos/companies/snowflake.png" alt="Snowflake" width="128" height="128">
        <img class="logo-icon" src="/assets/logos/companies/crowdstrike.png" alt="CrowdStrike" width="128" height="128">
        <img class="logo-icon" src="/assets/logos/companies/paloalto.png" alt="Palo Alto Networks" width="128" height="128">
        <img class="logo-icon" src="/assets/logos/companies/mongodb.png" alt="MongoDB" width="128" height="128">
        <img class="logo-icon" src="/assets/logos/companies/databricks.png" alt="Databricks" width="128" height="128">
    </div>
</section>

<section class="section-previews">
    <h2 class="section-previews-heading">Explore SE Career Intelligence</h2>
    <div class="preview-grid">
        <a href="/salary/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128176;</span></div>
            <h3>Salary Data</h3>
            <p>Breakdowns by seniority, location, and company stage. 10 head-to-head role comparisons. Calculator, methodology, and comp structure analysis.</p>
            <span class="preview-link">Browse salary data &rarr;</span>
        </a>
        <a href="/tools/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128295;</span></div>
            <h3>Tool Reviews</h3>
            <p>Practitioner-tested reviews of Consensus, Navattic, Gong, and 27 more tools across 8 categories. Honest scores. No pay-to-play.</p>
            <span class="preview-link">Browse tools &rarr;</span>
        </a>
        <a href="/careers/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128200;</span></div>
            <h3>Career Guides</h3>
            <p>How to break in, level up, and negotiate. Interview prep, role comparisons, and transition playbooks for every SE career stage.</p>
            <span class="preview-link">Browse guides &rarr;</span>
        </a>
        <a href="/glossary/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128218;</span></div>
            <h3>SE Glossary</h3>
            <p>Clear definitions for 40+ pre-sales terms. POC, technical win, champion, discovery call, competitive battlecard, and more.</p>
            <span class="preview-link">Browse glossary &rarr;</span>
        </a>
        <a href="/insights/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128202;</span></div>
            <h3>Insights &amp; Analysis</h3>
            <p>Data-driven articles on SE hiring trends, tool adoption, salary shifts, and market analysis.</p>
            <span class="preview-link">Read insights &rarr;</span>
        </a>
        <a href="/newsletter/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128232;</span></div>
            <h3>Weekly Newsletter</h3>
            <p>Salary shifts, tool intel, and job market data for Solutions Engineers. Delivered every Wednesday.</p>
            <span class="preview-link">Get the weekly pulse &rarr;</span>
        </a>
    </div>
</section>

<section class="home-comparisons">
    <div class="home-comparisons-inner">
        <h2>How Does SE Pay Compare?</h2>
        <p class="section-subtitle">Side-by-side salary data against 10 adjacent roles.</p>
        <div class="comparison-grid">
            <a href="/salary/comparisons/se-vs-ae/" class="comparison-link"><span class="vs-badge">VS</span> Account Executive</a>
            <a href="/salary/comparisons/se-vs-gtm-engineer/" class="comparison-link"><span class="vs-badge">VS</span> GTM Engineer</a>
            <a href="/salary/comparisons/se-vs-sales-engineer/" class="comparison-link"><span class="vs-badge">VS</span> Sales Engineer</a>
            <a href="/salary/comparisons/se-vs-csm/" class="comparison-link"><span class="vs-badge">VS</span> CSM</a>
            <a href="/salary/comparisons/se-vs-product-manager/" class="comparison-link"><span class="vs-badge">VS</span> Product Manager</a>
            <a href="/salary/comparisons/se-vs-tam/" class="comparison-link"><span class="vs-badge">VS</span> TAM</a>
            <a href="/salary/comparisons/se-vs-implementation-manager/" class="comparison-link"><span class="vs-badge">VS</span> Implementation Mgr</a>
            <a href="/salary/comparisons/se-vs-devrel/" class="comparison-link"><span class="vs-badge">VS</span> Developer Relations</a>
            <a href="/salary/comparisons/se-vs-solutions-architect/" class="comparison-link"><span class="vs-badge">VS</span> Solutions Architect</a>
            <a href="/salary/comparisons/se-vs-presales-consultant/" class="comparison-link"><span class="vs-badge">VS</span> PreSales Consultant</a>
        </div>
    </div>
</section>

'''
    body += newsletter_cta_html()

    page = get_page_wrapper(
        title=title,
        description=description,
        canonical_path="/",
        body_content=body,
        active_path="/",
        extra_head=get_homepage_schema(),
        body_class="page-home",
    )
    write_page("index.html", page)
    register_og("index.html", title, "Salary data, tool reviews, and career intelligence for SEs")
    print("  Built: index.html")


# ---------------------------------------------------------------------------
# Core pages
# ---------------------------------------------------------------------------

def build_about():
    title = "About PreSales Pulse"
    description = (
        "PreSales Pulse is an independent career intelligence hub for Solutions Engineers."
        " Vendor-neutral salary data, tool reviews, and career guides. Built by Rome Thorndike."
    )
    crumbs = [("Home", "/"), ("About", None)]
    bc_html = breadcrumb_html(crumbs)

    body = f'''{bc_html}
<section class="page-header">
    <h1>About PreSales Pulse</h1>
</section>
<div class="container">
    <p>PreSales Pulse is an independent resource for Solutions Engineers, Sales Engineers, and PreSales Consultants. We track salary data, review tools, and analyze the job market so you don't have to piece it together from vendor marketing, Glassdoor fragments, and LinkedIn anecdotes.</p>
    <p>Every data point comes from real job postings and verified compensation data. We analyze 4,250+ SE job postings across 15 US markets, cross-referenced with survey data from working SE professionals. No vendor affiliations drive our rankings. No pay-to-play reviews.</p>
    <h2>Why PreSales Pulse Exists</h2>
    <p>Two things are true about the SE profession: it pays well and it's poorly documented. The only salary data available comes from two annual vendor-sponsored PDFs (Consensus and Reprise), both gated behind email forms and both produced by companies that sell to SEs. Independent tool reviews are almost nonexistent. Career path data is scattered across Slack threads and informal conversations.</p>
    <p>PreSales Pulse fixes that. We provide always-on, searchable <a href="/salary/">salary data</a> broken down by <a href="/salary/by-seniority/">seniority</a>, <a href="/salary/by-location/">location</a>, and <a href="/salary/by-company-stage/">company stage</a>. We publish honest <a href="/tools/">tool reviews</a> from a practitioner's perspective. And we maintain <a href="/careers/">career guides</a> based on data, not opinions.</p>
    <h2>What You'll Find Here</h2>
    <ul>
        <li><strong><a href="/salary/">Salary benchmarks</a></strong> broken down by seniority, location, company stage, and 10 head-to-head role comparisons</li>
        <li><strong><a href="/tools/">Tool reviews</a></strong> of 30 SE tools across 8 categories, with honest criticism and practitioner perspective</li>
        <li><strong><a href="/careers/">Career guides</a></strong> for breaking into SE, leveling up, negotiating comp, and transitioning between roles</li>
        <li><strong><a href="/glossary/">Glossary</a></strong> of 40+ pre-sales terms with clear, practitioner-written definitions</li>
        <li><strong><a href="/newsletter/">Weekly newsletter</a></strong> with salary shifts, tool intel, and job market data</li>
    </ul>
    <h2>Built By</h2>
    <p><strong>Rome Thorndike</strong> builds data products for B2B sales teams. PreSales Pulse is one of several career intelligence sites he maintains for technical go-to-market roles, including <a href="https://gtmepulse.com" target="_blank" rel="noopener">GTME Pulse</a> (for GTM Engineers) and <a href="https://thecspulse.com" target="_blank" rel="noopener">The CS Pulse</a> (for Customer Success professionals).</p>
</div>
'''
    page = get_page_wrapper(
        title=title, description=description, canonical_path="/about/",
        body_content=body, active_path="/about/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("about/index.html", page)
    register_og("about/index.html", title, "Independent career intelligence for Solutions Engineers")
    print("  Built: about/index.html")


def build_newsletter():
    title = "The PreSales Pulse Newsletter for SEs"
    description = (
        "Weekly Solutions Engineer salary shifts, tool intel, and job market data."
        " Free newsletter built from 4,250+ tracked SE job postings. Every Wednesday."
    )
    crumbs = [("Home", "/"), ("Newsletter", None)]
    bc_html = breadcrumb_html(crumbs)

    body = f'''{bc_html}
<div class="newsletter-page">
    <section class="page-header">
        <h1>Free Weekly SE Salary Data and Tool Intel</h1>
    </section>
    <p class="lead">Every Wednesday: salary shifts, tool intel, hiring trends, and job market data for Solutions Engineers. Built from 4,250+ tracked SE job postings.</p>
    <p class="signup-proof" style="font-size: 1.1rem; font-weight: 600; color: var(--psp-accent);">Join 500+ solutions engineers who read it every week</p>
    <form class="hero-signup" onsubmit="return false;">
        <input type="email" placeholder="Your email" aria-label="Email address" required>
        <button type="submit" class="btn btn--primary">Get the Weekly Pulse</button>
    </form>
    <p style="color: var(--psp-text-secondary); margin-top: var(--psp-space-2, 0.5rem);">Free. Weekly. Unsubscribe anytime.</p>

    <h2>What You'll Get Every Wednesday</h2>
    <ul class="newsletter-features">
        <li><strong>Salary movements:</strong> week-over-week changes in SE compensation across seniority levels, locations, and company stages. Example: "Senior SE median in SF climbed $3K this month."</li>
        <li><strong>Tool trends:</strong> which demo platforms, conversation intelligence tools, and SE software are showing up in job postings (and which are fading). Example: "Navattic mentions up 18% in Q1 job posts."</li>
        <li><strong>Hiring signals:</strong> which companies are scaling their SE teams and what that tells us about the market. Example: "Datadog added 12 SE openings in 2 weeks."</li>
        <li><strong>One career insight:</strong> a data-backed take on comp negotiation, career transitions, or market positioning for SEs.</li>
    </ul>

    <h2>Why Subscribe</h2>
    <p>SE salary data changes faster than annual reports can capture. New tools emerge monthly. Companies adjust comp bands quarterly. Our weekly data gives you current information for <a href="/salary/">salary negotiations</a>, <a href="/careers/">career decisions</a>, and understanding where the SE market is heading.</p>
    <p>We analyze 4,250+ SE job postings across <a href="/salary/by-location/">15 US markets</a> and track compensation data from verified SE professionals. That data feeds the newsletter every Wednesday morning.</p>

    <p style="text-align:center; margin: var(--psp-space-6, 1.5rem) 0;"><a href="/insights/" class="btn btn--ghost">See a recent issue &rarr;</a></p>

    <h2 style="text-align:center;">Get the data before your next 1:1</h2>
    <p class="signup-proof" style="text-align:center;">Join 500+ solutions engineers getting weekly data</p>
    <form class="hero-signup" onsubmit="return false;">
        <input type="email" placeholder="Your email" aria-label="Email address" required>
        <button type="submit" class="btn btn--primary">Get the Weekly Pulse</button>
    </form>
    <p style="color: var(--psp-text-secondary); text-align:center; margin-top: var(--psp-space-2, 0.5rem);">Free. Weekly. Unsubscribe anytime.</p>
</div>
'''
    page = get_page_wrapper(
        title=title, description=description, canonical_path="/newsletter/",
        body_content=body, active_path="/newsletter/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("newsletter/index.html", page)
    register_og("newsletter/index.html", title, "Weekly SE salary data and tool intel")
    print("  Built: newsletter/index.html")


def build_privacy():
    title = "Privacy Policy for PreSales Pulse"
    description = (
        "PreSales Pulse privacy policy: how we collect, use, and protect your data."
        " We collect minimal information and never sell it. Updated April 2026."
    )
    crumbs = [("Home", "/"), ("Privacy Policy", None)]
    bc_html = breadcrumb_html(crumbs)

    body = f'''{bc_html}
<section class="page-header">
    <h1>Privacy Policy for PreSales Pulse</h1>
</section>
<div class="legal-content">
    <p>Last updated: April 10, 2026</p>
    <h2>What We Collect</h2>
    <p>When you subscribe to our newsletter, we collect your email address. That's it. We don't track you across the web, sell your data, or build advertising profiles.</p>
    <h2>How We Use Your Email</h2>
    <p>Your email address is used to send you The PreSales Pulse newsletter. We may also send occasional product updates or announcements. Every email includes an unsubscribe link that works immediately.</p>
    <h2>Email Service Provider</h2>
    <p>We use <a href="https://resend.com" target="_blank" rel="noopener">Resend</a> to manage our email list and send newsletters. Your email address is stored in Resend's infrastructure. Resend's privacy policy governs their handling of your data.</p>
    <h2>Analytics</h2>
    <p>We use privacy-respecting analytics to understand which pages are visited and how people find the site. We don't use cookies for tracking, and we don't collect personally identifiable information through analytics.</p>
    <h2>Cookies</h2>
    <p>PreSales Pulse does not set tracking cookies. Our site functions without cookies. Third-party services (Google Fonts) may set their own cookies per their respective policies.</p>
    <h2>Data Retention</h2>
    <p>Email addresses are retained as long as you're subscribed. When you unsubscribe, your email is removed from our active list within 30 days. Backup copies may persist for up to 90 days.</p>
    <h2>Your Rights (GDPR)</h2>
    <p>You have the right to access, rectify, or delete your personal data. You can unsubscribe from our newsletter at any time using the link in any email. To request deletion of your data, email us at the address listed on the <a href="/about/">About</a> page and we'll process it within 30 days. EU residents have additional rights under GDPR including the right to data portability and the right to restrict processing.</p>
    <h2>Changes to This Policy</h2>
    <p>We'll update this page when our practices change. Material changes will be noted at the top of this page with the updated date.</p>
    <h2>Contact</h2>
    <p>Questions about this policy? Reach out to Rome Thorndike at the email address listed on the <a href="/about/">About</a> page.</p>
</div>
'''
    page = get_page_wrapper(
        title=title, description=description, canonical_path="/privacy/",
        body_content=body, active_path="/privacy/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("privacy/index.html", page)
    register_og("privacy/index.html", title)
    print("  Built: privacy/index.html")


def build_terms():
    title = "Terms of Service for PreSales Pulse"
    description = (
        "PreSales Pulse terms of service. Free salary data, tool reviews, and career"
        " guides for Solutions Engineers. Use the site and respect the content. April 2026."
    )
    crumbs = [("Home", "/"), ("Terms of Service", None)]
    bc_html = breadcrumb_html(crumbs)

    body = f'''{bc_html}
<section class="page-header">
    <h1>Terms of Service for PreSales Pulse</h1>
</section>
<div class="legal-content">
    <p>Last updated: April 10, 2026</p>
    <h2>Using This Site</h2>
    <p>PreSales Pulse provides salary data, tool reviews, and career resources for Solutions Engineers. The content is free to read and share with attribution. You agree to use the site lawfully and not to scrape, republish, or redistribute our content at scale without permission.</p>
    <h2>Content Accuracy</h2>
    <p>Our salary data comes from analysis of public job postings and voluntary survey data. While we work to be accurate, this data is for informational purposes only. It should not be your sole source for salary negotiations, hiring decisions, or compensation planning. Individual compensation depends on factors we can't capture in aggregate data.</p>
    <h2>Newsletter</h2>
    <p>Subscribing to The PreSales Pulse is free. We send one email per week plus occasional announcements. You can unsubscribe at any time. We will never sell your email address or share it with third parties for marketing purposes.</p>
    <h2>Affiliate Links</h2>
    <p>Some tool reviews contain affiliate links. When you purchase through these links, we may earn a commission at no additional cost to you. Affiliate relationships never influence our ratings or recommendations. We disclose affiliate relationships on relevant pages.</p>
    <h2>Intellectual Property</h2>
    <p>All original content on PreSales Pulse (text, data analysis, graphics, code) is owned by PreSales Pulse. You may quote short excerpts with attribution and a link back to the source page. Reproducing full articles or datasets requires written permission.</p>
    <h2>Limitation of Liability</h2>
    <p>PreSales Pulse provides information as-is. We're not liable for decisions you make based on our salary data, tool reviews, or career advice. Use your judgment and consult relevant professionals for significant career or financial decisions.</p>
    <h2>Changes</h2>
    <p>We may update these terms. Continued use of the site after changes constitutes acceptance. Material changes will be noted with an updated date at the top of this page.</p>
    <h2>Contact</h2>
    <p>Questions about these terms? Reach out via the <a href="/about/">About</a> page.</p>
</div>
'''
    page = get_page_wrapper(
        title=title, description=description, canonical_path="/terms/",
        body_content=body, active_path="/terms/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("terms/index.html", page)
    register_og("terms/index.html", title)
    print("  Built: terms/index.html")


def build_404():
    title = "Page Not Found (404) on PreSales Pulse"
    description = (
        "The page you're looking for doesn't exist on PreSales Pulse. Browse SE"
        " salary data, tool reviews, and career guides, or head back to the homepage."
    )
    body = '''<div class="error-page">
    <div class="error-code">404</div>
    <h1>Page Not Found</h1>
    <p>The page you're looking for doesn't exist or has been moved. Try one of these instead:</p>
    <div style="display:flex;flex-direction:column;gap:0.75rem;align-items:center;">
        <a href="/" class="btn btn--primary">Back to Homepage</a>
        <a href="/salary/" class="btn btn--ghost">Browse Salary Data</a>
        <a href="/tools/" class="btn btn--ghost">Browse Tool Reviews</a>
        <a href="/newsletter/" class="btn btn--ghost">Get the Newsletter</a>
    </div>
</div>
'''
    page = get_page_wrapper(
        title=title, description=description, canonical_path="/404.html",
        body_content=body, body_class="page-inner",
        robots="noindex, nofollow",
    )
    # Write file directly instead of write_page() to avoid sitemap registration
    full_path = os.path.join(OUTPUT_DIR, "404.html")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(page)
    print("  Built: 404.html (noindex, excluded from sitemap)")


# ---------------------------------------------------------------------------
# Salary Index
# ---------------------------------------------------------------------------

def build_salary_index(comp_data):
    title = "SE Salary Data: Full Breakdown by Level and City"
    description = (
        "Solutions Engineer salary data: breakdowns by seniority, location, and company"
        " stage. 10 role comparisons. Calculator and methodology. 327 sample size."
    )
    crumbs = [("Home", "/"), ("Salary Data", None)]
    bc_html = breadcrumb_html(crumbs)

    seniority_cards = ""
    for key, data in SALARY_BY_SENIORITY.items():
        seniority_cards += f'''<a href="/salary/by-seniority/{data["slug"]}/" class="salary-index-card">
    <h3>{data["label"]}</h3>
    <div class="card-range">{fmt_salary(data["min"])}&#8209;{fmt_salary(data["max"])}</div>
    <p>Median: {fmt_salary(data["median"])} | {data["sample"]} respondents</p>
</a>\n'''

    location_cards = ""
    for key in ["san-francisco", "new-york", "seattle", "austin", "remote"]:
        data = SALARY_BY_LOCATION[key]
        location_cards += f'''<a href="/salary/by-location/{data["slug"]}/" class="salary-index-card">
    <h3>{data["label"]}</h3>
    <div class="card-range">{fmt_salary(data["min"])}&#8209;{fmt_salary(data["max"])}</div>
    <p>Median: {fmt_salary(data["median"])} | {data["sample"]} respondents</p>
</a>\n'''

    stage_cards = ""
    for key, data in SALARY_BY_STAGE.items():
        stage_cards += f'''<a href="/salary/by-company-stage/{data["slug"]}/" class="salary-index-card">
    <h3>{data["label"]}</h3>
    <div class="card-range">{fmt_salary(data["min"])}&#8209;{fmt_salary(data["max"])}</div>
    <p>Median: {fmt_salary(data["median"])}</p>
</a>\n'''

    vs_links = ""
    for key, data in SALARY_COMPARISONS.items():
        vs_links += f'<a href="/salary/comparisons/{data["slug"]}/" class="comparison-link"><span class="vs-badge">VS</span> {data["role_b"]}</a>\n'

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>Solutions Engineer Salary Data (2026)</h1>
        <p>Compensation data from 4,250+ job postings and 327 verified SE professionals across 15 US markets. Breakdowns by seniority, location, company stage, and 10 head-to-head role comparisons.</p>
    </div>
</section>

{salary_stats_html({"min": 95000, "max": 300000, "median": 155000, "sample": 327})}

<div class="salary-content">
    <h2>By Seniority</h2>
    <div class="salary-index-grid">{seniority_cards}</div>
    <p style="margin-top:var(--psp-space-4, 1rem)"><a href="/salary/by-seniority/">View all seniority levels &rarr;</a></p>

    <h2>By Location</h2>
    <div class="salary-index-grid">{location_cards}</div>
    <p style="margin-top:var(--psp-space-4, 1rem)"><a href="/salary/by-location/">View all 15 locations &rarr;</a></p>

    <h2>By Company Stage</h2>
    <div class="salary-index-grid">{stage_cards}</div>
    <p style="margin-top:var(--psp-space-4, 1rem)"><a href="/salary/by-company-stage/">View all company stages &rarr;</a></p>

    <h2>Role Comparisons</h2>
    <p>How Solutions Engineer compensation stacks up against 10 adjacent roles.</p>
    <div class="comparison-grid" style="margin-top:var(--psp-space-4, 1rem)">{vs_links}</div>

    <h2>Salary Calculator</h2>
    <p>Get a personalized salary estimate based on your seniority, location, and company stage.</p>
    <a href="/salary/calculator/" class="btn btn--primary" style="margin-top:var(--psp-space-3, 0.75rem)">Calculate My Market Rate</a>

    <h2>More Salary Analysis</h2>
    <div class="salary-index-grid">
        <a href="/salary/compensation-structure/" class="salary-index-card">
            <h3>Comp Structure</h3>
            <div class="card-range">Base/Variable/Equity</div>
            <p>How SE comp splits change by level</p>
        </a>
        <a href="/salary/se-to-ae-ratio/" class="salary-index-card">
            <h3>SE-to-AE Ratio</h3>
            <div class="card-range">1:2 to 1:4</div>
            <p>How ratio affects workload and pay</p>
        </a>
    </div>

    <h2>How We Collect This Data</h2>
    <p>Salary figures are sourced from analysis of 4,250+ SE job postings across 15 US markets, cross-referenced with compensation survey data from 327 verified SE professionals. We normalize titles (Solutions Engineer, Sales Engineer, Solutions Consultant, PreSales Engineer) and segment by seniority, location, and company stage. <a href="/salary/methodology/">Read our full methodology</a>.</p>
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get weekly salary data updates.")

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/",
        body_content=body, active_path="/salary/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("salary/index.html", page)
    register_og("salary/index.html", "SE Salary Data", "Full breakdown by level, city, and stage")
    print("  Built: salary/index.html")


# ---------------------------------------------------------------------------
# Salary: By Seniority
# ---------------------------------------------------------------------------

def build_salary_seniority_pages(comp_data):
    # Index page
    title = "SE Salary by Seniority Level (2026 Data)"
    description = (
        "Solutions Engineer salary breakdowns by seniority: Junior SE through Director."
        " Median, range, and sample size for each level. Updated weekly."
    )
    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Seniority", None)]
    bc_html = breadcrumb_html(crumbs)

    cards = ""
    for key, data in SALARY_BY_SENIORITY.items():
        cards += f'''<a href="/salary/by-seniority/{data["slug"]}/" class="salary-index-card">
    <h3>{data["label"]}</h3>
    <div class="card-range">{fmt_salary(data["min"])}&#8209;{fmt_salary(data["max"])}</div>
    <p>Median: {fmt_salary(data["median"])} | {data["sample"]} respondents</p>
</a>\n'''

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>SE Salary by Seniority Level (2026)</h1>
        <p>Solutions Engineer compensation data broken down by career level, from Junior SE ($115K median) through Director of SE ($255K median).</p>
    </div>
</section>
<div class="salary-content">
    <div class="salary-index-grid">{cards}</div>
    <p>Compensation increases significantly with seniority. The gap between Junior SE ($115K median) and Director of SE ($255K median) represents a $140K difference driven by deal complexity, team leadership, and organizational scope. For context on how these levels compare to other roles, see our <a href="/salary/comparisons/">role comparisons</a>.</p>
    {salary_section_related_links("by-seniority")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get weekly SE salary updates by level.")

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/by-seniority/",
        body_content=body, active_path="/salary/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("salary/by-seniority/index.html", page)
    register_og("salary/by-seniority/index.html", title, "Junior SE through Director salary data")
    print("  Built: salary/by-seniority/index.html")

    # Individual seniority pages
    for key, data in SALARY_BY_SENIORITY.items():
        _build_seniority_page(key, data)


def _build_seniority_page(key, data):
    slug = data["slug"]
    label = data["label"]

    title = f"{label} Salary Data and Comp Breakdown (2026)"
    full_title = f"{title} - {SITE_NAME}"
    if len(full_title) > 65:
        title = f"{label} Salary (2026)"

    description = (
        f"{label} salary: {fmt_salary(data['min'])} to {fmt_salary(data['max'])} range"
        f" with {fmt_salary(data['median'])} median. Comp drivers, total comp, and FAQ."
    )
    description = pad_description(description)

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Seniority", "/salary/by-seniority/"), (label, None)]
    bc_html = breadcrumb_html(crumbs)

    context_html = "".join(f"    <p>{p}</p>\n" for p in data["context"])
    drivers_html = "".join(f"        <li>{d}</li>\n" for d in data["drivers"])

    faq_pairs = [
        (f"What is the average {label} salary in 2026?",
         f"The median {label} salary is {fmt_salary(data['median'])}, based on analysis of 4,250+ SE job postings and 327 survey respondents. The full range spans {fmt_salary(data['min'])} to {fmt_salary(data['max'])}."),
        (f"What skills increase {label} pay?",
         f"Technical depth (product architecture, integration design, competitive positioning) and vertical specialization (healthcare, financial services, government) drive the highest premiums at the {label} level. SEs who demonstrate measurable deal impact earn at the top of the range."),
        (f"How does {label} SE comp compare to other roles?",
         f"At the {label} level, SE compensation ({fmt_salary(data['median'])} median) is competitive with Product Managers ($160K), higher than CSMs ($115K), and comparable to Solutions Architects ($170K). See our role comparisons for detailed breakdowns."),
    ]

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>{label} Salary Data (2026)</h1>
        <p>Compensation data for {label}s from 4,250+ job postings and {data["sample"]} survey respondents.</p>
    </div>
</section>
{salary_stats_html(data)}
{salary_range_bar_html(data)}
<div class="salary-content">
    <h2>Market Context</h2>
{context_html}
    <h2>What Drives {label} Compensation</h2>
    <ul>
{drivers_html}    </ul>
    <h2>Total Compensation</h2>
    <p>{data["total_comp"]}</p>

{faq_html(faq_pairs)}
{salary_related_links(slug, "seniority")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html(f"Get weekly {label} salary updates.")
    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title, description=description, canonical_path=f"/salary/by-seniority/{slug}/",
        body_content=body, active_path="/salary/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page(f"salary/by-seniority/{slug}/index.html", page)
    register_og(f"salary/by-seniority/{slug}/index.html", f"{label} Salary", f"Median: {fmt_salary(data['median'])}")
    print(f"  Built: salary/by-seniority/{slug}/index.html")


# ---------------------------------------------------------------------------
# Salary: By Location
# ---------------------------------------------------------------------------

def build_salary_location_pages(comp_data):
    # Index page
    title = "SE Salary by Location: 15 US Markets (2026)"
    description = (
        "Solutions Engineer salary data for 15 US cities and remote roles."
        " SF, NYC, Seattle, Austin, Boston, and more. Cost of living comparisons."
    )
    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Location", None)]
    bc_html = breadcrumb_html(crumbs)

    cards = ""
    for key, data in SALARY_BY_LOCATION.items():
        cards += f'''<a href="/salary/by-location/{data["slug"]}/" class="salary-index-card">
    <h3>{data["label"]}</h3>
    <div class="card-range">{fmt_salary(data["min"])}&#8209;{fmt_salary(data["max"])}</div>
    <p>Median: {fmt_salary(data["median"])} | {data["sample"]} respondents</p>
</a>\n'''

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>SE Salary by Location (2026)</h1>
        <p>Solutions Engineer compensation data across 15 US cities and remote roles. San Francisco leads at $195K median, with remote roles at $168K.</p>
    </div>
</section>
<div class="salary-content">
    <div class="salary-index-grid">{cards}</div>
    <p>Geography remains a significant factor in SE compensation. The gap between San Francisco ($195K median) and Atlanta ($162K median) represents a $33K difference, which narrows considerably when you account for cost of living and state income tax differences. For more on how compensation varies by career level, see our <a href="/salary/by-seniority/">seniority breakdown</a>.</p>
    {salary_section_related_links("by-location")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get weekly SE salary data by city.")

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/by-location/",
        body_content=body, active_path="/salary/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("salary/by-location/index.html", page)
    register_og("salary/by-location/index.html", title, "15 US cities + remote salary data")
    print("  Built: salary/by-location/index.html")

    # Individual location pages
    for key, data in SALARY_BY_LOCATION.items():
        _build_location_page(key, data)


def _build_location_page(key, data):
    slug = data["slug"]
    label = data["label"]

    title = f"SE Salary in {label} (2026 Breakdown)"
    full_title = f"{title} - {SITE_NAME}"
    if len(full_title) > 65:
        title = f"SE Salary in {label} (2026)"
    if len(f"{title} - {SITE_NAME}") > 65:
        title = f"SE Pay in {label} (2026)"

    description = (
        f"Solutions Engineer salary in {label}: {fmt_salary(data['min'])} to"
        f" {fmt_salary(data['max'])} range, {fmt_salary(data['median'])} median."
        f" Cost of living, comp drivers, FAQ."
    )
    description = pad_description(description)

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Location", "/salary/by-location/"), (label, None)]
    bc_html = breadcrumb_html(crumbs)

    context_html = "".join(f"    <p>{p}</p>\n" for p in data["context"])
    drivers_html = "".join(f"        <li>{d}</li>\n" for d in data["drivers"])

    faq_pairs = [
        (f"What is the average SE salary in {label}?",
         f"The median Solutions Engineer salary in {label} is {fmt_salary(data['median'])}. The full range spans {fmt_salary(data['min'])} to {fmt_salary(data['max'])} based on analysis of 4,250+ job postings."),
        (f"How does {label} SE pay compare to other cities?",
         f"The {label} median of {fmt_salary(data['median'])} compares to the San Francisco median of $195K and the national remote median of $168K. Cost of living and state income tax differences should factor into your comparison."),
        (f"Is {label} a good market for Solutions Engineers?",
         f"{data['context'][0][:250]}"),
    ]

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>Solutions Engineer Salary in {label} (2026)</h1>
        <p>Compensation data for Solutions Engineers in {label}, from 4,250+ job postings and {data["sample"]} survey respondents.</p>
    </div>
</section>
{salary_stats_html(data)}
{salary_range_bar_html(data)}
<div class="salary-content">
    <h2>Market Context</h2>
{context_html}
    <h2>What Drives SE Pay in {label}</h2>
    <ul>
{drivers_html}    </ul>
    <h2>Cost of Living</h2>
    <p>{data["cost_of_living"]}</p>

{faq_html(faq_pairs)}
{salary_related_links(slug, "location")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html(f"Get weekly SE salary data for {label}.")
    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title, description=description, canonical_path=f"/salary/by-location/{slug}/",
        body_content=body, active_path="/salary/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page(f"salary/by-location/{slug}/index.html", page)
    register_og(f"salary/by-location/{slug}/index.html", f"SE Salary: {label}", f"Median: {fmt_salary(data['median'])}")
    print(f"  Built: salary/by-location/{slug}/index.html")


# ---------------------------------------------------------------------------
# Salary: By Company Stage
# ---------------------------------------------------------------------------

def build_salary_stage_pages(comp_data):
    # Index page
    title = "SE Salary by Company Stage (2026 Data)"
    description = (
        "Solutions Engineer salary data by company stage: Seed through Enterprise."
        " Base salary, equity notes, and comp drivers for each funding round."
    )
    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Company Stage", None)]
    bc_html = breadcrumb_html(crumbs)

    cards = ""
    for key, data in SALARY_BY_STAGE.items():
        cards += f'''<a href="/salary/by-company-stage/{data["slug"]}/" class="salary-index-card">
    <h3>{data["label"]}</h3>
    <div class="card-range">{fmt_salary(data["min"])}&#8209;{fmt_salary(data["max"])}</div>
    <p>Median: {fmt_salary(data["median"])} | {data["sample"]} respondents</p>
</a>\n'''

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>SE Salary by Company Stage (2026)</h1>
        <p>How Solutions Engineer compensation changes across company stages, from Seed ($125K median) through Enterprise ($195K median). Includes equity and total comp analysis.</p>
    </div>
</section>
<div class="salary-content">
    <div class="salary-index-grid">{cards}</div>
    <p>Company stage is one of the strongest predictors of SE compensation. The $70K gap between Seed stage ($125K median) and Enterprise ($195K median) reflects the trade-off between cash comp and equity upside that SEs navigate at every career stage. For context on how seniority affects comp at each stage, see our <a href="/salary/by-seniority/">seniority breakdown</a>.</p>
    {salary_section_related_links("by-company-stage")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get weekly SE salary data by company stage.")

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/by-company-stage/",
        body_content=body, active_path="/salary/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("salary/by-company-stage/index.html", page)
    register_og("salary/by-company-stage/index.html", title, "Seed through Enterprise salary data")
    print("  Built: salary/by-company-stage/index.html")

    # Individual stage pages
    for key, data in SALARY_BY_STAGE.items():
        _build_stage_page(key, data)


def _build_stage_page(key, data):
    slug = data["slug"]
    label = data["label"]

    title = f"SE Salary at {label} Companies (2026)"
    full_title = f"{title} - {SITE_NAME}"
    if len(full_title) > 65:
        title = f"SE Pay at {label} (2026)"

    description = (
        f"Solutions Engineer salary at {label} companies: {fmt_salary(data['min'])} to"
        f" {fmt_salary(data['max'])} range, {fmt_salary(data['median'])} median."
        f" Equity notes and comp drivers."
    )
    description = pad_description(description)

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Company Stage", "/salary/by-company-stage/"), (label, None)]
    bc_html = breadcrumb_html(crumbs)

    context_html = "".join(f"    <p>{p}</p>\n" for p in data["context"])
    drivers_html = "".join(f"        <li>{d}</li>\n" for d in data["drivers"])

    faq_pairs = [
        (f"What do SEs earn at {label} companies?",
         f"The median Solutions Engineer salary at {label} companies is {fmt_salary(data['median'])}. The full range spans {fmt_salary(data['min'])} to {fmt_salary(data['max'])} based on {data['sample']} survey respondents."),
        (f"How much equity do SEs get at {label}?",
         f"{data['equity_note'][:300]}"),
        (f"Should I join a {label} company as an SE?",
         f"The decision depends on your risk tolerance, career goals, and financial situation. {label} companies offer {fmt_salary(data['median'])} median base salary with varying equity upside. Cash comp is lower than later stages, but equity potential can be significant if the company succeeds."),
    ]

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>SE Salary at {label} Companies (2026)</h1>
        <p>Compensation data for Solutions Engineers at {label} companies, from 4,250+ job postings and {data["sample"]} survey respondents.</p>
    </div>
</section>
{salary_stats_html(data)}
{salary_range_bar_html(data)}
<div class="salary-content">
    <h2>Market Context</h2>
{context_html}
    <h2>Comp Drivers at {label}</h2>
    <ul>
{drivers_html}    </ul>
    <h2>Equity at {label}</h2>
    <p>{data["equity_note"]}</p>

{faq_html(faq_pairs)}
{salary_related_links(slug, "stage")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html(f"Get weekly SE salary data for {label} companies.")
    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title, description=description, canonical_path=f"/salary/by-company-stage/{slug}/",
        body_content=body, active_path="/salary/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page(f"salary/by-company-stage/{slug}/index.html", page)
    register_og(f"salary/by-company-stage/{slug}/index.html", f"SE Salary: {label}", f"Median: {fmt_salary(data['median'])}")
    print(f"  Built: salary/by-company-stage/{slug}/index.html")


# ---------------------------------------------------------------------------
# Salary: Comparisons (SE vs X)
# ---------------------------------------------------------------------------

def build_salary_comparison_pages():
    # Index page
    title = "SE Salary Comparisons: 10 Role Matchups"
    description = (
        "Solutions Engineer salary compared to AE, GTM Engineer, CSM, Product Manager,"
        " TAM, and 5 more roles. Head-to-head compensation data. Updated 2026."
    )
    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("Comparisons", None)]
    bc_html = breadcrumb_html(crumbs)

    cards = ""
    for key, data in SALARY_COMPARISONS.items():
        cards += f'''<a href="/salary/comparisons/{data["slug"]}/" class="salary-index-card">
    <h3>SE vs {data["role_b"]}</h3>
    <div class="card-range">{fmt_salary(data["role_a_salary"]["median"])} vs {fmt_salary(data["role_b_salary"]["median"])}</div>
    <p>Head-to-head compensation analysis</p>
</a>\n'''

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>SE Salary Comparisons (2026)</h1>
        <p>How Solutions Engineer compensation stacks up against 10 adjacent roles. Side-by-side salary data with context on responsibilities, career paths, and key differences.</p>
    </div>
</section>
<div class="salary-content">
    <div class="salary-index-grid">{cards}</div>
    <p>These comparisons cover the roles most commonly adjacent to Solutions Engineering in B2B SaaS organizations. Each comparison includes salary data, daily work differences, and career crossover analysis. For SE salary breakdowns by level, see our <a href="/salary/by-seniority/">seniority data</a>.</p>
    {salary_section_related_links("comparisons")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get weekly SE salary comparisons.")

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/comparisons/",
        body_content=body, active_path="/salary/",
        extra_head=get_breadcrumb_schema(crumbs), body_class="page-inner",
    )
    write_page("salary/comparisons/index.html", page)
    register_og("salary/comparisons/index.html", title, "10 head-to-head role comparisons")
    print("  Built: salary/comparisons/index.html")

    # Individual comparison pages
    for key, data in SALARY_COMPARISONS.items():
        _build_comparison_page(key, data)


def _build_comparison_page(key, data):
    slug = data["slug"]
    role_b = data["role_b"]
    role_a_sal = data["role_a_salary"]
    role_b_sal = data["role_b_salary"]

    title = f"SE vs {role_b} Salary Comparison (2026)"
    full_title = f"{title} - {SITE_NAME}"
    if len(full_title) > 65:
        title = f"SE vs {role_b} Salary (2026)"
    if len(f"{title} - {SITE_NAME}") > 65:
        title = f"SE vs {role_b} Pay (2026)"

    description = (
        f"Solutions Engineer ({fmt_salary(role_a_sal['median'])}) vs {role_b}"
        f" ({fmt_salary(role_b_sal['median'])}): salary data, key differences,"
        f" career crossover analysis, and FAQ."
    )
    description = pad_description(description)

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("Comparisons", "/salary/comparisons/"), (f"SE vs {role_b}", None)]
    bc_html = breadcrumb_html(crumbs)

    context_html = "".join(f"    <p>{p}</p>\n" for p in data["context"])
    diff_html = "".join(f"        <li>{d}</li>\n" for d in data["key_differences"])
    faq_pairs = data["faq"]

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY COMPARISON</div>
        <h1>Solutions Engineer vs {role_b}: Salary Comparison</h1>
        <p>Head-to-head compensation data comparing Solutions Engineers to {role_b}s. Salary ranges, key differences, and career crossover analysis.</p>
    </div>
</section>

<div class="comparison-stats">
    <div class="comparison-column">
        <h3>Solutions Engineer</h3>
        <div class="salary-stat-card">
            <span class="stat-value">{fmt_salary(role_a_sal["median"])}</span>
            <span class="stat-label">Median Salary</span>
        </div>
        <p class="stat-range">{fmt_salary(role_a_sal["min"])}&#8209;{fmt_salary(role_a_sal["max"])}</p>
    </div>
    <div class="comparison-vs">VS</div>
    <div class="comparison-column">
        <h3>{role_b}</h3>
        <div class="salary-stat-card">
            <span class="stat-value">{fmt_salary(role_b_sal["median"])}</span>
            <span class="stat-label">Median Salary</span>
        </div>
        <p class="stat-range">{fmt_salary(role_b_sal["min"])}&#8209;{fmt_salary(role_b_sal["max"])}</p>
    </div>
</div>

<div class="salary-content">
    <h2>Context</h2>
{context_html}
    <h2>Key Differences</h2>
    <ul>
{diff_html}    </ul>

{faq_html(faq_pairs)}
{salary_related_links(slug, "comparison")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get weekly SE salary comparison data.")
    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title, description=description, canonical_path=f"/salary/comparisons/{slug}/",
        body_content=body, active_path="/salary/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page(f"salary/comparisons/{slug}/index.html", page)
    register_og(f"salary/comparisons/{slug}/index.html", f"SE vs {role_b}", f"{fmt_salary(role_a_sal['median'])} vs {fmt_salary(role_b_sal['median'])}")
    print(f"  Built: salary/comparisons/{slug}/index.html")


# ---------------------------------------------------------------------------
# Salary: Calculator
# ---------------------------------------------------------------------------

def build_salary_calculator():
    title = "SE Salary Calculator: Your Market Rate"
    description = (
        "Calculate your Solutions Engineer market rate based on seniority, location,"
        " and company stage. Free estimates, full results via email. Data from 327 SEs."
    )
    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("Calculator", None)]
    bc_html = breadcrumb_html(crumbs)

    seniority_options = ""
    for key, data in SALARY_BY_SENIORITY.items():
        seniority_options += f'<option value="{key}">{data["label"]}</option>\n'

    location_options = ""
    for key, data in SALARY_BY_LOCATION.items():
        location_options += f'<option value="{key}">{data["label"]}</option>\n'

    stage_options = ""
    for key, data in SALARY_BY_STAGE.items():
        stage_options += f'<option value="{key}">{data["label"]}</option>\n'

    faq_pairs = [
        ("How accurate is this salary calculator?", "The calculator uses data from 4,250+ SE job postings and 327 survey respondents to estimate your market rate. Individual compensation varies based on factors we can't capture (negotiation skill, company budget, specific product complexity). Use this as a starting point, not a definitive answer."),
        ("What data sources does this calculator use?", "We combine public job posting salary data with voluntary compensation survey responses from verified SE professionals across 15 US markets. The data is segmented by seniority level, geographic location, and company stage."),
        ("How often is the calculator data updated?", "The underlying data is refreshed weekly as we process new job postings and survey responses. The calculator reflects the most recent available data at any given time."),
    ]

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>Solutions Engineer Salary Calculator</h1>
        <p>Get your personalized SE market rate based on seniority, location, and company stage. Estimates based on 4,250+ job postings and 327 survey respondents.</p>
    </div>
</section>

<div class="calculator-container">
    <div class="calculator-form">
        <div class="form-group">
            <label for="calc-seniority">Seniority Level</label>
            <select id="calc-seniority">
                <option value="">Select your level</option>
                {seniority_options}
            </select>
        </div>
        <div class="form-group">
            <label for="calc-location">Location</label>
            <select id="calc-location">
                <option value="">Select your location</option>
                {location_options}
            </select>
        </div>
        <div class="form-group">
            <label for="calc-stage">Company Stage</label>
            <select id="calc-stage">
                <option value="">Select company stage</option>
                {stage_options}
            </select>
        </div>
        <button type="button" class="btn btn--primary" id="calc-btn" onclick="calculateSalary()">Calculate My Market Rate</button>
    </div>

    <div class="calculator-results" id="calc-results" style="display:none;">
        <h2>Your Estimated Market Rate</h2>
        <div class="salary-stats">
            <div class="salary-stat-card">
                <span class="stat-value" id="calc-range"></span>
                <span class="stat-label">Estimated Range</span>
            </div>
            <div class="salary-stat-card">
                <span class="stat-value" id="calc-median"></span>
                <span class="stat-label">Estimated Median</span>
            </div>
        </div>
        <p id="calc-context"></p>
        <div class="calculator-gate">
            <p><strong>Want the full breakdown?</strong> Subscribe to The PreSales Pulse for detailed comp analysis by level, city, and company stage.</p>
            <form class="newsletter-cta-form" onsubmit="return false;">
                <input type="email" placeholder="Your email" aria-label="Email address" required>
                <button type="submit" class="btn btn--primary">Get Full Report</button>
            </form>
        </div>
    </div>
</div>

<script>
var SALARY_DATA = {json.dumps({
    "seniority": {k: {"min": v["min"], "max": v["max"], "median": v["median"]} for k, v in SALARY_BY_SENIORITY.items()},
    "location": {k: {"min": v["min"], "max": v["max"], "median": v["median"]} for k, v in SALARY_BY_LOCATION.items()},
    "stage": {k: {"min": v["min"], "max": v["max"], "median": v["median"]} for k, v in SALARY_BY_STAGE.items()},
})};
function calculateSalary() {{
    var sen = document.getElementById('calc-seniority').value;
    var loc = document.getElementById('calc-location').value;
    var stg = document.getElementById('calc-stage').value;
    if (!sen || !loc || !stg) {{ alert('Please select all three fields.'); return; }}
    var s = SALARY_DATA.seniority[sen];
    var l = SALARY_DATA.location[loc];
    var g = SALARY_DATA.stage[stg];
    var avgMin = Math.round((s.min + l.min + g.min) / 3 / 1000) * 1000;
    var avgMax = Math.round((s.max + l.max + g.max) / 3 / 1000) * 1000;
    var avgMed = Math.round((s.median + l.median + g.median) / 3 / 1000) * 1000;
    document.getElementById('calc-range').textContent = '$' + (avgMin/1000) + 'K\\u2011$' + (avgMax/1000) + 'K';
    document.getElementById('calc-median').textContent = '$' + (avgMed/1000) + 'K';
    document.getElementById('calc-context').textContent = 'Based on ' + sen + ' level, ' + loc + ' location, and ' + stg + ' company stage data from 327 survey respondents.';
    document.getElementById('calc-results').style.display = 'block';
    document.getElementById('calc-results').scrollIntoView({{behavior: 'smooth'}});
}}
</script>

<div class="salary-content">
{faq_html(faq_pairs)}
{salary_related_links("calculator", "analysis")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get your weekly SE salary update.")
    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/calculator/",
        body_content=body, active_path="/salary/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page("salary/calculator/index.html", page)
    register_og("salary/calculator/index.html", title, "Calculate your SE market rate")
    print("  Built: salary/calculator/index.html")


# ---------------------------------------------------------------------------
# Salary: Methodology
# ---------------------------------------------------------------------------

def build_salary_methodology():
    title = "SE Salary Data Methodology"
    description = (
        "How PreSales Pulse collects, normalizes, and validates Solutions Engineer"
        " salary data. Sources, sample demographics, and limitations explained."
    )
    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("Methodology", None)]
    bc_html = breadcrumb_html(crumbs)

    faq_pairs = [
        ("Where does PreSales Pulse salary data come from?", "We combine two primary sources: public job posting analysis (4,250+ postings across major job boards) and voluntary compensation survey responses from 327 verified SE professionals. Job posting data provides salary ranges disclosed by employers. Survey data provides actual reported compensation from working SEs."),
        ("How often is the data updated?", "Job posting data is refreshed weekly as we process new listings. Survey data is updated quarterly as new responses are collected and validated. The combination of frequent posting data and periodic survey data provides a current and reliable picture of the SE compensation market."),
        ("What are the limitations of this data?", "Job posting salary data only captures ranges that employers choose to disclose (approximately 60% of SE postings include salary ranges). Survey data relies on self-reported figures that we cannot independently verify. Both sources skew toward US-based roles. Our sample of 327 respondents is meaningful but not exhaustive. We are transparent about these limitations and encourage users to treat our data as one input into compensation decisions, not the sole source."),
    ]

    body = f'''{bc_html}
<section class="page-header">
    <h1>Salary Data Methodology</h1>
</section>
<div class="container">
    <h2>Data Sources</h2>
    <p>PreSales Pulse salary data comes from two primary sources that we combine and cross-reference for accuracy.</p>
    <h3>Job Posting Analysis</h3>
    <p>We analyze 4,250+ Solutions Engineer job postings across major job boards (LinkedIn, Indeed, Glassdoor, company career pages). We track postings with disclosed salary ranges (approximately 60% of SE postings), normalize titles across four common variants (Solutions Engineer, Sales Engineer, Solutions Consultant, PreSales Engineer), and segment by seniority level, geographic location, and company stage.</p>
    <h3>Compensation Survey</h3>
    <p>We collect voluntary compensation data from 327 verified SE professionals across 15 US markets. Survey respondents self-report base salary, variable compensation, equity, and benefits. We validate responses against job posting data to identify and remove outliers.</p>

    <h2>Title Normalization</h2>
    <p>The pre-sales technical role goes by multiple titles across the industry. We normalize four common title variants into a single dataset: Solutions Engineer, Sales Engineer, Solutions Consultant, and PreSales Engineer. Our <a href="/salary/comparisons/se-vs-sales-engineer/">SE vs Sales Engineer comparison</a> shows these titles are functionally interchangeable with no meaningful compensation difference.</p>

    <h2>Segmentation</h2>
    <p>We segment salary data along three primary dimensions:</p>
    <ul>
        <li><strong><a href="/salary/by-seniority/">Seniority:</a></strong> Junior, Mid-Level, Senior, Principal/Staff, Manager, Director (based on title keywords and job description analysis)</li>
        <li><strong><a href="/salary/by-location/">Location:</a></strong> 15 US cities plus Remote (based on job posting location and survey respondent location)</li>
        <li><strong><a href="/salary/by-company-stage/">Company Stage:</a></strong> Seed, Series A, Series B, Growth, Enterprise (based on company funding data from Crunchbase and PitchBook)</li>
    </ul>

    <h2>Sample Demographics</h2>
    <p>Our 327 survey respondents break down as follows: 42 Junior SEs, 86 Mid-Level SEs, 94 Senior SEs, 38 Principal/Staff SEs, 45 SE Managers, and 22 Directors. Geographic distribution skews toward major tech hubs (SF, NYC, Seattle account for 46% of respondents), with remote workers making up 22% of the sample. The median respondent age is 31, with 5 years of SE experience.</p>

    <h2>Limitations and Caveats</h2>
    <p>We're transparent about what our data can and cannot tell you. Job posting data only captures disclosed salary ranges. Survey data is self-reported and unverifiable. Our sample is US-focused and skews toward major tech hubs. Individual compensation varies based on factors we can't capture: negotiation skill, specific product complexity, team dynamics, and company financial health.</p>
    <p>Treat our data as a well-informed starting point for compensation conversations, not as a definitive answer. For personalized estimates, use our <a href="/salary/calculator/">salary calculator</a> and combine the results with your own market research.</p>

{faq_html(faq_pairs)}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html()
    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/methodology/",
        body_content=body, active_path="/salary/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page("salary/methodology/index.html", page)
    register_og("salary/methodology/index.html", title, "Data sources, sample, and limitations")
    print("  Built: salary/methodology/index.html")


# ---------------------------------------------------------------------------
# Salary: Compensation Structure
# ---------------------------------------------------------------------------

def build_salary_comp_structure():
    title = "SE Compensation Structure: Base, Variable, Equity"
    description = (
        "How Solutions Engineer compensation breaks down: base salary, variable comp,"
        " equity, and bonuses by seniority level. Data from 327 SE professionals."
    )
    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("Compensation Structure", None)]
    bc_html = breadcrumb_html(crumbs)

    faq_pairs = [
        ("What is the typical SE base-to-variable split?", "The most common SE comp structure is 80/20 or 85/15 base-to-variable. Junior SEs often have 90/10 splits, while senior and principal SEs may have 75/25 or 70/30 splits. The variable component is typically tied to team or individual quota attainment."),
        ("Do Solutions Engineers get equity?", "It depends on the company stage. At seed and Series A startups, equity grants of 0.05% to 0.5% are common. At growth-stage companies, RSU grants of $40K to $100K/year are typical. At public companies, RSU packages of $50K to $150K/year provide liquid equity. Enterprise SEs at public companies also benefit from ESPP programs."),
        ("How do SE bonuses work?", "SE bonuses are typically tied to quota attainment: hitting 100% of assigned quota triggers the target bonus amount. Most companies offer accelerators above 100% (1.5x or 2x payouts on quota overage). Some companies also offer SPIFs (sales performance incentive funds) for specific product launches or competitive wins."),
    ]

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>SE Compensation Structure Analysis</h1>
        <p>How Solutions Engineer total comp breaks down across base salary, variable compensation, equity, and bonuses by seniority level.</p>
    </div>
</section>

<div class="salary-content">
    <h2>Base Salary: The Foundation</h2>
    <p>Base salary represents 70 to 90% of total SE compensation, depending on seniority and company stage. Junior SEs receive 85 to 90% base, while Directors typically have 65 to 75% base. The SE base-to-variable ratio is significantly more favorable than Account Executive splits (which are typically 50/50 to 60/40), making SE income more predictable year to year. For detailed base salary data, see our <a href="/salary/by-seniority/">seniority breakdown</a>.</p>

    <h2>Variable Compensation</h2>
    <p>SE variable comp typically ties to team or individual quota attainment. The most common structures are:</p>
    <ul>
        <li><strong>Team quota:</strong> variable pay based on the SE team's collective pipeline or revenue influence. Common at companies with shared territory models.</li>
        <li><strong>Individual overlay:</strong> variable pay based on the deals you personally support. Common at enterprise companies with named account assignments.</li>
        <li><strong>Hybrid:</strong> 50% team, 50% individual. Increasingly common at growth-stage companies.</li>
    </ul>
    <p>Accelerators above 100% quota are standard. Most companies pay 1.5x on the first 10 to 20% over quota and 2x on anything beyond that. In a strong year, a senior SE with a 20% variable target can earn 30 to 40% above base, making the effective split closer to 70/30 than the stated 80/20.</p>

    <h2>Equity by Company Stage</h2>
    <p>Equity is the most variable component of SE compensation. The expected value depends entirely on the company's success:</p>
    <ul>
        <li><strong><a href="/salary/by-company-stage/seed/">Seed stage:</a></strong> equity grants of 0.1% to 0.5%. High risk, high potential upside. Most seed companies fail, making this equity worthless in the majority of cases. But a 0.3% grant at a company that reaches a $1B valuation is worth $3M before dilution.</li>
        <li><strong><a href="/salary/by-company-stage/series-a/">Series A:</a></strong> grants of 0.05% to 0.2%. Lower risk than seed, with better-defined valuations. The company has proven product-market fit.</li>
        <li><strong><a href="/salary/by-company-stage/series-b/">Series B:</a></strong> grants of 0.02% to 0.1%. Some companies transition from options to RSUs at this stage, reducing strike price risk.</li>
        <li><strong><a href="/salary/by-company-stage/growth/">Growth stage:</a></strong> RSU grants of $40K to $100K/year. Secondary sale opportunities may exist. The equity is less speculative but offers less dramatic upside.</li>
        <li><strong><a href="/salary/by-company-stage/enterprise/">Enterprise/public:</a></strong> RSU grants of $50K to $150K/year. Fully liquid on vest. ESPP programs offer additional 5 to 15% discount on share purchases.</li>
    </ul>

    <h2>Comp Splits by Seniority</h2>
    <p>The balance between base, variable, and equity shifts significantly as you advance:</p>
    <ul>
        <li><strong><a href="/salary/by-seniority/junior/">Junior SE:</a></strong> 85 to 90% base, 10 to 15% variable, minimal equity. Focus is on building skills and proving impact.</li>
        <li><strong><a href="/salary/by-seniority/mid-level/">Mid-Level SE:</a></strong> 80 to 85% base, 15 to 20% variable, growing equity component at startups. Variable tied to team metrics.</li>
        <li><strong><a href="/salary/by-seniority/senior/">Senior SE:</a></strong> 75 to 80% base, 20 to 25% variable, meaningful equity at growth companies. Variable tied increasingly to individual deal outcomes.</li>
        <li><strong><a href="/salary/by-seniority/principal-staff/">Principal/Staff SE:</a></strong> 75% base, 20 to 25% variable, largest equity grants. Strategic bonus pools beyond standard variable.</li>
        <li><strong><a href="/salary/by-seniority/manager/">SE Manager:</a></strong> 75 to 80% base, 20 to 25% variable tied to team performance. Management bonuses add 5 to 10%.</li>
        <li><strong><a href="/salary/by-seniority/director/">Director of SE:</a></strong> 65 to 75% base, 25 to 35% variable. Executive comp structures with long-term incentives.</li>
    </ul>

    <h2>Other Compensation Components</h2>
    <p>Beyond base, variable, and equity, SE total comp includes several other elements:</p>
    <ul>
        <li><strong>Signing bonuses:</strong> $5K to $30K, most common at enterprise companies and for senior hires. Used to bridge the gap when your current equity or bonus would be lost by switching jobs.</li>
        <li><strong>401(k) match:</strong> typically 3 to 6% of base salary. Some companies offer dollar-for-dollar matching, others match 50 cents on the dollar.</li>
        <li><strong>Professional development:</strong> $1K to $5K annual budgets for conferences, certifications, and training. More common at growth-stage and enterprise companies.</li>
        <li><strong>Tool stipends:</strong> some companies provide dedicated budgets for SE-specific tools (second monitors, demo equipment, home office setup).</li>
    </ul>

{faq_html(faq_pairs)}
{salary_related_links("compensation-structure", "analysis")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get weekly SE compensation data.")
    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/compensation-structure/",
        body_content=body, active_path="/salary/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page("salary/compensation-structure/index.html", page)
    register_og("salary/compensation-structure/index.html", title, "Base, variable, and equity splits by level")
    print("  Built: salary/compensation-structure/index.html")


# ---------------------------------------------------------------------------
# Salary: SE-to-AE Ratio
# ---------------------------------------------------------------------------

def build_salary_ae_ratio():
    title = "SE-to-AE Ratio: Impact on Comp and Workload"
    description = (
        "How the SE-to-AE ratio affects Solutions Engineer compensation, workload,"
        " and career growth. Industry benchmarks and data from 327 SE professionals."
    )
    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("SE-to-AE Ratio", None)]
    bc_html = breadcrumb_html(crumbs)

    faq_pairs = [
        ("What is the typical SE-to-AE ratio?", "The most common SE-to-AE ratio in B2B SaaS is 1:3 (one SE supporting three AEs). Ratios range from 1:1 at highly technical enterprise companies to 1:6+ at companies with simpler products. The ratio is the single biggest determinant of SE workload and deal involvement depth."),
        ("How does the SE-to-AE ratio affect compensation?", "Lower ratios (1:1 or 1:2) correlate with higher SE compensation because the SE carries more deal influence and revenue attribution. Companies with 1:1 or 1:2 ratios typically pay 10 to 15% above market median. Higher ratios (1:4+) mean more deals but less individual deal influence, which can reduce variable comp."),
        ("What SE-to-AE ratio should I look for?", "For career development and compensation, 1:2 to 1:3 is the sweet spot. You get enough deal volume to develop pattern recognition while maintaining the depth of involvement that drives strong variable comp and clear promotion evidence. Avoid ratios above 1:4 unless the product has a very short sales cycle."),
    ]

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>SE-to-AE Ratio: Impact on Comp and Workload</h1>
        <p>The SE-to-AE ratio is the single biggest factor in SE workload, deal involvement, and ultimately compensation. Here's what the data shows.</p>
    </div>
</section>

<div class="salary-content">
    <h2>The Ratio Spectrum</h2>
    <p>SE-to-AE ratios in B2B SaaS typically fall between 1:1 and 1:6. The ratio is driven by product complexity, average deal size, and the company's sales motion. Understanding where a company sits on this spectrum tells you more about your day-to-day experience than the job description ever will.</p>
    <ul>
        <li><strong>1:1 ratio:</strong> Highly technical enterprise products (infrastructure, security platforms). The SE is a full partner in every deal. Comp is highest, workload is intense but focused, and deal influence is maximum. Common at companies like Palo Alto Networks, Snowflake, and similar enterprise vendors.</li>
        <li><strong>1:2 ratio:</strong> Complex SaaS products with 6+ month sales cycles. You carry 8 to 12 active deals and have deep involvement in each. This is the sweet spot for most SEs: enough volume for pattern recognition, enough depth for genuine technical selling. Common at growth-stage companies selling $100K+ ACV products.</li>
        <li><strong>1:3 ratio:</strong> The industry average. You support 12 to 18 active deals, with varying levels of involvement. Some deals get full technical evaluations; others get quick demos and qualification calls. Time management becomes a critical skill. Common at mid-market SaaS companies with $30K to $100K ACV.</li>
        <li><strong>1:4 to 1:6 ratio:</strong> Simpler products with shorter sales cycles. You're running many demos but going shallow on each. Variable comp may be lower because individual deal influence is diluted. Common at companies with $10K to $30K ACV or PLG-assisted sales motions.</li>
    </ul>

    <h2>Comp Impact</h2>
    <p>Our data shows a clear correlation between SE-to-AE ratio and compensation. SEs at companies with 1:1 or 1:2 ratios earn 10 to 15% above the median for their seniority level. SEs at companies with 1:4+ ratios earn 5 to 10% below median. The mechanism is straightforward: lower ratios mean more deal influence, which means clearer revenue attribution, which means stronger compensation negotiation leverage.</p>
    <p>Variable compensation is even more affected. At a 1:2 ratio, you can clearly attribute pipeline influence to specific deals. At 1:4+, your contribution is spread across many deals, making it harder to claim credit for specific wins. Companies know this and structure their SE comp plans accordingly: lower-ratio companies offer more aggressive variable plans because the attribution is cleaner.</p>

    <h2>Workload Impact</h2>
    <p>The ratio directly determines how many deals you juggle simultaneously and how deeply you can invest in each one. At 1:2, you have time to build custom demo environments, run thorough POCs, and provide detailed technical evaluations. At 1:4+, you're doing rapid-fire demos and quick qualification calls, with less time for the deep technical work that builds SE skills and wins competitive deals.</p>
    <p>Burnout risk also correlates with ratio. Our survey data shows that SEs at companies with ratios above 1:4 report 35% higher burnout indicators than those at 1:2 or below. The volume of context-switching (moving between 15+ deals at different stages, with different products and different stakeholders) creates cognitive load that accumulates over time.</p>

    <h2>What to Ask in Interviews</h2>
    <p>When evaluating an SE opportunity, always ask about the current SE-to-AE ratio and the planned ratio. Companies planning to hire more SEs will reduce the ratio over time, improving your experience. Companies planning to hire more AEs without adding SEs will increase the ratio, increasing your workload. The planned ratio tells you more about your 12-month experience than the current one.</p>
    <p>Also ask how deals are assigned. Some companies use pod models (dedicated SE-AE partnerships), while others use pool models (SEs are assigned to deals from a shared queue). Pod models create stronger partnerships and typically lead to better SE outcomes. Pool models offer more variety but can create assignment conflicts and weaker AE-SE relationships. For more on how the SE-AE dynamic affects compensation, see our <a href="/salary/comparisons/se-vs-ae/">SE vs AE comparison</a>.</p>

    <h2>Industry Benchmarks</h2>
    <p>SE-to-AE ratios vary by company category:</p>
    <ul>
        <li><strong>Enterprise infrastructure/security:</strong> 1:1 to 1:2</li>
        <li><strong>Enterprise SaaS ($100K+ ACV):</strong> 1:2 to 1:3</li>
        <li><strong>Mid-market SaaS ($30K to $100K ACV):</strong> 1:3 to 1:4</li>
        <li><strong>SMB/Commercial SaaS ($10K to $30K ACV):</strong> 1:4 to 1:6</li>
        <li><strong>PLG-assisted sales:</strong> 1:5 to 1:8 (SEs handle only escalated technical evaluations)</li>
    </ul>

{faq_html(faq_pairs)}
{salary_related_links("se-to-ae-ratio", "analysis")}
</div>
'''
    body += source_citation_html()
    body += newsletter_cta_html("Get weekly SE market data.")
    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)

    page = get_page_wrapper(
        title=title, description=description, canonical_path="/salary/se-to-ae-ratio/",
        body_content=body, active_path="/salary/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page("salary/se-to-ae-ratio/index.html", page)
    register_og("salary/se-to-ae-ratio/index.html", title, "Industry benchmarks and comp impact")
    print("  Built: salary/se-to-ae-ratio/index.html")


# ---------------------------------------------------------------------------
# Build orchestration
# ---------------------------------------------------------------------------

def build_sitemap():
    urls = ""
    for page_path in ALL_PAGES:
        clean = page_path.replace("index.html", "")
        if not clean.startswith("/"):
            clean = "/" + clean
        if not clean.endswith("/"):
            clean += "/"
        if clean == "//":
            clean = "/"
        urls += f"  <url>\n    <loc>{SITE_URL}{clean}</loc>\n    <lastmod>{BUILD_DATE}</lastmod>\n  </url>\n"

    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"  Built: sitemap.xml ({len(ALL_PAGES)} URLs)")


def build_robots():
    content = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml

# AI/LLM crawlers - explicitly allowed for AI search citations
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GoogleOther
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: CCBot
Allow: /

User-agent: Meta-ExternalAgent
Allow: /
"""
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(content)
    print("  Built: robots.txt")


def build_llms_txt():
    content = f"""# PreSales Pulse

> PreSales Pulse is an independent career intelligence platform for Solutions Engineers, Sales Engineers, and Solutions Consultants. The site provides salary benchmarks by seniority, location, and company stage, independent tool reviews for demo platforms, RFP automation, proposal tools, and conversation intelligence software, a searchable glossary of pre-sales terminology, and career guides covering SE career paths, certifications, and role transitions. All data is updated weekly and free to access.

## Core Pages
- [Homepage]({SITE_URL}/)
- [About]({SITE_URL}/about/)
- [Newsletter]({SITE_URL}/newsletter/)

## Salary Data
- [Salary Index]({SITE_URL}/salary/): Aggregate SE salary benchmarks
- [By Seniority]({SITE_URL}/salary/by-seniority/): Junior through Director
- [By Location]({SITE_URL}/salary/by-location/): 15 major metros + remote
- [By Company Stage]({SITE_URL}/salary/by-company-stage/): Seed through Enterprise
- [Salary Calculator]({SITE_URL}/salary/calculator/)
- [Compensation Structure]({SITE_URL}/salary/compensation-structure/)
- [SE-to-AE Ratio]({SITE_URL}/salary/se-to-ae-ratio/)

### Salary Comparisons
- [SE vs AE]({SITE_URL}/salary/comparisons/se-vs-ae/)
- [SE vs GTM Engineer]({SITE_URL}/salary/comparisons/se-vs-gtm-engineer/)
- [SE vs CSM]({SITE_URL}/salary/comparisons/se-vs-csm/)
- [SE vs Product Manager]({SITE_URL}/salary/comparisons/se-vs-product-manager/)
- [SE vs Solutions Architect]({SITE_URL}/salary/comparisons/se-vs-solutions-architect/)

## Tool Reviews
- [Tools Index]({SITE_URL}/tools/): All SE tools reviewed
- [Demo Platforms]({SITE_URL}/tools/category/demo-platforms/)
- [POC/Trial Management]({SITE_URL}/tools/category/poc-trial/)
- [Proposal & CPQ]({SITE_URL}/tools/category/proposal-cpq/)
- [RFP Automation]({SITE_URL}/tools/category/rfp-automation/)
- [Conversation Intelligence]({SITE_URL}/tools/category/conversation-intelligence/)

### Tool Comparisons
- [Consensus vs Navattic]({SITE_URL}/tools/compare/consensus-vs-navattic/)
- [Demostack vs Walnut]({SITE_URL}/tools/compare/demostack-vs-walnut/)
- [Gong vs Chorus]({SITE_URL}/tools/compare/gong-vs-chorus/)
- [Lucidchart vs Miro]({SITE_URL}/tools/compare/lucidchart-vs-miro/)

## Career Resources
- [Career Guides]({SITE_URL}/careers/)
- [What is a Solutions Engineer?]({SITE_URL}/careers/what-is-solutions-engineer/)
- [How to Become a Solutions Engineer]({SITE_URL}/careers/how-to-become-solutions-engineer/)
- [SE Interview Questions]({SITE_URL}/careers/se-interview-questions/)
- [SE Certification Guide]({SITE_URL}/careers/se-certification-guide/)

## Glossary
- [Glossary Index]({SITE_URL}/glossary/): Pre-sales terminology defined
- [Proof of Concept]({SITE_URL}/glossary/proof-of-concept/)
- [Technical Win]({SITE_URL}/glossary/technical-win/)
- [Discovery Call]({SITE_URL}/glossary/discovery-call/)
- [Value Selling]({SITE_URL}/glossary/value-selling/)
- [Competitive Battlecard]({SITE_URL}/glossary/competitive-battlecard/)
"""
    with open(os.path.join(OUTPUT_DIR, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(content)
    print("  Built: llms.txt")


def build_top_voices():
    """Build the Top 25 Solutions Engineering Voices page."""
    data_path = os.path.join(PROJECT_DIR, "data", "top_voices.json")
    if not os.path.exists(data_path):
        print("  SKIP top voices (no data file)")
        return
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    voices = data["voices"]
    leaders = [v for v in voices if v.get("tier") == "leader"]
    rising = [v for v in voices if v.get("tier") == "rising"]
    last_updated = data.get("last_updated", BUILD_DATE)

    title = "Top 25 SE Voices of 2026"
    meta_desc = pad_description(
        "Data-driven rankings of the 25 most influential Solutions Engineers, "
        "authors, and community builders shaping presales. Updated for 2026."
    )

    crumbs = [("Home", "/"), ("Top Voices", None)]
    bc_html = breadcrumb_html(crumbs)
    bc_schema = get_breadcrumb_schema(crumbs)

    # ItemList schema
    list_items = ""
    for v in voices:
        list_items += f'''
        {{"@type":"ListItem","position":{v["rank"]},"item":{{"@type":"Person","name":"{v["name"]}","jobTitle":"{v["title"]}","worksFor":{{"@type":"Organization","name":"{v["company"]}"}},"url":"{v["linkedin_url"]}"}}}},'''
    list_items = list_items.rstrip(",")
    list_schema = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"ItemList","name":"{data["title"]}","numberOfItems":{len(voices)},"itemListElement":[{list_items}]}}
</script>'''

    article_obj = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": data["title"],
        "description": meta_desc,
        "author": {"@type": "Person", "name": "Rome Thorndike", "url": f"{SITE_URL}/about/"},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
        "datePublished": "2026-04-14", "dateModified": last_updated,
        "url": f"{SITE_URL}/top-voices/",
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE_URL}/top-voices/"},
    }
    article_schema = f'    <script type="application/ld+json">{json.dumps(article_obj)}</script>\n'

    def voice_card(v):
        tags_html = "".join(f'<span class="voice-tag">{t}</span>' for t in v.get("tags", []))
        rank_class = "voice-rank-top" if v["rank"] <= 3 else "voice-rank"
        return f'''<div class="voice-card" id="voice-{v["rank"]}">
    <div class="voice-card-header">
        <div class="{rank_class}">#{v["rank"]}</div>
        <div class="voice-card-info">
            <h3 class="voice-name"><a href="{v["linkedin_url"]}" target="_blank" rel="noopener">{v["name"]}</a></h3>
            <p class="voice-title">{v["title"]} at {v["company"]}</p>
            <div class="voice-tags">{tags_html}</div>
        </div>
        <a href="{v["linkedin_url"]}" target="_blank" rel="noopener" class="voice-linkedin-btn" aria-label="View {v["name"]} on LinkedIn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        </a>
    </div>
    <p class="voice-bio">{v["bio"]}</p>
</div>'''

    leaders_html = "".join(voice_card(v) for v in leaders)
    rising_html = "".join(voice_card(v) for v in rising)
    jump_links = "".join(f'<a href="#voice-{v["rank"]}" class="voice-jump-link">#{v["rank"]} {v["name"].split()[0]}</a>' for v in voices)

    methodology_html = f'''<details class="voice-methodology">
    <summary><strong>How We Ranked These Voices</strong></summary>
    <div class="methodology-content">
        <p>{data.get("methodology", "")}</p>
        <p>We evaluated candidates across five dimensions:</p>
        <ul>
            <li><strong>Topic relevance</strong> (required): Must actively contribute to the presales/SE profession.</li>
            <li><strong>Published work</strong> (30%): Books, courses, certifications that advance the profession.</li>
            <li><strong>Community impact</strong> (25%): Building communities, hosting podcasts, mentoring.</li>
            <li><strong>Content frequency</strong> (25%): Regular posting cadence with practical SE content.</li>
            <li><strong>Originality</strong> (20%): Original frameworks, methodologies, and insights.</li>
        </ul>
        <p>This list is updated annually. <a href="/newsletter/">Subscribe to PreSales Pulse</a> to get notified when we refresh the rankings.</p>
    </div>
</details>'''

    body = f'''{bc_html}
<section class="salary-header">
    <div class="salary-header-inner">
        <div class="salary-eyebrow">2026 RANKINGS</div>
        <h1>{data["title"]}</h1>
        <p>{data.get("subtitle", "")}</p>
        <p style="font-size: 0.85rem; color: var(--psp-text-tertiary);">Last updated: {last_updated} &middot; {len(voices)} voices ranked</p>
    </div>
</section>

<div class="salary-content" style="max-width: 800px; margin: 0 auto;">
    {methodology_html}

    <div class="voices-jump-nav">
        {jump_links}
    </div>

    <h2 class="voices-section-heading">Top 10 Leaders</h2>
    <p>The most recognized voices shaping Solutions Engineering today.</p>
    <div class="voices-grid">
        {leaders_html}
    </div>

    <h2 class="voices-section-heading">Rising Voices (11-25)</h2>
    <p>Practitioners and thought leaders gaining momentum in the SE community.</p>
    <div class="voices-grid">
        {rising_html}
    </div>
</div>

{newsletter_cta_html("Get weekly SE career intelligence from the voices shaping the profession.")}

<section style="text-align: center; padding: var(--psp-space-8) var(--psp-space-4); max-width: 600px; margin: 0 auto;">
    <h2>Made the List?</h2>
    <p style="color: var(--psp-text-secondary);">Share it. Tag us on LinkedIn. We will amplify your post.</p>
    <p style="color: var(--psp-text-secondary);">Know someone who should be on next year's list? <a href="mailto:rome@getprovyx.com">Let us know</a>.</p>
</section>
'''

    extra_head = bc_schema + list_schema + article_schema + '''<style>
.voice-methodology { margin-bottom: var(--psp-space-8); border: 1px solid var(--psp-border); border-radius: var(--psp-radius-lg); background: var(--psp-bg-surface); }
.voice-methodology summary { padding: var(--psp-space-4); cursor: pointer; font-size: 1rem; color: var(--psp-text-primary); }
.voice-methodology summary:hover { color: var(--psp-accent); }
.methodology-content { padding: 0 var(--psp-space-4) var(--psp-space-4); font-size: 0.9rem; color: var(--psp-text-secondary); line-height: 1.7; }
.methodology-content ul { padding-left: var(--psp-space-4); margin: 0.75rem 0; }
.methodology-content li { margin-bottom: 0.5rem; }
.voices-jump-nav { display: flex; flex-wrap: wrap; gap: 0.25rem; margin-bottom: var(--psp-space-8); padding: var(--psp-space-3); background: var(--psp-accent-subtle); border-radius: var(--psp-radius-lg); }
.voice-jump-link { font-size: 0.75rem; font-family: "Source Code Pro", monospace; padding: 0.25rem 0.5rem; border-radius: var(--psp-radius-sm); color: var(--psp-text-secondary); text-decoration: none; transition: background 0.15s, color 0.15s; }
.voice-jump-link:hover { background: var(--psp-accent); color: #fff; }
.voices-section-heading { font-size: 1.25rem; margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--psp-accent); }
.voices-grid { display: flex; flex-direction: column; gap: var(--psp-space-4); margin-bottom: var(--psp-space-8); }
.voice-card { border: 1px solid var(--psp-border); border-radius: var(--psp-radius-lg); background: var(--psp-bg-surface); padding: var(--psp-space-4); transition: border-color 0.2s, box-shadow 0.2s; }
.voice-card:hover { border-color: var(--psp-accent); box-shadow: 0 2px 12px rgba(30, 58, 95, 0.08); }
.voice-card-header { display: flex; align-items: flex-start; gap: 0.75rem; }
.voice-rank, .voice-rank-top { font-family: "Source Code Pro", monospace; font-weight: 700; font-size: 1.1rem; min-width: 2.5rem; text-align: center; flex-shrink: 0; padding-top: 0.15rem; color: var(--psp-text-tertiary); }
.voice-rank-top { color: var(--psp-accent); font-size: 1.25rem; }
.voice-card-info { flex: 1; min-width: 0; }
.voice-name { font-size: 1.1rem; font-weight: 600; margin: 0 0 0.25rem; line-height: 1.3; }
.voice-name a { color: var(--psp-text-primary); text-decoration: none; }
.voice-name a:hover { color: var(--psp-accent); }
.voice-title { font-size: 0.85rem; color: var(--psp-text-secondary); margin: 0 0 0.5rem; }
.voice-tags { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.voice-tag { font-size: 0.7rem; font-family: "Source Code Pro", monospace; padding: 0.15rem 0.5rem; border-radius: 999px; background: var(--psp-accent-subtle); color: var(--psp-accent); font-weight: 500; }
.voice-linkedin-btn { flex-shrink: 0; display: flex; align-items: center; justify-content: center; width: 2.25rem; height: 2.25rem; border-radius: var(--psp-radius-sm); color: var(--psp-text-tertiary); text-decoration: none; transition: color 0.15s, background 0.15s; }
.voice-linkedin-btn:hover { color: #0077B5; background: rgba(0, 119, 181, 0.08); }
.voice-bio { margin: 0.75rem 0 0; font-size: 0.9rem; color: var(--psp-text-secondary); line-height: 1.7; padding-left: calc(2.5rem + 0.75rem); }
@media (max-width: 640px) { .voice-bio { padding-left: 0; } .voice-card-header { flex-wrap: wrap; } .voice-card { position: relative; } .voice-linkedin-btn { position: absolute; top: var(--psp-space-3); right: var(--psp-space-3); } .voices-jump-nav { display: none; } }
</style>'''

    page = get_page_wrapper(
        title=title, description=meta_desc, canonical_path="/top-voices/",
        body_content=body, active_path="/top-voices/",
        extra_head=extra_head, body_class="page-inner",
    )
    write_page("top-voices/index.html", page)
    print(f"  Built: top-voices/index.html ({len(voices)} voices)")


def main():
    print(f"Building {SITE_NAME}...")

    # Clean and create output dir
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # Copy assets
    src_assets = os.path.join(PROJECT_DIR, "assets")
    dst_assets = os.path.join(OUTPUT_DIR, "assets")
    if os.path.exists(src_assets):
        shutil.copytree(src_assets, dst_assets)
        print("  Copied assets/")

    # Copy static pages (self-contained HTML pages not generated by build)
    static_dir = os.path.join(PROJECT_DIR, "static")
    if os.path.exists(static_dir):
        for item in os.listdir(static_dir):
            src = os.path.join(static_dir, item)
            dst = os.path.join(OUTPUT_DIR, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        print("  Copied static/")

    # Load data
    comp_data = load_data("comp_analysis.json")
    market_data = load_data("market_intelligence.json")

    # Build core pages
    print("\n  Building core pages...")
    build_homepage(market_data, comp_data)
    build_about()
    build_newsletter()
    build_privacy()
    build_terms()
    build_404()

    # Build salary pages
    print("\n  Building salary pages...")
    build_salary_index(comp_data)
    build_salary_seniority_pages(comp_data)
    build_salary_location_pages(comp_data)
    build_salary_stage_pages(comp_data)
    build_salary_comparison_pages()
    build_salary_calculator()
    build_salary_methodology()
    build_salary_comp_structure()
    build_salary_ae_ratio()

    # Build tool pages (Wave 2)
    print("\n  Building tool pages...")
    tools_count = build_all_tools()
    print(f"  Built {tools_count} tool pages")

    # Build career pages (Wave 3)
    print("\n  Building career pages...")
    careers_count = build_all_careers()
    print(f"  Built {careers_count} career pages")

    # Build glossary pages (Wave 3)
    print("\n  Building glossary pages...")
    glossary_count = build_all_glossary()
    print(f"  Built {glossary_count} glossary pages")

    # Build extra pages (Wave 3)
    print("\n  Building extra pages...")
    extras_count = build_all_extras()
    print(f"  Built {extras_count} extra pages")

    # Build top voices
    print("\n  Building top voices...")
    build_top_voices()

    # Register all pages for OG image generation
    print("\n  Registering OG pages...")
    for rel_path in ALL_PAGES:
        filepath = os.path.join(OUTPUT_DIR, rel_path)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()
            title_match = re.search(r'<meta property="og:title" content="(.*?)"', html)
            title = title_match.group(1).replace(f" - {SITE_NAME}", "") if title_match else SITE_NAME
            desc_match = re.search(r'<meta name="description" content="(.*?)"', html)
            subtitle = desc_match.group(1)[:80] if desc_match else ""
            # Only register if not already registered
            registered_paths = {p["rel_path"] for p in OG_PAGES}
            if rel_path not in registered_paths:
                register_og(rel_path, title, subtitle)
    print(f"  Registered {len(OG_PAGES)} pages for OG generation")

    # Generate OG images
    if not SKIP_OG:
        print("\n  Generating OG images...")
        generate_og_images(OG_PAGES, OUTPUT_DIR, os.path.join(PROJECT_DIR, "og-templates"))
    else:
        print("\n  Skipping OG image generation (--skip-og)")

    # Meta files
    print("\n  Building meta files...")
    build_sitemap()
    build_robots()
    build_llms_txt()

    with open(os.path.join(OUTPUT_DIR, "CNAME"), "w", encoding="utf-8") as f:
        f.write("presalespulse.com\n")
    print("  Built: CNAME")

    # Google Search Console verification file
    if GOOGLE_SITE_VERIFICATION:
        verification_path = os.path.join(OUTPUT_DIR, GOOGLE_SITE_VERIFICATION)
        with open(verification_path, "w", encoding="utf-8") as f:
            f.write(f"google-site-verification: {GOOGLE_SITE_VERIFICATION}")
        print(f"  Generated {GOOGLE_SITE_VERIFICATION}")

    print(f"\n=== Build complete: {len(ALL_PAGES)} pages ===")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Preview: cd output && python3 -m http.server 8091")


if __name__ == "__main__":
    main()
