#!/usr/bin/env python3
"""
Roca Fuel — Project Onboarding Form
Visual continuity with the proposal (same dark theme, #ffd00a accent,
Space Grotesk / Inter / JetBrains Mono).
Submits to Zoho Flow webhook → fallback to WhatsApp → fallback to copy.
Includes Adaline bank details + UPI QR for 40% advance payment.
"""
import base64
import pathlib
import qrcode
from io import BytesIO
from urllib.parse import quote

ASSETS = pathlib.Path(__file__).parent / 'assets'

def b64(name):
    return base64.b64encode((ASSETS / name).read_bytes()).decode()

WM_FOOTER = b64('wordmark_footer.png')
SIGN_PLUS = b64('sign_plus.png')
SIGN_CIRCLE = b64('sign_circle.png')
SIGN_CROSS = b64('sign_cross.png')

# These get replaced by Zo when Zoho Flow is set up.
# Until then, the form falls back to WhatsApp + clipboard.
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz1WGf-IVNVd0efTrXV1oY8U1bAHSCIiO-OEmQJ6CeI5gfMaUhooKIXke2tr92zvOdE/exec"
WA_NUMBER = "919048191616"

# ============================================================
# ADALINE PAYMENT DETAILS — REPLACE PLACEHOLDERS BEFORE SHARING
# ============================================================
# These show up in two places: the Payment section of the form,
# and the success state after submission. The UPI QR code is
# auto-generated from upi_id + deposit_amount on rebuild.
PAYMENT = {
    'account_holder': 'Myadaline Communications LLP',
    'bank_name': 'Federal Bank',
    'account_number': '14130200024155',
    'ifsc': 'FDRL0001413',
    'branch': 'Calicut, Kerala',
    'upi_id': '1myadaline@fbl',
    'deposit_amount': 66600,            # 40% of ₹1,66,500 approved scope (website + engagement engine)
    'deposit_amount_display': '₹66,600',
    'deposit_note': 'Roca Fuel Project Deposit',
}

