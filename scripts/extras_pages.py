import os
import json

from nav_config import *
from templates import (get_page_wrapper, write_page, get_breadcrumb_schema,
                       breadcrumb_html, newsletter_cta_html)


def _extras_related_links(current_page):
    """Generate cross-links between extras pages and main content sections."""
    all_links = [
        ("/companies/", "Companies Hiring SEs"),
        ("/reports/", "SE Reports"),
        ("/conferences/", "SE Conferences"),
        ("/tools/", "SE Tool Reviews"),
        ("/salary/", "SE Salary Data"),
        ("/careers/", "Career Guides"),
        ("/glossary/", "SE Glossary"),
    ]
    items = ""
    for href, label in all_links:
        if href.strip("/") == current_page.strip("/"):
            continue
        items += f'<a href="{href}" class="related-link-card">{label}</a>\n'
    return f'''<section class="related-links">
    <h2>Explore More</h2>
    <div class="related-links-grid">
        {items}
    </div>
</section>'''


def build_companies_index():
    """Generate /companies/ coming soon page."""
    title = "Companies Hiring Solutions Engineers"
    description = "Which companies hire SEs, what they pay, team sizes, and growth trends. Company profiles updated weekly from job posting data."

    crumbs = [("Home", "/"), ("Companies", None)]
    extra_head = get_breadcrumb_schema(crumbs)

    body = f'''<div class="container">
    <div class="salary-content">
    {breadcrumb_html(crumbs)}
    <h1>Companies Hiring Solutions Engineers</h1>

    <p>We're building detailed company profiles for every major employer of Solutions Engineers. Each profile will include SE salary ranges, team sizes, SE-to-AE ratios, tools used, and growth trends pulled from live job posting data.</p>

    <h2>What's Coming</h2>
    <ul>
        <li><strong>100+ company profiles</strong> covering Salesforce, ServiceNow, Datadog, Snowflake, CrowdStrike, MongoDB, HashiCorp, and more</li>
        <li><strong>SE team size estimates</strong> based on job posting volume and LinkedIn data</li>
        <li><strong>Salary ranges by company</strong> from disclosed ranges in job postings</li>
        <li><strong>Tool stacks</strong> which demo platforms, CRMs, and SE tools each company uses</li>
        <li><strong>Growth signals</strong> whether SE hiring is accelerating or slowing at each company</li>
    </ul>

    <p>Company data comes from our job posting scraper that runs twice weekly, covering all major job boards. We cross-reference with LinkedIn, Glassdoor, and Levels.fyi for salary validation.</p>

    <h2>Get Notified When This Launches</h2>
    <p>Company profiles will launch in the next few weeks. Subscribe to get notified and receive weekly SE job market data in the meantime.</p>

    {_extras_related_links("companies")}
    {newsletter_cta_html("Be the first to see company profiles when they go live.")}
    </div>
</div>'''

    html = get_page_wrapper(title, description, "/companies/", body, active_path="/insights/", extra_head=extra_head)
    write_page("companies/index.html", html)
    print("  Built: companies/index.html")


