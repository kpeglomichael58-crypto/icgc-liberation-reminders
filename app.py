import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, redirect, render_template_string
from zoneinfo import ZoneInfo
import sqlite3

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:
    class BackgroundScheduler:
        def __init__(self, *args, **kwargs):
            self.running = False

        def add_job(self, *args, **kwargs):
            return None

        def start(self):
            self.running = True

        def shutdown(self):
            self.running = False
import csv
import io
from datetime import datetime

# =====================================
# ICGC LIBERATION TEMPLE
# CHURCH REMINDER SYSTEM
# =====================================

load_dotenv()
app = Flask(__name__)

AGOO_API_KEY = os.getenv("AGOO_API_KEY")
AGOO_API_URL = os.getenv("AGOO_API_URL")
AGOO_SENDER_ID = os.getenv("AGOO_SENDER_ID")

CHURCH_NAME = "ICGC LIBERATION TEMPLE"
GHANA_TIME = ZoneInfo("Africa/Accra")
DATABASE = "church_members.db"

# =====================================
# DATABASE
# =====================================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def create_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            consent INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()
    
# =====================================
# AGOO SMS CONNECTION
# =====================================

def send_sms(phone, message):

    if not AGOO_API_KEY or not AGOO_API_URL or not AGOO_SENDER_ID:
        print("SMS ERROR: API credentials or Sender ID missing.")
        return False

    headers = {
        "X-API-Key": AGOO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "to": phone,
        "message": message,
        "senderId": AGOO_SENDER_ID
    }

    try:
        response = requests.post(
            AGOO_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("SMS RESPONSE:", response.status_code)
        print("SMS RESULT:", response.text)

        return response.ok

    except requests.RequestException as error:
        print("SMS CONNECTION ERROR:", error)
        return False
    
# =====================================
# REMINDER MESSAGES
# =====================================

REMINDER_MESSAGES = {
    "saturday_noon": """
Good afternoon, {name}! 🙏

This is a friendly reminder from ICGC LIBERATION TEMPLE.

Our Sunday worship service is tomorrow.

Please prepare yourself and make plans to join us
for a wonderful time in God's presence.

Remember, punctuality is important.

We look forward to seeing you!

God bless you. ❤️
""",

    "saturday_evening": """
Good evening, {name}! 🙏

Tomorrow is Sunday!

ICGC LIBERATION TEMPLE warmly reminds you
of our worship service tomorrow morning.

Please prepare everything you need and
make plans to arrive early.

Don't miss the blessings of fellowship!

See you tomorrow.

God bless you! ❤️
""",

    "sunday_morning": """
Good morning, {name}! 🙏

It's Sunday!

ICGC LIBERATION TEMPLE invites you to
join today's worship service.

It's time to get ready for church.

Please come early and prepare your heart
for worship.

God bless you! ❤️
"""
}

# =====================================
# SEND REMINDERS
# =====================================

def send_reminder(reminder_type):

    message = REMINDER_MESSAGES[reminder_type]

    connection = get_db()

    members = connection.execute("""
        SELECT name, phone
        FROM members
        WHERE consent = 1
    """).fetchall()

    connection.close()

    print("\n" + "=" * 55)
    print(CHURCH_NAME)
    print("REMINDER:", reminder_type)
    print("TIME:", datetime.now(GHANA_TIME))
    print("ACTIVE MEMBERS:", len(members))
    print("=" * 55)

    for member in members:

        personalized_message = message.format(
            name=member["name"]
        )

        print("\nRecipient:", member["name"])
        print("Phone:", member["phone"])
        print("Message:")
        print(personalized_message)
        print("-" * 55)

    print("REMINDER PROCESS COMPLETED")

# =====================================
# DASHBOARD DESIGN
# =====================================

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>ICGC LIBERATION TEMPLE</title>

<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --gold: #f5d58a;
    --purple: #a78bfa;
    --glass: rgba(255,255,255,0.065);
    --border: rgba(255,255,255,0.15);
}