def gen_upi_qr(upi_id, name, amount, note):
    """Build a UPI deep-link QR — any UPI app (GPay/PhonePe/Paytm) reads it
    and pre-fills the payment with the account, amount, and reference note."""
    name_enc = quote(name)
    note_enc = quote(note)
    upi_str = f"upi://pay?pa={upi_id}&pn={name_enc}&am={amount}&cu=INR&tn={note_enc}"
    qr = qrcode.QRCode(box_size=10, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(upi_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#0a0a0a', back_color='#f5f1ea')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()

UPI_QR = gen_upi_qr(PAYMENT['upi_id'], PAYMENT['account_holder'], PAYMENT['deposit_amount'], PAYMENT['deposit_note'])

CSS = """
:root{
  --paper:#0b0b0b;--paper-2:#141414;--paper-3:#1c1c1c;--paper-4:#242424;
  --ink:#f5f1ea;--ink-soft:#d8d3cc;--muted:#807a72;--muted-2:#56524c;
  --line:#262626;--line-2:#363636;
  --acc:#ffd00a;--acc-2:#ffa733;--acc-soft:#cca308;
  --green:#3dd483;--red:#ff5e62;--cream:#f5f1ea;
  --display:'Space Grotesk',system-ui,sans-serif;
  --mono:'JetBrains Mono','Space Mono',monospace;
  --body:'Inter','Space Grotesk',system-ui,sans-serif;
  --pad:clamp(20px,5vw,48px);--maxw:1080px;--nav-h:54px;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{scroll-behavior:smooth;scroll-padding-top:var(--nav-h)}
body{margin:0;background:radial-gradient(ellipse 80% 50% at 50% 0%,rgba(255,208,10,.045),transparent 60%),var(--paper);color:var(--ink);font-family:var(--body);font-size:15.5px;line-height:1.65;-webkit-font-smoothing:antialiased;min-height:100vh;overflow-x:hidden}
::selection{background:var(--acc);color:var(--paper)}
:focus-visible{outline:2px solid var(--acc);outline-offset:2px;border-radius:2px}
button:focus-visible{outline-offset:4px}

.scroll-progress{position:fixed;top:0;left:0;height:2px;background:linear-gradient(90deg,var(--acc),var(--acc-2));width:0%;z-index:60;transition:width .1s ease}

.topnav{position:fixed;top:0;left:0;right:0;z-index:50;background:rgba(11,11,11,.85);backdrop-filter:blur(16px) saturate(150%);-webkit-backdrop-filter:blur(16px) saturate(150%);border-bottom:1px solid var(--line);height:var(--nav-h);display:flex;align-items:center;justify-content:space-between;padding:0 var(--pad);font-family:var(--mono);font-size:11.5px;letter-spacing:.04em}
.topnav .ntag{color:var(--ink);font-weight:600;letter-spacing:.08em;text-transform:uppercase;display:flex;align-items:center;gap:10px;min-width:0;flex:1}
.topnav .ntag .ntag-main{flex-shrink:0}
.topnav .ntag .sep{color:var(--muted-2);flex-shrink:0}
.topnav .ntag .small{color:var(--muted);font-weight:400;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.topnav .nlinks{display:flex;gap:20px}
.topnav .nlinks a{color:var(--muted);text-decoration:none;transition:color .15s;padding:8px 0;position:relative}
.topnav .nlinks a:hover{color:var(--ink-soft)}
.topnav .nlinks a.active{color:var(--ink)}
.topnav .nlinks a.active::after{content:"";position:absolute;left:0;right:0;bottom:-2px;height:2px;background:var(--acc);border-radius:1px}
.menu-toggle{display:none;background:none;border:1px solid var(--line);color:var(--ink);width:36px;height:32px;cursor:pointer;border-radius:3px;flex-direction:column;justify-content:center;align-items:center;gap:4px;flex-shrink:0;transition:border-color .2s,background .2s}
.menu-toggle:hover{border-color:var(--line-2);background:var(--paper-2)}
.menu-toggle span{display:block;width:14px;height:1.5px;background:var(--ink);transition:transform .25s,opacity .15s}
body.menu-open .menu-toggle span:nth-child(1){transform:translateY(5.5px) rotate(45deg)}
body.menu-open .menu-toggle span:nth-child(2){opacity:0}
body.menu-open .menu-toggle span:nth-child(3){transform:translateY(-5.5px) rotate(-45deg)}
@media(max-width:840px){.topnav .nlinks{display:none}.menu-toggle{display:flex}}

.mobile-menu{position:fixed;top:0;right:0;width:280px;max-width:85vw;height:100vh;background:var(--paper-2);border-left:1px solid var(--line);z-index:55;padding:calc(var(--nav-h) + 24px) 28px 28px;transform:translateX(100%);transition:transform .3s cubic-bezier(.4,0,.2,1);overflow-y:auto;display:flex;flex-direction:column;gap:4px}
body.menu-open .mobile-menu{transform:translateX(0)}
.mobile-menu a{font-family:var(--display);font-size:18px;font-weight:600;color:var(--ink-soft);text-decoration:none;padding:14px 0;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}
.mobile-menu a:hover,.mobile-menu a.active{color:var(--ink)}
.mobile-menu a .mm-num{font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.1em}
.mobile-menu a.active .mm-num{color:var(--acc)}
.menu-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);z-index:54;opacity:0;pointer-events:none;transition:opacity .25s}
body.menu-open .menu-backdrop{opacity:1;pointer-events:auto}

.page{max-width:var(--maxw);margin:0 auto;padding:0 var(--pad)}
section{padding:72px 0;border-top:1px solid var(--line);position:relative;scroll-margin-top:calc(var(--nav-h) + 12px)}
section:first-of-type{border-top:none;padding-top:calc(var(--nav-h) + 24px)}
@media(max-width:680px){section{padding:48px 0}}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.16em;color:var(--muted);text-transform:uppercase;margin-bottom:18px;display:flex;align-items:center;gap:12px}
.kicker::before{content:"";width:24px;height:1px;background:var(--muted)}
h1,h2,h3,h4{font-family:var(--display);font-weight:700;letter-spacing:-.015em;margin:0}
h2.sec-title{font-size:clamp(26px,4.2vw,38px);line-height:1.1;color:var(--ink);max-width:680px;margin-bottom:16px}
.sec-sub{color:var(--muted);font-size:15px;line-height:1.6;max-width:620px;margin:0 0 36px}
@media(max-width:680px){.sec-sub{font-size:14px;margin-bottom:28px}}

/* HERO */
.hero{padding-top:0;padding-bottom:0;min-height:calc(100vh - var(--nav-h));display:flex;flex-direction:column;justify-content:space-between;border-top:none}
.hero-head{padding:36px 0 0;display:flex;justify-content:space-between;align-items:flex-start;gap:24px;border-bottom:1px solid var(--line);padding-bottom:24px}
.hero-head .tag{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.hero-head .meta{font-family:var(--mono);font-size:11px;text-align:right;line-height:1.7}
.hero-head .meta .ml{color:var(--muted);letter-spacing:.1em;text-transform:uppercase}
.hero-head .meta .mv{color:var(--ink);font-weight:600}
@media(max-width:480px){.hero-head{flex-direction:column;align-items:flex-start;gap:14px}.hero-head .meta{text-align:left;font-size:10.5px}.hero-head .meta div{display:flex;gap:8px}}
.hero-mid{flex:1;display:flex;align-items:center;padding:36px 0}
.hero-mid .label{font-family:var(--mono);font-size:12px;letter-spacing:.18em;color:var(--muted);text-transform:uppercase;margin-bottom:16px}
.hero-mid h1{font-family:var(--display);font-size:clamp(52px,11vw,128px);font-weight:800;line-height:.9;letter-spacing:-.03em;color:var(--ink);margin:0}
.hero-mid h1 .ac{color:var(--acc)}
.hero-mid .sub{font-family:var(--mono);font-size:12.5px;letter-spacing:.05em;color:var(--ink-soft);margin-top:28px;display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center}
.hero-mid .sub .dot{width:4px;height:4px;background:var(--muted);border-radius:50%;flex-shrink:0}
@media(max-width:480px){.hero-mid .sub{font-size:11px;gap:5px 12px}}
.hero-foot{padding:24px 0 40px;display:flex;justify-content:space-between;align-items:flex-end;gap:24px;border-top:1px solid var(--line)}
.hero-foot .desc{font-size:14px;color:var(--ink-soft);max-width:520px;line-height:1.55}
.hero-foot .byline{font-family:var(--mono);font-size:10.5px;color:var(--muted);letter-spacing:.16em;text-transform:uppercase;text-align:right;line-height:1.7;flex-shrink:0}
.hero-foot .byline strong{color:var(--ink-soft)}
@media(max-width:680px){.hero-foot{flex-direction:column;align-items:flex-start;padding-bottom:32px}.hero-foot .byline{text-align:left}}

/* PROCESS STRIP */
.proc-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:8px}
@media(max-width:780px){.proc-strip{grid-template-columns:1fr 1fr}}
@media(max-width:460px){.proc-strip{grid-template-columns:1fr}}
.proc-step{background:var(--paper-2);border:1px solid var(--line);border-radius:4px;padding:22px;transition:border-color .2s;position:relative}
.proc-step.now{border-color:var(--acc)}
.proc-step.now::before{content:"YOU ARE HERE";position:absolute;top:-9px;left:18px;background:var(--acc);color:var(--paper);font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.14em;padding:2px 8px;border-radius:2px}
.proc-step .pn{font-family:var(--mono);font-size:11px;color:var(--acc);letter-spacing:.14em;margin-bottom:12px}
.proc-step h4{font-size:17px;color:var(--ink);margin-bottom:6px}
.proc-step p{font-size:13px;color:var(--muted);margin:0;line-height:1.5}

/* FORM */
.form-section{margin-top:4px}
.fld{margin-bottom:18px;position:relative}
.fld-row{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:0}
.fld-row .fld{margin-bottom:18px}
@media(max-width:680px){.fld-row{grid-template-columns:1fr;gap:0}}
.fld label{display:block;font-family:var(--mono);font-size:11px;color:var(--ink-soft);letter-spacing:.06em;text-transform:uppercase;margin-bottom:8px;font-weight:600}
.fld label .req{color:var(--acc);margin-left:3px}
.fld .hint{font-family:var(--body);font-size:12px;color:var(--muted);margin-top:6px;line-height:1.45;letter-spacing:normal;text-transform:none;font-weight:400}
.fld input[type="text"],.fld input[type="email"],.fld input[type="tel"],.fld input[type="number"],.fld input[type="date"],.fld input[type="url"],.fld select,.fld textarea{
  width:100%;background:var(--paper-2);border:1px solid var(--line);color:var(--ink);font-family:var(--body);font-size:14.5px;padding:11px 14px;border-radius:4px;transition:border-color .2s,background .2s;-webkit-appearance:none;appearance:none
}
.fld input:focus,.fld select:focus,.fld textarea:focus{outline:none;border-color:var(--acc);background:var(--paper-3)}
.fld input:hover,.fld select:hover,.fld textarea:hover{border-color:var(--line-2)}
.fld input.mirrored{opacity:.5;cursor:not-allowed;border-style:dashed}
.fld textarea{min-height:84px;resize:vertical;font-family:var(--body);line-height:1.55}
.fld select{cursor:pointer;background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);background-position:calc(100% - 18px) 50%,calc(100% - 13px) 50%;background-size:5px 5px,5px 5px;background-repeat:no-repeat;padding-right:36px}
.fld input::placeholder,.fld textarea::placeholder{color:var(--muted-2)}
.fld input:invalid:not(:placeholder-shown){border-color:rgba(255,94,98,.6)}
.fld.err input,.fld.err select,.fld.err textarea{border-color:var(--red)}
.fld .err-msg{color:var(--red);font-size:12px;font-family:var(--mono);margin-top:6px;display:none}
.fld.err .err-msg{display:block}
.confirm-card.err{border-color:var(--red)}
.confirm-card.err .opt{border-color:var(--red)}

/* RADIO + CHECKBOX */
.opt-group{display:flex;flex-wrap:wrap;gap:8px}
.opt{flex:0 1 auto;background:var(--paper-2);border:1px solid var(--line);border-radius:4px;padding:12px 14px;cursor:pointer;font-family:var(--mono);font-size:12px;color:var(--ink-soft);letter-spacing:.04em;transition:all .15s;display:inline-flex;align-items:center;gap:8px;position:relative;user-select:none;min-height:42px}
.opt:hover{border-color:var(--line-2);background:var(--paper-3)}
.opt input{position:absolute;opacity:0;pointer-events:none}
.opt .dot{display:inline-block;width:13px;height:13px;border:1.5px solid var(--muted-2);border-radius:50%;flex-shrink:0;transition:all .15s;position:relative}
.opt input[type="checkbox"] ~ .dot{border-radius:3px}
.opt:has(input:checked){background:var(--paper-3);border-color:var(--acc);color:var(--ink)}
.opt input:checked ~ .dot{border-color:var(--acc);background:var(--acc)}
.opt input[type="radio"]:checked ~ .dot::after{content:"";position:absolute;inset:3px;background:var(--paper);border-radius:50%}
.opt input[type="checkbox"]:checked ~ .dot::after{content:"";position:absolute;left:3px;top:0px;width:4px;height:8px;border:solid var(--paper);border-width:0 2px 2px 0;transform:rotate(45deg)}

.opt-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.opt-card{background:var(--paper-2);border:1px solid var(--line);border-radius:4px;padding:14px;cursor:pointer;transition:all .15s;position:relative;display:flex;align-items:flex-start;gap:12px}
.opt-card:hover{border-color:var(--line-2);background:var(--paper-3)}
.opt-card input{position:absolute;opacity:0;pointer-events:none}
.opt-card .dot{width:14px;height:14px;border:1.5px solid var(--muted-2);border-radius:50%;flex-shrink:0;transition:all .15s;position:relative;margin-top:2px}
.opt-card input[type="checkbox"] ~ .dot{border-radius:3px}
.opt-card:has(input:checked){border-color:var(--acc);background:var(--paper-3)}
.opt-card input:checked ~ .dot{border-color:var(--acc);background:var(--acc)}
.opt-card input[type="radio"]:checked ~ .dot::after{content:"";position:absolute;inset:3px;background:var(--paper);border-radius:50%}
.opt-card input[type="checkbox"]:checked ~ .dot::after{content:"";position:absolute;left:3px;top:0px;width:4px;height:8px;border:solid var(--paper);border-width:0 2px 2px 0;transform:rotate(45deg)}
.opt-card .ct{flex:1;min-width:0}
.opt-card .ct .h{font-size:13.5px;color:var(--ink);font-weight:600;margin-bottom:3px}
.opt-card .ct .d{font-size:12px;color:var(--muted);line-height:1.45}

/* CONFIRMATION CARDS */
.confirm-card{background:var(--paper-2);border:1px solid var(--line);border-radius:4px;padding:24px;margin-bottom:18px;display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center}
@media(max-width:560px){.confirm-card{grid-template-columns:1fr;gap:12px}}
.confirm-card .cc-label{font-family:var(--mono);font-size:10.5px;color:var(--muted);letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}
.confirm-card .cc-value{font-family:var(--display);font-size:22px;color:var(--ink);font-weight:700;letter-spacing:-.01em;margin-bottom:4px}
.confirm-card .cc-detail{font-family:var(--mono);font-size:12px;color:var(--ink-soft);line-height:1.55}
.confirm-card .cc-detail strong{color:var(--ink);font-weight:700}

/* PAYMENT DETAILS CARD (bank + UPI for advance deposit) */
.pay-card{margin-top:32px;background:linear-gradient(135deg,var(--paper-2),var(--paper-3));border:1px solid var(--line);border-radius:6px;overflow:hidden;position:relative}
.pay-card::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--acc),var(--acc-2))}
.pay-head{padding:22px 24px 18px;border-bottom:1px solid var(--line)}
.pay-head .pl{font-family:var(--mono);font-size:11px;color:var(--acc);letter-spacing:.16em;text-transform:uppercase;margin-bottom:8px}
.pay-head h3{font-family:var(--display);font-size:24px;color:var(--ink);font-weight:700;letter-spacing:-.01em;margin:0 0 4px}
.pay-head .pd{font-family:var(--mono);font-size:12px;color:var(--muted);letter-spacing:.04em}
.pay-body{display:grid;grid-template-columns:1.4fr 1fr;gap:0}
@media(max-width:680px){.pay-body{grid-template-columns:1fr}}
.pay-bank{padding:22px 24px;border-right:1px solid var(--line)}
@media(max-width:680px){.pay-bank{border-right:none;border-bottom:1px solid var(--line)}}
.pay-upi{padding:22px 24px;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px}
.pay-bank .ph,.pay-upi .ph{font-family:var(--mono);font-size:10.5px;color:var(--muted);letter-spacing:.16em;text-transform:uppercase;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.pay-bank .ph::before,.pay-upi .ph::before{content:"";width:14px;height:1px;background:var(--muted)}
.pay-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px dashed var(--line);gap:14px}
.pay-row:last-child{border-bottom:none}
.pay-row .pr-l{flex:1;min-width:0}
.pay-row .pr-label{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px}
.pay-row .pr-value{font-family:var(--mono);font-size:13.5px;color:var(--ink);font-weight:600;word-break:break-all;line-height:1.4}
.pay-row .pr-value.placeholder{color:var(--muted);font-style:italic;font-weight:400;border-bottom:1px dashed var(--muted-2);display:inline-block}
.pay-row .copy-btn{background:var(--paper);border:1px solid var(--line);color:var(--ink-soft);width:32px;height:32px;border-radius:3px;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s}
.pay-row .copy-btn:hover{background:var(--paper-2);border-color:var(--acc);color:var(--acc)}
.pay-row .copy-btn.copied{background:var(--acc);border-color:var(--acc);color:var(--paper)}
.pay-row .copy-btn svg{width:14px;height:14px}
.pay-qr{background:var(--cream);padding:12px;border-radius:4px;display:inline-block;line-height:0}
.pay-qr img{width:160px;height:160px;display:block;image-rendering:pixelated}
@media(max-width:680px){.pay-qr img{width:140px;height:140px}}
.pay-upi-id{font-family:var(--mono);font-size:13px;color:var(--ink);font-weight:600;display:flex;align-items:center;gap:8px;justify-content:center}
.pay-upi-id .copy-btn{width:26px;height:26px}
.pay-upi-id .copy-btn svg{width:11px;height:11px}
.pay-upi-hint{font-family:var(--mono);font-size:10.5px;color:var(--muted);letter-spacing:.06em;margin-top:2px;max-width:200px;line-height:1.5}
.pay-foot{padding:14px 24px;background:var(--paper);font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.06em;text-align:center;border-top:1px solid var(--line)}
.pay-foot strong{color:var(--ink-soft);font-weight:700}

/* SUBMIT */
.submit-box{margin-top:32px;padding:32px;background:linear-gradient(135deg,var(--paper-2),var(--paper-3));border:1px solid var(--line);border-radius:6px;text-align:center}
.submit-box h3{font-size:22px;color:var(--ink);margin:0 0 8px;letter-spacing:-.01em}
.submit-box p{color:var(--muted);font-size:14px;margin:0 0 22px;line-height:1.55}
.submit-btn{display:inline-flex;align-items:center;gap:10px;background:var(--acc);color:var(--paper);padding:14px 26px;border-radius:4px;font-family:var(--mono);font-size:13px;font-weight:700;letter-spacing:.06em;border:none;cursor:pointer;text-decoration:none;transition:transform .15s,box-shadow .2s,opacity .2s;text-transform:uppercase}
.submit-btn:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 6px 24px rgba(255,208,10,.3)}
.submit-btn:disabled{opacity:.5;cursor:not-allowed}
.submit-btn .arr{display:inline-block;width:10px;height:10px;border:solid currentColor;border-width:2px 2px 0 0;transform:rotate(45deg);margin-left:2px}
.submit-box .sb-note{margin-top:18px;font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.04em}

/* SUCCESS STATE */
/* SUCCESS STATE */
.success-wrap{display:none;padding:0;border-top:none}
.success-wrap:has(.success-state.show){display:block;padding:60px 0}
.success-state{display:none;text-align:center;padding:40px 24px}
.success-state.show{display:block}
.success-state .check{width:64px;height:64px;background:var(--acc);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;margin-bottom:20px}
.success-state .check::after{content:"";width:24px;height:14px;border:solid var(--paper);border-width:0 0 3px 3px;transform:rotate(-45deg);margin-top:-6px}
.success-state h3{font-size:26px;color:var(--ink);margin-bottom:10px;letter-spacing:-.01em}
.success-state p{color:var(--ink-soft);font-size:15px;line-height:1.6;max-width:480px;margin:0 auto 18px}
.success-state .next-steps{margin-top:24px;background:var(--paper-2);border:1px solid var(--line);border-radius:4px;padding:20px 24px;text-align:left;font-family:var(--mono);font-size:13px;color:var(--ink-soft);line-height:1.65}
.success-state .next-steps strong{color:var(--acc);font-weight:700;letter-spacing:.04em}

/* SUCCESS STATE — PAYMENT BLOCK */
.success-pay{margin-top:24px;background:linear-gradient(135deg,var(--paper-2),var(--paper-3));border:1px solid var(--line);border-radius:6px;overflow:hidden;position:relative;text-align:left}
.success-pay::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--acc),var(--acc-2))}
.success-pay .sp-head{padding:20px 24px 18px;border-bottom:1px solid var(--line)}
.success-pay .sp-l{font-family:var(--mono);font-size:11px;color:var(--acc);letter-spacing:.16em;text-transform:uppercase;margin-bottom:6px}
.success-pay .sp-head h4{font-family:var(--display);font-size:22px;color:var(--ink);font-weight:700;letter-spacing:-.01em;margin:0 0 4px}
.success-pay .sp-d{font-family:var(--body);font-size:13px;color:var(--muted);line-height:1.5}
.success-pay-body{display:grid;grid-template-columns:auto 1fr;gap:24px;padding:22px 24px;align-items:center}
@media(max-width:560px){.success-pay-body{grid-template-columns:1fr;justify-items:center;text-align:center}}
.success-pay .sp-qr{text-align:center}
.success-pay .sp-bank{font-family:var(--mono);font-size:12.5px;width:100%}
.success-pay .sp-bank-row{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px dashed var(--line);gap:14px}
.success-pay .sp-bank-row:last-child{border-bottom:none}
.success-pay .sp-k{color:var(--muted);text-transform:uppercase;letter-spacing:.1em;font-size:10px;flex-shrink:0}
.success-pay .sp-v{color:var(--ink);font-weight:600;text-align:right;word-break:break-all}
.success-pay .sp-v.ph{color:var(--muted);font-style:italic;font-weight:400}
.success-pay .sp-foot{padding:14px 24px;background:var(--paper);font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.04em;text-align:center;border-top:1px solid var(--line)}
.success-pay .sp-foot strong{color:var(--ink-soft);font-weight:700}

/* CLOSE */
.close{padding:80px var(--pad) 60px;text-align:center;border-top:1px solid var(--line);max-width:var(--maxw);margin:0 auto}
@media(max-width:480px){.close{padding:56px var(--pad) 40px}}
.close .signs{display:flex;justify-content:center;gap:32px;margin-bottom:32px}
@media(max-width:480px){.close .signs{gap:22px;margin-bottom:22px}.close .signs img{width:30px;height:30px}}
.close .signs img{width:36px;height:36px;opacity:.5;filter:brightness(0) invert(1)}
.close h2.thanks{font-family:var(--display);font-size:clamp(40px,7vw,72px);font-weight:800;letter-spacing:-.025em;line-height:.95;color:var(--ink);margin:0 0 18px}
.close .ck{font-family:var(--mono);font-size:12.5px;color:var(--muted);letter-spacing:.06em;max-width:520px;margin:0 auto;line-height:1.7}

.foot-block{margin-top:60px;padding:28px;background:var(--paper-2);border:1px solid var(--line);border-radius:4px;display:grid;grid-template-columns:auto auto 1fr auto;gap:20px 32px;align-items:center;text-align:left}
@media(max-width:780px){.foot-block{grid-template-columns:1fr;gap:18px;text-align:left;padding:22px}}
.foot-block .fb-wm img{height:30px;width:auto;filter:brightness(0) invert(1) opacity(.85);display:block}
.foot-block .fb-sep{width:1px;height:42px;background:var(--line)}
@media(max-width:780px){.foot-block .fb-sep{width:100%;height:1px}}
.foot-block .fb-tag{font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;line-height:1.7}
.foot-block .fb-tag strong{color:var(--ink-soft)}
.foot-block .fb-contact{font-family:var(--mono);font-size:12px;line-height:1.7;color:var(--ink-soft);text-align:right}
@media(max-width:780px){.foot-block .fb-contact{text-align:left}}
.foot-block .fb-contact .fbc-em{color:var(--ink);font-weight:700;font-size:13px;margin-bottom:4px}
.foot-block .fb-contact .fbc-fade{color:var(--muted);font-size:11px;margin-top:8px}

/* PROGRESS BAR (sticky bottom while filling) */
.fill-bar{position:fixed;bottom:0;left:0;right:0;background:rgba(11,11,11,.92);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-top:1px solid var(--line);padding:12px var(--pad);z-index:45;display:flex;align-items:center;gap:14px;justify-content:space-between;font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;transition:transform .3s}
.fill-bar.hide{transform:translateY(100%)}
.fill-bar .fb-status{color:var(--ink-soft);display:flex;align-items:center;gap:10px;min-width:0}
.fill-bar .fb-status b{color:var(--acc);font-weight:700}
.fill-bar .fb-progress-track{flex:1;max-width:200px;height:3px;background:var(--paper-3);border-radius:2px;overflow:hidden;margin:0 12px}
.fill-bar .fb-progress-fill{height:100%;background:linear-gradient(90deg,var(--acc),var(--acc-2));width:0%;transition:width .3s ease}
.fill-bar .fb-cta{background:var(--acc);color:var(--paper);border:none;padding:8px 16px;border-radius:3px;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.06em;cursor:pointer;text-transform:uppercase;transition:transform .15s;flex-shrink:0;text-decoration:none}
.fill-bar .fb-cta:hover{transform:translateY(-1px)}
@media(max-width:560px){.fill-bar .fb-progress-track{display:none}}

/* TOAST */
.toast-wrap{position:fixed;bottom:80px;left:50%;transform:translateX(-50%);z-index:90;pointer-events:none}
.toast{background:var(--ink);color:var(--paper);padding:10px 18px;border-radius:3px;font-family:var(--mono);font-size:12px;font-weight:700;letter-spacing:.04em;opacity:0;transform:translateY(10px);transition:opacity .25s,transform .25s;display:flex;align-items:center;gap:10px;max-width:90vw}
.toast.show{opacity:1;transform:translateY(0)}
.toast.err{background:var(--red);color:white}

/* PRINT — for backup record */
@media print{
  .topnav,.scroll-progress,.menu-toggle,.mobile-menu,.menu-backdrop,.fill-bar,.toast-wrap{display:none!important}
  body{background:white;color:black;font-size:11pt}
  section{padding:14pt 0;break-inside:avoid;border-color:#ccc}
  section:first-of-type{padding-top:0}
  .hero-mid h1{font-size:48pt;color:black}
  h2.sec-title{font-size:18pt;color:black}
  .fld input,.fld select,.fld textarea{border:1px solid #999;background:white;color:black}
  .opt,.opt-card,.confirm-card,.proc-step{background:#fafafa;color:black;border-color:#ccc}
  .submit-box{background:#f0f0f0;color:black;border-color:#ccc}
  .submit-btn{background:#333;color:white}
  .close{background:white}
  .foot-block{background:#fafafa;color:black;border-color:#ccc}
}
"""


JS = """
(function(){
  const form = document.getElementById('onboarding-form');
  const submitBtn = document.getElementById('submit-btn');
  const successState = document.getElementById('success-state');
  const fillBar = document.getElementById('fill-bar');
  const progressFill = document.querySelector('.fb-progress-fill');
  const progressLabel = document.querySelector('.fb-progress-label');
  const sp = document.querySelector('.scroll-progress');
  const toast = document.querySelector('.toast');

  const WEBHOOK_URL = '__WEBHOOK_URL__';
  const WA_NUMBER = '__WA_NUMBER__';

  // SCROLL PROGRESS
  let scrollTick=false;
  function updateScroll(){
    const h=document.documentElement;
    const max=h.scrollHeight-h.clientHeight;
    const pct=max>0?(h.scrollTop/max)*100:0;
    sp.style.width=pct+'%';
  }
  window.addEventListener('scroll',()=>{
    if(!scrollTick){
      requestAnimationFrame(()=>{ updateScroll(); scrollTick=false; });
      scrollTick=true;
    }
  },{passive:true});
  updateScroll();

  // ACTIVE NAV
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.topnav a, .mobile-menu a');
  function setActive(id){
    navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + id));
  }
  const obs = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting && e.intersectionRatio > 0.25) setActive(e.target.id);
  }), { threshold: [0.25,0.5], rootMargin: '-80px 0px -40% 0px' });
  sections.forEach(s => obs.observe(s));

  // MOBILE MENU
  const menuBtn = document.querySelector('.menu-toggle');
  const menuBackdrop = document.querySelector('.menu-backdrop');
  const mobileMenu = document.querySelector('.mobile-menu');
  function closeMenu() { document.body.classList.remove('menu-open'); }
  function openMenu() { document.body.classList.add('menu-open'); }
  if (menuBtn) menuBtn.addEventListener('click', () => {
    document.body.classList.contains('menu-open') ? closeMenu() : openMenu();
  });
  if (menuBackdrop) menuBackdrop.addEventListener('click', closeMenu);
  if (mobileMenu) mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });

  // PROGRESS TRACKING — unified walk of .fld + .confirm-card containers,
  // using closest-match so nested containers don't double-count
  function updateProgress() {
    let realFilled = 0;
    let realTotal = 0;
    document.querySelectorAll('.fld, .confirm-card').forEach(container => {
      const req = container.querySelector('[required]');
      if (!req) return;
      // Skip outer containers whose required field belongs to a nested container
      if (req.closest('.fld, .confirm-card') !== container) return;
      realTotal++;
      let filled = false;
      if (req.type === 'radio') {
        filled = !!form.querySelector(`[name="${req.name}"]:checked`);
      } else if (req.type === 'checkbox') {
        filled = req.checked;
      } else {
        filled = !!(req.value && req.value.trim());
      }
      if (filled) realFilled++;
    });
    const pct = realTotal > 0 ? Math.round((realFilled / realTotal) * 100) : 0;
    progressFill.style.width = pct + '%';
    progressLabel.innerHTML = `<b>${realFilled}</b> of ${realTotal} required fields`;
  }
  form.addEventListener('input', updateProgress);
  form.addEventListener('change', updateProgress);
  updateProgress();

  // SHOW FILL BAR ONLY AFTER FIRST SECTION
  const firstFormSection = document.getElementById('company');
  if (firstFormSection) {
    const fillObs = new IntersectionObserver(es => {
      es.forEach(e => {
        if (e.isIntersecting) fillBar.classList.remove('hide');
      });
    }, { threshold: 0.1 });
    fillObs.observe(firstFormSection);
  }

  // FILL BAR CTA = JUMP TO SUBMIT
  const fbCta = document.querySelector('.fb-cta');
  if (fbCta) fbCta.addEventListener('click', e => {
    e.preventDefault();
    document.getElementById('submit').scrollIntoView({ behavior: 'smooth' });
  });

  // TOAST
  function showToast(msg, isErr) {
    toast.textContent = msg;
    toast.classList.toggle('err', !!isErr);
    toast.classList.add('show');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove('show'), 3000);
  }

  // COPY-TO-CLIPBOARD for payment details (bank fields + UPI ID)
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.preventDefault();
      const text = btn.getAttribute('data-copy') || '';
      if (!text || text.includes('⟨')) {
        showToast('Detail not yet configured', true);
        return;
      }
      try {
        await navigator.clipboard.writeText(text);
        btn.classList.add('copied');
        // Swap icon to checkmark briefly
        const orig = btn.innerHTML;
        btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12l5 5L20 7"/></svg>';
        showToast('Copied to clipboard');
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = orig;
        }, 1600);
      } catch (err) {
        showToast('Copy failed — long-press to select instead', true);
      }
    });
  });

  // "SAME AS ABOVE" — mirror decision-maker into the day-to-day contact
  (function () {
    const ddSame = document.getElementById('dd_same');
    if (!ddSame) return;
    const map = [['dd_name', 'dm_name'], ['dd_role', 'dm_title'], ['dd_email', 'dm_email'], ['dd_phone', 'dm_phone']];
    function sync() {
      map.forEach(pair => {
        const d = document.getElementById(pair[0]);
        const m = document.getElementById(pair[1]);
        if (!d || !m) return;
        if (ddSame.checked) { d.value = m.value; d.readOnly = true; d.classList.add('mirrored'); }
        else { d.readOnly = false; d.classList.remove('mirrored'); }
      });
    }
    ddSame.addEventListener('change', () => {
      if (!ddSame.checked) map.forEach(pair => { const d = document.getElementById(pair[0]); if (d) d.value = ''; });
      sync();
    });
    // keep in sync if the decision-maker details change while ticked
    ['dm_name', 'dm_title', 'dm_email', 'dm_phone'].forEach(id => {
      const m = document.getElementById(id);
      if (m) m.addEventListener('input', () => { if (ddSame.checked) sync(); });
    });
  })();

  // GATHER FORM DATA AS STRUCTURED JSON
  function gatherFormData() {
    const data = { _meta: { client: 'Roca Fuel', form: 'onboarding', submitted_at: new Date().toISOString(), project_total: '₹1,66,500' } };
    const sections = ['company', 'project', 'access', 'comms', 'payment'];
    sections.forEach(sec => data[sec] = {});

    form.querySelectorAll('input, select, textarea').forEach(f => {
      if (!f.name) return;
      const sectionMatch = f.closest('section[id]');
      const sec = sectionMatch ? sectionMatch.id : 'misc';
      if (!data[sec]) data[sec] = {};

      if (f.type === 'checkbox') {
        if (!Array.isArray(data[sec][f.name])) data[sec][f.name] = [];
        if (f.checked) data[sec][f.name].push(f.value || true);
      } else if (f.type === 'radio') {
        if (f.checked) data[sec][f.name] = f.value;
      } else if (f.value && f.value.trim()) {
        data[sec][f.name] = f.value.trim();
      }
    });
    // Clean empty arrays
    Object.keys(data).forEach(sec => {
      if (typeof data[sec] === 'object') {
        Object.keys(data[sec]).forEach(k => {
          if (Array.isArray(data[sec][k]) && data[sec][k].length === 0) delete data[sec][k];
        });
      }
    });
    return data;
  }

  function formatForWhatsApp(data) {
    let lines = [`*Roca Fuel — Project Onboarding Submission*`, ''];
    lines.push(`Submitted: ${new Date().toLocaleString()}`);
    lines.push(`Project Total: ₹1,66,500`);
    lines.push('');
    const labels = { company: '01 · Company & Billing', project: '02 · Project Foundation', access: '03 · Technical Access', comms: '04 · Communication', payment: '05 · Payment' };
    Object.keys(labels).forEach(sec => {
      lines.push(`*${labels[sec]}*`);
      const obj = data[sec] || {};
      Object.keys(obj).forEach(k => {
        const v = Array.isArray(obj[k]) ? obj[k].join(', ') : obj[k];
        lines.push(`• ${k.replace(/_/g, ' ')}: ${v}`);
      });
      lines.push('');
    });
    return lines.join('\\n');
  }

  // VALIDATION
  function validate() {
    let firstError = null;
    form.querySelectorAll('.fld, .confirm-card').forEach(fld => fld.classList.remove('err'));
    form.querySelectorAll('[required]').forEach(f => {
      const fld = f.closest('.fld, .confirm-card');
      if (!fld) return;
      let ok = true;
      if (f.type === 'radio') {
        ok = !!form.querySelector(`[name="${f.name}"]:checked`);
      } else if (f.type === 'checkbox') {
        ok = f.checked;
      } else {
        ok = !!(f.value && f.value.trim());
      }
      if (!ok) {
        fld.classList.add('err');
        if (!firstError) firstError = fld;
      }
    });
    if (firstError) {
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      showToast('Please complete the highlighted required fields', true);
    }
    return !firstError;
  }

  // SUBMIT HANDLER
  submitBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    if (!validate()) return;

    const data = gatherFormData();
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Submitting…';

    let success = false;

    // Try webhook first
    if (WEBHOOK_URL && !WEBHOOK_URL.includes('REPLACE_WITH')) {
      try {
        const r = await fetch(WEBHOOK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
          mode: 'no-cors'
        });
        success = true;
      } catch (err) {
        console.warn('Webhook failed:', err);
      }
    }

    // Always copy to clipboard as backup
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    } catch (e) {}

    if (success) {
      // Show success state
      form.style.display = 'none';
      successState.classList.add('show');
      fillBar.classList.add('hide');
      successState.scrollIntoView({ behavior: 'smooth' });
    } else {
      // Fallback: open WhatsApp with structured summary
      const summary = formatForWhatsApp(data);
      const waUrl = 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(summary);
      showToast('Opening WhatsApp with your details — please send the message to confirm submission');
      setTimeout(() => {
        window.open(waUrl, '_blank');
        // Show success after they've opened WA
        setTimeout(() => {
          form.style.display = 'none';
          successState.classList.add('show');
          fillBar.classList.add('hide');
          successState.scrollIntoView({ behavior: 'smooth' });
        }, 800);
      }, 600);
    }
    submitBtn.disabled = false;
    submitBtn.innerHTML = 'Submit & Start the Project <span class="arr"></span>';
  });
})();
""".replace('__WEBHOOK_URL__', WEBHOOK_URL).replace('__WA_NUMBER__', WA_NUMBER)


HERO = """
<section class="hero page" id="cover" aria-label="Cover">
  <div class="hero-head">
    <div class="tag">Project Onboarding</div>
    <div class="meta">
      <div><span class="ml">Project</span> <span class="mv">Roca Fuel · Customer Engagement Engine + Website</span></div>
      <div><span class="ml">Programme</span> <span class="mv">₹1,66,500 · ≈ 8-week build</span></div>
    </div>
  </div>
  <div class="hero-mid">
    <div>
      <div class="label">Welcome aboard</div>
      <h1>Let's get<br/>you set<span class="ac">.</span> up</h1>
      <div class="sub">
        <span>~10 minutes</span><span class="dot"></span>
        <span>5 sections</span><span class="dot"></span>
        <span>Save as you go</span><span class="dot"></span>
        <span>Goes straight to your project lead</span>
      </div>
    </div>
  </div>
  <div class="hero-foot">
    <div class="desc">A short onboarding form to give Adaline everything we need to start work on the Roca Fuel website and customer engagement engine. Fill it in, hit submit, and kickoff happens within 48 hours. Sticky bar at the bottom tracks your progress.</div>
    <div class="byline">Onboarding by<br/><strong>Adaline · The Agency</strong></div>
  </div>
</section>
"""

PROCESS_STRIP = """
<section id="process" class="page" aria-labelledby="process-title">
  <div class="kicker">00 · What Happens After You Submit</div>
  <h2 class="sec-title" id="process-title">From here to live — about eight weeks.</h2>
  <p class="sec-sub">Once this form is submitted, your project lead reaches out within 48 hours. Kickoff books for week 1, the website launches around week 4, and the customer engagement engine follows around week 7–8.</p>

  <div class="proc-strip">
    <div class="proc-step now"><div class="pn">STEP 01</div><h4>You Submit</h4><p>This form. Right now. ~10 minutes.</p></div>
    <div class="proc-step"><div class="pn">STEP 02</div><h4>Kickoff Call</h4><p>Within 48 hours. 60 minutes. Project lead introduces team, locks the kickoff date, schedules weekly syncs.</p></div>
    <div class="proc-step"><div class="pn">STEP 03</div><h4>Build</h4><p>Track A — website (16–18 working days). Track B — engagement engine (30–35 working days). Weekly sync updates, mid-project demo.</p></div>
    <div class="proc-step"><div class="pn">STEP 04</div><h4>Launch</h4><p>Website live first (~week 4), engagement engine around week 7–8. Testing, hosting, training, handover.</p></div>
  </div>
</section>
"""

COMPANY = """
<section id="company" class="page" aria-labelledby="company-title">
  <div class="kicker">01 · Company &amp; Billing</div>
  <h2 class="sec-title" id="company-title">Who you are. Where invoices go.</h2>
  <p class="sec-sub">The legal entity, billing address, and the people on your side who can make decisions and answer questions.</p>

  <div class="form-section">
    <div class="fld-row">
      <div class="fld">
        <label for="legal_name">Legal Entity Name <span class="req">*</span></label>
        <input type="text" id="legal_name" name="legal_name" required placeholder="e.g. Roca Fuel Energy LLP">
        <div class="err-msg">Required</div>
      </div>
      <div class="fld">
        <label for="trade_name">Trade Name (if different)</label>
        <input type="text" id="trade_name" name="trade_name" placeholder="e.g. Roca Fuel">
      </div>
    </div>

    <div class="fld-row">
      <div class="fld">
        <label for="tax_id">GSTIN / Company Registration <span class="req">*</span></label>
        <input type="text" id="tax_id" name="tax_id" required placeholder="GSTIN or company registration number">
        <div class="err-msg">Required for invoicing</div>
      </div>
      <div class="fld">
        <label for="country">Country <span class="req">*</span></label>
        <select id="country" name="country" required>
          <option value="India" selected>India</option>
          <option value="UAE">UAE</option>
          <option value="KSA">Saudi Arabia</option>
          <option value="Qatar">Qatar</option>
          <option value="Bahrain">Bahrain</option>
          <option value="Oman">Oman</option>
          <option value="Other">Other</option>
        </select>
      </div>
    </div>

    <div class="fld">
      <label for="billing_address">Billing Address <span class="req">*</span></label>
      <textarea id="billing_address" name="billing_address" required placeholder="Full registered address — used on invoices"></textarea>
      <div class="err-msg">Required</div>
    </div>

  </div>

  <h3 style="font-family:var(--display);font-size:18px;color:var(--ink);margin:36px 0 18px;font-weight:700">Decision-Maker (signs off on design, scope, payment)</h3>
  <div class="form-section">
    <div class="fld-row">
      <div class="fld">
        <label for="dm_name">Name <span class="req">*</span></label>
        <input type="text" id="dm_name" name="dm_name" required>
        <div class="err-msg">Required</div>
      </div>
      <div class="fld">
        <label for="dm_title">Title / Role <span class="req">*</span></label>
        <input type="text" id="dm_title" name="dm_title" required placeholder="e.g. Managing Director">
        <div class="err-msg">Required</div>
      </div>
    </div>
    <div class="fld-row">
      <div class="fld">
        <label for="dm_email">Email <span class="req">*</span></label>
        <input type="email" id="dm_email" name="dm_email" required placeholder="name@rocafuel.com">
        <div class="err-msg">Valid email required</div>
      </div>
      <div class="fld">
        <label for="dm_phone">Phone / WhatsApp <span class="req">*</span></label>
        <input type="tel" id="dm_phone" name="dm_phone" required placeholder="+91...">
        <div class="err-msg">Required</div>
      </div>
    </div>
  </div>

  <h3 style="font-family:var(--display);font-size:18px;color:var(--ink);margin:36px 0 14px;font-weight:700">Day-to-Day Contact</h3>
  <label class="opt dd-same" style="margin-bottom:16px"><input type="checkbox" id="dd_same"><span class="dot"></span>Same as the decision-maker above</label>
  <div class="form-section">
    <div class="fld-row">
      <div class="fld">
        <label for="dd_name">Name</label>
        <input type="text" id="dd_name" name="dd_name" placeholder="If different from the decision-maker">
      </div>
      <div class="fld">
        <label for="dd_role">Role</label>
        <input type="text" id="dd_role" name="dd_role" placeholder="e.g. Marketing Manager">
      </div>
    </div>
    <div class="fld-row">
      <div class="fld">
        <label for="dd_email">Email</label>
        <input type="email" id="dd_email" name="dd_email">
      </div>
      <div class="fld">
        <label for="dd_phone">Phone / WhatsApp</label>
        <input type="tel" id="dd_phone" name="dd_phone">
      </div>
    </div>
  </div>
</section>
"""

PROJECT = """
<section id="project" class="page" aria-labelledby="project-title">
  <div class="kicker">02 · Project Foundation</div>
  <h2 class="sec-title" id="project-title">Your brand. What we'll build from.</h2>
  <p class="sec-sub">Honest answers here save everyone time. If something's not ready we'll plan around it, not pretend it is.</p>

  <div class="form-section">
    <div class="fld">
      <label>Brand Assets <span class="req">*</span></label>
      <div class="hint" style="margin-bottom:10px">Logo files, brand colors, fonts, brand guidelines document</div>
      <div class="opt-cards">
        <label class="opt-card"><input type="radio" name="brand_assets" value="ready" required><span class="dot"></span><div class="ct"><div class="h">All ready</div><div class="d">Logo files + brand guide both available</div></div></label>
        <label class="opt-card"><input type="radio" name="brand_assets" value="partial"><span class="dot"></span><div class="ct"><div class="h">Partial</div><div class="d">Logo yes, no formal brand guide</div></div></label>
        <label class="opt-card"><input type="radio" name="brand_assets" value="will_send"><span class="dot"></span><div class="ct"><div class="h">Will share via WhatsApp</div><div class="d">Got the files, just need to send them across</div></div></label>
        <label class="opt-card"><input type="radio" name="brand_assets" value="need_help"><span class="dot"></span><div class="ct"><div class="h">Need our help</div><div class="d">Brand needs work — let's discuss in kickoff</div></div></label>
      </div>
      <div class="err-msg">Pick one</div>
    </div>

    <div class="fld">
      <label for="brand_notes">Brand Notes (optional)</label>
      <textarea id="brand_notes" name="brand_notes" placeholder="Colors you must use / must avoid, fonts, tone of voice, visual references you love or hate"></textarea>
    </div>
  </div>
</section>
"""

ACCESS = """
<section id="access" class="page" aria-labelledby="access-title">
  <div class="kicker">03 · Technical Access</div>
  <h2 class="sec-title" id="access-title">Domain and hosting — who controls what.</h2>
  <p class="sec-sub">We need access to deploy. Tell us what exists and who holds the keys.</p>

  <div class="form-section">
    <div class="fld-row">
      <div class="fld">
        <label for="domain_registrar">Domain Registrar <span class="req">*</span></label>
        <select id="domain_registrar" name="domain_registrar" required>
          <option value="">Select registrar</option>
          <option value="GoDaddy">GoDaddy</option>
          <option value="Namecheap">Namecheap</option>
          <option value="Cloudflare">Cloudflare</option>
          <option value="Google Domains">Google Domains</option>
          <option value="Local provider">Local provider (India)</option>
          <option value="Other">Other</option>
          <option value="Unknown">Don't know</option>
        </select>
        <div class="err-msg">Required</div>
      </div>
      <div class="fld">
        <label for="domain_access">Domain Control <span class="req">*</span></label>
        <select id="domain_access" name="domain_access" required>
          <option value="">Select access level</option>
          <option value="Full">Full — we have login</option>
          <option value="Partial">Partial — via agency / IT vendor</option>
          <option value="Need_to_acquire">Need to acquire / transfer</option>
        </select>
        <div class="err-msg">Required</div>
      </div>
    </div>

    <div class="fld-row">
      <div class="fld">
        <label for="current_hosting">Current Hosting Provider</label>
        <input type="text" id="current_hosting" name="current_hosting" placeholder="e.g. Hostinger, GoDaddy, cPanel, own server">
      </div>
      <div class="fld">
        <label>Need Migration Support?</label>
        <div class="opt-group">
          <label class="opt"><input type="radio" name="migration_needed" value="yes"><span class="dot"></span>Yes</label>
          <label class="opt"><input type="radio" name="migration_needed" value="no"><span class="dot"></span>No</label>
          <label class="opt"><input type="radio" name="migration_needed" value="unsure"><span class="dot"></span>Not sure</label>
        </div>
      </div>
    </div>
  </div>
</section>
"""

COMMS = """
<section id="comms" class="page" aria-labelledby="comms-title">
  <div class="kicker">04 · Communication &amp; Calendar</div>
  <h2 class="sec-title" id="comms-title">How we talk. When we sync.</h2>
  <p class="sec-sub">Project rhythm — cadence and channel.</p>

  <div class="form-section">
    <div class="fld">
      <label>Primary Communication Channel <span class="req">*</span></label>
      <div class="opt-cards">
        <label class="opt-card"><input type="radio" name="channel" value="whatsapp_group" required><span class="dot"></span><div class="ct"><div class="h">WhatsApp Group</div><div class="d">Project group with stakeholders + Adaline lead</div></div></label>
        <label class="opt-card"><input type="radio" name="channel" value="email"><span class="dot"></span><div class="ct"><div class="h">Email primary</div><div class="d">Formal, threaded, slower turnaround</div></div></label>
        <label class="opt-card"><input type="radio" name="channel" value="slack"><span class="dot"></span><div class="ct"><div class="h">Slack</div><div class="d">If you already use it internally</div></div></label>
        <label class="opt-card"><input type="radio" name="channel" value="mixed"><span class="dot"></span><div class="ct"><div class="h">Mixed</div><div class="d">WhatsApp daily, email for formal sign-offs</div></div></label>
      </div>
      <div class="err-msg">Pick one</div>
    </div>

    <div class="fld">
      <label for="sync_freq">Sync Frequency <span class="req">*</span></label>
      <select id="sync_freq" name="sync_freq" required>
        <option value="weekly">Weekly</option>
        <option value="biweekly">Every two weeks</option>
        <option value="as_needed">As needed</option>
      </select>
      <div class="err-msg">Pick one</div>
    </div>
  </div>
</section>
"""

PAYMENT_SECTION = f"""
<section id="payment" class="page" aria-labelledby="payment-title">
  <div class="kicker">05 · Payment Confirmation</div>
  <h2 class="sec-title" id="payment-title">Confirm the numbers. Where invoices go.</h2>
  <p class="sec-sub">Mirroring the proposal so there's no ambiguity. Confirm or flag.</p>

  <div class="confirm-card">
    <div>
      <div class="cc-label">▸ TOTAL ENGAGEMENT FEE</div>
      <div class="cc-value">₹1,66,500</div>
      <div class="cc-detail">Portfolio website (₹68,500, incl. 1-year hosting) + customer engagement engine (₹98,000). Exclusive of GST.</div>
    </div>
    <label class="opt"><input type="checkbox" name="confirm_total" value="confirmed" required><span class="dot"></span>Confirmed</label>
  </div>

  <div class="confirm-card">
    <div>
      <div class="cc-label">▸ PAYMENT SCHEDULE — 40 / 40 / 20</div>
      <div class="cc-value">₹66,600 + ₹66,600 + ₹33,300</div>
      <div class="cc-detail"><strong>40%</strong> deposit on engagement start · <strong>40%</strong> at design sign-off (~end of week 2) · <strong>20%</strong> on launch &amp; handover</div>
    </div>
    <label class="opt"><input type="checkbox" name="confirm_schedule" value="confirmed" required><span class="dot"></span>Confirmed</label>
  </div>

  <div class="form-section" style="margin-top:32px">
    <div class="fld">
      <label>Payment Method <span class="req">*</span></label>
      <div class="opt-group">
        <label class="opt"><input type="radio" name="payment_method" value="bank_transfer" required><span class="dot"></span>Bank Transfer</label>
        <label class="opt"><input type="radio" name="payment_method" value="wire"><span class="dot"></span>International Wire</label>
        <label class="opt"><input type="radio" name="payment_method" value="cheque"><span class="dot"></span>Cheque</label>
        <label class="opt"><input type="radio" name="payment_method" value="other"><span class="dot"></span>Other</label>
      </div>
      <div class="err-msg">Pick one</div>
    </div>

    <div class="fld">
      <label for="ap_email">Accounts Payable Email <span class="req">*</span></label>
      <input type="email" id="ap_email" name="ap_email" required placeholder="Where invoices should be sent">
      <div class="err-msg">Required</div>
    </div>

    <div class="fld">
      <label for="invoice_notes">Invoice Requirements (optional)</label>
      <textarea id="invoice_notes" name="invoice_notes" placeholder="PO number formats, GST registration to reference, addressee lines, attachments required, etc."></textarea>
    </div>

    <div class="fld">
      <label>40% Deposit Timing <span class="req">*</span></label>
      <div class="opt-group">
        <label class="opt"><input type="radio" name="deposit_timing" value="immediately" required><span class="dot"></span>Within 3 days</label>
        <label class="opt"><input type="radio" name="deposit_timing" value="week"><span class="dot"></span>Within 7 days</label>
        <label class="opt"><input type="radio" name="deposit_timing" value="fortnight"><span class="dot"></span>Within 14 days</label>
        <label class="opt"><input type="radio" name="deposit_timing" value="end_of_month"><span class="dot"></span>End of month</label>
      </div>
      <div class="hint">Kickoff scheduling depends on this — design phase begins once deposit clears</div>
      <div class="err-msg">Pick one</div>
    </div>
  </div>

  <div class="pay-card">
    <div class="pay-head">
      <div class="pl">▸ PAY THE DEPOSIT</div>
      <h3>{PAYMENT['deposit_amount_display']} to start the build</h3>
      <div class="pd">Bank transfer or UPI · Reference: {PAYMENT['deposit_note']}</div>
    </div>
    <div class="pay-body">
      <div class="pay-bank">
        <div class="ph">Bank Transfer</div>
        <div class="pay-row">
          <div class="pr-l">
            <div class="pr-label">Account Holder</div>
            <div class="pr-value">{PAYMENT['account_holder']}</div>
          </div>
          <button type="button" class="copy-btn" data-copy="{PAYMENT['account_holder']}" aria-label="Copy account holder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="11" height="11" rx="1"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>
          </button>
        </div>
        <div class="pay-row">
          <div class="pr-l">
            <div class="pr-label">Bank</div>
            <div class="pr-value">{PAYMENT['bank_name']}</div>
          </div>
          <button type="button" class="copy-btn" data-copy="{PAYMENT['bank_name']}" aria-label="Copy bank name">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="11" height="11" rx="1"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>
          </button>
        </div>
        <div class="pay-row">
          <div class="pr-l">
            <div class="pr-label">Account Number</div>
            <div class="pr-value">{PAYMENT['account_number']}</div>
          </div>
          <button type="button" class="copy-btn" data-copy="{PAYMENT['account_number']}" aria-label="Copy account number">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="11" height="11" rx="1"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>
          </button>
        </div>
        <div class="pay-row">
          <div class="pr-l">
            <div class="pr-label">IFSC</div>
            <div class="pr-value">{PAYMENT['ifsc']}</div>
          </div>
          <button type="button" class="copy-btn" data-copy="{PAYMENT['ifsc']}" aria-label="Copy IFSC code">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="11" height="11" rx="1"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>
          </button>
        </div>
        <div class="pay-row">
          <div class="pr-l">
            <div class="pr-label">Branch</div>
            <div class="pr-value">{PAYMENT['branch']}</div>
          </div>
          <button type="button" class="copy-btn" data-copy="{PAYMENT['branch']}" aria-label="Copy branch">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="11" height="11" rx="1"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>
          </button>
        </div>
      </div>
      <div class="pay-upi">
        <div class="ph">Or Pay via UPI</div>
        <div class="pay-qr"><img src="data:image/png;base64,{UPI_QR}" alt="UPI QR code — scan to pay the project deposit" loading="lazy"></div>
        <div class="pay-upi-id">
          {PAYMENT['upi_id']}
          <button type="button" class="copy-btn" data-copy="{PAYMENT['upi_id']}" aria-label="Copy UPI ID">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="11" height="11" rx="1"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>
          </button>
        </div>
        <div class="pay-upi-hint">Scan with GPay / PhonePe / Paytm — amount pre-fills</div>
      </div>
    </div>
    <div class="pay-foot">Share the transaction reference with your project lead once paid</div>
  </div>

</section>
"""

SUBMIT_BOX = f"""
<section id="submit" class="page" aria-labelledby="submit-title">
  <div class="kicker">06 · Submit</div>
  <h2 class="sec-title" id="submit-title">All done. Hit submit and we get moving.</h2>

  <div class="submit-box">
    <h3>Submit &amp; start the Roca Fuel project</h3>
    <p>Your project lead at Adaline will reach out within 48 hours to confirm receipt, introduce the team, and schedule the kickoff call.</p>
    <button type="button" class="submit-btn" id="submit-btn">Submit &amp; Start the Project <span class="arr"></span></button>
    <div class="sb-note">Your details go straight to Adaline · No third-party tracking</div>
  </div>
</section>
"""

# Success state lives OUTSIDE the form so it stays visible when form is hidden
SUCCESS_BLOCK = f"""
<section class="page success-wrap" aria-label="Submission success">
  <div class="success-state" id="success-state" role="status" aria-live="polite">
    <div class="check"></div>
    <h3>You're in. Welcome to the project.</h3>
    <p>Submission received. Your project lead at Adaline will reach out within 48 hours to schedule the kickoff call and walk you through next steps.</p>
    <div class="next-steps">
      <strong>NEXT 48 HOURS</strong><br/>
      → Your project lead introduces themselves via WhatsApp<br/>
      → Deposit invoice goes to your AP email<br/>
      → Kickoff call gets booked into your calendar<br/>
      → Brand assets collection starts<br/>
    </div>

    <div class="success-pay">
      <div class="sp-head">
        <div class="sp-l">▸ LOCK IN KICKOFF</div>
        <h4>Pay the {PAYMENT['deposit_amount_display']} deposit now</h4>
        <div class="sp-d">The build starts the day the deposit clears. Scan to pay or use the bank details below.</div>
      </div>
      <div class="success-pay-body">
        <div class="sp-qr">
          <div class="pay-qr"><img src="data:image/png;base64,{UPI_QR}" alt="UPI QR for the project deposit"></div>
          <div class="pay-upi-id" style="margin-top:10px">{PAYMENT['upi_id']}</div>
        </div>
        <div class="sp-bank">
          <div class="sp-bank-row"><span class="sp-k">Holder</span><span class="sp-v">{PAYMENT['account_holder']}</span></div>
          <div class="sp-bank-row"><span class="sp-k">Bank</span><span class="sp-v">{PAYMENT['bank_name']}</span></div>
          <div class="sp-bank-row"><span class="sp-k">A/C</span><span class="sp-v">{PAYMENT['account_number']}</span></div>
          <div class="sp-bank-row"><span class="sp-k">IFSC</span><span class="sp-v">{PAYMENT['ifsc']}</span></div>
          <div class="sp-bank-row"><span class="sp-k">Ref</span><span class="sp-v">{PAYMENT['deposit_note']}</span></div>
        </div>
      </div>
      <div class="sp-foot">Share the transaction reference with your project lead when paid</div>
    </div>
  </div>
</section>
"""

CLOSE = f"""
<section class="close page" aria-label="Close">
  <div class="signs">
    <img src="data:image/png;base64,{SIGN_PLUS}" alt="" loading="lazy">
    <img src="data:image/png;base64,{SIGN_CIRCLE}" alt="" loading="lazy">
    <img src="data:image/png;base64,{SIGN_CROSS}" alt="" loading="lazy">
  </div>
  <h2 class="thanks">Let's<br/>get to it.</h2>
  <div class="ck">Questions before submitting? <strong style="color:var(--acc)">Connect with us</strong> — your project lead is one message away.</div>

  <div class="foot-block">
    <div class="fb-wm"><img src="data:image/png;base64,{WM_FOOTER}" alt="Adaline"></div>
    <div class="fb-sep" aria-hidden="true"></div>
    <div class="fb-tag">Onboarding by<br/><strong>Myadaline Communications LLP</strong></div>
    <div class="fb-contact">
      <div class="fbc-em">+91 90481 91616</div>
      <div>bettercall@myadaline.com</div>
      <div class="fbc-fade">GSTIN 32ABYFM6787D1ZN · Calicut, Kerala</div>
    </div>
  </div>
</section>
"""

MOBILE_MENU = """
<div class="menu-backdrop" aria-hidden="true"></div>
<aside class="mobile-menu" aria-label="Mobile navigation">
  <a href="#cover"><span>Welcome</span><span class="mm-num">00</span></a>
  <a href="#process"><span>What Happens Next</span><span class="mm-num">00</span></a>
  <a href="#company"><span>Company &amp; Billing</span><span class="mm-num">01</span></a>
  <a href="#project"><span>Project Foundation</span><span class="mm-num">02</span></a>
  <a href="#access"><span>Technical Access</span><span class="mm-num">03</span></a>
  <a href="#comms"><span>Communication</span><span class="mm-num">04</span></a>
  <a href="#payment"><span>Payment</span><span class="mm-num">05</span></a>
  <a href="#submit"><span>Submit</span><span class="mm-num">06</span></a>
</aside>
"""

FILL_BAR = """
<div class="fill-bar hide" id="fill-bar">
  <div class="fb-status">
    <span class="fb-progress-label"><b>0</b> of 0 required fields</span>
  </div>
  <div class="fb-progress-track"><div class="fb-progress-fill"></div></div>
  <a href="#submit" class="fb-cta">Jump to Submit →</a>
</div>
"""

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b0b0b">
<title>Project Onboarding · Roca Fuel</title>
<meta name="description" content="Project Onboarding for Roca Fuel — Adaline The Agency.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<div class="scroll-progress" aria-hidden="true"></div>

<nav class="topnav" aria-label="Primary">
  <div class="ntag">
    <span class="ntag-main">Roca Fuel</span>
    <span class="sep">/</span>
    <span class="small">Project Onboarding</span>
  </div>
  <div class="nlinks">
    <a href="#company">Company</a>
    <a href="#project">Project</a>
    <a href="#access">Access</a>
    <a href="#comms">Comms</a>
    <a href="#payment">Payment</a>
    <a href="#submit">Submit</a>
  </div>
  <button class="menu-toggle" aria-label="Open navigation menu">
    <span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span>
  </button>
</nav>

{MOBILE_MENU}

<main>
<form id="onboarding-form" novalidate>
{HERO}
{PROCESS_STRIP}
{COMPANY}
{PROJECT}
{ACCESS}
{COMMS}
{PAYMENT_SECTION}
{SUBMIT_BOX}
</form>
{SUCCESS_BLOCK}
{CLOSE}
</main>

{FILL_BAR}

<div class="toast-wrap"><div class="toast" role="status" aria-live="polite"></div></div>

<script>{JS}</script>
</body>
</html>
"""

OUT = pathlib.Path(__file__).parent.parent / 'roca-fuel' / 'index.html'
OUT.write_text(HTML, encoding='utf-8')
print(f"Built. Size: {len(HTML)/1024:.1f} KB")
