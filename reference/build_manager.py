#!/usr/bin/env python3
"""Build public/manager/index.html = guest page (unchanged) + Calendar tab + New booking + passcode gate.

Run from anywhere: `python3 reference/build_manager.py` from the project root, or
`python3 build_manager.py` from inside reference/. Edit public/index.html (guest pricing/services)
or reference/manager-old-dashboard-version.html (calendar's own PRICES/ADDONS/DEPOSIT_FLAT, sample
bookings) and rerun this script rather than hand-editing public/manager/index.html directly.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUEST = os.path.join(ROOT, "public/index.html")
OLD_MANAGER = os.path.join(ROOT, "reference/manager-old-dashboard-version.html")
OUT = os.path.join(ROOT, "public/manager/index.html")

GATE_CODE = "6278"

guest = open(GUEST, encoding="utf-8").read()
old = open(OLD_MANAGER, encoding="utf-8").read().split("\n")


def old_lines(a, b):  # 1-indexed inclusive
    return "\n".join(old[a - 1:b])


def once(s, a, b):
    assert s.count(a) == 1, ("expected exactly one match", a, s.count(a))
    return s.replace(a, b)


# ---------------------------------------------------------------- CSS
CAL_CSS = r"""
  /* ================= Manager: Calendar + New booking (scoped, guest styles above are untouched) ================= */
  :root {
    --c-basic: #4b6fb7;
    --c-deep: #b45f14;
    --c-leather: #d92d2d;
    --c-specialty: #6b7078;
  }
  nav.main a.calnav[aria-current="page"] { color: var(--ink); box-shadow: inset 0 -2px 0 var(--red); }
  @media (max-width: 620px) { nav.main a.calnav, nav.main a#lockBtn { display: inline-block; padding: 10px 8px; } }

  #calView[hidden], #calToast[hidden], #newView[hidden] { display: none !important; }
  #calView button, #calDlg button { font: inherit; color: inherit; }
  #calView .calwrap, #newView .calwrap { padding-block: 34px 90px; }

  #calView .vhead, #newView .vhead { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 6px 24px; padding-bottom: 10px; border-bottom: 2px solid var(--red); margin-bottom: 28px; }
  #calView .vhead h1, #newView .vhead h1 { margin: 0; font-family: "Barlow Condensed", "Arial Narrow", sans-serif; font-style: italic; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; font-size: clamp(34px, 4.6vw, 50px); line-height: 1; }
  #calView .vhead p, #newView .vhead p { margin: 0; color: var(--mute); }

  #calView .ctrl { display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 10px 22px; margin-bottom: 24px; }
  #calView .arrow { background: none; border: 0; cursor: pointer; font-size: 28px; line-height: 1; padding: 4px 12px; color: var(--ink); }
  #calView .arrow:hover { color: var(--red-text); }
  #calView .datepill {
    display: inline-flex; align-items: baseline; gap: 12px; padding: 10px 32px; border-radius: 999px;
    background: var(--panel); border: 1px solid #3a3a3a; color: var(--mute); font-size: 18px; cursor: pointer;
  }
  #calView .datepill b { color: #fff; font-weight: 700; }
  #calView .datepill:hover { border-color: #777; }
  #calView .makebtn { background: var(--red); color: #fff; font-weight: 700; border: 0; border-radius: 999px; padding: 11px 26px; font-size: 16px; cursor: pointer; }
  #calView .makebtn:hover { background: #ff1f2d; }

  #calView .legend { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 24px; margin-bottom: 18px; color: #d0d0d0; font-size: 15px; }
  #calView .legend > span { display: inline-flex; align-items: center; gap: 8px; }
  #calView .sw { width: 16px; height: 16px; border-radius: 4px; display: inline-block; flex: none; }
  #calView .capdemo { display: inline-flex; gap: 3px; }
  #calView .capdemo i { width: 7px; height: 16px; border-radius: 4px; display: block; box-shadow: 0 0 0 1px rgba(255,255,255,.45); }
  #calView .ckd { font-weight: 800; }

  #calView .dow, #calView .grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); }
  #calView .dow { border-top: 1px solid var(--line); }
  #calView .dow div { text-align: center; font-weight: 700; font-size: 13px; letter-spacing: .07em; color: var(--mute); padding: 13px 0; }
  #calView .grid { border-top: 1px solid var(--line); border-left: 1px solid var(--line); }
  #calView .day {
    min-width: 0; min-height: 152px; padding: 8px 8px 10px; display: flex; flex-direction: column; gap: 5px;
    background: #050505; border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); position: relative;
  }
  #calView .day.out { background: #000; }
  #calView .day .cn { align-self: flex-end; font-weight: 700; font-size: 15px; color: #d8d8d8; text-decoration: underline; text-underline-offset: 3px; margin-bottom: 2px; }
  #calView .day.out .cn { color: #5c5c5c; text-decoration: none; font-weight: 600; }
  #calView .day.today { outline: 3px solid var(--ink); outline-offset: -3px; z-index: 1; }

  #calView .calscroll { overflow-x: auto; padding-bottom: 6px; }
  #calView .calin { min-width: 1050px; }
  #calView .ev {
    position: relative; display: flex; align-items: center; gap: 7px; width: 100%; min-height: 32px; padding: 5px 9px;
    border: 0; border-radius: 6px; background: var(--c); color: #fff; font-weight: 700; font-size: 13.5px; line-height: 1.2; text-align: left; cursor: pointer;
  }
  #calView .ev .nm { min-width: 0; font-weight: 700; overflow-wrap: anywhere; }
  #calView .ev .ck { flex: none; font-weight: 800; opacity: .92; }
  #calView .ev .caps { margin-left: auto; flex: none; display: flex; gap: 4px; padding-left: 4px; }
  #calView .ev .caps i { display: block; width: 10px; height: 22px; border-radius: 6px; box-shadow: 0 0 0 1px rgba(255,255,255,.55); }
  #calView .ev .tip {
    position: absolute; left: 0; bottom: calc(100% + 6px); z-index: 10; pointer-events: none; opacity: 0; transform: translateY(3px);
    background: var(--ink); color: #000; padding: 6px 12px; border-radius: 8px; font-size: 13px; font-weight: 700; white-space: nowrap;
    transition: opacity .12s ease, transform .12s ease;
  }
  #calView .ev .tip.r { left: auto; right: 0; }
  #calView .ev:hover .tip, #calView .ev:focus-visible .tip { opacity: 1; transform: none; }
  #calView :focus-visible, #calDlg :focus-visible, #newView :focus-visible { outline: 2px solid #fff; outline-offset: 3px; border-radius: 2px; }

  /* ---------- New booking form (reuses guest's fieldset/legend/.field/.grid2/.opt/.addons/.btn/.hint styling) ---------- */
  #newView .form { max-width: 760px; }
  #newView .err { color: var(--red-text); font-size: 14.5px; min-height: 1.4em; margin: 0 0 10px; }
  #newView .nbsum { border: 1px solid #333; padding: 16px 18px; margin-bottom: 18px; }
  #newView .nbsum .r { display: flex; justify-content: space-between; gap: 12px; padding: 2px 0; }
  #newView .nbsum .r.dep { font-weight: 800; }

  #calDlg { width: min(580px, calc(100% - 24px)); max-height: calc(100vh - 40px); max-height: calc(100dvh - 40px); overflow: auto; padding: 0; background: var(--panel); color: var(--ink); border: 1px solid #3a3a3a; border-radius: 8px; font-family: var(--font); font-size: 16px; line-height: 1.5; }
  #calDlg::backdrop { background: rgba(0,0,0,.74); }
  #calDlg .dlg-h { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; padding: 22px 24px 14px; border-bottom: 1px solid var(--line); }
  #calDlg .dlg-h h2 { margin: 0; font-family: "Barlow Condensed", "Arial Narrow", sans-serif; font-style: italic; font-weight: 700; text-transform: uppercase; font-size: 32px; line-height: 1.05; }
  #calDlg .dlg-h .sub { margin: 4px 0 0; color: var(--mute); }
  #calDlg .x { background: none; border: 1px solid #444; width: 38px; height: 38px; border-radius: 50%; font-size: 22px; line-height: 1; cursor: pointer; flex: none; }
  #calDlg .x:hover { border-color: #fff; }
  #calDlg .dlg-b { padding: 18px 24px 24px; }
  #calDlg .badge { display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: 13px; font-weight: 700; margin: 0 0 16px; }
  #calDlg .badge.ok { border: 1px solid #fff; color: #fff; }
  #calDlg .badge.wait { border: 1px solid var(--red-text); color: var(--red-text); }
  #calDlg .kv { display: grid; grid-template-columns: 110px minmax(0, 1fr); gap: 8px 16px; margin: 0 0 20px; }
  #calDlg .kv dt { color: var(--mute); font-size: 14px; padding-top: 2px; }
  #calDlg .kv dd { margin: 0; font-weight: 600; overflow-wrap: anywhere; }
  #calDlg .dsec { margin: 0 0 8px; font-size: 14px; color: var(--mute); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
  #calDlg .svc { list-style: none; margin: 0 0 8px; padding: 0; }
  #calDlg .svc li { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-top: 1px solid var(--line); }
  #calDlg .svc li .nm { flex: 1; font-weight: 600; }
  #calDlg .svc li .pr { color: var(--mute); }
  #calDlg .dot { display: inline-block; width: 12px; height: 12px; border-radius: 3px; flex: none; }
  #calDlg .dots { display: inline-flex; gap: 5px; align-items: center; margin-right: 8px; vertical-align: middle; }
  #calDlg .foot { color: var(--mute); font-size: 14px; }
  #calDlg .tot { border-top: 1px solid #333; padding-top: 10px; margin-bottom: 20px; }
  #calDlg .tot .r { display: flex; justify-content: space-between; gap: 12px; padding: 3px 0; }
  #calDlg .tot .r.cdep { font-weight: 800; }
  #calDlg .tot .r.mu { color: var(--mute); font-size: 15px; }
  #calDlg .dacts { display: flex; flex-wrap: wrap; gap: 10px; }
  #calDlg .warn { flex-basis: 100%; margin: 0; color: #e8e8e8; }
  #calDlg .cbtn { display: inline-block; font-weight: 700; font-size: 16px; padding: 13px 24px; border-radius: 2px; border: 1px solid transparent; cursor: pointer; text-align: center; }
  #calDlg .cbtn.cprimary { background: var(--red); color: #fff; }
  #calDlg .cbtn.cprimary:hover { background: #ff1f2d; }
  #calDlg .cbtn.cghost { background: transparent; border-color: #444; color: var(--ink); }
  #calDlg .cbtn.cghost:hover { border-color: var(--ink); }
  #calDlg .dayrow { display: flex; align-items: center; gap: 14px; width: 100%; text-align: left; background: none; border: 0; border-top: 1px solid var(--line); padding: 14px 4px; cursor: pointer; }
  #calDlg .dayrow:hover { background: var(--panel-2); }
  #calDlg .dayrow .ct { width: 84px; color: var(--mute); flex: none; }
  #calDlg .dayrow .cp { flex: 1; min-width: 0; font-weight: 600; }
  #calDlg .dayrow .cp small { display: block; color: var(--mute); font-weight: 400; font-size: 14px; }

  #calToast { position: fixed; left: 50%; transform: translateX(-50%); bottom: calc(env(safe-area-inset-bottom, 0px) + 20px); z-index: 50; background: var(--ink); color: #000; font-family: var(--font); font-weight: 700; padding: 12px 20px; border-radius: 999px; max-width: calc(100% - 24px); }

  @media (max-width: 760px) {
    #calView .legend { font-size: 14px; gap: 8px 16px; }
    #calDlg .kv { grid-template-columns: 1fr; gap: 2px; }
    #calDlg .kv dd { margin-bottom: 8px; }
  }
  @media (prefers-reduced-motion: reduce) { #calView .ev .tip { transition: none; } }

  /* ================= Manager: passcode gate ================= */
  html.locked body > *:not(#gate) { display: none !important; }
  html:not(.locked) #gate { display: none !important; }
  #gate {
    position: fixed; inset: 0; z-index: 999; display: flex; align-items: center; justify-content: center;
    background: var(--black); padding: 24px;
  }
  #gate .card { width: min(360px, 100%); text-align: center; }
  #gate .logo { height: 70px; margin: 0 auto 28px; }
  #gate h1 { margin: 0 0 8px; font-family: "Barlow Condensed", "Arial Narrow", sans-serif; font-style: italic; font-weight: 700; text-transform: uppercase; font-size: 28px; letter-spacing: .01em; }
  #gate p { margin: 0 0 22px; color: var(--mute); font-size: 15px; }
  #gate input {
    width: 100%; font: inherit; font-size: 22px; letter-spacing: .3em; text-align: center; color: var(--ink); background: var(--panel);
    border: 1px solid #3a3a3a; border-radius: 2px; padding: 13px 14px; margin-bottom: 14px;
  }
  #gate input:focus { outline: 2px solid #fff; outline-offset: 1px; border-color: #fff; }
  #gate button { width: 100%; }
  #gate .err { min-height: 1.4em; margin: 12px 0 0; color: var(--red-text); font-size: 14.5px; }
  #gate .back { display: inline-block; margin-top: 22px; color: var(--mute); font-size: 14px; text-decoration: underline; text-underline-offset: 3px; }
  #gate .back:hover { color: var(--ink); }
