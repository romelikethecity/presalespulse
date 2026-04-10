SITE_NAME = "PreSales Pulse"
SITE_URL = "https://presalespulse.com"
SITE_TAGLINE = "Career intelligence for solutions engineers"
COPYRIGHT_YEAR = "2026"
CURRENT_YEAR = 2026
CSS_VERSION = "1"

CTA_HREF = "/newsletter/"
CTA_LABEL = "Get the Weekly Pulse"

SIGNUP_WORKER_URL = "https://presales-newsletter-signup.rome-workers.workers.dev/subscribe"

GA_MEASUREMENT_ID = ""
GOOGLE_SITE_VERIFICATION = ""
GOOGLE_SITE_VERIFICATION_META = ""

NAV_ITEMS = [
    {
        "href": "/salary/",
        "label": "Salary Data",
        "children": [
            {"href": "/salary/", "label": "Salary Index"},
            {"href": "/salary/by-seniority/", "label": "By Seniority"},
            {"href": "/salary/by-location/", "label": "By Location"},
            {"href": "/salary/by-company-stage/", "label": "By Company Stage"},
            {"href": "/salary/comparisons/", "label": "Comparisons"},
            {"href": "/salary/calculator/", "label": "Salary Calculator"},
        ],
    },
    {
        "href": "/tools/",
        "label": "Tools",
        "children": [
            {"href": "/tools/", "label": "Tools Index"},
            {"href": "/tools/category/demo-platforms/", "label": "Tool Categories"},
        ],
    },
    {
        "href": "/careers/",
        "label": "Careers",
        "children": [
            {"href": "/careers/", "label": "Career Guides"},
            {"href": "/careers/what-is-solutions-engineer/", "label": "What is an SE?"},
        ],
    },
    {"href": "/glossary/", "label": "Glossary"},
    {
        "href": "/insights/",
        "label": "Resources",
        "children": [
            {"href": "/insights/", "label": "Insights"},
            {"href": "/jobs/", "label": "Job Board"},
            {"href": "/companies/", "label": "Companies"},
            {"href": "/reports/", "label": "Reports"},
        ],
    },
]

FOOTER_COLUMNS = {
    "Salary Data": [
        {"href": "/salary/", "label": "Salary Index"},
        {"href": "/salary/by-seniority/", "label": "By Seniority"},
        {"href": "/salary/by-location/", "label": "By Location"},
        {"href": "/salary/by-company-stage/", "label": "By Stage"},
        {"href": "/salary/comparisons/", "label": "Comparisons"},
        {"href": "/salary/calculator/", "label": "Calculator"},
        {"href": "/salary/methodology/", "label": "Methodology"},
    ],
    "Resources": [
        {"href": "/tools/", "label": "SE Tools"},
        {"href": "/careers/", "label": "Career Guides"},
        {"href": "/glossary/", "label": "Glossary"},
        {"href": "/insights/", "label": "Insights"},
        {"href": "/jobs/", "label": "Job Board"},
        {"href": "/newsletter/", "label": "Newsletter"},
        {"href": "/about/", "label": "About"},
    ],
    "Site": [
        {"href": "/privacy/", "label": "Privacy Policy"},
        {"href": "/terms/", "label": "Terms of Service"},
        {"href": "/salary/methodology/", "label": "Methodology"},
    ],
    "SE Tools & Resources": [
        {"href": "https://gtmepulse.com", "label": "GTME Pulse", "external": True},
        {"href": "https://thecspulse.com", "label": "The CS Pulse", "external": True},
        {"href": "https://therevopsreport.com", "label": "RevOps Report", "external": True},
        {"href": "https://b2bsalestools.com", "label": "B2B Sales Tools", "external": True},
    ],
}
