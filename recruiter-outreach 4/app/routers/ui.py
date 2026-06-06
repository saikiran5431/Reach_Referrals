from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Recruiter Outreach</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1117;--surface:#161b22;--surface2:#1c2330;--border:#30363d;
  --text:#e6edf3;--muted:#8b949e;--accent:#7c3aed;--accent2:#5b21b6;
  --green:#238636;--greentext:#3fb950;--red:#8b2020;--redtext:#f85149;
  --yellow:#9e6a03;--yellowtext:#d29922;
}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}

/* Layout */
.shell{display:flex;height:100vh;overflow:hidden}
.sidebar{width:220px;min-width:220px;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:16px 0}
.logo{padding:0 16px 20px;font-size:15px;font-weight:700;color:var(--text);border-bottom:1px solid var(--border);margin-bottom:12px}
.logo span{color:var(--accent)}
.nav-item{padding:9px 16px;font-size:13px;cursor:pointer;color:var(--muted);border-left:3px solid transparent;transition:all .15s;display:flex;align-items:center;gap:8px}
.nav-item:hover{color:var(--text);background:var(--surface2)}
.nav-item.active{color:var(--text);border-left-color:var(--accent);background:var(--surface2)}
.main{flex:1;overflow-y:auto;padding:32px}
.page{display:none;max-width:760px;margin:0 auto}
.page.active{display:block}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:24px;margin-bottom:20px}
.card-title{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:18px}
h1{font-size:22px;font-weight:700;margin-bottom:6px}
.subtitle{color:var(--muted);font-size:14px;margin-bottom:28px}

