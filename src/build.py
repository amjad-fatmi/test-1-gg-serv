""".

    .venv/bin/python groundgame/src/build.py   ->  groundgame/site/

Writes every page, copies assets, then checks that every internal link
resolves and every page is reachable from the homepage.
"""
import html
import math
import random
import re
import shutil
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent / "site"

# Firm facts. Leave as None until confirmed; the page shows a yellow
# placeholder instead of an invented value.
FIRM = {
    "name": "Ground Game Consulting Services",
    "short": "Ground Game",
    "city": "Las Vegas, Nevada",
    "email": "farrah@groundgameservices.com",
    "phone": "(702) 695-9150",
    "address": None,    # street address, if you want one public
    "form_endpoint": "https://formspree.io/f/xljdnyll",  # contact form inbox (Formspree)
    "year": 2026,
}

NAV = [
    ("index.html", "Home"),
    ("approach.html", "Approach"),
    ("engagements.html", "Engagements"),
    ("firm.html", "The Firm"),
]


def fact(key, label):
    value = FIRM.get(key)
    if value:
        return html.escape(value)
    return f'<span class="todo">[{label}]</span>'


def tel():
    digits = re.sub(r"\D", "", FIRM.get("phone") or "")
    return "+1" + digits if len(digits) == 10 else digits


# ---------------------------------------------------------------- artwork

def topo_svg(seed=7, rings=16, cx=500, cy=500, base=40, step=28, stroke="#b9a27c", accent="#e0784f", width=1000):
    """Contour-line 'terrain' drawn from wobbly concentric rings."""
    rnd = random.Random(seed)
    phases = [rnd.uniform(0, math.tau) for _ in range(4)]
    amps = [rnd.uniform(.06, .14), rnd.uniform(.03, .08), rnd.uniform(.02, .05), rnd.uniform(.01, .03)]
    paths = []
    for i in range(rings):
        r = base + i * step
        pts = []
        for k in range(120):
            a = k / 120 * math.tau
            wob = 1 + sum(amps[j] * math.sin((j + 2) * a + phases[j] + i * .09 * (j + 1)) for j in range(4))
            pts.append((cx + math.cos(a) * r * wob * 1.25, cy + math.sin(a) * r * wob))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
        colour = accent if i == 3 else stroke
        op = .9 if i == 3 else max(.18, .75 - i * .035)
        sw = 1.4 if i == 3 else 1
        paths.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-opacity="{op:.2f}" stroke-width="{sw}"/>')
    marker = f'<circle cx="{cx}" cy="{cy}" r="5" fill="{accent}"/><circle cx="{cx}" cy="{cy}" r="14" fill="none" stroke="{accent}" stroke-opacity=".5"/>'
    return f'<svg viewBox="0 0 {width} 1000" aria-hidden="true" focusable="false">{"".join(paths)}{marker}</svg>'


def grid_figure():
    """Abstract 'district' of blocks, a few highlighted — hints at targeting without saying it."""
    rnd = random.Random(21)
    cells = []
    cols, rows, size, gap = 14, 11, 30, 6
    ox, oy = 44, 40
    hot = {(c, r) for c, r in [(3, 3), (4, 3), (4, 4), (5, 4), (5, 5), (8, 6), (9, 6), (9, 7), (10, 7), (6, 8), (7, 8)]}
    warm = {(c, r) for c, r in [(3, 4), (6, 4), (6, 5), (4, 5), (8, 5), (10, 6), (8, 7), (7, 7), (5, 8), (11, 7)]}
    for r in range(rows):
        for c in range(cols):
            x, y = ox + c * (size + gap), oy + r * (size + gap)
            if (c, r) in hot:
                fill, op = "#e0784f", .95
            elif (c, r) in warm:
                fill, op = "#e0784f", .35
            else:
                fill, op = "#b9a27c", round(rnd.uniform(.06, .2), 2)
            cells.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="2" fill="{fill}" fill-opacity="{op}"/>')
    route = '<path d="M150 170 L186 170 L186 206 L222 206 L222 242 L330 242 L330 278 L366 278 L366 314" fill="none" stroke="#f3eee5" stroke-width="1.5" stroke-dasharray="4 5" stroke-opacity=".7"/>'
    return f'<svg viewBox="0 0 600 480" aria-hidden="true" focusable="false">{"".join(cells)}{route}</svg>'