"""

# ---------------------------------------------------------------- Markup
CAL_HTML = """
<main id="calView" hidden>
  <div class="wrap calwrap">
    <div class="vhead"><h1>Calendar</h1><p>Every booking, color-coded by service &middot; click one for full details</p></div>
    <div class="ctrl">
      <button type="button" class="arrow" id="prevM" aria-label="Previous month">&larr;</button>
      <button type="button" class="datepill" id="thisM" title="Jump to this month"><span>Date</span><b id="mlabel"></b></button>
      <button type="button" class="arrow" id="nextM" aria-label="Next month">&rarr;</button>
      <button type="button" class="makebtn" id="makeBtn">+ New booking</button>
    </div>
    <div class="legend" aria-label="Legend">
      <span><i class="sw" style="background:var(--c-basic)"></i>Basic</span>
      <span><i class="sw" style="background:var(--c-deep)"></i>Deep interior</span>
      <span><i class="sw" style="background:var(--c-leather)"></i>Leather &amp; upholstery</span>
      <span><i class="sw" style="background:var(--c-specialty)"></i>Specialty</span>
      <span><span class="capdemo"><i style="background:var(--c-deep)"></i><i style="background:var(--c-leather)"></i></span>More services on the same booking</span>
      <span><b class="ckd">&#10003;</b>Confirmed</span>
    </div>
    <div class="calscroll"><div class="calin">
      <div class="dow"><div>MON</div><div>TUE</div><div>WED</div><div>THU</div><div>FRI</div><div>SAT</div><div>SUN</div></div>
      <div class="grid" id="grid"></div>
    </div></div>
  </div>