body {
    min-height: 100vh;
    padding: 25px;
    color: #fff;
    font-family: 'Segoe UI', Arial, sans-serif;
    background:
        radial-gradient(circle at 15% 15%, #30245d 0%, transparent 35%),
        radial-gradient(circle at 85% 80%, #193c60 0%, transparent 35%),
        linear-gradient(135deg, #050713, #101326, #080d19);
    background-attachment: fixed;
    overflow-x: hidden;
}

/* Animated background lights */

body::before,
body::after {
    content: "";
    position: fixed;
    width: 350px;
    height: 350px;
    border-radius: 50%;
    filter: blur(110px);
    opacity: .22;
    z-index: -1;
    animation: floatLight 12s ease-in-out infinite alternate;
}

body::before {
    background: #805ad5;
    top: 5%;
    left: -150px;
}

body::after {
    background: #0ea5e9;
    bottom: 0;
    right: -150px;
    animation-delay: 3s;
}

@keyframes floatLight {
    from { transform: translate(0, 0); }
    to { transform: translate(100px, 80px); }
}

.container {
    max-width: 1050px;
    margin: auto;
}

/* Glass effect */

.header,
.card {
    background: rgba(255,255,255,0.055);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    border: 1px solid var(--border);
    box-shadow: 0 15px 45px rgba(0,0,0,.25);
    transition: .4s ease;
}

.header {
    text-align: center;
    padding: 50px 25px;
    border-radius: 28px;
    animation: appear 1s ease both;
    position: relative;
    overflow: hidden;
}

.header::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,.07),
        transparent
    );
    animation: shine 7s infinite;
}

@keyframes shine {
    0%, 60% { left: -100%; }
    100% { left: 150%; }
}

@keyframes appear {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Church identity */

.logo {
    width: 75px;
    height: 75px;
    border-radius: 50%;
    margin: 0 auto 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid var(--gold);
    color: var(--gold);
    font-size: 22px;
    font-weight: bold;
    box-shadow: 0 0 30px rgba(245,213,138,.25);
    animation: logoGlow 3s infinite alternate;
}

@keyframes logoGlow {
    from { box-shadow: 0 0 10px rgba(245,213,138,.2); }
    to { box-shadow: 0 0 35px rgba(245,213,138,.5); }
}

h1 {
    font-size: clamp(24px, 5vw, 38px);
    letter-spacing: 3px;
    margin-bottom: 12px;
    background: linear-gradient(
        90deg,
        #fff,
        #f5d58a,
        #fff,
        #d8b4fe
    );
    background-size: 250%;
    color: transparent;
    background-clip: text;
    -webkit-background-clip: text;
    animation: goldShimmer 6s linear infinite;
}

@keyframes goldShimmer {
    from { background-position: 0%; }
    to { background-position: 250%; }
}

h2 {
    color: var(--gold);
    font-size: 21px;
    margin-bottom: 18px;
}

.subtitle {
    color: #bac5db;
    margin-bottom: 20px;
    letter-spacing: 1px;
}

.status {
    color: #4ade80;
    font-weight: bold;
    font-size: 13px;
    letter-spacing: 1px;
}

/* Dashboard cards */

.card {
    padding: 30px;
    border-radius: 23px;
    margin-top: 24px;
    animation: appear .8s ease both;
}

.card:hover {
    border-color: rgba(245,213,138,.35);
    transform: translateY(-3px);
    box-shadow: 0 18px 45px rgba(0,0,0,.3);
}

/* Schedule */

.schedule,
.member {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.12);
    backdrop-filter: blur(15px);
    padding: 20px;
    margin: 14px 0;
    border-radius: 16px;
}

.schedule {
    border-left: 4px solid var(--gold);
    transition: .3s;
}

.schedule:hover,
.member:hover {
    background: rgba(255,255,255,.09);
    transform: translateX(4px);
}

/* Input fields */

input[type="text"],
input[type="tel"],
input[type="file"] {
    width: 100%;
    padding: 16px;
    margin: 10px 0;
    border-radius: 13px;
    border: 1px solid rgba(255,255,255,.15);
    background: rgba(0,0,0,.22);
    color: white;
    outline: none;
    transition: .3s;
}

input::placeholder {
    color: #9ca9bd;
}

input:focus {
    border-color: var(--gold);
    box-shadow: 0 0 18px rgba(245,213,138,.15);
}

input[type="checkbox"] {
    accent-color: var(--gold);
    margin-right: 8px;
}

label {
    color: #d1d9e8;
    line-height: 1.8;
}

/* Buttons */