def curve_figure():
    """Two lines closing on a target: where you are vs. where you need to be."""
    w, h = 600, 480
    need = "M40 400 C 180 380, 300 250, 560 90"
    have = "M40 400 C 180 395, 260 330, 380 270"
    ticks = "".join(f'<line x1="{40 + i * 52}" y1="420" x2="{40 + i * 52}" y2="426" stroke="#b9a27c" stroke-opacity=".6"/>' for i in range(11))
    grid = "".join(f'<line x1="40" y1="{80 + i * 80}" x2="560" y2="{80 + i * 80}" stroke="#b9a27c" stroke-opacity=".12"/>' for i in range(5))
    return (f'<svg viewBox="0 0 {w} {h}" aria-hidden="true" focusable="false">{grid}'
            f'<line x1="40" y1="420" x2="560" y2="420" stroke="#b9a27c" stroke-opacity=".5"/>{ticks}'
            f'<line x1="40" y1="90" x2="560" y2="90" stroke="#e0784f" stroke-opacity=".6" stroke-dasharray="3 6"/>'
            f'<path d="{need}" fill="none" stroke="#f3eee5" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="6 6"/>'
            f'<path d="{have}" fill="none" stroke="#e0784f" stroke-width="2.5"/>'
            f'<circle cx="380" cy="270" r="6" fill="#e0784f"/><circle cx="560" cy="90" r="6" fill="none" stroke="#f3eee5" stroke-width="1.5"/>'
            f'<text x="548" y="74" text-anchor="end" fill="#b9a27c" font-family="Inter, sans-serif" font-size="13" letter-spacing="2">THE NUMBER</text>'
            f'<text x="394" y="296" fill="#f3eee5" fill-opacity=".8" font-family="Inter, sans-serif" font-size="13" letter-spacing="2">TODAY</text>'
            f'<text x="40" y="452" fill="#b9a27c" fill-opacity=".7" font-family="Inter, sans-serif" font-size="12" letter-spacing="2">FILING</text>'
            f'<text x="560" y="452" text-anchor="end" fill="#b9a27c" font-family="Inter, sans-serif" font-size="12" letter-spacing="2">ELECTION DAY</text>'
            f'</svg>')


# Nevada outline from its real border corners (lon/lat projected onto 300x400).
NV_PATH = "M20 20 L278 20 L278 330 L250 338 L253 390 L20 179 Z"
NEVADA = ('<svg viewBox="0 0 300 400" aria-hidden="true" focusable="false">'
          f'<defs><clipPath id="nv-clip"><path d="{NV_PATH}"/></clipPath></defs>'
          '<g clip-path="url(#nv-clip)" stroke="currentColor" stroke-opacity=".25">'
          + "".join(f'<line x1="20" y1="{20 + i * 26}" x2="280" y2="{20 + i * 26}"/>' for i in range(1, 15))
          + '</g>'
          f'<path d="{NV_PATH}" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
          '<circle cx="231" cy="328" r="5" fill="#e0784f"/>'
          '<circle cx="231" cy="328" r="16" fill="none" stroke="#e0784f" stroke-opacity=".55"/>'
          '<circle cx="231" cy="328" r="30" fill="none" stroke="#e0784f" stroke-opacity=".25"/>'
          '<text x="192" y="332" text-anchor="end" fill="currentColor" font-family="Inter, sans-serif" font-size="12" letter-spacing="2">LAS VEGAS</text>'
          '</svg>')

LOGO = ('<svg viewBox="0 0 40 40" aria-hidden="true" focusable="false">'
        '<rect x="1" y="1" width="38" height="38" rx="3" fill="none" stroke="#b9a27c" stroke-opacity=".6"/>'
        '<path d="M8 28 C 14 22, 18 26, 24 18 S 32 12, 33 11" fill="none" stroke="#f3eee5" stroke-width="1.6"/>'
        '<path d="M8 33 C 14 28, 20 31, 26 24 S 32 19, 33 18" fill="none" stroke="#b9a27c" stroke-width="1" stroke-opacity=".7"/>'
        '<circle cx="33" cy="11" r="3" fill="#e0784f"/></svg>')


# ---------------------------------------------------------------- layout

def header(current):
    active = ' aria-current="page"'
    links = "".join(
        f'<a href="{href}"{active if href == current else ""}>{label}</a>'
        for href, label in NAV
    )
    cur = ' aria-current="page"' if current == "contact.html" else ""
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="{FIRM['name']} home">{LOGO}
      <span class="brand-text"><span class="brand-name">Ground Game</span><span class="brand-sub">Consulting Services</span></span></a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span></button>
    <nav class="nav" id="site-nav" aria-label="Main">{links}<a class="btn btn-primary" href="contact.html"{cur}>Start a conversation</a></nav>
  </div>