</main>
"""

NEW_HTML = """
<main id="newView" hidden>
  <div class="wrap calwrap">
    <div class="vhead"><h1>New booking</h1><p>Add a phone or walk-in booking to the calendar</p></div>
    <form class="form" id="nbForm" novalidate>
      <fieldset>
        <legend>Customer</legend>
        <div class="field"><label for="nbName">Name</label><input type="text" id="nbName" autocomplete="off"></div>
        <div class="grid2">
          <div class="field"><label for="nbPhone">Phone</label><input type="tel" id="nbPhone" autocomplete="off"></div>
          <div class="field"><label for="nbEmail">Email</label><input type="email" id="nbEmail" autocomplete="off"></div>
        </div>
        <div class="field"><label for="nbVehicle">Vehicle (year, make, model)</label><input type="text" id="nbVehicle" autocomplete="off"></div>
      </fieldset>
      <fieldset>
        <legend>Appointment</legend>
        <div class="grid2">
          <div class="field"><label for="nbDate">Date</label><input type="date" id="nbDate"></div>
          <div class="field"><label for="nbTime">Start time</label><select id="nbTime"></select></div>
        </div>
      </fieldset>
      <fieldset>
        <legend>Services</legend>
        <p class="hint">Each service level shows in its own color on the calendar.</p>
        <div id="nbServices"></div>
        <p class="hint" style="margin-top:18px">Specialty add-ons (grey on the calendar)</p>
        <div class="addons" id="nbAddons"></div>
      </fieldset>
      <fieldset>
        <legend>Details</legend>
        <div class="field"><label for="nbNotes">Notes</label><textarea id="nbNotes" placeholder="Stains, smells, pets, gate codes..."></textarea></div>
        <label class="opt"><input type="checkbox" id="nbConf" checked><span class="box"><span class="name">Mark as confirmed</span></span></label>
        <label class="opt"><input type="checkbox" id="nbDep"><span class="box"><span class="name">Deposit collected</span></span></label>
      </fieldset>
      <div class="nbsum" aria-live="polite">
        <div class="r"><span>Estimated total</span><span id="nbTotal"></span></div>
        <div class="r dep"><span id="nbDepLabel"></span><span id="nbDepAmt"></span></div>
      </div>
      <p class="err" id="nbErr" role="alert"></p>
      <button type="button" class="btn primary" id="nbSave">Add to calendar</button>
    </form>
  </div>