/* Form */
.field{margin-bottom:14px}
.field label{display:block;font-size:13px;font-weight:500;color:#cdd9e5;margin-bottom:5px}
.field .hint{font-size:11px;color:var(--muted);margin-top:4px;line-height:1.5}
input,textarea,select{width:100%;background:#0d1117;border:1px solid var(--border);border-radius:6px;padding:9px 12px;color:var(--text);font-size:13px;outline:none;transition:border-color .15s;font-family:inherit}
input:focus,textarea:focus{border-color:var(--accent)}
input::placeholder,textarea::placeholder{color:#484f58}
textarea{resize:vertical;line-height:1.5}

/* Buttons */
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 18px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all .15s}
.btn:active{transform:scale(.97)}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:var(--accent2)}
.btn-ghost{background:transparent;border:1px solid var(--border);color:var(--muted)}
.btn-ghost:hover{border-color:var(--accent);color:var(--text)}
.btn-danger{background:var(--red);color:#fff}
.btn-danger:hover{opacity:.85}
.btn:disabled{opacity:.4;cursor:not-allowed}
.btn-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}

/* Badges */
.badge{display:inline-flex;align-items:center;gap:4px;padding:2px 9px;border-radius:12px;font-size:11px;font-weight:600}
.badge.set{background:#0d2818;color:var(--greentext)}
.badge.unset{background:#2d1a00;color:var(--yellowtext)}
.badge.sent{background:#0d2818;color:var(--greentext)}
.badge.ready{background:#0c1a3a;color:#79c0ff}
.badge.failed{background:#2d0a0a;color:var(--redtext)}

/* Status rows */
.status-row{display:flex;align-items:center;justify-content:space-between;padding:9px 0;border-bottom:1px solid #1c2330;font-size:13px;color:var(--muted)}
.status-row:last-child{border:none}

/* Alert */
.alert{padding:12px 14px;border-radius:6px;font-size:13px;font-weight:500;margin-top:16px;display:none;line-height:1.5}
.alert.show{display:block}
.alert.success{background:#0d2818;color:var(--greentext);border:1px solid #238636}
.alert.error{background:#2d0a0a;color:var(--redtext);border:1px solid #8b2020}
.alert.info{background:#0c1a3a;color:#79c0ff;border:1px solid #1f4a8a}

/* Table */
.table-wrap{overflow-x:auto;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:8px 12px;color:var(--muted);font-weight:500;border-bottom:1px solid var(--border);font-size:11px;text-transform:uppercase;letter-spacing:.06em}
td{padding:10px 12px;border-bottom:1px solid #1c2330;vertical-align:top}
tr:last-child td{border:none}
tr:hover td{background:var(--surface2)}
.email-cell{font-family:'SF Mono',Monaco,monospace;font-size:12px;color:#79c0ff}

/* Preview modal */
.modal-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center;z-index:100;padding:20px}
.modal-backdrop.show{display:flex}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:12px;width:100%;max-width:620px;max-height:80vh;overflow-y:auto}
.modal-header{padding:20px 24px 16px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.modal-header h3{font-size:15px;font-weight:600}
.modal-close{background:none;border:none;color:var(--muted);font-size:20px;cursor:pointer;padding:0 4px}
.modal-close:hover{color:var(--text)}
.modal-body{padding:20px 24px}
.email-preview{background:#0d1117;border:1px solid var(--border);border-radius:6px;padding:16px;font-size:13px;line-height:1.7;white-space:pre-wrap;color:#cdd9e5;margin-top:8px;max-height:320px;overflow-y:auto}
.preview-subject{font-size:14px;font-weight:600;color:var(--text);margin-bottom:10px}
.meta-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;margin-top:12px}

/* Spinner */
.spinner{width:14px;height:14px;border:2px solid rgba(255,255,255,.25);border-top-color:#fff;border-radius:50%;animation:spin .6s linear infinite;display:inline-block}
@keyframes spin{to{transform:rotate(360deg)}}

/* Parse preview */
.parse-preview{margin-top:12px;padding:10px 14px;background:#0d1117;border:1px solid var(--border);border-radius:6px;font-size:12px;color:var(--muted);display:none}
.parse-preview.show{display:block}
.parse-row{display:flex;gap:8px;padding:3px 0;border-bottom:1px solid #1c2330}
.parse-row:last-child{border:none}
.parse-col{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text)}
.parse-col.dim{color:var(--muted)}
.parse-header{display:flex;gap:8px;padding:3px 0 6px;border-bottom:1px solid var(--border);margin-bottom:4px}
.parse-header span{flex:1;font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
</style>
</head>
<body>
<div class="shell">

  <!-- Sidebar -->
  <nav class="sidebar">
    <div class="logo">📨 <span>Outreach</span></div>
    <div class="nav-item active" onclick="nav('page-setup')">⚙️ Setup</div>
    <div class="nav-item" onclick="nav('page-contacts')">👥 Contacts</div>
    <div class="nav-item" onclick="nav('page-context')">✍️ Email Context</div>
    <div class="nav-item" onclick="nav('page-send')">🚀 Generate & Send</div>
    <div class="nav-item" onclick="nav('page-results')">📊 Results</div>
  </nav>

  <!-- Main -->
  <main class="main">

    <!-- ══ PAGE: Setup ══ -->
    <div id="page-setup" class="page active">
      <h1>Setup</h1>
      <p class="subtitle">Configure your sender profile and API credentials.</p>

      <div class="card">
        <div class="card-title">Status</div>
        <div id="statusRows"><div class="status-row"><span>Loading…</span></div></div>
      </div>

      <div class="card">
        <div class="card-title">Your Profile</div>
        <div class="field">
          <label>Full Name</label>
          <input id="s_name" placeholder="Sai Kiran">
        </div>
        <div class="field">
          <label>Gmail Address</label>
          <input id="s_email" type="email" placeholder="you@gmail.com">
        </div>
        <div class="field">
          <label>LinkedIn URL</label>
          <input id="s_linkedin" placeholder="https://linkedin.com/in/yourname">
        </div>
        <div class="field">
          <label>Role You're Seeking</label>
          <input id="s_role" placeholder="Senior Backend Engineer">
        </div>
        <div class="field">
          <label>Your Background <span style="color:var(--muted);font-weight:400">(Claude uses this to personalize emails)</span></label>
          <textarea id="s_exp" rows="3" placeholder="4 years Python/FastAPI, built fintech products at two startups, open to remote roles in India or abroad"></textarea>
        </div>
      </div>

      <div class="card">
        <div class="card-title">API Credentials</div>
        <div class="field">
          <label>Gmail App Password</label>
          <input id="s_gmail_pw" type="password" placeholder="xxxx xxxx xxxx xxxx">
          <div class="hint">Not your regular password. Create one at <a href="https://myaccount.google.com/apppasswords" target="_blank" style="color:#79c0ff">myaccount.google.com/apppasswords</a> (requires 2FA on).</div>
        </div>
        <div class="field">
          <label>Groq API Key</label>
          <input id="s_gemini" type="password" placeholder="gsk_...">
          <div class="hint">Free at <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#79c0ff">aistudio.google.com/app/apikey</a> — 1500 emails/day free, no card needed.</div>
        </div>
        <div class="field">
          <label>Hunter.io API Key <span style="color:var(--muted);font-weight:400">(optional — only needed if using domain lookup)</span></label>
          <input id="s_hunter" type="password" placeholder="Paste your key">
          <div class="hint"><a href="https://hunter.io/api" target="_blank" style="color:#79c0ff">hunter.io/api</a> — free tier, 25 searches/month</div>
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-primary" onclick="saveSettings()"><span id="saveLabel">💾 Save Settings</span></button>
        <button class="btn btn-ghost" onclick="testGmail()">🔌 Test Gmail</button>
      </div>
      <div id="setupAlert" class="alert"></div>
    </div>

    <!-- ══ Resume Upload Card ══ -->
    <div class="card">
      <div class="card-title">📎 Resume Attachment</div>
      <p style="font-size:13px;color:var(--muted);margin-bottom:14px">Attach your resume PDF to every outreach email automatically.</p>
      <div id="resumeStatus" style="font-size:13px;margin-bottom:12px;color:var(--muted)">Loading…</div>
      <div class="field">
        <label>Upload Resume (PDF only)</label>
        <input type="file" id="resumeFile" accept=".pdf" style="color:var(--text);font-size:13px">
      </div>
      <div class="btn-row">
        <button class="btn btn-primary" onclick="uploadResume()">📤 Upload Resume</button>
        <button class="btn btn-ghost" id="deleteResumeBtn" onclick="deleteResume()" style="display:none">🗑 Remove</button>
      </div>
      <div id="resumeAlert" class="alert"></div>
    </div>

    <!-- ══ PAGE: Contacts ══ -->
    <div id="page-contacts" class="page">
      <h1>Contacts</h1>
      <p class="subtitle">Paste your recruiter list. You control the emails directly.</p>

      <div class="card">
        <div class="card-title">Paste Email List</div>
        <div class="field">
          <label>One entry per line — name, email, company is all you need:</label>
          <div class="hint" style="margin-bottom:10px">
            • <code style="color:#79c0ff">Firstname Lastname, email@company.com, Company</code><br>
            • <code style="color:#79c0ff">email@company.com, Company</code> (name is optional)<br>
            • <code style="color:#79c0ff">email@company.com</code> (just email works too)<br>
            <span style="color:var(--greentext)">✦ Groq (llama-3.3-70b) writes personalized emails for each contact</span>
          </div>
          <textarea id="emailPaste" rows="10" placeholder="Shreya Ghumtane, shreya@stripe.com, Stripe
mike@openai.com, OpenAI
Emma Taylor, emma@figma.com, Figma
psk33034@gmail.com, Equifax"></textarea>
        </div>
        <div id="parsePreview" class="parse-preview"></div>
        <div class="btn-row">
          <button class="btn btn-ghost" onclick="previewParse()">👁 Preview Parse</button>
          <button class="btn btn-primary" onclick="addContacts()"><span id="addLabel">➕ Add Contacts</span></button>
        </div>
        <div id="contactAlert" class="alert"></div>
      </div>

      <div class="card">
        <div class="card-title">Current Contacts (<span id="contactCount">0</span>)</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Email</th><th>Company</th><th>Status</th><th></th></tr></thead>
            <tbody id="contactTable"><tr><td colspan="5" style="color:var(--muted);text-align:center;padding:20px">No contacts yet</td></tr></tbody>
          </table>
        </div>
        <div class="btn-row">
          <button class="btn btn-ghost" onclick="loadContacts()">🔄 Refresh</button>
          <button class="btn btn-danger" onclick="clearAll()" style="margin-left:auto">🗑 Clear All</button>
        </div>
      </div>
    </div>

    <!-- ══ PAGE: Email Context ══ -->
    <div id="page-context" class="page">
      <h1>Email Context</h1>
      <p class="subtitle">Write your own email template or talking points. Claude uses this as the base for every email.</p>

      <div class="card">
        <div class="card-title">Your Email Template / Context</div>
        <div class="field">
          <div class="hint" style="margin-bottom:10px;font-size:12px">
            Write anything — a rough draft, bullet points, your key skills, or a full template. Claude will personalize it for each recruiter.<br><br>
            <strong style="color:var(--text)">Tips:</strong> Include your key achievements, tech stack, what you're looking for, and any specific message you want to get across. You can also write a complete email — Claude will adapt it.
          </div>
          <textarea id="ctx_email" rows="16" placeholder="Hi [Name],

I came across [Company] and was impressed by [their work/product]. I'm a backend engineer with 4 years of experience building scalable Python services.

Key highlights:
- Built payment processing system handling $2M/day at my last startup
- Strong in FastAPI, PostgreSQL, Redis, Docker
- Led a team of 3 engineers

I'm currently exploring new opportunities and would love to chat about any backend roles at [Company].

Would you be open to a 15-minute call this week?

Thanks,
Sai"></textarea>
        </div>
        <div class="btn-row">
          <button class="btn btn-primary" onclick="saveContext()"><span id="ctxLabel">💾 Save Context</span></button>
        </div>
        <div id="contextAlert" class="alert"></div>
      </div>

      <div class="card" style="border-color:#1f4a8a">
        <div class="card-title" style="color:#79c0ff">How Claude uses this</div>
        <p style="font-size:13px;color:var(--muted);line-height:1.7">
          Claude receives your context + the recruiter's name, company, and email. It rewrites and personalizes the email for each person — keeping your key points but making it feel tailored. The more specific your context, the better the output. You can also just write bullet points and Claude will turn them into a proper email.
        </p>
      </div>
    </div>

    <!-- ══ PAGE: Generate & Send ══ -->
    <div id="page-send" class="page">
      <h1>Generate & Send</h1>
      <p class="subtitle">Claude writes a personalized email for each contact, then sends via Gmail.</p>

      <div class="card">
        <div class="card-title">Pipeline Summary</div>
        <div id="sendStats"><div style="color:var(--muted);font-size:13px">Loading…</div></div>
      </div>

      <div class="card">
        <div class="card-title">Options</div>
        <div class="field">
          <label>
            <input type="checkbox" id="opt_send" checked style="width:auto;margin-right:6px">
            Send emails immediately after generating (uncheck to just generate + preview first)
          </label>
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-primary" onclick="runCampaign()" id="runBtn">
          <span id="runLabel">⚡ Generate &amp; Send All</span>
        </button>
        <button class="btn btn-ghost" onclick="runCampaign(false)" id="genOnlyBtn">
          ✍️ Generate Only (Preview First)
        </button>
      </div>

      <div id="sendAlert" class="alert"></div>

      <div id="sendProgress" style="display:none;margin-top:20px">
        <div class="card">
          <div class="card-title">Progress</div>
          <div id="progressList"></div>
        </div>
      </div>
    </div>

    <!-- ══ PAGE: Results ══ -->
    <div id="page-results" class="page">
      <h1>Results</h1>
      <p class="subtitle">View sent emails and preview generated drafts.</p>

      <div class="card">
        <div class="card-title">All Contacts</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Email</th><th>Company</th><th>Status</th><th>Subject</th><th></th></tr></thead>
            <tbody id="resultsTable"><tr><td colspan="6" style="color:var(--muted);text-align:center;padding:20px">No data yet</td></tr></tbody>
          </table>
        </div>
        <div class="btn-row">
          <button class="btn btn-ghost" onclick="loadResults()">🔄 Refresh</button>
        </div>
      </div>
    </div>

  </main>
</div>

<!-- Preview Modal -->
<div id="modal" class="modal-backdrop" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-header">
      <h3 id="modalTitle">Email Preview</h3>
      <button class="modal-close" onclick="closeModal()">×</button>
    </div>
    <div class="modal-body">
      <div class="meta-label">To</div>
      <div id="modalTo" style="font-size:13px;color:#79c0ff"></div>
      <div class="meta-label">Subject</div>
      <div id="modalSubject" class="preview-subject"></div>
      <div class="meta-label">Body</div>
      <div id="modalBody" class="email-preview"></div>
    </div>
  </div>
</div>

<script>
// ── Navigation ─────────────────────────────────────────────────────────────
function nav(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(pageId).classList.add('active');
  event.currentTarget.classList.add('active');

  // Auto-load data when switching pages
  if (pageId === 'page-contacts') loadContacts();
  if (pageId === 'page-send') loadSendStats();
  if (pageId === 'page-results') loadResults();
  if (pageId === 'page-context') loadContext();
}

// ── Alert helper ───────────────────────────────────────────────────────────
function alert$(id, msg, type) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = 'alert show ' + type;
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  if (type === 'success') setTimeout(() => el.classList.remove('show'), 4000);
}

// ══════════════════════════════════════════════════════════════════════════
// SETUP PAGE
// ══════════════════════════════════════════════════════════════════════════
async function loadSettings() {
  try {
    const d = await (await fetch('/settings/')).json();
    document.getElementById('s_name').value    = d.sender_name    || '';
    document.getElementById('s_email').value   = d.sender_email   || '';
    document.getElementById('s_linkedin').value= d.sender_linkedin|| '';
    document.getElementById('s_role').value    = d.sender_role    || '';
    document.getElementById('s_exp').value     = d.sender_experience || '';

    const rows = [
      { label:'Your Name',       set: !!d.sender_name },
      { label:'Gmail Address',   set: !!d.sender_email },
      { label:'Gmail Password',  set: d.gmail_configured },
      { label:'Groq API Key', set: d.gemini_api_key_set },
      { label:'Hunter.io Key',   set: d.hunter_api_key_set },
      { label:'Email Context',   set: !!d.email_context },
      { label:'Resume Attached',  set: !!d.resume_filename },
    ];
    document.getElementById('statusRows').innerHTML = rows.map(r =>
      `<div class="status-row"><span>${r.label}</span>
       <span class="badge ${r.set?'set':'unset'}">${r.set?'✓ Set':'✗ Not set'}</span></div>`
    ).join('');

    // Update resume status
    const rs = document.getElementById('resumeStatus');
    const delBtn = document.getElementById('deleteResumeBtn');
    if (d.resume_filename) {
      rs.innerHTML = `<span style="color:#3fb950">✓ Attached: <strong>${d.resume_filename}</strong></span>`;
      delBtn.style.display = 'inline-block';
    } else {
      rs.textContent = 'No resume attached yet.';
      delBtn.style.display = 'none';
    }
  } catch(e) { alert$('setupAlert', 'Could not load: '+e.message, 'error'); }
}

async function saveSettings() {
  document.getElementById('saveLabel').innerHTML = '<span class="spinner"></span> Saving…';
  const payload = {
    sender_name:       document.getElementById('s_name').value.trim(),
    sender_email:      document.getElementById('s_email').value.trim(),
    sender_linkedin:   document.getElementById('s_linkedin').value.trim(),
    sender_role:       document.getElementById('s_role').value.trim(),
    sender_experience: document.getElementById('s_exp').value.trim(),
  };
  const pw = document.getElementById('s_gmail_pw').value.trim();
  const ak = document.getElementById('s_gemini').value.trim();
  const hk = document.getElementById('s_hunter').value.trim();
  if (pw) payload.gmail_app_password = pw;
  if (ak) payload.gemini_api_key = ak;
  if (hk) payload.hunter_api_key     = hk;

  try {
    const res = await fetch('/settings/', { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
    if (!res.ok) throw new Error((await res.json()).detail);
    alert$('setupAlert', '✓ Settings saved!', 'success');
    ['s_gmail_pw','s_gemini','s_hunter'].forEach(id => document.getElementById(id).value='');
    await loadSettings();
  } catch(e) { alert$('setupAlert', 'Error: '+e.message, 'error'); }
  finally { document.getElementById('saveLabel').textContent = '💾 Save Settings'; }
}

async function uploadResume() {
  const fileInput = document.getElementById('resumeFile');
  if (!fileInput.files.length) {
    alert$('resumeAlert', 'Please select a PDF file first.', 'error');
    return;
  }
  const file = fileInput.files[0];
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    alert$('resumeAlert', 'Only PDF files are accepted.', 'error');
    return;
  }
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await fetch('/settings/resume', { method: 'POST', body: form });
    if (!res.ok) throw new Error((await res.json()).detail);
    alert$('resumeAlert', '✓ Resume uploaded!', 'success');
    fileInput.value = '';
    await loadSettings();
  } catch(e) { alert$('resumeAlert', 'Error: '+e.message, 'error'); }
}

async function deleteResume() {
  try {
    const res = await fetch('/settings/resume', { method: 'DELETE' });
    if (!res.ok) throw new Error((await res.json()).detail);
    alert$('resumeAlert', 'Resume removed.', 'info');
    await loadSettings();
  } catch(e) { alert$('resumeAlert', 'Error: '+e.message, 'error'); }
}

async function testGmail() {
  alert$('setupAlert', 'Testing…', 'info');
  try {
    const d = await (await fetch('/settings/test-gmail')).json();
    if (d.success) alert$('setupAlert', '✓ Gmail works! Ready to send.', 'success');
    else alert$('setupAlert', '✗ ' + (d.error||'Failed') + (d.help?' — '+d.help:''), 'error');
  } catch(e) { alert$('setupAlert', 'Error: '+e.message, 'error'); }
}

// ══════════════════════════════════════════════════════════════════════════
// CONTACTS PAGE
// ══════════════════════════════════════════════════════════════════════════


const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : '';

// Parse a single line into {first_name, last_name, email, company}
// Format: "Name, email, Company" or "email, Company" or just "email"
function parseLine(line) {
  line = line.trim();
  if (!line || line.startsWith('#')) return null;

  // Split by comma
  const parts = line.split(',').map(s => s.trim()).filter(Boolean);

  // Find the email part (contains @)
  const emailIdx = parts.findIndex(p => p.includes('@'));
  if (emailIdx === -1) return null;

  const email = parts[emailIdx].toLowerCase();

  // Everything before email = name
  const nameParts = parts.slice(0, emailIdx).join(' ').trim().split(/\s+/).filter(Boolean);
  const first = cap(nameParts[0] || '');
  const last  = cap(nameParts.slice(1).join(' ') || '');

  // Everything after email = company (just first item)
  const company = parts.slice(emailIdx + 1)[0] || '';

  return { first_name: first, last_name: last, email, company };
}

function parseAll() {
  const lines = document.getElementById('emailPaste').value.split('\n');
  return lines.map(parseLine).filter(Boolean);
}

function previewParse() {
  const parsed = parseAll();
  const el = document.getElementById('parsePreview');
  if (!parsed.length) { el.classList.remove('show'); return; }

  el.innerHTML = `
    <div class="parse-header">
      <span>First</span><span>Last</span><span>Email</span><span>Company</span>
    </div>
    ${parsed.map(r=>`
    <div class="parse-row">
      <span class="parse-col">${r.first_name||'—'}</span>
      <span class="parse-col">${r.last_name||'—'}</span>
      <span class="parse-col" style="color:#79c0ff">${r.email}</span>
      <span class="parse-col dim">${r.company||'—'}</span>
    </div>`).join('')}
    <div style="margin-top:8px;font-size:11px;color:var(--muted)">${parsed.length} contact${parsed.length!==1?'s':''} detected</div>
  `;
  el.classList.add('show');
}

async function addContacts() {
  const parsed = parseAll();
  if (!parsed.length) { alert$('contactAlert','No valid emails found. Make sure each line has an @ symbol.','error'); return; }

  document.getElementById('addLabel').innerHTML = '<span class="spinner"></span> Adding…';
  try {
    const res = await fetch('/recruiters/bulk', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ recruiters: parsed })
    });
    const data = await res.json();
    if (!res.ok) {
      // FastAPI validation errors come back as {detail: [{msg:...}]} or {detail: "string"}
      const errMsg = Array.isArray(data.detail)
        ? data.detail.map(e => e.msg || JSON.stringify(e)).join(', ')
        : (data.detail || JSON.stringify(data));
      throw new Error(errMsg);
    }
    alert$('contactAlert', `✓ Added ${data.length} contacts successfully!`, 'success');
    document.getElementById('emailPaste').value = '';
    document.getElementById('parsePreview').classList.remove('show');
    await loadContacts();
  } catch(e) { alert$('contactAlert', 'Error: ' + e.message, 'error'); }
  finally { document.getElementById('addLabel').textContent = '➕ Add Contacts'; }
}

async function loadContacts() {
  try {
    const data = await (await fetch('/recruiters/')).json();
    document.getElementById('contactCount').textContent = data.length;
    const tbody = document.getElementById('contactTable');
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="5" style="color:var(--muted);text-align:center;padding:20px">No contacts yet</td></tr>';
      return;
    }
    tbody.innerHTML = data.map(r => `
      <tr>
        <td>${r.first_name} ${r.last_name}</td>
        <td class="email-cell">${r.email}</td>
        <td style="color:var(--muted)">${r.company||'—'}</td>
        <td><span class="badge ${r.status}">${r.status}</span></td>
        <td><button class="btn btn-ghost" style="padding:4px 10px;font-size:11px" onclick="deleteContact(${r.id})">✕</button></td>
      </tr>`).join('');
  } catch(e) {}
}

async function deleteContact(id) {
  await fetch('/recruiters/'+id, {method:'DELETE'});
  await loadContacts();
}

async function clearAll() {
  if (!confirm('Delete all contacts? This cannot be undone.')) return;
  // delete one by one
  const data = await (await fetch('/recruiters/')).json();
  for (const r of data) await fetch('/recruiters/'+r.id, {method:'DELETE'});
  await loadContacts();
}

// ══════════════════════════════════════════════════════════════════════════
// EMAIL CONTEXT PAGE
// ══════════════════════════════════════════════════════════════════════════
async function loadContext() {
  try {
    const d = await (await fetch('/settings/')).json();
    document.getElementById('ctx_email').value = d.email_context || '';
  } catch(e) {}
}

async function saveContext() {
  document.getElementById('ctxLabel').innerHTML = '<span class="spinner"></span> Saving…';
  const ctx = document.getElementById('ctx_email').value.trim();
  try {
    const res = await fetch('/settings/', {
      method:'PUT',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ email_context: ctx })
    });
    if (!res.ok) throw new Error((await res.json()).detail);
    alert$('contextAlert', '✓ Email context saved! Claude will use this for all emails.', 'success');
  } catch(e) { alert$('contextAlert','Error: '+e.message,'error'); }
  finally { document.getElementById('ctxLabel').textContent = '💾 Save Context'; }
}

// ══════════════════════════════════════════════════════════════════════════
// GENERATE & SEND PAGE
// ══════════════════════════════════════════════════════════════════════════
async function loadSendStats() {
  try {
    const d = await (await fetch('/recruiters/stats')).json();
    document.getElementById('sendStats').innerHTML = `
      <div class="status-row"><span>Total contacts</span><span style="color:var(--text);font-weight:600">${d.total}</span></div>
      <div class="status-row"><span>Ready to send</span><span style="color:#3fb950;font-weight:600">${d.by_status?.ready||0}</span></div>
      <div class="status-row"><span>Already sent</span><span style="color:var(--muted)">${d.by_status?.sent||0}</span></div>
      <div class="status-row"><span>Failed</span><span style="color:var(--redtext)">${d.by_status?.failed||0}</span></div>
    `;
  } catch(e) {}
}

async function runCampaign(sendImmediately) {
  const shouldSend = sendImmediately !== false && document.getElementById('opt_send').checked;

  document.getElementById('runBtn').disabled = true;
  document.getElementById('genOnlyBtn').disabled = true;
  document.getElementById('runLabel').innerHTML = '<span class="spinner"></span> Running…';

  const progDiv = document.getElementById('sendProgress');
  const progList = document.getElementById('progressList');
  progDiv.style.display = 'block';
  progList.innerHTML = '<div style="color:var(--muted);font-size:13px">Starting…</div>';

  try {
    const res = await fetch('/campaigns/run', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ send_after_generate: shouldSend, campaign_name: 'Batch ' + new Date().toLocaleDateString() })
    });
    const data = await res.json();

    if (!res.ok) {
      alert$('sendAlert', '✗ ' + (data.detail||'Unknown error'), 'error');
      progDiv.style.display = 'none';
      return;
    }

    // Show per-contact results
    progList.innerHTML = data.results.map(r => {
      const genIcon  = r.generated ? '✓' : '✗';
      const sendIcon = shouldSend ? (r.sent ? '✓' : '✗') : '—';
      const color    = (r.generated && (!shouldSend || r.sent)) ? 'var(--greentext)' : 'var(--redtext)';
      return `<div style="display:flex;gap:12px;padding:7px 0;border-bottom:1px solid #1c2330;font-size:13px">
        <span style="color:${color};font-weight:600">${genIcon}</span>
        <span style="flex:2">${r.name||r.email}</span>
        <span class="email-cell" style="flex:2">${r.email}</span>
        <span style="color:var(--muted);flex:3;font-size:12px">${r.subject||r.error||''}</span>
        ${shouldSend?`<span style="color:${r.sent?'var(--greentext)':'var(--redtext)'}">${sendIcon} ${r.sent?'Sent':'Failed'}</span>`:''}
      </div>`;
    }).join('');

    const msg = shouldSend
      ? `✓ Done — ${data.sent} sent, ${data.failed} failed out of ${data.total}`
      : `✓ Generated ${data.total} emails. Go to Results to preview, then send.`;
    alert$('sendAlert', msg, data.failed > 0 ? 'info' : 'success');
    await loadSendStats();

  } catch(e) { alert$('sendAlert','Error: '+e.message,'error'); }
  finally {
    document.getElementById('runBtn').disabled = false;
    document.getElementById('genOnlyBtn').disabled = false;
    document.getElementById('runLabel').textContent = '⚡ Generate & Send All';
  }
}

// ══════════════════════════════════════════════════════════════════════════
// RESULTS PAGE
// ══════════════════════════════════════════════════════════════════════════
async function loadResults() {
  try {
    const data = await (await fetch('/recruiters/')).json();
    const tbody = document.getElementById('resultsTable');
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="6" style="color:var(--muted);text-align:center;padding:20px">No data yet</td></tr>';
      return;
    }
    tbody.innerHTML = data.map(r => `
      <tr>
        <td>${r.first_name} ${r.last_name}</td>
        <td class="email-cell">${r.email}</td>
        <td style="color:var(--muted)">${r.company||'—'}</td>
        <td><span class="badge ${r.status}">${r.status}</span></td>
        <td style="color:var(--muted);font-size:12px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${r.generated_subject||'—'}</td>
        <td>${r.generated_subject ? `<button class="btn btn-ghost" style="padding:4px 10px;font-size:11px" onclick='previewEmail(${JSON.stringify(r)})'>👁 Preview</button>` : ''}</td>
      </tr>`).join('');
  } catch(e) {}
}

// ── Modal ──────────────────────────────────────────────────────────────────
function previewEmail(r) {
  document.getElementById('modalTitle').textContent = `Email to ${r.first_name} ${r.last_name}`.trim() || r.email;
  document.getElementById('modalTo').textContent    = r.email;
  document.getElementById('modalSubject').textContent = r.generated_subject || '—';
  document.getElementById('modalBody').textContent    = r.generated_body    || '—';
  document.getElementById('modal').classList.add('show');
}
function closeModal() { document.getElementById('modal').classList.remove('show'); }
document.addEventListener('keydown', e => { if(e.key==='Escape') closeModal(); });

// ── Boot ───────────────────────────────────────────────────────────────────
loadSettings();
</script>
</body>
</html>"""


@router.get("/setup", response_class=HTMLResponse, include_in_schema=False)
async def setup_page():
    return HTML

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root_redirect():
    return '<meta http-equiv="refresh" content="0;url=/setup">'