# Inside the Door Detailing

Interior-only car detailing business. Tagline: **Clean | Protect | Preserve**.
This folder holds two working front-end prototypes (no backend yet) that are ready to become a real website.

- `public/index.html` is the **guest site**: services, quote/booking form, deposit step (mock).
- `public/manager/index.html` is the **manager site**: the guest site's content plus a Calendar tab and a New booking form, behind a shared passcode gate (see "Placeholders" below). It's built by `reference/build_manager.py` from `public/index.html` + `reference/manager-old-dashboard-version.html` — edit those two, then rerun the script, rather than hand-editing `public/manager/index.html` directly.
- `public/assets/logo.png` is the logo (transparent background, 874x414, cropped from an AI-generated logo sheet).
- `reference/` holds design references only. Do not ship anything in it.

Both pages are single self-contained HTML files (inline CSS and JS). Run them locally with
`python3 -m http.server -d public 8000`, then open http://localhost:8000 and http://localhost:8000/manager/.

## Business goals and decisions already made

1. Guests choose services and book on the guest site.
2. Pricing is **$50 an hour**. The guest pays a **flat $50 deposit up front** (their first hour) to avoid no-shows and late cancellations. The deposit goes toward the final balance.
3. After the deposit is paid, a **confirmation email goes to the manager**, and the booking appears on the manager's calendar.
4. The manager reviews it and confirms (or declines and refunds the deposit).
5. Payments run through the owner's **Square** account (the owner already uses Square).
6. The owner is deciding whether to also write appointments into Square's own calendar. See "Square notes" below. The owner prefers a custom manager site with a calendar over managing appointments inside Square.

Contact details on the site: Insidethedoordetailing@gmail.com and (920) 421-1493.

## Owner's other project (reuse patterns)

The owner has a separate marina reservation system whose calendar this manager Calendar tab mirrors (layout, month grid, colored bars, click for details). The owner built a hosted version of that with a backend and database using Claude Code. If that code is available, reuse its patterns for bookings, availability, and auth.

## Brand and design (locked in, don't change without asking)

- Colors: black `#000`, off-white `#f4f4f2`, red `#e5121f` (small red text uses `#ff4650`). Dark theme only.
- Headlines: **Barlow Condensed, italic, 700, uppercase** ("Speed italic"). Body: Archivo. Both from Google Fonts.
- Hero: the car outline is an SVG traced from a BMW 840i reference image (a free-download stock vector). It is outline only, reveals left to right, then the red taillight glows. **Check that image's license for commercial use before launch, or replace it with an original or licensed illustration.**
- Guest site service lists are sorted shortest to longest so wrapped lines sit at the bottom.
- Manager calendar service colors: **Basic blue `#4b6fb7`, Deep orange `#b45f14`, Leather red `#d92d2d`, Specialty grey `#6b7078`.**
  - A booking bar takes the color of its first service in the order Basic, Deep, Leather, Specialty.
  - Any additional services show as tall rounded capsules on the right end of the bar (see `reference/marina-calendar-multi-service-pill.png`).
  - The bar shows the customer's full name (wraps, never truncates). A check mark means confirmed. Hover shows time, name and services. Click opens details.
  - The owner asked that names and colors always be visible, so the calendar scrolls sideways on narrow screens instead of shrinking.

## Services (source of truth is the `CATEGORIES` array in the guest page)

1. Basic interior cleaning: included in the standard interior detail.
2. Deep interior cleaning: for vehicles needing extra attention. (Steam cleaning and headliner spot cleaning were intentionally removed.)
3. Leather & upholstery care.
4. Specialty interior services: individual add-ons (pet hair, odor, smoke odor, sanitization, sand, excessive dirt, child seat area, spill cleanup, spot treatment).

## Placeholders and known prototype limits (replace these)

- **Prices and deposit are sample values.** The rate is $50/hour (`HOURLY_RATE` in `public/index.html`) with a flat $50 deposit (`DEPOSIT_FLAT`, the first hour). The guest page derives `PRICES` from a `HOURS` map (estimated duration per service/add-on) — those durations are guesses and need the owner's real numbers. The manager page's calendar keeps its own matching dollar amounts (`PRICES`, `ADDONS`, `DEPOSIT_FLAT`) since it doesn't share code with the guest page; update both if the rate or durations change. Move all of this to one server-side source of truth. Ask the owner for real per-service durations (or a different pricing model entirely) and whether price varies by vehicle size (SUV/truck/van).
- Sample bookings and customer names in the manager site are fake. The manager site keeps its data in `localStorage` only.
- The guest "Book request" flow ends in a mock "Continue to Square" screen. No payment or email is sent.
- **No real login on the manager site.** It's gated by a single shared passcode (`6278`, `GATE_CODE` in `reference/build_manager.py`), stored in the visitor's browser (`localStorage`) once entered, with a "Lock" link in the nav to clear it. This keeps casual visitors out but is **not real security** — the code is sitting in the page's own source, so anyone who looks at it (view source, devtools) can read it and get in. Real per-person login (per `Suggested build order` below) still needs to happen before this holds real customer data at any real risk.
- Service area, business hours, appointment length, and time zone are not decided. Confirm the time zone with the owner (probably America/Chicago based on the phone area code).
- The owner will provide a higher-resolution logo later (the current one is about 440px wide in the source).

## Suggested build order

1. **Pick a simple, low-cost stack and hosting** (static front end plus serverless functions and a hosted database is probably enough). Propose options and let the owner choose. Keep the current look and markup.
2. **Bookings data model and API**: services, bookings, status (pending, confirmed, declined, cancelled), deposit status. Server-side availability check and double-booking prevention.
3. **Deposit payment with Square**: the server computes the total and deposit (never trust the browser). Use Square hosted checkout or payment links so card data never touches our server. Use a webhook to mark the deposit paid. Start in Square's sandbox.
4. **Email on paid booking**: a transactional email service (Resend, SendGrid, or similar) emails the manager the full request, and sends the guest a receipt. API keys only in environment variables.
5. **Manager site backend**: login (only the owner and staff), replace `localStorage` with the API, confirm/decline/cancel actions, and a refund path (Square refunds) for declined or cancelled bookings.
6. **Guest site**: replace the mock deposit step with the real one, show only open time slots, add spam protection (honeypot and rate limiting).
7. Polish: domain, SEO basics, accessibility pass, error states, and basic monitoring.

## Square notes (verify against current Square docs before building)

- Square Appointments can take a fixed or percentage deposit per service at online booking, and can hold a card to charge a cancellation fee. Its own booking page could replace parts of this custom flow.
- Square's Bookings API can create, retrieve, update and cancel appointments. Creating bookings on the seller's calendar needs a paid Appointments plan (Plus or Premium). It cannot double-book or book outside business hours, cannot create a booking that has a non-zero cancellation fee, and team members must be made bookable in the Square Dashboard. It also has webhooks for booking created and updated.
- **Decided for now:** the custom manager calendar is the only system of record. Bookings are entered and tracked there (manually, via New booking, until there's a real intake pipeline) and are **not** written to Square's own calendar. The owner would like real Square Bookings API sync eventually (see git history / prior conversation for the tradeoffs already discussed), but explicitly deferred it to focus on getting the two sites live first. Revisit this once there's a real backend (needs a paid Appointments plan, real per-service durations, and team-member setup in the Square Dashboard before it's possible).

## Security reminders

- Never put Square tokens, email keys, or any secret in front-end code. Use environment variables (see `.env.example`).
- Validate and sanitize all input on the server. Render user text with `textContent` (the prototypes already do).
- Protect every manager route and API behind authentication.