</main>
"""

CAL_DIALOGS = """
<dialog id="calDlg" aria-label="Booking details"></dialog>
<div id="calToast" role="status" hidden></div>
"""

GATE_HTML = """
<div id="gate" role="dialog" aria-modal="true" aria-label="Manager access">
  <div class="card">
    <span class="logo" role="img" aria-label="Inside the Door Detailing"></span>
    <h1>Manager access</h1>
    <p>Enter the passcode to open the manager site.</p>
    <form id="gateForm" novalidate>
      <input type="password" inputmode="numeric" pattern="[0-9]*" maxlength="4" id="gateCode" autocomplete="off" aria-label="Passcode">
      <button type="submit" class="btn primary">Unlock</button>
      <p class="err" id="gateErr" role="alert"></p>
    </form>
    <a class="back" href="../">Back to the guest site</a>
  </div>
</div>
<script>if (localStorage.getItem("itd-manager-unlocked") === "1") document.documentElement.classList.remove("locked");</script>
"""

# ---------------------------------------------------------------- Script
data_block = old_lines(321, 411)                      # settings, helpers, sample data, storage, byDate, find
toast_block = old_lines(413, 418).replace('$("toast")', '$("calToast")')
cal_block = old_lines(437, 480)                       # makePill, renderCal, month buttons (line 481 = New booking button, added back separately)
dlg_block = old_lines(483, 578)                       # dialog + openBooking + openDay, including "Add a booking for this day"
new_block = old_lines(618, 663)                       # buildForm, renderNb, nbSave


def rename(s):
    """Scope the old dashboard's generic class names to the calendar dialog so they don't collide with guest CSS."""
    s = s.replace('"btn primary"', '"cbtn cprimary"').replace('"btn ghost"', '"cbtn cghost"')
    s = s.replace('el("span", "n", ', 'el("span", "cn", ')
    s = s.replace('el("span", "t", ', 'el("span", "ct", ')
    s = s.replace('el("span", "p")', 'el("span", "cp")')
    s = s.replace('money(t.deposit), "dep"]', 'money(t.deposit), "cdep"]')
    return s


dlg_block = dlg_block.replace('var dlg = $("dlg");', 'var dlg = $("calDlg");')
dlg_block = rename(dlg_block)
cal_block = rename(cal_block)

# Route by hash instead of the old tab-based go(): #calendar, #new, or the guest page.
dlg_block = once(dlg_block, 'go("new"); renderNb();', 'location.hash = "#new"; renderNb();')
new_block = once(new_block, 'renderAll(); go("calendar"); toast(', 'renderAll(); location.hash = "#calendar"; toast(')

CAL_JS = """
<script>
(function () {
  "use strict";
""" + data_block + "\n\n" + toast_block + "\n\n  function renderAll() { renderCal(); }\n\n" + cal_block + """
  $("makeBtn").addEventListener("click", function () { location.hash = "#new"; });
""" + "\n\n" + dlg_block + "\n\n" + new_block + """

  /* ----- Guest page <-> Calendar <-> New booking ----- */
  var guestEl = $("top"), calEl = $("calView"), newEl = $("newView"), calNav = $("calNav");
  function route() {
    var h = location.hash, isCal = h === "#calendar", isNew = h === "#new";
    calEl.hidden = !isCal; newEl.hidden = !isNew; guestEl.hidden = (isCal || isNew);
    if (isCal) { calNav.setAttribute("aria-current", "page"); renderCal(); window.scrollTo(0, 0); }
    else { calNav.removeAttribute("aria-current"); }
    if (isNew) { buildForm(); renderNb(); window.scrollTo(0, 0); }
    if (!isCal && !isNew) {
      var id = h.slice(1), t = id && $(id);
      if (t && t !== guestEl) t.scrollIntoView(); else if (!id || id === "top") window.scrollTo(0, 0);
    }
  }
  window.addEventListener("hashchange", route);
  route();

  /* ----- Passcode gate ----- */
  var GATE_KEY = "itd-manager-unlocked", GATE_CODE = \"""" + GATE_CODE + """\";
  var gateForm = $("gateForm"), gateCode = $("gateCode"), gateErr = $("gateErr"), lockBtn = $("lockBtn");
  gateForm.addEventListener("submit", function (e) {
    e.preventDefault();
    if (gateCode.value.trim() === GATE_CODE) {
      try { localStorage.setItem(GATE_KEY, "1"); } catch (err) {}
      document.documentElement.classList.remove("locked");
      gateErr.textContent = ""; gateCode.value = "";
    } else {
      gateErr.textContent = "That code isn't right. Try again.";
      gateCode.value = ""; gateCode.focus();
    }
  });
  lockBtn.addEventListener("click", function (e) {
    e.preventDefault();
    try { localStorage.removeItem(GATE_KEY); } catch (err) {}
    document.documentElement.classList.add("locked");
    gateCode.focus();
  });
})();
</script>
"""

# ---------------------------------------------------------------- Assemble
out = guest
out = once(out, '--logo: url("assets/logo.png");', '--logo: url("../assets/logo.png");')
out = once(out, "<title>Inside the Door Detailing</title>",
           '<title>Inside the Door Detailing · Manager</title>\n<meta name="robots" content="noindex, nofollow">')
out = once(out, "</style>", CAL_CSS + "</style>")
out = once(out, "<body>\n\n<header class=\"site\">", "<body>\n" + GATE_HTML + "\n<header class=\"site\">")
out = once(out, '<html lang="en">', '<html lang="en" class="locked">')
out = once(out, '      <a href="#contact">Contact</a>\n',
           '      <a href="#contact">Contact</a>\n      <a class="calnav" id="calNav" href="#calendar">Calendar</a>\n'
           '      <a href="#" id="lockBtn">Lock</a>\n')
out = once(out, "</main>\n", "</main>\n" + CAL_HTML + NEW_HTML)
out = once(out, "</body>", CAL_DIALOGS + CAL_JS + "\n</body>")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(out)
print("wrote", OUT, len(out), "bytes")