def build_reports_index():
    """Generate /reports/ coming soon page."""
    title = "SE Salary and Tool Reports"
    description = "Free and gated reports on SE compensation, tool adoption, and job market trends. Data-driven analysis for solutions engineers."

    crumbs = [("Home", "/"), ("Reports", None)]
    extra_head = get_breadcrumb_schema(crumbs)

    body = f'''<div class="container">
    <div class="salary-content">
    {breadcrumb_html(crumbs)}
    <h1>Solutions Engineer Reports</h1>

    <p>Data-driven reports on SE compensation, tool adoption, and job market trends. Built from our proprietary dataset of job postings, salary disclosures, and practitioner surveys.</p>

    <h2>Upcoming Reports</h2>

    <div class="card-grid">
        <div class="card">
            <h3>SE Salary Report 2026</h3>
            <p>Comprehensive salary data by seniority, location, company stage, and industry. Based on 4,000+ job postings and 327 survey responses. Includes base, variable, and equity breakdowns.</p>
            <span class="tag">Coming Soon</span>
        </div>
        <div class="card">
            <h3>SE Tool Stack Report</h3>
            <p>Which tools SE teams use in practice, adoption rates by company size, satisfaction scores, and budget benchmarks. Covers demo platforms, RFP tools, conversation intelligence, and more.</p>
            <span class="tag">Coming Soon</span>
        </div>
        <div class="card">
            <h3>State of Solutions Engineering 2026</h3>
            <p>The definitive market overview. Team structures, SE-to-AE ratios, remote work trends, career satisfaction, and hiring velocity across B2B SaaS.</p>
            <span class="tag">Coming Soon</span>
        </div>
    </div>

    <h2>Get Reports First</h2>
    <p>Subscribe to get reports delivered to your inbox as soon as they publish.</p>

    {_extras_related_links("reports")}
    {newsletter_cta_html("Get reports delivered as soon as they publish.")}
    </div>
</div>'''

    html = get_page_wrapper(title, description, "/reports/", body, active_path="/insights/", extra_head=extra_head)
    write_page("reports/index.html", html)
    print("  Built: reports/index.html")


def build_conferences_index():
    """Generate /conferences/ coming soon page."""
    title = "SE Conferences and Events 2026"
    description = "Conferences, summits, and meetups for solutions engineers and pre-sales professionals. PreSales Collective, vendor events, and community meetups."

    crumbs = [("Home", "/"), ("Conferences", None)]
    extra_head = get_breadcrumb_schema(crumbs)

    body = f'''<div class="container">
    <div class="salary-content">
    {breadcrumb_html(crumbs)}
    <h1>SE Conferences and Events</h1>

    <p>A calendar of conferences, summits, and meetups relevant to solutions engineers and pre-sales professionals. We track events from the PreSales Collective, vendor conferences, and community-organized meetups.</p>

    <h2>Major Events</h2>

    <div class="card-grid">
        <div class="card">
            <h3>PreSales Collective Summit</h3>
            <p>The largest gathering of pre-sales professionals. Workshops, networking, and career development sessions. Typically held annually in major US cities.</p>
            <a href="https://www.presalescollective.com" target="_blank" rel="noopener">presalescollective.com</a>
        </div>
        <div class="card">
            <h3>Consensus Xperience</h3>
            <p>Demo automation focused conference from Consensus. Product updates, customer stories, and best practices for demo-led selling.</p>
            <a href="https://www.goconsensus.com" target="_blank" rel="noopener">goconsensus.com</a>
        </div>
        <div class="card">
            <h3>SaaStr Annual</h3>
            <p>The largest SaaS conference. Not SE-specific, but includes pre-sales tracks and heavy SE networking opportunities.</p>
            <a href="https://www.saastr.com" target="_blank" rel="noopener">saastr.com</a>
        </div>
    </div>

    <h2>Know About an Event?</h2>
    <p>If you're organizing or aware of an SE-focused event, let us know. We'll add it to the calendar.</p>

    {_extras_related_links("conferences")}
    {newsletter_cta_html("Get event announcements and SE community updates.")}
    </div>
</div>'''

    html = get_page_wrapper(title, description, "/conferences/", body, active_path="/insights/", extra_head=extra_head)
    write_page("conferences/index.html", html)
    print("  Built: conferences/index.html")


