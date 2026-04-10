import os
import json

from nav_config import *
from templates import (get_page_wrapper, write_page, get_breadcrumb_schema,
                       breadcrumb_html, newsletter_cta_html)


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
            <p>Which tools SE teams actually use, adoption rates by company size, satisfaction scores, and budget benchmarks. Covers demo platforms, RFP tools, conversation intelligence, and more.</p>
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

    {newsletter_cta_html("Get event announcements and SE community updates.")}
    </div>
</div>'''

    html = get_page_wrapper(title, description, "/conferences/", body, active_path="/insights/", extra_head=extra_head)
    write_page("conferences/index.html", html)
    print("  Built: conferences/index.html")


def build_all_extras():
    """Build all placeholder/coming-soon pages."""
    build_companies_index()
    build_reports_index()
    build_conferences_index()
    return 3