</header>'''


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="foot-top">
      <div>
        <a class="brand" href="index.html">{LOGO}<span class="brand-text"><span class="brand-name">Ground Game</span><span class="brand-sub">Consulting Services</span></span></a>
        <p>A campaign consultancy in {FIRM['city']}. We help candidates see how the race is won, then help them win it.</p>
      </div>
      <div class="foot-col">
        <h4>Firm</h4>
        <a href="approach.html">Approach</a>
        <a href="engagements.html">Engagements</a>
        <a href="firm.html">The Firm</a>
        <a href="contact.html">Contact</a>
      </div>
      <div class="foot-col">
        <h4>Reach us</h4>
        <a href="mailto:{FIRM['email']}">{fact('email', 'email address')}</a>
        <a href="tel:{tel()}">{fact('phone', 'phone number')}</a>
        <a href="contact.html">{FIRM['city']}</a>
      </div>
    </div>
    <div class="foot-bottom">
      <span>&copy; {FIRM['year']} {FIRM['name']}. All rights reserved.</span>
      <span>All conversations are confidential.</span>
    </div>
  </div>
</footer>'''


def cta(title="Every race has a number. <em>Let&rsquo;s find yours.</em>",
        body="Tell us about the race. We&rsquo;ll tell you honestly what it takes, and whether we&rsquo;re the right team for it."):
    return f'''<section class="cta">
  <div class="cta-topo">{topo_svg(seed=3, rings=12, stroke="#ffffff", accent="#ffffff")}</div>
  <div class="wrap">
    <div><h2>{title}</h2><p>{body}</p></div>
    <a class="btn" href="contact.html">Start a confidential conversation <span class="arr">&rarr;</span></a>
  </div>
</section>'''


def page(filename, title, description, body):
    full_title = FIRM["name"] if filename == "index.html" else f"{title} — {FIRM['name']}"
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#0f1318">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{html.escape(description)}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..500;1,9..144,300..500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
{header(filename)}
<main id="main">
{body}
</main>
{footer()}
<script src="assets/site.js"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- content

PILLARS = [
    ("01", "Read the ground",
     "Before anyone spends a dollar, we work out what winning looks like in your district: how many votes, from where, and from whom."),
    ("02", "Build the machine",
     "A campaign is an organization. The plan, the budget, the people, the money coming in and the money going out, all run on one calendar."),
    ("03", "Win the conversation",
     "What you say, how you say it, and where people see it. Steady when the news is good, and steadier when it isn&rsquo;t."),
    ("04", "Move the field",
     "Neighbors, volunteers and community partners, organized into a plan that turns support into votes, all the way through Election Day."),
]

CADENCE = [
    ("Month one", "Diagnosis", "We study the district and the race until the path is clear."),
    ("Months two–three", "Blueprint", "The number, the map, and the calendar. Written down and agreed."),
    ("The build", "Assemble", "People, tools and systems put in place before they&rsquo;re needed."),
    ("The push", "Pressure", "Steady, measured work. We track it every week and adjust."),
    ("The close", "Deliver", "Every hour of the final stretch goes where it counts most."),
]

TIERS = [
    {
        "label": "Tier one",
        "name": "Groundwork",
        "for": "For candidates deciding whether, and how, to run. A clear read of the race before you commit.",
        "items": ["A full read of your district and the race",
                  "Your number: the votes it takes to win",
                  "A written campaign plan, timeline and budget",
                  "A finance plan with clear fundraising goals",
                  "Setup guidance alongside your treasurer"],
        "inherit": None,
    },
    {
        "label": "Tier two",
        "name": "Campaign",
        "featured": True,
        "for": "For declared campaigns that need the plan turned into daily work, and the people to reach.",
        "items": ["Day-to-day campaign management support",
                  "Your field plan, mapped and ready to run",
                  "Your message, talking points and online presence",
                  "A fundraising program you can run every week",
                  "Weekly tracking against the number"],
        "inherit": "Everything in Groundwork",
    },
    {
        "label": "Tier three",
        "name": "Full Ground Game",
        "for": "For competitive races that need a senior team in the room from start to finish.",
        "items": ["A dedicated senior team, embedded",
                  "Press, debates and rapid response",
                  "Creative and paid media, start to finish",
                  "Community partnerships and public events",
                  "Early vote and Election Day operations"],
        "inherit": "Everything in Campaign",
    },
]