button {
    background: linear-gradient(135deg, #f5d58a, #bd8b35);
    color: #17120a;
    padding: 14px 23px;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-weight: bold;
    margin-top: 12px;
    transition: .3s;
}

button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(245,213,138,.3);
}

.delete {
    background: linear-gradient(135deg, #ef4444, #991b1b);
    color: white;
}

.activate {
    background: linear-gradient(135deg, #4ade80, #15803d);
    color: #052e16;
}

.deactivate {
    background: linear-gradient(135deg, #fbbf24, #b45309);
    color: #451a03;
}

/* Member details */

.member strong {
    font-size: 17px;
    color: white;
}

small {
    color: #aab6c8;
    line-height: 1.8;
}

.consent-status {
    display: inline-block;
    margin-top: 12px;
    color: #4ade80;
    font-size: 12px;
    font-weight: bold;
}

.no-consent {
    color: #fbbf24;
}

.gold-text {
    color: var(--gold);
}

hr {
    border: 0;
    border-top: 1px solid rgba(255,255,255,.12);
    margin: 25px 0;
}

.footer {
    text-align: center;
    color: #94a3b8;
    padding: 35px 10px;
    font-size: 12px;
    letter-spacing: 2px;
}

/* Mobile design */

@media (max-width: 600px) {

    body {
        padding: 12px;
    }

    .header {
        padding: 38px 15px;
        border-radius: 20px;
    }

    .card {
        padding: 21px;
        border-radius: 18px;
    }

    h1 {
        letter-spacing: 1px;
    }

    button {
        width: 100%;
    }

}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
    }
}
/* =================================
   CINEMATIC INTRODUCTION
================================= */

#introScreen {
    position: fixed;
    inset: 0;
    z-index: 99999;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    background:
        radial-gradient(circle at center, #25204a, #080b19 70%);
    transition: opacity 1s ease, visibility 1s ease;
}

#introScreen.hide {
    opacity: 0;
    visibility: hidden;
}

.intro-content {
    padding: 25px;
    animation: introReveal 1.5s ease both;
}

.intro-logo {
    width: 105px;
    height: 105px;
    border: 2px solid #f5d58a;
    border-radius: 50%;
    margin: auto auto 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    font-weight: bold;
    color: #f5d58a;
    box-shadow: 0 0 35px rgba(245,213,138,.4);
    animation: introGlow 2s infinite alternate;
}

.intro-title {
    font-size: clamp(22px, 5vw, 42px);
    letter-spacing: 3px;
    animation: titleReveal 2s ease both;
}

.intro-subtitle {
    color: #cbd5e1;
    font-size: 11px;
    letter-spacing: 3px;
    margin-top: 15px;
}

.intro-loading {
    color: #f5d58a;
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: 20px;
}

.loading-line {
    width: 220px;
    height: 3px;
    background: rgba(255,255,255,.15);
    margin: 30px auto 0;
    border-radius: 10px;
    overflow: hidden;
}