def build_insights_index():
    """Generate /insights/ coming soon page."""
    title = "SE Market Insights and Analysis"
    description = "Job market analysis, tool trends, salary reports, and weekly pulse reports for Solutions Engineers. Data-driven insights updated regularly."

    crumbs = [("Home", "/"), ("Insights", None)]
    extra_head = get_breadcrumb_schema(crumbs)

    body = f'''<div class="container">
    <div class="salary-content">
    {breadcrumb_html(crumbs)}
    <h1>SE Market Insights and Analysis</h1>

    <p>We're building a library of data-driven insights for Solutions Engineers. Every piece is backed by real job posting data, salary disclosures, and practitioner input rather than recycled industry talking points.</p>

    <h2>What's Coming</h2>

    <div class="card-grid">
        <div class="card">
            <h3>Job Market Analysis</h3>
            <p>Weekly snapshots of SE hiring velocity, which companies are ramping and which are pulling back, broken out by seniority, location, and industry vertical.</p>
            <span class="tag">Coming Soon</span>
        </div>
        <div class="card">
            <h3>Tool Trends</h3>
            <p>Which demo platforms, RFP tools, and conversation intelligence products are gaining traction in SE teams. Based on job posting requirements and practitioner surveys.</p>
            <span class="tag">Coming Soon</span>
        </div>
        <div class="card">
            <h3>Salary Reports</h3>
            <p>Quarterly deep dives into SE compensation shifts. Base, variable, and equity breakdowns by seniority, geography, and company stage.</p>
            <span class="tag">Coming Soon</span>
        </div>
        <div class="card">
            <h3>Weekly Pulse Reports</h3>
            <p>A concise weekly digest of what moved in the SE job market. New openings, closed roles, salary shifts, and hiring signals across B2B SaaS.</p>
            <span class="tag">Coming Soon</span>
        </div>
    </div>

    <h2>Get Notified When Insights Launch</h2>
    <p>Subscribe to receive insights as soon as they publish, plus weekly SE job market data in the meantime.</p>

    {_extras_related_links("insights")}
    {newsletter_cta_html("Be the first to read new insights when they go live.")}
    </div>
</div>'''

    html = get_page_wrapper(title, description, "/insights/", body, active_path="/insights/", extra_head=extra_head)
    write_page("insights/index.html", html)
    print("  Built: insights/index.html")


def build_jobs_index():
    """Generate /jobs/ coming soon page."""
    title = "Solutions Engineer Job Board"
    description = "SE job board aggregating Solutions Engineer, Sales Engineer, and Pre-Sales roles from major job boards. Updated twice weekly. 4,250+ jobs tracked."

    crumbs = [("Home", "/"), ("Job Board", None)]
    extra_head = get_breadcrumb_schema(crumbs)

    body = f'''<div class="container">
    <div class="salary-content">
    {breadcrumb_html(crumbs)}
    <h1>Solutions Engineer Job Board</h1>

    <p>We're building a dedicated job board that aggregates SE roles from every major job board into one searchable feed. No recruiter spam, no irrelevant titles, just Solutions Engineer, Sales Engineer, and Pre-Sales roles at B2B SaaS companies.</p>

    <h2>What the Job Board Will Include</h2>
    <ul>
        <li><strong>4,250+ SE jobs being tracked</strong> across LinkedIn, Indeed, Greenhouse, Lever, and company career pages</li>
        <li><strong>Updated twice weekly</strong> so you see new postings within days, not weeks</li>
        <li><strong>Salary data where disclosed</strong> from job postings that include compensation ranges</li>
        <li><strong>Filters by seniority, location, and company</strong> to find exactly what you're looking for</li>
        <li><strong>Remote-friendly tagging</strong> so you can filter for remote, hybrid, or on-site roles</li>
    </ul>

    <p>Every listing is verified as a real SE role. We filter out the "solutions engineer" titles that are in reality IT support, implementation, or post-sale positions.</p>

    <h2>Get Notified When This Launches</h2>
    <p>The job board is in development. Subscribe to get notified when it goes live and receive weekly SE job market data in the meantime.</p>

    {_extras_related_links("jobs")}
    {newsletter_cta_html("Get notified when the SE job board launches.")}
    </div>
</div>'''

    html = get_page_wrapper(title, description, "/jobs/", body, active_path="/insights/", extra_head=extra_head)
    write_page("jobs/index.html", html)
    print("  Built: jobs/index.html")


def build_all_extras():
    """Build all placeholder/coming-soon pages."""
    build_companies_index()
    build_reports_index()
    build_conferences_index()
    build_insights_index()
    build_jobs_index()
    return 5