# (capability, groundwork, campaign, full)  —  2 = included, 1 = limited, 0 = not included
COMPARE = [
    ("Strategy", [
        ("Campaign plan, timeline and budget", 2, 2, 2),
        ("District analysis and path to win", 2, 2, 2),
        ("Staffing and vendor coordination", 0, 1, 2),
    ]),
    ("Research", [
        ("Voter and turnout research", 1, 2, 2),
        ("Opinion research and candidate research", 0, 1, 2),
    ]),
    ("Field", [
        ("Field plan, territory and volunteers", 0, 2, 2),
        ("Voter contact programs", 0, 2, 2),
        ("Early vote and Election Day operations", 0, 1, 2),
    ]),
    ("Finance", [
        ("Fundraising plan and goals", 2, 2, 2),
        ("Donor research and call time", 0, 2, 2),
        ("Fundraising events and organizational outreach", 0, 1, 2),
    ]),
    ("Message", [
        ("Message and talking points", 1, 2, 2),
        ("Press, speeches and debate preparation", 0, 1, 2),
        ("Rapid response", 0, 1, 2),
    ]),
    ("Media and creative", [
        ("Online and social content", 0, 1, 2),
        ("Print, mail, video and ad placement", 0, 0, 2),
    ]),
    ("Community", [
        ("Coalition and community relationships", 0, 1, 2),
        ("Public events", 0, 1, 2),
    ]),
    ("Operations", [
        ("Campaign calendar and spending tracking", 1, 2, 2),
        ("Coordination with your treasurer and attorney", 1, 2, 2),
    ]),
]

FAQ = [
    ("What does an engagement cost?",
     "It depends on the size of the district, the timeline, and how competitive the race is. After a first conversation we send a written scope with one clear price. No surprises, no hidden add-ons."),
    ("Can we start with one tier and move up?",
     "Yes. Many candidates start with Groundwork to decide whether to run, then move to Campaign or Full Ground Game. The work we&rsquo;ve already done together carries forward."),
    ("How early should we talk to you?",
     "As early as you can. The most valuable decisions in a race are made months before most people are paying attention. It&rsquo;s never too early to know your number."),
    ("What kinds of races do you take?",
     "Candidates and causes across Nevada, from local and county seats to legislative and congressional districts. We take a limited number of races each cycle so every client gets our full attention."),
    ("Do you replace our treasurer or lawyer?",
     "No. We work alongside them. We keep the calendar, track spending and make sure nothing slips, while your treasurer and attorney handle filings and legal advice."),
    ("We already have vendors. Can you work with them?",
     "Yes. We can coordinate the vendors you have, bring in ones we trust, or both. Either way, everyone works from one plan."),
    ("Will you tell us if we can&rsquo;t win?",
     "Yes. An honest read is the most useful thing we can give you. If the path isn&rsquo;t there, we&rsquo;ll say so and show you why."),
    ("Is our conversation confidential?",
     "Always. We don&rsquo;t publish client lists, and nothing you share with us leaves the room."),
]


def home():
    pillars = "".join(
        f'<div class="pillar reveal"><span class="num">{n}</span><h3>{t}</h3><p>{d}</p></div>'
        for n, t, d in PILLARS)
    steps = "".join(
        f'<div class="step reveal"><span class="when">{w}</span><h3>{t}</h3><p>{d}</p></div>'
        for w, t, d in CADENCE)
    return f'''
<section class="hero dark">
  <div class="hero-topo">{topo_svg()}</div>
  <div class="wrap">
    <span class="eyebrow">Campaign strategy &middot; {FIRM['city']}</span>
    <h1>Know how you win <em>before</em> you start running.</h1>
    <p class="lede">Ground Game is a team of campaign professionals who study races for a living. We help candidates see the path to victory, then walk it with them, one door and one day at a time.</p>
    <div class="btn-row">
      <a class="btn btn-primary" href="contact.html">Start a conversation <span class="arr">&rarr;</span></a>
      <a class="btn btn-ghost" href="approach.html">How we work</a>
    </div>
  </div>
  <div class="hero-meta"><div class="wrap">
    <span><b>Built in Nevada</b></span><span>Local &middot; Legislative &middot; Congressional</span><span>Strictly confidential</span>
  </div></div>
</section>

<section class="pad statement">
  <div class="wrap reveal">
    <span class="eyebrow">What we believe</span>
    <p>Most campaigns run on instinct and hope. <span>The ones that win know their number, know where it lives, and know exactly when to go get it.</span></p>
  </div>
</section>

<section class="pad bone">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">How we think</span><h2>Four disciplines. <em>One plan.</em></h2></div>
      <p class="lede">We don&rsquo;t sell pieces of a campaign. Everything we do fits together, because in a close race the gaps are where you lose.</p>
    </div>
    <div class="pillars">{pillars}</div>
  </div>
</section>

<section class="pad dark">
  <div class="wrap">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow">The numbers behind the race</span>
        <h2>We start with the math. <em>Then we go outside.</em></h2>
        <p class="lede" style="margin-top:26px">Every district has a winning number and a map of where those votes live. We find both, then build the calendar backwards from Election Day, so you know what needs to happen and when.</p>
        <a class="link-arrow" href="approach.html">Read our approach &rarr;</a>
      </div>
      <div class="figure reveal">{curve_figure()}</div>
    </div>
  </div>
</section>

<section class="pad dark" style="padding-top:0">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">The cadence</span><h2>Timing is <em>strategy.</em></h2></div>
      <p class="lede">Doing the right thing too early wastes money. Doing it too late loses races. Every engagement follows a rhythm built around your election date.</p>
    </div>
    <div class="cadence">{steps}</div>
  </div>
</section>

<section class="pad">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">Engagements</span><h2>Three ways to <em>work with us.</em></h2></div>
      <p class="lede">Each tier is a complete package, scoped to your race. Pick the level of support you need now and move up when you&rsquo;re ready.</p>
    </div>
    {tiers_html(compact=True)}
    <p class="tier-note">Every engagement is priced per race after a first conversation. <a class="link-arrow" href="engagements.html">Compare tiers in detail &rarr;</a></p>
  </div>
</section>

<section class="pad bone">
  <div class="wrap nv">
    <div class="reveal">
      <span class="eyebrow">Home ground</span>
      <h2>Nevada is <em>our</em> district.</h2>
      <p class="lede" style="margin-top:24px">We live here. We know its neighborhoods, its communities, its calendar and its rules. That local knowledge shows up in every plan we write, and in every conversation on every doorstep.</p>
      <a class="link-arrow" href="firm.html">Meet the firm &rarr;</a>
    </div>
    <div class="nv-map reveal">{NEVADA}</div>
  </div>
</section>

{cta()}
'''