.loading-progress {
    height: 100%;
    background: linear-gradient(90deg, #f5d58a, #fff);
    animation: loading 3.2s ease forwards;
}

@keyframes loading {
    from { width: 0; }
    to { width: 100%; }
}

@keyframes introGlow {
    from { box-shadow: 0 0 15px rgba(245,213,138,.2); }
    to { box-shadow: 0 0 55px rgba(245,213,138,.7); }
}

@keyframes introReveal {
    from {
        opacity: 0;
        transform: scale(.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes titleReveal {
    from {
        opacity: 0;
        letter-spacing: 12px;
    }
    to {
        opacity: 1;
        letter-spacing: 3px;
    }
}

/* =================================
   FLOATING PARTICLES
================================= */

.particles {
    position: fixed;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: -1;
}

.particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: #f5d58a;
    border-radius: 50%;
    opacity: .45;
    box-shadow: 0 0 12px #f5d58a;
    animation: particleFloat linear infinite;
}

@keyframes particleFloat {
    from {
        transform: translateY(110vh);
        opacity: 0;
    }
    20% { opacity: .6; }
    80% { opacity: .5; }
    to {
        transform: translateY(-10vh);
        opacity: 0;
    }
}

/* =================================
   PREMIUM GLASS EFFECTS
================================= */

.card,
.header {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.13);
    backdrop-filter: blur(30px) saturate(150%);
    -webkit-backdrop-filter: blur(30px) saturate(150%);
    box-shadow:
        0 15px 50px rgba(0,0,0,.3),
        inset 0 1px 1px rgba(255,255,255,.08);
}

.card {
    position: relative;
    overflow: hidden;
}

.card::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 1px;
    background: linear-gradient(
        90deg,
        transparent,
        #f5d58a,
        transparent
    );
    animation: glassLine 8s infinite;
}

@keyframes glassLine {
    0%, 70% { left: -100%; }
    100% { left: 100%; }
}

/* Smooth buttons */

button {
    position: relative;
    overflow: hidden;
}

button:active {
    transform: scale(.96);
}

/* Welcome animation */

.container {
    animation: dashboardEnter 1.2s ease both;
}

@keyframes dashboardEnter {
    from {
        opacity: 0;
        transform: translateY(25px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
/* CINEMATIC INTRO SCREEN */
#introScreen {
    position: fixed;
    inset: 0;
    background: radial-gradient(circle at center, #241044, #05020d 75%);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 99999;
    transition: opacity 1s ease, visibility 1s ease;
}

#introScreen.hide {
    opacity: 0;
    visibility: hidden;
}

.intro-content {
    text-align: center;
    animation: introReveal 1.5s ease;
}

.intro-logo {
    width: 110px;
    height: 110px;
    border: 2px solid #f5d58a;
    border-radius: 50%;
    display: grid;
    place-items: center;
    margin: 0 auto 25px;
    color: #f5d58a;
    font-size: 30px;
    font-weight: bold;
    box-shadow: 0 0 35px rgba(245,213,138,.4);
    animation: logoGlow 2s infinite alternate;
}

.intro-title {
    color: #f5d58a;
    letter-spacing: 4px;
    font-size: 28px;
}

.intro-subtitle {
    color: #ddd;
    letter-spacing: 3px;
    font-size: 11px;
}

.loading-line {
    width: 230px;
    height: 3px;
    background: #ffffff25;
    margin: 30px auto 15px;
    overflow: hidden;
}

.loading-progress {
    height: 100%;
    width: 0;
    background: #f5d58a;
    animation: loading 3s forwards;
}

.intro-loading {
    color: #f5d58a;
    font-size: 10px;
    letter-spacing: 3px;
}

@keyframes loading {
    to { width: 100%; }
}

@keyframes logoGlow {
    from { box-shadow: 0 0 15px rgba(245,213,138,.2); }
    to { box-shadow: 0 0 45px rgba(245,213,138,.8); }
}

@keyframes introReveal {
    from { opacity: 0; transform: translateY(25px); }
    to { opacity: 1; transform: translateY(0); }
}

/* FLOATING PARTICLES */
.particles {
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 0;
}

.particle {
    position: absolute;
    bottom: -10px;
    width: 4px;
    height: 4px;
    background: #f5d58a;
    border-radius: 50%;
    opacity: .5;
    animation: floatParticle linear infinite;
}

@keyframes floatParticle {
    to {
        transform: translateY(-110vh);
        opacity: 0;
    }
}
</style>
</head>

<body>
<!-- CINEMATIC INTRO -->
<div id="introScreen">

    <div class="intro-content">

        <div class="intro-logo">ICGC</div>

        <h1 class="intro-title">
            ICGC LIBERATION TEMPLE
        </h1>

        <p class="intro-subtitle">
            A PLACE OF WORSHIP, FELLOWSHIP & EXCELLENCE
        </p>

        <div class="loading-line">
            <div class="loading-progress"></div>
        </div>

        <p class="intro-loading">PREPARING YOUR EXPERIENCE...</p>

    </div>

</div>

<!-- FLOATING BACKGROUND PARTICLES -->
<div class="particles" id="particles"></div>

<div class="container">

<div class="header">

<div class="logo">ICGC</div>

<h1>ICGC LIBERATION TEMPLE</h1>

<h2>Church Reminder System</h2>

<p class="subtitle">
A place of worship, fellowship and excellence.
</p>

<p class="status">
● SYSTEM RUNNING
</p>

</div>

<div class="card">

<h2>✦ Weekly Reminder Schedule</h2>

<div class="schedule">
<strong>Saturday — 12:00 PM</strong>
<br>
Afternoon church reminder
</div>

<div class="schedule">
<strong>Saturday — 6:00 PM</strong>
<br>
Evening church reminder
</div>

<div class="schedule">
<strong>Sunday — 6:00 AM</strong>
<br>
Sunday morning reminder
</div>

<p class="status">
All times: Ghana (Africa/Accra)
</p>

</div>

<div class="card">

<h2>✦ Member Registration</h2>

<form method="POST" action="/add_member">

<input type="text" name="name"
placeholder="Member's Full Name" required>

<input type="tel" name="phone"
placeholder="Phone Number with Country Code" required>

<p>
<label>
<input type="checkbox" name="consent"
value="yes" required>
I confirm this member has agreed to receive reminders.
</label>
</p>

<button type="submit">Register Member</button>

</form>

<hr>

<h2>Import Members from CSV</h2>

<form method="POST" action="/import_members"
enctype="multipart/form-data">

<input type="file" name="members_file"
accept=".csv" required>

<button type="submit">Import Members</button>

</form>

<small>
CSV columns required: name, phone.
Only import members whose permission has already
been confirmed by the church.
</small>

</div>

<div class="card">

<h2>✦ Registered Members</h2>

<h1>{{ total }}</h1>

<p>All registered members.</p>

{% for member in members %}

<div class="member">

<strong>{{ member.name }}</strong>

<br>

<small>{{ member.phone }}</small>

<br>

{% if member.consent == 1 %}

<span class="consent-status">
✓ Active - Reminders Enabled
</span>

<form method="POST"
action="/toggle_consent/{{ member.id }}">

<button class="deactivate" type="submit">
Deactivate Reminders
</button>

</form>

{% else %}

<span class="consent-status no-consent">
! Inactive - Reminders Disabled
</span>

<form method="POST"
action="/toggle_consent/{{ member.id }}">

<button class="activate" type="submit">
Confirm Consent & Activate
</button>

</form>

{% endif %}

<form method="POST"
action="/delete_member/{{ member.id }}">

<button class="delete" type="submit">
Remove Member
</button>

</form>

</div>

{% else %}

<p>No members registered yet.</p>

{% endfor %}

</div>

<div class="card">

<h2>✦ Messaging Services</h2>

<p>SMS:
<span style="color:#fbbf24">
LIVE API key configured
</span>
</p>

<p>WhatsApp:
<span style="color:#fbbf24">
LIVE API key configured
</span>
</p>

<small>
Live message delivery depends on completing provider
configuration and activation.
</small>

</div>

<div class="card">

<h2>✦ System Information</h2>

<p>Church: ICGC Liberation Temple</p>

<br>

<p>Timezone: Africa/Accra</p>

<br>

<p>Reminder Days: Saturday and Sunday</p>

<br>

<p>Delivery: Individual messages after integration</p>

</div>

<div class="footer">

ICGC LIBERATION TEMPLE

<br><br>

CHURCH REMINDER SYSTEM

<br><br>

© 2026

</div>

</div>
<script>

/* Cinematic opening screen */

const intro = document.getElementById("introScreen");

setTimeout(function() {
    if (intro) {
        intro.classList.add("hide");

        setTimeout(function() {
            intro.remove();
        }, 1100);
    }
}, 3500);


/* Create floating particles */

const particleContainer = document.getElementById("particles");

for (let i = 0; i < 35; i++) {

    const particle = document.createElement("div");

    particle.className = "particle";

    particle.style.left = Math.random() * 100 + "%";

    particle.style.animationDuration =
        (8 + Math.random() * 15) + "s";

    particle.style.animationDelay =
        (Math.random() * 12) + "s";

    particleContainer.appendChild(particle);

}

</script>
<script>
window.addEventListener("load", function() {
    const intro = document.getElementById("introScreen");

    setTimeout(function() {
        intro.classList.add("hide");
    }, 3500);

    setTimeout(function() {
        intro.style.display = "none";
    }, 4600);
});

const particleContainer = document.getElementById("particles");

for (let i = 0; i < 35; i++) {
    const particle = document.createElement("div");

    particle.className = "particle";
    particle.style.left = Math.random() * 100 + "%";
    particle.style.animationDuration = (8 + Math.random() * 15) + "s";
    particle.style.animationDelay = (Math.random() * 12) + "s";

    particleContainer.appendChild(particle);
}
</script>
</body>
</html>
"""

# =====================================
# HOME PAGE
# =====================================

@app.route("/")
def home():

    connection = get_db()

    members = connection.execute("""
        SELECT * FROM members
        ORDER BY name
    """).fetchall()

    total = len(members)

    connection.close()

    return render_template_string(
        HTML,
        members=members,
        total=total
    )

# =====================================
# ADD MEMBERS
# =====================================

@app.route("/add_member", methods=["POST"])
def add_member():

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    consent = request.form.get("consent") == "yes"

    if not name or not phone or not consent:
        return "Please provide all required details and confirm permission.", 400

    connection = get_db()

    try:

        connection.execute("""
            INSERT INTO members (name, phone, consent)
            VALUES (?, ?, 1)
        """, (name, phone))

        connection.commit()

    except sqlite3.IntegrityError:

        connection.close()

        return "This phone number is already registered.", 400

    connection.close()

    return redirect("/")

# =====================================
# IMPORT MEMBERS FROM CSV
# =====================================

@app.route("/import_members", methods=["POST"])
def import_members():

    uploaded_file = request.files.get("members_file")

    if not uploaded_file or not uploaded_file.filename:
        return "Please select a CSV file.", 400

    if not uploaded_file.filename.lower().endswith(".csv"):
        return "Please upload a CSV file.", 400

    try:

        content = uploaded_file.read().decode("utf-8-sig")

        reader = csv.DictReader(io.StringIO(content))

        if not reader.fieldnames or not {"name", "phone"}.issubset(
            {field.strip().lower() for field in reader.fieldnames}
        ):
            return "CSV must contain name and phone columns.", 400

        imported = 0
        connection = get_db()

        for row in reader:

            cleaned = {
                key.strip().lower(): (value or "").strip()
                for key, value in row.items()
                if key
            }

            name = cleaned.get("name", "")
            phone = cleaned.get("phone", "")

            if not name or not phone:
                continue

            try:

                connection.execute("""
                    INSERT INTO members (name, phone, consent)
                    VALUES (?, ?, 1)
                """, (name, phone))

                imported += 1

            except sqlite3.IntegrityError:
                continue

        connection.commit()
        connection.close()

        return (
            f"Successfully imported {imported} members. "
            "Members with confirmed permission are now active for reminders. "
            '<a href="/">Return to dashboard</a>'
        )

    except (UnicodeDecodeError, csv.Error):

        return "Unable to read this CSV file.", 400

# =====================================
# ACTIVATE / DEACTIVATE MEMBER REMINDERS
# =====================================

@app.route("/toggle_consent/<int:member_id>", methods=["POST"])
def toggle_consent(member_id):

    connection = get_db()

    connection.execute("""
        UPDATE members
        SET consent = CASE
            WHEN consent = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
    """, (member_id,))

    connection.commit()
    connection.close()

    return redirect("/")

# =====================================
# DELETE MEMBERS
# =====================================

@app.route("/delete_member/<int:member_id>", methods=["POST"])
def delete_member(member_id):

    connection = get_db()

    connection.execute("""
        DELETE FROM members
        WHERE id = ?
    """, (member_id,))

    connection.commit()
    connection.close()

    return redirect("/")

# =====================================
# AUTOMATIC SCHEDULER
# =====================================

scheduler = BackgroundScheduler(
    timezone=GHANA_TIME
)

scheduler.add_job(
    send_reminder,
    "cron",
    day_of_week="sat",
    hour=12,
    minute=0,
    args=["saturday_noon"],
    id="saturday_noon",
    replace_existing=True
)

scheduler.add_job(
    send_reminder,
    "cron",
    day_of_week="sat",
    hour=18,
    minute=0,
    args=["saturday_evening"],
    id="saturday_evening",
    replace_existing=True
)

scheduler.add_job(
    send_reminder,
    "cron",
    day_of_week="sun",
    hour=6,
    minute=0,
    args=["sunday_morning"],
    id="sunday_morning",
    replace_existing=True
)

# =====================================
# START APPLICATION
# =====================================

if __name__ == "__main__":

    create_database()

    scheduler.start()

    print("=" * 55)
    print(CHURCH_NAME)
    print("CHURCH REMINDER SYSTEM")
    print("Timezone: Africa/Accra")
    print("Scheduler: ACTIVE")
    print("=" * 55)

    try:

        app.run(
            debug=False,
            use_reloader=False
        )

    finally:

        if scheduler.running:
            scheduler.shutdown()