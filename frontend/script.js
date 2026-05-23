// ─── CONFIG ──────────────────────────────────────────────────────────────────
const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://127.0.0.1:8000"
  : window.location.origin;

// ─── COLLEGE SLUG (auto-detected from URL ?college=SLUG) ─────────────────────
const urlParams   = new URLSearchParams(window.location.search);
const COLLEGE_SLUG = urlParams.get("college") || "";

// Show warning if no college slug in URL
window.addEventListener("DOMContentLoaded", () => {
  if (!COLLEGE_SLUG) {
    const banner = document.getElementById("noCollegeBanner");
    if (banner) banner.style.display = "block";
  } else {
    // Fetch and display college name silently
    fetch(`${API_BASE}/api/college/${COLLEGE_SLUG}`)
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          const el = document.getElementById("collegeNameDisplay");
          if (el) el.textContent = data.college.college_name;
          const badge = document.getElementById("collegeBadge");
          if (badge) badge.style.display = "inline-flex";
        }
      }).catch(() => {});
  }
});

// ─── SECTION NAVIGATION ───────────────────────────────────────────────────────
function showSection(name) {
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
  const target = document.getElementById(`section-${name}`);
  if (target) target.classList.add("active");
  const activeBtn = [...document.querySelectorAll(".nav-btn")].find(b =>
    b.getAttribute("onclick")?.includes(`'${name}'`)
  );
  if (activeBtn) activeBtn.classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function toggleMenu() {
  document.getElementById("mobileMenu").classList.toggle("open");
}

// ─── GRIEVANCE SUBMISSION ─────────────────────────────────────────────────────
async function submitGrievance(e) {
  e.preventDefault();

  if (!COLLEGE_SLUG) {
    document.getElementById("submitError").textContent = "❌ Invalid portal link. Please use your college's specific link.";
    document.getElementById("submitError").style.display = "block";
    return;
  }

  const btn = document.getElementById("submitBtn");
  btn.textContent = "⏳ Submitting...";
  btn.disabled = true;

  const body = {
    college_slug:  COLLEGE_SLUG,
    student_name:  document.getElementById("studentName").value.trim(),
    student_roll:  document.getElementById("studentRoll").value.trim(),
    department:    document.getElementById("department").value,
    category:      document.getElementById("category").value,
    subject:       document.getElementById("subject").value.trim(),
    description:   document.getElementById("description").value.trim(),
    contact_email: document.getElementById("contactEmail").value.trim() || null,
  };

  try {
    const resp = await fetch(`${API_BASE}/api/grievance/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await resp.json();

    if (data.success) {
      const el = document.getElementById("submitSuccess");
      el.innerHTML = `✅ <strong>Grievance Submitted!</strong> Your ticket is <strong>${data.ticket}</strong>. Note this number to track your complaint.`;
      el.style.display = "block";
      document.getElementById("submitError").style.display = "none";
      document.getElementById("grievanceForm").reset();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      throw new Error(data.detail || "Submission failed.");
    }
  } catch (err) {
    const el = document.getElementById("submitError");
    el.textContent = `❌ Error: ${err.message}`;
    el.style.display = "block";
    document.getElementById("submitSuccess").style.display = "none";
  } finally {
    btn.textContent = "📩 Submit Grievance";
    btn.disabled = false;
  }
}

// ─── TRACK GRIEVANCE ──────────────────────────────────────────────────────────
async function trackGrievance() {
  const roll = document.getElementById("trackRoll").value.trim();
  const resultsEl = document.getElementById("trackResults");

  if (!roll) {
    resultsEl.innerHTML = `<div class="error-banner">Please enter your roll number.</div>`;
    return;
  }

  if (!COLLEGE_SLUG) {
    resultsEl.innerHTML = `<div class="error-banner">Invalid portal link. Please use your college's specific link.</div>`;
    return;
  }

  resultsEl.innerHTML = `<p style="color:var(--muted);font-size:0.9rem;margin-top:1rem">🔍 Searching...</p>`;

  try {
    const resp = await fetch(`${API_BASE}/api/grievance/track/${COLLEGE_SLUG}/${encodeURIComponent(roll)}`);
    const data = await resp.json();

    if (!resp.ok) {
      resultsEl.innerHTML = `<div class="error-banner">${data.detail || "No grievances found."}</div>`;
      return;
    }

    const html = data.grievances.map(g => {
      const date = new Date(g.submitted_at).toLocaleDateString("en-IN", { day:"2-digit", month:"short", year:"numeric" });
      const statusClass = g.status.toLowerCase().replace(" ", "-");
      return `
        <div class="grievance-item">
          <div class="grievance-item-header">
            <div>
              <h4>${g.subject}</h4>
              <p>${g.category} · Submitted on ${date}</p>
            </div>
            <span class="status-badge ${statusClass}">${g.status}</span>
          </div>
          ${g.admin_remarks ? `<p style="margin-top:0.5rem;font-size:0.85rem;background:#F8F9FF;padding:0.5rem 0.75rem;border-radius:6px;border-left:3px solid var(--primary)"><strong>Admin Note:</strong> ${g.admin_remarks}</p>` : ""}
        </div>`;
    }).join("");

    resultsEl.innerHTML = `
      <p style="font-size:0.87rem;color:var(--muted);margin-bottom:0.75rem">Found <strong>${data.grievances.length}</strong> grievance(s) for roll <strong>${roll}</strong></p>
      ${html}`;
  } catch {
    resultsEl.innerHTML = `<div class="error-banner">Cannot connect to server.</div>`;
  }
}

// ─── AI CHATBOT ───────────────────────────────────────────────────────────────
function openChat() {
  document.getElementById("chatModal").style.display = "flex";
  document.getElementById("chatInput").focus();
}

function closeChat() {
  document.getElementById("chatModal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("chatModal")?.addEventListener("click", function(e) {
    if (e.target === this) closeChat();
  });
});