def tiers_html(compact=False):
    out = []
    for t in TIERS:
        feat = " featured" if t.get("featured") else ""
        badge = '<span class="badge">Most chosen</span>' if t.get("featured") else ""
        items = t["items"][:4] if compact else t["items"]
        inherit = f'<li class="inherit">{t["inherit"]}</li>' if t["inherit"] else ""
        lis = inherit + "".join(f"<li>{i}</li>" for i in items)
        btn_cls = "btn-primary" if feat else "btn-ghost"
        out.append(f'''<article class="tier{feat} reveal">{badge}
  <span class="tier-label">{t["label"]}</span>
  <h3>{t["name"]}</h3>
  <p class="for">{t["for"]}</p>
  <ul>{lis}</ul>
  <a class="btn {btn_cls}" href="contact.html">Ask about {t["name"]} <span class="arr">&rarr;</span></a>
</article>''')
    return f'<div class="tiers">{"".join(out)}</div>'


def approach():
    phases = [
        ("Diagnosis", "We study the district: who votes, who doesn&rsquo;t, how they&rsquo;ve voted before, and what&rsquo;s changed. We talk to people on the ground. By the end, we can tell you plainly what this race will take."),
        ("Blueprint", "We write down the number of votes you need, where they are, and who can be persuaded. Then we build a calendar backwards from Election Day, so every week has a job."),
        ("Assemble", "We put the right people, tools and systems in place before they&rsquo;re needed, so nothing is rushed when it matters."),
        ("Pressure", "The plan goes to work. We measure progress every week against the number and move resources to where they&rsquo;ll do the most good."),
        ("Deliver", "In the final stretch, every hour and every dollar goes to the people who will decide the race. Then we make sure they show up."),
    ]
    rows = "".join(f'<div class="list-row reveal"><h3>{t}</h3><p>{d}</p></div>' for t, d in phases)
    principles = [
        ("Evidence over instinct", "Gut feeling has its place. We check it against the numbers first."),
        ("One plan, not ten vendors", "Strategy, field, money, message and media all work from the same map and the same calendar."),
        ("Honest about the odds", "We&rsquo;ll tell you what we see, even when it&rsquo;s not what you hoped to hear."),
        ("Ready for the bad day", "Every campaign has one. We plan for it in advance, so it doesn&rsquo;t become the story."),
        ("Community first", "We build relationships around the issues people care about, not assumptions about who they are."),
        ("By the book", "Every dollar tracked, every deadline met, and your treasurer and attorney in the loop from day one."),
    ]
    kick = "".join(f'<div class="kicker reveal"><h3>{t}</h3><p>{d}</p></div>' for t, d in principles)
    return f'''
<section class="hero page-hero dark">
  <div class="hero-topo">{topo_svg(seed=11, rings=14)}</div>
  <div class="wrap">
    <span class="eyebrow">Approach</span>
    <h1>A method, <em>not a mood.</em></h1>
    <p class="lede">Campaigns are won by the people who understand the race best and act on it soonest. Our work follows one discipline, from the first conversation to the final count.</p>
  </div>
</section>

<section class="pad">
  <div class="wrap split top">
    <div class="reveal">
      <span class="eyebrow">Where it starts</span>
      <h2>Every race comes down to <em>a number.</em></h2>
    </div>
    <div class="reveal">
      <p class="lede">How many votes does it take to win? Where do those voters live? Who is already with you, who could be, and who never will be?</p>
      <p>Most campaigns can&rsquo;t answer these questions with confidence. Ours can. Once we know the answers, every other decision gets easier: where to spend time, where to spend money, what to say, and when to say it.</p>
      <p>We call it knowing your ground. Everything else is built on top of it.</p>
    </div>
  </div>
</section>

<section class="pad dark">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">Five phases</span><h2>From first look <em>to final count.</em></h2></div>
      <p class="lede">Each phase has clear outputs you can see and hold us to. You always know where the campaign stands.</p>
    </div>
    <div class="list-rows">{rows}</div>
  </div>
</section>

<section class="pad">
  <div class="wrap split">
    <div class="figure reveal">{grid_figure()}</div>
    <div class="reveal">
      <span class="eyebrow">Precision</span>
      <h2>Not everyone. <em>The right ones.</em></h2>
      <p class="lede" style="margin-top:24px">A campaign that tries to talk to everyone ends up reaching no one. We find the specific neighborhoods, blocks and people who will decide your race, and focus there.</p>
      <p>It&rsquo;s the difference between being busy and being effective.</p>
    </div>
  </div>
</section>

<section class="pad bone">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">Principles</span><h2>How we <em>carry ourselves.</em></h2></div>
      <p class="lede">The way we work matters as much as the work itself.</p>
    </div>
    <div class="kicker-grid">{kick}</div>
  </div>
</section>

{cta()}
'''


