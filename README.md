README
Transport Service (Django)

A lightweight ride-coordination web app for patients (“sick”) and volunteers. Patients can create transport requests; volunteers see open requests and accept or reject them. The UI updates dynamically via a small front-end script, and roles are strictly enforced on the server. If all volunteers reject a request, the system automatically cancels it and records that no volunteers were available so the patient can see why it was cancelled.

Distinctiveness and Complexity

Distinctiveness.
This project isn’t a simple CRUD demo. It implements a two-sided workflow with role-aware behavior and a state machine for requests (open → accepted → done / cancelled). Unlike a generic blog or to-do app, the UI and API change based on who is logged in:

Volunteers see only requests they can act on (open, not previously rejected by them, and not flagged as “no volunteers available”). They can accept or reject in one click, with rejections tracked per volunteer.

Patients see only their own open requests, and a separate view of closed/cancelled items that also includes “accepted but already assigned” rides as historical records. They can cancel open requests and remove cancelled ones from their own list.

Complexity.
Under the hood, the app contains several pieces that go beyond basic CRUD:

Aggregated rejection logic: Every volunteer’s rejection is recorded with an optional reason; when all volunteers on the platform have rejected a request, the server automatically marks the request as cancelled and sets no_volunteers_available=True. Patients then see a human-friendly label (“No volunteers available”).

Role-scoped deletion endpoints: Volunteers can “Done & Delete” any request they accepted; patients can delete only their own cancelled requests. This requires careful authorization in the API.

Optimized open-request feed for volunteers: Volunteers never see requests they already rejected, nor ones that were globally cancelled due to no availability.

CSRF-aware, SPA-like front end: The UI is rendered server-side but behaves like a mini single-page app using static/stransport/stransport.js, which switches panels (open/closed/accepted) smoothly and updates DOM in place. All write actions use CSRF tokens from the cookie.

Clear serialization boundary: serialize_request centralizes how request objects are exposed to the front end, including derived labels and nested volunteer info. That keeps templates minimal and front-end rendering straightforward.

Together, these elements make the project both distinctive (a real, two-party workflow) and non-trivial (stateful logic, permissions, aggregation, and a dynamic UI).

Project Structure
service/                    # Django project
  manage.py
  service/
    settings.py
    urls.py
    wsgi.py
  stransport/               # Main app
    apps.py
    models.py               # Profile, TransportRequest, TransportAssignment, TransportRejection
    views.py                # Role-aware JSON APIs + page view
    urls.py                 # Routes for page + JSON endpoints
    signals.py              # Auto-create Profile for new User
    static/stransport/
      stransport.js         # SPA-like UI logic (fetch, CSRF, panels, buttons)
      stransport.css        # Clean UI styling + “open” alert animation
    templates/
      stransport/
        layout.html         # Base layout (nav, static includes, user exposure to JS)
        home.html           # Role-specific panels & containers for JS to fill
      registration/
        login.html          # Auth login page (styled)
        signup.html         # Sign-up (role select + Django form)
README.md
requirements.txt

Data Model

Profile (user, role in {sick, volunteer}, phone)

TransportRequest (sick FK, pickup_address, destination, requested_time, notes, status in {open, accepted, done, cancelled}, no_volunteers_available)

TransportAssignment (O2O request, volunteer, accepted_time, comment)

TransportRejection (request, volunteer, reason, unique per volunteer per request)

API Endpoints (JSON)

GET /api/requests/

Volunteer: open requests excluding their rejections and those with no_volunteers_available=True.

Sick: their own open requests.

POST /api/requests/create/ — Sick only; creates a new request.

POST /api/requests/accept/<id>/ — Volunteer only; assigns and sets accepted.

POST /api/requests/reject/<id>/ — Volunteer only; records rejection (+auto-cancel if everyone rejected).

POST /api/requests/cancel/<id>/ — Sick only; cancels an open request.

GET /api/requests/accepted/ — Volunteer: all requests they accepted (still accepted).

GET /api/requests/closed/ — Sick: cancelled/done plus accepted with an assigned volunteer (history).

POST /api/requests/delete/<id>/

Volunteer: delete requests they accepted.

Sick: delete their own cancelled requests.

All write endpoints require CSRF and a logged-in session (Django auth).

Front End

static/stransport/stransport.js powers the dynamic UI:

Smooth panel switching between Open, Closed (sick), and Accepted (volunteer).

Inline actions:

Sick: Cancel (open), Delete (closed/cancelled).

Volunteer: Accept, Reject, Done & Delete (accepted).

Open cards visually “pulse” to draw attention (CSS animation in stransport.css).

How to Run

Clone and create a virtual environment

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate


Install dependencies

pip install -r requirements.txt


Migrate database

python manage.py migrate


(Optional) Create a superuser

python manage.py createsuperuser


Run the development server

Local only:

python manage.py runserver


Accessible on your LAN (Windows example):

# Either bind to all interfaces:
python manage.py runserver 0.0.0.0:8000
# Or bind to your actual IPv4 from ipconfig, e.g.:
python manage.py runserver 192.168.33.23:8000


If you see “That IP address can’t be assigned to,” use 0.0.0.0:8000 and browse from another device to http://<your-ip>:8000.
Note: ALLOWED_HOSTS already includes localhost, 127.0.0.1, and sample LAN hosts.

Visit: http://localhost:8000

Using the App

Register via Sign Up as either sick (patient) or volunteer.

Sick:

Create requests (pickup, destination, date/time, notes, phone).

Cancel open requests.

See Closed / Cancelled and “No volunteers available” reasons.

Delete cancelled requests from your history.

Volunteer:

See Open requests (excluding ones you already rejected).

Accept or Reject; give a reason if you want.

See My Accepted Requests.

Done & Delete to remove an accepted request you completed.

Notes & Decisions

Security: Uses Django’s session auth + CSRF. All role checks are server-side; front-end buttons are convenience only.

DB: SQLite for simplicity (no external services required).

Simplicity of deployment: Static files are served by Django in DEBUG; production would use a proper static file server.

Known Limitations / Future Work

No real-time push; volunteers/patients refresh via fetch calls (could add WebSockets/Channels).

No geocoding or maps yet; addresses are free-text.

No background cleanup of very old requests (could add a periodic task).

Could add status “completed by volunteer” distinct from deletion if you want full audit history.

Files You’ll Find

service/settings.py – Django configuration (DEBUG, templates, static, installed apps).

service/urls.py – Root URLconf (auth views + stransport.urls).

stransport/models.py – Data models.

stransport/views.py – Page view + JSON APIs with role enforcement.

stransport/urls.py – App routes for the above APIs.

stransport/signals.py – Auto-creates a Profile when a User is created.

Templates: stransport/layout.html, stransport/home.html, registration/login.html, registration/signup.html.

Static: stransport/stransport.js, stransport/stransport.css.

Requirements

See requirements.txt (minimal set for Windows/macOS/Linux dev):

Django==5.2.4
tzdata>=2024.1 ; platform_system == "Windows"


tzdata helps Windows handle time zones correctly. Django installs other sub-deps automatically.

License

For class submission only. Feel free to adapt as needed.

requirements.txt
Django==5.2.4
tzdata>=2024.1 ; platform_system == "Windows"