async function sendChat() {
  const input = document.getElementById("chatInput");
  const msg = input.value.trim();
  if (!msg) return;
  input.value = "";
  appendMessage(msg, "user");
  showTyping();

  try {
    const resp = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });
    const data = await resp.json();
    removeTyping();
    appendMessage(data.response || "Sorry, I couldn't process that. Please try again.", "bot");
  } catch {
    removeTyping();
    appendMessage("I'm having trouble connecting. Please try again later.", "bot");
  }
}

function sendQuick(msg) {
  document.getElementById("chatInput").value = msg;
  sendChat();
}

function appendMessage(text, type) {
  const container = document.getElementById("chatMessages");
  const div = document.createElement("div");
  div.className = `msg ${type === "bot" ? "bot-msg" : "user-msg"}`;
  div.innerHTML = `
    <div class="msg-avatar">${type === "bot" ? "🤖" : "👤"}</div>
    <div class="msg-bubble">${escapeHtml(text)}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function showTyping() {
  const container = document.getElementById("chatMessages");
  const div = document.createElement("div");
  div.className = "msg bot-msg";
  div.id = "typingIndicator";
  div.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div class="msg-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function removeTyping() {
  document.getElementById("typingIndicator")?.remove();
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n/g, "<br>");
}

// ─── VOICE INPUT ──────────────────────────────────────────────────────────────
let recognition = null;
let isListening = false;

function toggleVoice() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('Voice input is not supported in this browser. Please use Chrome.');
    return;
  }

  if (isListening) {
    recognition.stop();
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = 'en-IN';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isListening = true;
    document.getElementById('voiceBtn').classList.add('listening');
    document.getElementById('chatInput').placeholder = '🎤 Listening...';
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById('chatInput').value = transcript;
    sendChat();
  };

  recognition.onend = () => {
    isListening = false;
    document.getElementById('voiceBtn').classList.remove('listening');
    document.getElementById('chatInput').placeholder = 'Type or speak your message...';
  };

  recognition.onerror = (event) => {
    isListening = false;
    document.getElementById('voiceBtn').classList.remove('listening');
    document.getElementById('chatInput').placeholder = 'Type or speak your message...';
    if (event.error !== 'aborted') {
      alert('Microphone error: ' + event.error + '. Please allow microphone access.');
    }
  };

  recognition.start();
}