def engagements():
    def cell(v):
        if v == 2:
            return '<td><span class="dot" role="img" aria-label="Included"></span></td>'
        if v == 1:
            return '<td><span class="dot half" role="img" aria-label="Limited"></span></td>'
        return '<td><span class="dash" aria-label="Not included">&mdash;</span></td>'

    body_rows = []
    for group, rows in COMPARE:
        body_rows.append(f'<tr class="group"><td colspan="4">{group}</td></tr>')
        for name, a, b, c in rows:
            body_rows.append(f"<tr><td>{name}</td>{cell(a)}{cell(b)}{cell(c)}</tr>")
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
    return f'''
<section class="hero page-hero dark">
  <div class="hero-topo">{topo_svg(seed=5, rings=14)}</div>
  <div class="wrap">
    <span class="eyebrow">Engagements</span>
    <h1>Complete packages. <em>No piecework.</em></h1>
    <p class="lede">We work in three tiers. Each one is a full, connected set of support, sized to where your campaign is today.</p>
  </div>
</section>

<section class="pad bone">
  <div class="wrap">
    {tiers_html()}
    <p class="tier-note">Pricing is set per race, based on district size, timeline and how competitive the contest is. You get a written scope and one clear price before any work begins.</p>
  </div>
</section>

<section class="pad">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">Side by side</span><h2>Compare <em>the tiers.</em></h2></div>
      <p class="lede">A high-level view. The details are shaped around your race in our first conversations.</p>
    </div>
    <div class="compare-wrap reveal">
      <table class="compare">
        <thead><tr><th scope="col">What&rsquo;s included</th><th scope="col">Groundwork</th><th scope="col" class="hl">Campaign</th><th scope="col">Full Ground Game</th></tr></thead>
        <tbody>{"".join(body_rows)}</tbody>
      </table>
    </div>
    <div class="legend"><span><span class="dot"></span> Included</span><span><span class="dot half"></span> Limited</span><span><span class="dash">&mdash;</span> Not included</span></div>
  </div>
</section>

<section class="pad bone">
  <div class="wrap split top">
    <div class="reveal">
      <span class="eyebrow">Questions</span>
      <h2>Good questions <em>to ask us.</em></h2>
      <p class="lede" style="margin-top:24px">Don&rsquo;t see yours? <a class="link-arrow" href="contact.html">Ask us directly</a>.</p>
    </div>
    <div class="faq reveal">{faq}</div>
  </div>
</section>

{cta(title="Not sure which tier fits? <em>Neither are most.</em>",
     body="Start with a conversation. We&rsquo;ll recommend the right level of support for your race, and we&rsquo;ll tell you if you need less than you think.")}
'''


def firm():
    values = [
        ("Discretion", "We don&rsquo;t list clients or talk about races in public. What happens in a campaign stays with the campaign."),
        ("Rigor", "Every recommendation we make can be traced back to evidence. If we can&rsquo;t show our work, we don&rsquo;t make the call."),
        ("Candor", "We tell candidates the truth about their race. It&rsquo;s the most valuable thing we offer."),
    ]
    vals = "".join(f'<div class="list-row reveal"><h3>{t}</h3><p>{d}</p></div>' for t, d in values)
    who = [
        ("Analysts", "People who read election results, voter files and district maps the way others read the news."),
        ("Strategists", "People who have sat in the room when the hard calls get made, and made them."),
        ("Organizers", "People who have built volunteer teams and run programs on the ground, in heat and in cold."),
        ("Communicators", "People who know how to find the right words, and how to keep a campaign calm when the phone won&rsquo;t stop ringing."),
        ("Fundraisers", "People who know that a campaign runs on the money it raises, and how to raise it the right way."),
        ("Operators", "People who keep the calendar, the budget and the paperwork in order, so the candidate can focus on voters."),
    ]
    kick = "".join(f'<div class="kicker reveal"><h3>{t}</h3><p>{d}</p></div>' for t, d in who)
    return f'''
<section class="hero page-hero dark">
  <div class="hero-topo">{topo_svg(seed=17, rings=14)}</div>
  <div class="wrap">
    <span class="eyebrow">The Firm</span>
    <h1>A small team <em>that wins close races.</em></h1>
    <p class="lede">Ground Game Consulting Services is a {FIRM['city']} firm of campaign professionals. We combine deep skill with numbers and hard-won experience on the ground.</p>
  </div>
</section>

<section class="pad">
  <div class="wrap split top">
    <div class="reveal">
      <span class="eyebrow">Why we exist</span>
      <h2>Good candidates <em>lose</em> for avoidable reasons.</h2>
    </div>
    <div class="reveal">
      <p class="lede">They start too late. They talk to the wrong people. They spend in the wrong places. They get caught off guard.</p>
      <p>We started Ground Game to fix that. We give candidates the kind of clear, honest, numbers-first thinking that used to be available only to the biggest campaigns, and we pair it with a team that knows how to turn a plan into votes.</p>
      <p>We take a limited number of races each cycle. That&rsquo;s deliberate. Every client gets senior attention, not a junior account manager.</p>
    </div>
  </div>
</section>

<section class="pad bone">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">Who we are</span><h2>The whole campaign, <em>one team.</em></h2></div>
      <p class="lede">Most campaigns stitch these people together from different firms. We bring them to the table as one team.</p>
    </div>
    <div class="kicker-grid">{kick}</div>
  </div>
</section>

<section class="pad dark">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">What we stand for</span><h2>The way <em>we work.</em></h2></div>
      <p class="lede">Three commitments we make to every candidate who works with us.</p>
    </div>
    <div class="list-rows">{vals}</div>
  </div>
</section>

<section class="pad">
  <div class="wrap nv">
    <div class="reveal">
      <span class="eyebrow">Based in</span>
      <h2>{FIRM['city']}.</h2>
      <p class="lede" style="margin-top:24px">We work across the state, from the Las Vegas valley to the rural counties. Knowing a place well is not something you can fly in.</p>
    </div>
    <div class="nv-map reveal">{NEVADA}</div>
  </div>
</section>

{cta(title="Thinking about a run? <em>Talk to us first.</em>")}
'''


def contact():
    return f'''
<section class="hero page-hero dark">
  <div class="hero-topo">{topo_svg(seed=29, rings=14)}</div>
  <div class="wrap">
    <span class="eyebrow">Contact</span>
    <h1>Start a <em>confidential</em> conversation.</h1>
    <p class="lede">Tell us a little about the race. A senior member of our team will read it and reply personally.</p>
  </div>
</section>

<section class="pad">
  <div class="wrap contact-grid">
    <div class="contact-aside reveal">
      <span class="eyebrow">What happens next</span>
      <h2 style="font-size:clamp(28px,3vw,38px)">A first call, <em>no obligation.</em></h2>
      <p class="lede" style="margin-top:20px">We&rsquo;ll listen, ask questions about the district and your goals, and give you an honest first read. If it&rsquo;s a fit, we&rsquo;ll follow up with a written scope.</p>
      <dl>
        <dt>Email</dt><dd><a href="mailto:{FIRM['email']}">{fact('email', 'email address')}</a></dd>
        <dt>Phone</dt><dd><a href="tel:{tel()}">{fact('phone', 'phone number')}</a></dd>
        <dt>Office</dt><dd>{fact('address', 'street address') + '<br>' if FIRM['address'] else ''}{FIRM['city']}</dd>
      </dl>
    </div>
    <form class="form reveal" id="inquiry" action="{FIRM['form_endpoint']}" method="POST">
      <input type="hidden" name="_subject" value="New inquiry from the Ground Game website">
      <div class="hp" aria-hidden="true"><label for="f-gotcha">Leave this empty</label><input id="f-gotcha" name="_gotcha" tabindex="-1" autocomplete="off"></div>
      <div class="form-grid">
        <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
        <div class="field"><label for="f-role">Your role</label>
          <select id="f-role" name="role"><option>Candidate</option><option>Campaign manager or staff</option><option>Party or committee</option><option>Cause or ballot measure</option><option>Other</option></select></div>
        <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
        <div class="field"><label for="f-phone">Phone <small>(optional)</small></label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
        <div class="field"><label for="f-office">Office or race</label><input id="f-office" name="office" placeholder="e.g. State Assembly"></div>
        <div class="field"><label for="f-district">District or area</label><input id="f-district" name="district" placeholder="e.g. Clark County"></div>
        <div class="field"><label for="f-date">Election date <small>(if known)</small></label><input id="f-date" name="date" type="date"></div>
        <div class="field"><label for="f-stage">Where are you now?</label>
          <select id="f-stage" name="stage"><option>Thinking about running</option><option>Planning to file</option><option>Filed and running</option><option>Mid-campaign, need help</option></select></div>
        <div class="field full"><label for="f-tier">Which engagement interests you?</label>
          <select id="f-tier" name="engagement"><option>Not sure yet</option><option>Groundwork</option><option>Campaign</option><option>Full Ground Game</option></select></div>
        <div class="field full"><label for="f-msg">Tell us about the race</label><textarea id="f-msg" name="message" required placeholder="What's on your mind? Anything you share stays confidential."></textarea></div>
      </div>
      <div class="form-foot">
        <p>Your details are used only to reply to you. We never sell them.</p>
        <button class="btn btn-primary" type="submit">Send inquiry <span class="arr">&rarr;</span></button>
      </div>
      <p class="form-status" id="form-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>
'''


def not_found():
    return f'''
<section class="hero page-hero dark">
  <div class="hero-topo">{topo_svg(seed=41, rings=14)}</div>
  <div class="wrap">
    <span class="eyebrow">Page not found</span>
    <h1>This ground is <em>unmapped.</em></h1>
    <p class="lede">The page you were looking for isn&rsquo;t here. It may have moved, or the link may be out of date.</p>
    <div class="btn-row">
      <a class="btn btn-primary" href="/">Back to the homepage <span class="arr">&rarr;</span></a>
      <a class="btn btn-ghost" href="/contact.html">Contact us</a>
    </div>
  </div>
</section>
'''


PAGES = [
    ("index.html", "Home", "Ground Game Consulting Services is a Las Vegas campaign consultancy. We help candidates see how they win, then help them win.", home),
    ("approach.html", "Approach", "Our method: find the number, map the ground, build the calendar, and run the plan to Election Day.", approach),
    ("engagements.html", "Engagements", "Three complete engagement tiers — Groundwork, Campaign and Full Ground Game — scoped and priced per race.", engagements),
    ("firm.html", "The Firm", "A small Las Vegas team of analysts, organizers and strategists who help candidates win close races.", firm),
    ("contact.html", "Contact", "Start a confidential conversation with Ground Game Consulting Services.", contact),
]

FAVICON = LOGO.replace('<svg viewBox="0 0 40 40"', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"').replace(
    'aria-hidden="true" focusable="false">', '><rect width="40" height="40" rx="6" fill="#0f1318"/>', 1)


# ---------------------------------------------------------------- build + check

def check_routes():
    href_re = re.compile(r'(?:href|src)="([^"#:?]+)(?:[#?][^"]*)?"')
    pages = {p.name for p in OUT.glob("*.html")} - {"404.html"}
    links, broken = {}, []
    for name in pages:
        text = (OUT / name).read_text()
        targets = set(href_re.findall(text))
        links[name] = {t for t in targets if t.endswith(".html")}
        for t in targets:
            if not (OUT / t).exists():
                broken.append((name, t))
    seen, queue = {"index.html"}, ["index.html"]
    while queue:
        for nxt in sorted(links.get(queue.pop(0), ())):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    unreachable = pages - seen
    if broken or unreachable:
        raise SystemExit(f"Route check failed. Broken: {broken}  Unreachable: {sorted(unreachable)}")
    (OUT / "_routes.txt").write_text("\n".join(sorted(seen)) + "\n")
    return sorted(seen)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for f in (SRC / "assets").iterdir():
        shutil.copy(f, OUT / "assets" / f.name)
    (OUT / "assets" / "favicon.svg").write_text(FAVICON)
    for filename, title, desc, fn in PAGES:
        (OUT / filename).write_text(page(filename, title, desc, fn()))
    # Netlify serves 404.html for unknown paths. It sits outside the route
    # check, and uses root-relative URLs so it works at any depth.
    missing = page("404.html", "Page not found", "This page could not be found.", not_found())
    missing = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/)', r'\1="/', missing)
    (OUT / "404.html").write_text(missing)
    routes = check_routes()
    print(f"Built {len(PAGES)} pages -> {OUT}")
    print("Route check OK:", ", ".join(routes))


if __name__ == "__main__":
    main()
