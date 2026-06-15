"""
SmartClassNotes v3 — main.py
"The Nocturnal Scholar / Digital Curator" design system
Updated with Native Streamlit Audio Input, Supabase Integration & Centered UI
"""
import streamlit as st
import os, time, base64, re, json
from datetime import datetime

# Map Streamlit secrets to environment variables for auth_supabase.py
if "supabase" in st.secrets:
    os.environ["SUPABASE_URL"] = st.secrets["supabase"]["url"]
    os.environ["SUPABASE_KEY"] = st.secrets["supabase"]["key"]
    if "service_role_key" in st.secrets["supabase"]:
        os.environ["SUPABASE_SERVICE_KEY"] = st.secrets["supabase"]["service_role_key"]

# Supabase Initialization
from supabase import create_client, Client
def init_supabase() -> Client:
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
supabase = init_supabase()
BACKEND = "supabase"

from auth_supabase import (login_user, register_user, get_profile,
    update_profile, delete_account, logout_user, update_profile_picture,
    remove_profile_picture, request_password_reset, reset_password)

from lecture4 import process_input

st.set_page_config(
    page_title="SMARTIE",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session defaults ──────────────────────────────────────────────────────────
DEFAULTS = {
    "logged_in": False, "user_id": None, "user_email": None,
    "user_name": None,  "profile_pic": "", "page": "login",
    "theme": "dark",    "language": "en", "history": [],
    "current_result": None, "input_method": None,
    "reset_token": None, "reset_email": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════════════════════════════════════════
TR = {
"en": {
    "app_name":"SMARTIE","tagline":"AI-powered lecture summarization",
    "how_help":"How can I help you today?",
    "command_placeholder":"Type a command or ask a question...",
    "chip_summarize":"Summarize Lecture","chip_quiz":"Generate Quiz",
    "chip_mic":"Record Audio","chip_youtube":"YouTube Video",
    "thinking":"Thinking...",
    "nav_summarize":"Summarize","nav_history":"History",
    "nav_analytics":"Analytics","nav_profile":"Profile",
    "new_note":"New Note",
    "sidebar_title":"SMARTIE",
    "sidebar_sub":"AI Note Summarization",
    "login_title":"Welcome Back","login_sub":"Enter your credentials to access your library",
    "email":"Email Address","password":"Password","sign_in":"Sign In",
    "forgot_password":"Forgot Password?","create_account":"Create Account",
    "new_curator":"New here?",
    "every_note":"Every note, a legacy.",
    "register_title":"Begin Your Archive",
    "register_sub":"Curate your academic journey with the precision of a digital scholar.",
    "full_name":"Full Name","confirm_password":"Confirm Password",
    "register_btn":"Create Account","already_member":"Already have an account?",
    "back_login":"Back to Login","ai_enhanced":"AI Enhanced","vault_secure":"Vault Secure",
    "forgot_title":"Reset Your Password",
    "forgot_badge":"Security Protocol",
    "forgot_sub":"Enter your email address to receive a 6-digit reset code.",
    "send_reset":"Send Reset Code","back_to_login":"Back to Login",
    "system_status":"System Status","servers_ok":"Global Servers Operational",
    "reset_title":"Set New Password","reset_btn":"Update Password",
    "new_password":"New Password","confirm_new_pass":"Confirm Password",
    "profile_title":"Account Settings",
    "profile_sub":"Manage your digital identity and academic preferences.",
    "personal_details":"Personal Details","full_name_lbl":"Full Name",
    "email_lbl":"Email Address","course_lbl":"Course / Major","bio_lbl":"Professional Bio",
    "save_changes":"Save Changes","last_updated":"Last updated: ",
    "upload_pic":"Upload Photo","remove_pic":"Remove Photo",
    "danger_zone":"Danger Zone",
    "danger_text":"Once you delete your account, there is no going back. Please be certain. All your curated notes and analytics will be permanently erased.",
    "delete_account":"Delete My Account","confirm_delete":"Type your email to confirm deletion",
    "input_method":"Choose Input Method",
    "paste_text":"Paste Text","microphone":"Microphone",
    "file_upload":"File Upload","youtube":"YouTube",
    "your_notes":"Your lecture notes",
    "notes_placeholder":"Paste lecture notes, textbook excerpts, or study material here…",
    "generate":"Generate Summary",
    "analysis_complete":"Analysis Complete",
    "summary_ready":"Summary Ready!",
    "summary_ready_sub":"Your academic transcript has been curated and distilled. We've preserved the core intellectual intent while reducing the cognitive load.",
    "key_pts_found":"Key Points Found","words_sum":"Words in Summary","reduction":"Reduction",
    "exec_summary":"Executive Summary","quick_overview":"Quick Overview",
    "primary_insight":"Primary Insight","synthesis":"Synthesis (Key Points)",
    "export_artifacts":"Export Artifacts",
    "pdf":"PDF","word":"Word","json":"JSON","new_summary":"+ New Summary",
    "history_title":"Recent Curator Logs",
    "history_sub":"Reviewing your intellectual trajectory.",
    "view_all":"View All",
    "analytics_title":"Intelligence Hub",
    "analytics_sub":"Quantitative insights from your digital library.",
    "total_summaries":"Total Summaries","avg_time":"Avg. Time Saved",
    "success_rate":"Success Rate",
    "input_dist":"Input Distribution",
    "no_summaries":"No curator logs yet. Generate your first summary.",
    "start_hint":"Select an input method above to get started",
    "duration_min":"Duration (minutes)",
    "start_rec":"Start Recording","stop_rec":"Stop & Discard",
    "gen_sum_from_rec":"Generate Summary",
    "process_file":"Process File","process_video":"Process Video",
    "valid_url":"Valid YouTube URL","invalid_url":"Invalid YouTube URL",
    "words":"words","characters":"characters",
    "pw_weak":"Weak","pw_medium":"Medium","pw_strong":"Strong",
    "pw_hint":"Use uppercase, lowercase, numbers & symbols.",
    "logout":"Logout",
    "about_title":"About SMARTIE",
    "about_sub":"Empowering university students through intelligent AI summarization",
},
"ms": {
    "app_name":"SMARTIE","tagline":"Ringkasan kuliah berkuasa AI",
    "how_help":"Bagaimana saya boleh bantu anda hari ini?",
    "command_placeholder":"Taip arahan atau tanya soalan...",
    "chip_summarize":"Ringkaskan Kuliah","chip_quiz":"Jana Kuiz",
    "chip_mic":"Rakam Audio","chip_youtube":"Video YouTube",
    "thinking":"Sedang berfikir...",
    "nav_summarize":"Ringkasan","nav_history":"Sejarah",
    "nav_analytics":"Analitik","nav_profile":"Profil",
    "new_note":"Nota Baharu",
    "sidebar_title":"SMARTIE",
    "sidebar_sub":"Ringkasan Nota AI",
    "login_title":"Selamat Kembali","login_sub":"Masukkan kelayakan anda untuk mengakses perpustakaan",
    "email":"Alamat E-mel","password":"Kata Laluan","sign_in":"Log Masuk",
    "forgot_password":"Lupa Kata Laluan?","create_account":"Daftar Akaun",
    "new_curator":"Ahli baharu?",
    "every_note":"Setiap nota, satu warisan.",
    "register_title":"Mulakan Arkib Anda",
    "register_sub":"Kurasi perjalanan akademik anda dengan ketepatan seorang sarjana digital.",
    "full_name":"Nama Penuh","confirm_password":"Sahkan Kata Laluan",
    "register_btn":"Cipta Akaun","already_member":"Sudah ada akaun?",
    "back_login":"Kembali ke Log Masuk","ai_enhanced":"Dipertingkat AI","vault_secure":"Selamat Peti Besi",
    "forgot_title":"Tetapkan Semula Kata Laluan",
    "forgot_badge":"Protokol Keselamatan",
    "forgot_sub":"Masukkan alamat e-mel anda untuk menerima kod 6-digit.",
    "send_reset":"Hantar Kod Tetapan Semula","back_to_login":"Kembali ke Log Masuk",
    "system_status":"Status Sistem","servers_ok":"Pelayan Global Beroperasi",
    "reset_title":"Tetapkan Kata Laluan Baharu","reset_btn":"Kemaskini Kata Laluan",
    "new_password":"Kata Laluan Baharu","confirm_new_pass":"Sahkan Kata Laluan",
    "profile_title":"Tetapan Akaun",
    "profile_sub":"Urus identiti digital dan keutamaan akademik anda.",
    "personal_details":"Maklumat Peribadi","full_name_lbl":"Nama Penuh",
    "email_lbl":"Alamat E-mel","course_lbl":"Kursus / Major","bio_lbl":"Bio Profesional",
    "save_changes":"Simpan Perubahan","last_updated":"Kemas kini terakhir: ",
    "upload_pic":"Muat Naik Foto","remove_pic":"Buang Foto",
    "danger_zone":"Zon Bahaya",
    "danger_text":"Setelah anda memadam akaun, tiada jalan balik. Sila pastikan. Semua nota dan analitik anda akan dihapuskan secara kekal.",
    "delete_account":"Padam Akaun Saya","confirm_delete":"Taip e-mel anda untuk mengesahkan pemadaman",
    "input_method":"Pilih Kaedah Input",
    "paste_text":"Tampal Teks","microphone":"Mikrofon",
    "file_upload":"Muat Naik Fail","youtube":"YouTube",
    "your_notes":"Nota kuliah anda",
    "notes_placeholder":"Tampal nota kuliah, petikan buku teks, atau bahan kajian di sini…",
    "generate":"Jana Ringkasan",
    "analysis_complete":"Analisis Selesai",
    "summary_ready":"Ringkasan Sedia!",
    "summary_ready_sub":"Transkrip akademik anda telah dikurasi dan disuling. Kami mengekalkan hasrat intelektual teras sambil mengurangkan beban kognitif.",
    "key_pts_found":"Poin Utama Dijumpai","words_sum":"Patah Perkataan Ringkasan","reduction":"Pengurangan",
    "exec_summary":"Ringkasan Eksekutif","quick_overview":"Gambaran Ringkas",
    "primary_insight":"Pandangan Utama","synthesis":"Sintesis (Poin Utama)",
    "export_artifacts":"Eksport Artifak",
    "pdf":"PDF","word":"Word","json":"JSON","new_summary":"+ Ringkasan Baharu",
    "history_title":"Log Pustakawan Terkini",
    "history_sub":"Menyemak trajektori intelektual anda.",
    "view_all":"Lihat Semua",
    "analytics_title":"Hab Kecerdasan",
    "analytics_sub":"Pandangan kuantitatif daripada perpustakaan digital anda.",
    "total_summaries":"Jumlah Ringkasan","avg_time":"Masa Purata Jimat",
    "success_rate":"Kadar Kejayaan",
    "input_dist":"Agihan Input",
    "no_summaries":"Tiada log lagi. Jana ringkasan pertama anda.",
    "start_hint":"Pilih kaedah input di atas untuk bermula",
    "duration_min":"Tempoh (minit)",
    "start_rec":"Mula Rakaman","stop_rec":"Henti & Buang",
    "gen_sum_from_rec":"Jana Ringkasan",
    "process_file":"Proses Fail","process_video":"Proses Video",
    "valid_url":"URL Sah","invalid_url":"URL Tidak Sah",
    "words":"patah perkataan","characters":"aksara",
    "pw_weak":"Lemah","pw_medium":"Sederhana","pw_strong":"Kuat",
    "pw_hint":"Gunakan huruf besar, huruf kecil, nombor & simbol.",
    "logout":"Log Keluar",
    "about_title":"Tentang SMARTIE",
    "about_sub":"Memperkasakan pelajar universiti melalui ringkasan AI yang pintar",
},
}

def T(k):
    l = st.session_state.get("language","en")
    return TR.get(l, TR["en"]).get(k, TR["en"].get(k, k))

# ══════════════════════════════════════════════════════════════════════════════
# CSS + THEME
# ══════════════════════════════════════════════════════════════════════════════
def load_css():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def inject_theme():
    t = st.session_state.get("theme","dark")
    if t == "light":
        st.markdown("""<style>
        :root {
            --surface:#f4f6fb;
            --surface-container-lowest:#ffffff;
            --surface-container-low:#ffffff;
            --surface-container:#eef1f8;
            --surface-container-high:#e8edff;
            --surface-container-highest:#dde4f8;
            --on-surface:#111827;
            --on-surface-variant:#374151;
            --glass-bg:rgba(255,255,255,0.88);
            --outline-variant:rgba(0,0,0,0.10);
        }
        .stApp { background: #f0f4ff !important; }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: #ffffff !important; color: #111827 !important;
            border: 1px solid rgba(79,70,229,0.25) !important;
        }
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder { color: #9ca3af !important; }
        .stSelectbox [data-baseweb="select"] > div { background: #ffffff !important; color: #111827 !important; }
        [data-baseweb="popover"] > div, [data-baseweb="menu"] { background-color: #ffffff !important; }
        [data-baseweb="menu"] li { color: #111827 !important; }
        [data-baseweb="menu"] li:hover { background-color: #f0f4ff !important; }
        p, span, div, li, .stMarkdown, .stCaption, .page-headline, .page-subtext, .log-title, .log-sub,
        .log-meta-label, .log-meta-value, .stat-card-label, .stat-card-badge, .input-title, .input-desc,
        .exec-summary-body, .insight-body, .kp-text, .results-subtext, .metric-pill-label, .metric-pill-value,
        .danger-text, .profile-section-title, [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
            color: #111827 !important;
        }
        .scn-topnav { background: rgba(240,244,255,0.95) !important; }
        .scn-sidebar { background: #f4f6fb !important; border-color: rgba(0,0,0,0.08) !important; }
        .auth-card { background: rgba(255,255,255,0.92) !important; }
        .glass-content-card { background: rgba(255,255,255,0.80) !important; }
        .exec-summary-card, .insight-card, .metric-pill, .stat-card,
        .log-item, .kp-item { background: #ffffff !important; }
        [data-testid="metric-container"] { background: #ffffff !important; }
        [data-testid="stExpander"] { background: rgba(255,255,255,0.85) !important; }
        .stButton > button, .stDownloadButton > button { color: #111827 !important; }
        [data-testid="baseButton-primary"], .stButton > button[kind="primary"], 
        .stDownloadButton > button[kind="primary"] { color: #fff !important; }
        .scn-brand { color: #4f46e5 !important; }
        .scn-nav-link { color: #374151 !important; }
        .scn-nav-link.active { color: #fff !important; }
        </style>""", unsafe_allow_html=True)

def _avatar_html(pic, name, cls="scn-avatar"):
    if pic: return f"<div class='{cls}'><img src='{pic}' alt='avatar'/></div>"
    ini = "".join([w[0].upper() for w in name.split()[:2]]) if name else "U"
    return f"<div class='{cls}'>{ini}</div>"

load_css()
inject_theme()

def _pw_strength(pw: str):
    if not pw: return 0, "", "pw-bar-empty"
    score = 0
    if re.search(r'[A-Z]', pw): score += 1
    if re.search(r'[a-z]', pw): score += 1
    if re.search(r'[0-9]', pw): score += 1
    if re.search(r'[^A-Za-z0-9]', pw): score += 1
    if len(pw) < 6: score = min(score, 1)
    if score <= 1: return 1, T("pw_weak"),   "pw-bar-weak"
    elif score == 2: return 2, T("pw_medium"), "pw-bar-medium"
    else: return 3, T("pw_strong"), "pw-bar-strong"

def _render_pw_strength(pw: str):
    score, label, cls = _pw_strength(pw)
    if not pw: return
    pct = {1: 33, 2: 66, 3: 100}.get(score, 0)
    color = {"pw-bar-weak":"#ef4444","pw-bar-medium":"#f59e0b","pw-bar-strong":"#10b981"}.get(cls,"#ccc")
    st.markdown(f"""<div class='pw-strength-wrap'><div class='pw-strength-track'>
    <div class='pw-strength-fill' style='width:{pct}%;background:{color}'></div>
    </div><span class='pw-strength-label' style='color:{color}'>{label}</span></div>
    <div class='pw-hint'>{T('pw_hint')}</div>""", unsafe_allow_html=True)

def render_topnav(show_lang=True, show_theme=True, show_avatar=True):
    lang  = st.session_state.get("language","en")
    theme = st.session_state.get("theme","dark")
    pic   = st.session_state.get("profile_pic","")
    name  = st.session_state.get("user_name","")
    lang_lbl = "EN/BM" if lang=="en" else "BM/EN"
    av_html  = _avatar_html(pic, name) if show_avatar and name else ""
    theme_emoji = "☀️" if theme=="light" else "🌙"

    st.markdown(f"""<div class='scn-topnav'><span class='scn-brand'>SMARTIE</span>
    <div class='scn-nav-right'>{"<span class='scn-lang-label'>" + lang_lbl + "</span>" if show_lang else ""}
    <span class='scn-theme-label'>{theme_emoji}</span>{av_html}</div></div>
    <div class='scn-topnav-spacer'></div>""", unsafe_allow_html=True)

    cols = st.columns([8, 0.9, 0.6, 0.6])
    with cols[1]:
        if show_lang and st.button(lang_lbl, key="nb_lang_btn", use_container_width=True):
            nl = "ms" if lang=="en" else "en"
            st.session_state.language = nl
            if st.session_state.user_id and BACKEND == "supabase":
                supabase.table("users").update({"language": nl}).eq("id", st.session_state.user_id).execute()
            st.rerun()
    with cols[2]:
        th_lbl = "☀️" if theme=="dark" else "🌙"
        if show_theme and st.button(th_lbl, key="nb_theme_btn", use_container_width=True):
            nt = "light" if theme=="dark" else "dark"
            st.session_state.theme = nt
            if st.session_state.user_id and BACKEND == "supabase":
                supabase.table("users").update({"theme": nt}).eq("id", st.session_state.user_id).execute()
            inject_theme(); st.rerun()
    with cols[3]:
        if show_avatar and name:
            if st.button("👤", key="nb_avatar_btn", use_container_width=True):
                st.session_state.page = "profile"; st.rerun()

def sidebar_nav(active_page="app"):
    nav_items = [("app", T("nav_summarize"), "✦"),("history", T("nav_history"), "◷"),
                 ("analytics", T("nav_analytics"), "⊞"),("profile", T("nav_profile"), "◉")]
    sb_html = f"""<div style='padding:1rem 0.5rem'><div style='padding:0.5rem 1rem 1.5rem'>
    <div style='font-family:"Noto Serif",serif;font-size:1.05rem;font-weight:700;color:#a7a5ff'>{T('sidebar_title')}</div>
    <div style='font-size:0.62rem;text-transform:uppercase;letter-spacing:0.11em;color:#a7abb6;margin-top:0.2rem'>{T('sidebar_sub')}</div></div>"""
    for pk, lbl, ico in nav_items:
        is_a = active_page == pk
        bg   = "background:linear-gradient(135deg,#a7a5ff,#645efb);color:#fff;" if is_a else "color:#8a95ff;"
        sb_html += f"""<div style='display:flex;align-items:center;gap:0.75rem;padding:0.75rem 1rem;border-radius:9999px;{bg}font-size:0.875rem;font-weight:{"600" if is_a else "500"};margin-bottom:0.25rem'><span>{ico}</span><span>{lbl}</span></div>"""
    sb_html += "</div>"
    st.markdown(sb_html, unsafe_allow_html=True)

    for pk, lbl, ico in nav_items:
        if st.button(f"{ico} {lbl}", key=f"sb_{pk}", use_container_width=True):
            st.session_state.page = pk; st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    if st.button(f"+ {T('new_note')}", key="sb_new_note", use_container_width=True, type="primary"):
        st.session_state.input_method = None; st.session_state.current_result = None
        st.session_state.page = "app"; st.rerun()

    st.markdown("<hr style='border-color:rgba(68,72,82,0.15);margin:1rem 0'>", unsafe_allow_html=True)
    if st.button(f"🚪 {T('logout')}", key="sb_logout", use_container_width=True):
        st.session_state.update({k: v for k, v in DEFAULTS.items()}); st.rerun()

def render_mobile_nav(active_page="app"):
    items = [("app","✦",T("nav_summarize")),("history","◷",T("nav_history")),
             ("analytics","⊞",T("nav_analytics")),("profile","◉",T("nav_profile"))]
    html = "<div class='mobile-bottom-nav'>"
    for pk, ico, lbl in items:
        cls = "mob-nav-item active" if active_page == pk else "mob-nav-item"
        html += f"<div class='{cls}'><span style='font-size:1.5rem'>{ico}</span><span class='mob-nav-label'>{lbl}</span></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def _lbl(txt): st.markdown(f"<div class='field-label'>{txt}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════
def page_login():
    render_topnav(show_lang=True, show_avatar=False)
    lang = st.session_state.get("language","en")
    st.markdown("""<div class='auth-bg-glow-1'></div><div class='auth-bg-glow-2'></div>""", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(f"<div class='auth-card' data-glow><h1 class='auth-headline'>{T('login_title')}</h1><p class='auth-subtext'>{T('login_sub')}</p></div>", unsafe_allow_html=True)
        _lbl(T("email"))
        email = st.text_input("email_field", placeholder="name@institution.edu", key="li_email", label_visibility="collapsed")
        _lbl(T("password"))
        pw = st.text_input("password_field", type="password", placeholder="••••••••", key="li_pass", label_visibility="collapsed")
        _, fc2 = st.columns([2, 1])
        with fc2:
            if st.button(T("forgot_password"), key="li_forgot", use_container_width=True): st.session_state.page = "forgot"; st.rerun()
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button(T("sign_in"), use_container_width=True, type="primary", key="li_btn"):
            if not email or not pw: st.error("⚠️ Please fill in all fields." if lang=="en" else "⚠️ Sila isi semua medan.")
            else:
                with st.spinner(""): r = login_user(email, pw)
                if r["success"]:
                    st.session_state.update({
                        "logged_in": True, "user_id": r["user_id"], "user_email": r["email"], "user_name": r["name"],
                        "profile_pic": r.get("profile_pic",""), "theme": r.get("theme","dark"), "language": r.get("language","en"), "page": "app",
                    }); inject_theme(); st.rerun()
                else: st.error(f"❌ {r['message']}")
        st.markdown(f"<div class='auth-divider'></div><div class='auth-footer-link'>{T('new_curator')}</div>", unsafe_allow_html=True)
        if st.button(T("create_account"), key="li_reg", use_container_width=True): st.session_state.page = "register"; st.rerun()
    st.markdown(f"<div class='auth-footer-tagline'>{T('every_note')}</div>", unsafe_allow_html=True)

def page_register():
    render_topnav(show_lang=True, show_avatar=False)
    lang = st.session_state.get("language","en")
    st.markdown("""<div class='auth-bg-glow-1'></div><div class='auth-bg-glow-2'></div>""", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(f"<div class='auth-card' data-glow><h1 class='auth-headline'>{T('register_title')}</h1><p class='auth-subtext'>{T('register_sub')}</p></div>", unsafe_allow_html=True)
        _lbl(T("full_name")); name = st.text_input("name_field", placeholder="Your Full Name", key="rg_name", label_visibility="collapsed")
        _lbl(T("email")); email = st.text_input("email_field_r", placeholder="you@example.com", key="rg_email", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1: _lbl(T("password")); pw = st.text_input("pw_field", type="password", placeholder="••••••••", key="rg_pw", label_visibility="collapsed")
        with c2: _lbl(T("confirm_password")); pw2 = st.text_input("pw2_field", type="password", placeholder="••••••••", key="rg_pw2", label_visibility="collapsed")
        _render_pw_strength(pw)
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        if st.button(T("register_btn"), use_container_width=True, type="primary", key="rg_btn"):
            if not all([name, email, pw, pw2]): st.error("⚠️ Please fill in all fields." if lang=="en" else "⚠️ Sila isi semua medan.")
            elif pw != pw2: st.error("❌ Passwords do not match." if lang=="en" else "❌ Kata laluan tidak sepadan.")
            elif len(pw) < 6: st.error("❌ Min. 6 characters." if lang=="en" else "❌ Min. 6 aksara.")
            else:
                with st.spinner(""): r = register_user(name, email, pw)
                if r["success"]:
                    st.success("✅ Account created! Please sign in." if lang=="en" else "✅ Akaun dicipta!")
                    time.sleep(1); st.session_state.page = "login"; st.rerun()
                else: st.error(f"❌ {r['message']}")
        if st.button(T("back_login"), key="rg_back", use_container_width=True): st.session_state.page = "login"; st.rerun()

def page_forgot():
    render_topnav(show_lang=True, show_avatar=False)
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(f"<div class='auth-card' data-glow><h1 class='auth-headline'>{T('forgot_title')}</h1><p class='auth-subtext'>{T('forgot_sub')}</p></div>", unsafe_allow_html=True)
        _lbl(T("email")); email = st.text_input("fe", key="fp_email", label_visibility="collapsed")
        if st.button(T("send_reset"), use_container_width=True, type="primary"):
            if not email: st.error("⚠️ Please enter your email.")
            else:
                with st.spinner("Sending code..."):
                    r = request_password_reset(email)
                    if r["success"]: 
                        st.session_state.update({"reset_email": email, "page": "reset_pw"}); st.rerun()
                    else: st.error(f"❌ {r['message']}")
        if st.button(T("back_to_login"), use_container_width=True): st.session_state.page = "login"; st.rerun()

def page_reset_pw():
    render_topnav(show_lang=True, show_avatar=False)
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(f"<div class='auth-card' data-glow><h1 class='auth-headline'>{T('reset_title')}</h1><p class='auth-subtext'>Enter the 6-digit code sent to {st.session_state.get('reset_email','')}</p></div>", unsafe_allow_html=True)
        _lbl("6-Digit Reset Code")
        otp = st.text_input("otp", placeholder="123456", key="rp_otp", label_visibility="collapsed")
        _lbl(T("new_password"))
        np1 = st.text_input("np1", type="password", key="rp_pw", label_visibility="collapsed")
        _lbl(T("confirm_new_pass"))
        np2 = st.text_input("np2", type="password", key="rp_pw2", label_visibility="collapsed")
        
        if st.button(T("reset_btn"), use_container_width=True, type="primary"):
            if np1 != np2: st.error("❌ Passwords do not match.")
            elif not otp: st.error("❌ Please enter the 6-digit code.")
            else:
                with st.spinner("Verifying & Updating..."):
                    r = reset_password(st.session_state.reset_email, otp, np1)
                    if r["success"]:
                        st.success("✅ Password successfully updated! Please log in.")
                        time.sleep(1.5); st.session_state.page = "login"; st.rerun()
                    else: st.error(f"❌ {r['message']}")
        if st.button("Cancel", use_container_width=True): st.session_state.page = "login"; st.rerun()

def page_profile():
    render_topnav()
    lang = st.session_state.get("language","en")
    sc, mc = st.columns([1, 4.2])
    with sc: sidebar_nav("profile")
    with mc:
        prof = get_profile(st.session_state.user_id)
        pic  = prof.get("profile_pic","")

        formatted_date = "Recently"
        if prof.get("updated_at"):
            try:
                from datetime import timezone, timedelta
                dt_utc = datetime.fromisoformat(prof["updated_at"].replace("Z", "+00:00"))
                myt_tz = timezone(timedelta(hours=8))
                dt_local = dt_utc.astimezone(myt_tz)
                formatted_date = dt_local.strftime("%b %d, %Y %I:%M %p")
            except Exception as e: 
                pass

        st.markdown(f"<h1 class='page-headline'>{T('profile_title')}</h1><p class='page-subtext'>{T('profile_sub')}</p>", unsafe_allow_html=True)

        av_col, form_col = st.columns([1, 2.5])
        with av_col:
            st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
            if pic: st.markdown(f"<div class='profile-avatar-ring'><div class='profile-avatar-inner'><img src='{pic}' alt='avatar'/></div></div>", unsafe_allow_html=True)
            else:
                ini = "".join([w[0].upper() for w in prof.get("name","U").split()[:2]])
                st.markdown(f"<div class='profile-avatar-ring'><div class='profile-avatar-inner'>{ini}</div></div>", unsafe_allow_html=True)
            st.markdown("</div><div style='height:1.25rem'></div>", unsafe_allow_html=True)

            up_clicked = st.button(f"⬆ {T('upload_pic')}", use_container_width=True, key="pic_up_btn")
            uploaded   = st.file_uploader("upload_photo", type=["jpg","jpeg","png","webp","gif"], key="pic_up", label_visibility="collapsed")
            if up_clicked:
                if uploaded:
                    r = update_profile_picture(st.session_state.user_id, uploaded.read(), uploaded.type or "image/jpeg")
                    if r["success"]:
                        st.session_state.profile_pic = r["profile_pic"]
                        st.success("✅ Photo updated!" if lang=="en" else "✅ Gambar dikemas kini!"); st.rerun()
                    else: st.error(f"❌ {r['message']}")
                else: st.warning("Select an image first." if lang=="en" else "Pilih gambar dahulu.")
            if pic:
                if st.button(f"🗑 {T('remove_pic')}", use_container_width=True, key="pic_rm"):
                    r = remove_profile_picture(st.session_state.user_id)
                    if r["success"]:
                        st.session_state.profile_pic = ""
                        st.success("Photo removed." if lang=="en" else "Gambar dibuang."); st.rerun()

        with form_col:
            st.markdown(f"<div class='profile-form-section'><h2 class='profile-section-title'>{T('personal_details')}</h2></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: _lbl(T("full_name_lbl")); n = st.text_input("full_name_input", value=prof.get("name",""), key="pn", label_visibility="collapsed")
            with c2: _lbl(T("email_lbl")); e = st.text_input("email_input", value=prof.get("email",""), key="pe", label_visibility="collapsed")
            _lbl(T("course_lbl")); co = st.text_input("course_input", value=prof.get("course",""), key="pc", label_visibility="collapsed")
            _lbl(T("bio_lbl")); b = st.text_area("bio_input", value=prof.get("bio",""), key="pb", height=120, label_visibility="collapsed")

            sc1, sc2 = st.columns([2, 1])
            with sc2: st.markdown(f"<div style='font-size:0.8rem;font-style:italic;color:#a7abb6;padding-top:0.5rem'>{T('last_updated')} {formatted_date}</div>", unsafe_allow_html=True)
            with sc1:
                if st.button(T("save_changes"), use_container_width=True, type="primary", key="p_save"):
                    r = update_profile(st.session_state.user_id, {"name":n,"email":e,"bio":b,"course":co})
                    if r["success"]: 
                        st.session_state.user_name = n
                        st.session_state.user_email = e
                        st.success("✅ Changes saved to database!")
                        time.sleep(0.5) 
                        st.rerun()
                    else: 
                        st.error(f"❌ {r['message']}")

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='danger-zone'><div class='danger-title'>⚠️ {T('danger_zone')}</div><p class='danger-text'>{T('danger_text')}</p></div>", unsafe_allow_html=True)
        _lbl(T("confirm_delete"))
        conf = st.text_input("delete_confirm_input", key="dc", label_visibility="collapsed")
        if st.button(T("delete_account"), key="p_del"):
            if conf != st.session_state.user_email: st.error("❌ Email does not match.")
            else:
                r = delete_account(st.session_state.user_id)
                if r["success"]: st.session_state.update({k: v for k, v in DEFAULTS.items()}); st.rerun()
                else: st.error(f"❌ {r['message']}")
    render_mobile_nav("profile")

def page_app():
    render_topnav()
    lang   = st.session_state.get("language","en")
    sc, mc = st.columns([1, 4.2])
    with sc: sidebar_nav("app")
    with mc:
        st.markdown(f"<h1 class='scn-hero-title'>{T('how_help')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='section-label-text'>{T('input_method')}</p>", unsafe_allow_html=True)

        cards = [("📝", T("paste_text"), "Paste notes or material<br>"), ("🎙", T("microphone"), "Record live audio"),
                 ("📁", T("file_upload"), "Upload WAV, MP3, MP4"), ("▶", T("youtube"), "Paste any YouTube URL")]
        method_keys = ["text","mic","file","youtube"]
        ch = "<div class='input-method-grid'>"
        for i,(ico,ttl,dsc) in enumerate(cards):
            sel = " selected" if st.session_state.input_method == method_keys[i] else ""
            ch += f"<div class='input-card{sel}' style='animation-delay:{i*0.08:.2f}s' data-glow><span class='input-icon'>{ico}</span><div class='input-title'>{ttl}</div><div class='input-desc'>{dsc}</div></div>"
        ch += "</div>"
        st.markdown(ch, unsafe_allow_html=True)

        b1,b2,b3,b4 = st.columns(4)
        if b1.button(f"📝 {T('paste_text')}", use_container_width=True, key="m_text"): st.session_state.input_method="text"; st.rerun()
        if b2.button(f"🎙 {T('microphone')}", use_container_width=True, key="m_mic"): st.session_state.input_method="mic"; st.rerun()
        if b3.button(f"📁 {T('file_upload')}", use_container_width=True, key="m_file"): st.session_state.input_method="file"; st.rerun()
        if b4.button(f"▶ {T('youtube')}", use_container_width=True, key="m_youtube"): st.session_state.input_method="youtube"; st.rerun()

        method = st.session_state.input_method
        st.markdown("<div class='glass-content-card' data-glow>", unsafe_allow_html=True)

        if method == "text":
            st.markdown(f"<h4 class='input-heading'>✦ {T('your_notes')}</h4>", unsafe_allow_html=True)
            # DROPDOWNS REMOVED FOR CLEANER UI
            notes = st.text_area("notes_area", height=260, placeholder=T("notes_placeholder"), key="notes_text", label_visibility="collapsed")
            wc = len(notes.split()) if notes.strip() else 0
            st.caption(f"{wc:,} {T('words')} · {len(notes):,} {T('characters')}")
            if st.button(f"✦  {T('generate')}", type="primary", use_container_width=True, key="gen_btn"):
                if not notes.strip() or wc < 15: st.warning("⚠️ Please paste at least a few sentences." if lang=="en" else "⚠️ Sila tampal sekurang-kurangnya beberapa ayat.")
                else:
                    with st.spinner("Analysing…" if lang=="en" else "Menganalisis…"): result = process_input(text=notes, source_type="text")
                    st.session_state.current_result = result; _push_history(result,"text")

        elif method == "mic":
            st.markdown(f"<h4 class='input-heading'>🎙 {T('microphone')}</h4>", unsafe_allow_html=True)
            audio_bytes = st.audio_input("Record your lecture" if lang == "en" else "Rakam kuliah anda")
            if audio_bytes:
                st.success("Audio captured successfully! Click Generate below." if lang == "en" else "Audio berjaya dirakam!")
                if st.button(f"✦ {T('gen_sum_from_rec')}", type="primary", key="mic_gen", use_container_width=True):
                    tmp = "temp_mic_recording.wav"
                    try:
                        with open(tmp, "wb") as f: f.write(audio_bytes.read())
                        with st.spinner("Processing audio…" if lang=="en" else "Memproses audio…"): 
                            result = process_input(source_type="file", file_path=tmp)
                        st.session_state.current_result = result
                        _push_history(result, "mic")
                    finally:
                        if os.path.exists(tmp): os.remove(tmp)

        elif method == "file":
            st.markdown(f"<h4 class='input-heading'>📁 {T('file_upload')}</h4>", unsafe_allow_html=True)
            up = st.file_uploader("file_uploader", type=["wav","mp3","m4a","mp4","avi","mov"], key="f_up", label_visibility="collapsed")
            if up:
                st.info(f"📄 {up.name}")
                if up.type and up.type.startswith("audio"): st.audio(up)
                if st.button(f"⚡ {T('process_file')}", type="primary", key="f_btn", use_container_width=True):
                    tmp = f"temp_{up.name}"
                    try:
                        with open(tmp,"wb") as f: f.write(up.getvalue())
                        with st.spinner("Transcribing…" if lang=="en" else "Menyalin teks…"): result = process_input(source_type="file", file_path=tmp)
                        st.session_state.current_result = result; _push_history(result,"file")
                    finally:
                        if os.path.exists(tmp): os.remove(tmp)

        elif method == "youtube":
            st.markdown(f"<h4 class='input-heading'>▶ {T('youtube')}</h4>", unsafe_allow_html=True)
            url = st.text_input("yt_url_input", placeholder="https://youtube.com/watch?v=…", key="yt_url", label_visibility="collapsed")
            if url:
                if "youtube.com" in url or "youtu.be" in url:
                    st.success(f"✅ {T('valid_url')}")
                    if st.button(f"⚡ {T('process_video')}", type="primary", key="yt_btn", use_container_width=True):
                        with st.spinner("Downloading and processing..." if lang=="en" else "Memproses video..."): 
                            result = process_input(source_type="youtube", youtube_url=url)
                        st.session_state.current_result = result; _push_history(result,"youtube")
                else: st.error(f"❌ {T('invalid_url')}")
        else:
            st.markdown(f"<div class='empty-state-box'><div class='empty-icon'>📚</div><div class='empty-sub'>{T('start_hint')}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.current_result: _show_results(st.session_state.current_result)
    render_mobile_nav("app")

def page_history():
    render_topnav()
    lang   = st.session_state.get("language","en")
    sc, mc = st.columns([1, 4.2])
    with sc: sidebar_nav("history")
    with mc:
        st.markdown(f"<h1 class='page-headline'>{T('history_title')}</h1><p class='page-subtext'>{T('history_sub')}</p>", unsafe_allow_html=True)

        history_data = []
        if BACKEND == "supabase" and st.session_state.user_id:
            try:
                from auth_supabase import get_history
                history_data = get_history(st.session_state.user_id)
            except Exception as e:
                st.error(f"Error loading history: {str(e)}")
        else:
            history_data = st.session_state.history

        if history_data:
            for item in history_data:
                t = item.get("type", "text")
                ts = item.get("timestamp", item.get("created_at", "")[:10])
                
                if "result" in item:
                    summ = item["result"].get("executive_summary", item["result"].get("overall_summary", ""))[:80]
                    kps = item["result"].get("key_points_found", [])
                else:
                    summ = item.get("overall_summary", "")[:80]
                    kps = item.get("keypoints", [])

                icon = {"text":"📄","mic":"🎙","file":"📁","youtube":"▶"}.get(t,"📄")
                meta_lbl = {"text":"WORDS","mic":"VOICE","file":"PAGES","youtube":"DURATION"}.get(t,"ITEMS")
                meta_val = f"{len(kps)} pts"
                
                st.markdown(f"""
                <div class='log-item' data-glow>
                  <div class='log-icon'>{icon}</div>
                  <div class='log-info'>
                    <div class='log-title'>📌 {summ}…</div>
                    <div class='log-sub'>{ts} [{t.title()}]</div>
                  </div>
                  <div class='log-meta'>
                    <div class='log-meta-label'>{meta_lbl}</div>
                    <div class='log-meta-value'>{meta_val}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='empty-state-box'><div class='empty-icon' style='font-size:2rem;opacity:0.18'>📂</div><div class='empty-sub'>{T('no_summaries')}</div></div>", unsafe_allow_html=True)
    render_mobile_nav("history")

def page_analytics():
    render_topnav()
    lang   = st.session_state.get("language","en")
    sc, mc = st.columns([1, 4.2])
    with sc: sidebar_nav("analytics")
    with mc:
        st.markdown(f"<h1 class='page-headline'>{T('analytics_title')}</h1><p class='page-subtext'>{T('analytics_sub')}</p>", unsafe_allow_html=True)

        if BACKEND == "supabase" and st.session_state.user_id:
            try:
                from auth_supabase import get_analytics
                d = get_analytics(st.session_state.user_id)
                total = d.get("total_summaries", 0)
                tot_time = d.get("total_time_saved_minutes", 0)
                suc = d.get("success_count", 0)
                fail = d.get("fail_count", 0)
                
                avg_time = round(tot_time / total) if total > 0 else 0
                success_rate = round((suc / (suc + fail)) * 100, 1) if (suc + fail) > 0 else 0.0
                types_dist = {
                    "text": d.get("text_count", 0),
                    "mic": d.get("mic_count", 0),
                    "file": d.get("file_count", 0),
                    "youtube": d.get("youtube_count", 0)
                }
            except Exception as e:
                total, avg_time, success_rate = 0, 0, 0.0
                types_dist = {"text": 0, "mic": 0, "file": 0, "youtube": 0}
        else:
            total = len(st.session_state.history)
            avg_time, success_rate = 0, 0.0
            types_dist = {"text": 0, "mic": 0, "file": 0, "youtube": 0}

        st.markdown(f"""
        <div class='stat-card-grid'>
          <div class='stat-card' data-glow>
            <div>
              <div class='stat-card-label'>{T('total_summaries')}</div>
              <div class='stat-card-value'>{total}<span></span></div>
            </div>
            <div class='stat-icon-wrap'>📄</div>
          </div>
          <div class='stat-card' data-glow>
            <div>
              <div class='stat-card-label'>{T('avg_time')}</div>
              <div class='stat-card-value'>{avg_time}<span>min</span></div>
            </div>
            <div class='stat-icon-wrap'>⏱</div>
          </div>
          <div class='stat-card' data-glow>
            <div>
              <div class='stat-card-label'>{T('success_rate')}</div>
              <div class='stat-card-value'>{success_rate}<span>%</span></div>
            </div>
            <div class='stat-icon-wrap'>✅</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class='glass-content-card' data-glow><div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem'><div style='font-family:"Noto Serif",serif;font-size:1.2rem;font-weight:700;color:#ebedfa'>{T('input_dist')}</div></div></div>""", unsafe_allow_html=True)
        st.bar_chart(types_dist)

    render_mobile_nav("analytics")

def _format_ai_data(data):
    if isinstance(data, str): return data
    elif isinstance(data, dict):
        formatted = ""
        for k, v in data.items():
            clean_k = str(k).replace("_", " ").title()
            if isinstance(v, list):
                formatted += f"**{clean_k}:**\n"
                for item in v: formatted += f"- {item}\n"
                formatted += "\n"
            else: formatted += f"**{clean_k}:** {v}\n\n"
        return formatted
    elif isinstance(data, list): return "\n".join([f"- {item}" for item in data])
    return str(data)

def _show_results(result):
    lang = st.session_state.get("language","en")
    if "error" in result: st.error(f"❌ {result['error']}"); return

    kps      = result.get("key_points_found", result.get("keypoints", []))
    sum_wc   = result.get("words_in_summary", len(result.get("executive_summary", "").split()))
    overview = result.get("quick_overview", result.get("overview", ""))
    exec_sum = result.get("executive_summary", result.get("overall_summary", ""))
    pri_ins  = result.get("primary_insights", "")
    red_pct  = result.get("reduction_percentage", "~70%")
    syn_kps  = result.get("synthesis_key_points", [])

    st.markdown(f"<div style='margin-top:2rem'><div class='analysis-badge'>✓ {T('analysis_complete')}</div><h1 class='results-hero-title'>✅ {T('summary_ready')}</h1><p class='results-subtext'>{T('summary_ready_sub')}</p></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='metric-grid'>
      <div class='metric-pill'>
        <div class='metric-pill-icon'>≡</div>
        <div><div class='metric-pill-label'>{T('key_pts_found')}</div><div class='metric-pill-value'>{len(kps)}</div></div>
      </div>
      <div class='metric-pill'>
        <div class='metric-pill-icon'>≡</div>
        <div><div class='metric-pill-label'>{T('words_sum')}</div><div class='metric-pill-value'>{sum_wc}</div></div>
      </div>
      <div class='metric-pill'>
        <div class='metric-pill-icon'>↕</div>
        <div><div class='metric-pill-label'>{T('reduction')}</div><div class='metric-pill-value'>{red_pct}</div></div>
      </div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Executive View", "📚 Academic Deep Dive", "✂️ Smart Reductions"])
    
    with tab1:
        main_c, side_c = st.columns([2, 1])
        with main_c:
            st.markdown("<div class='exec-summary-card' data-glow><div class='exec-summary-title'>✦ Executive Summary</div><div class='exec-summary-body'>", unsafe_allow_html=True)
            st.markdown(_format_ai_data(exec_sum)); st.markdown("</div></div>", unsafe_allow_html=True)
        with side_c:
            ov_snip = str(overview)[:180] + ("…" if len(str(overview)) > 180 else "")
            fi = str(pri_ins) if pri_ins else (str(kps[0]) if kps else "—")
            st.markdown(f"<div class='insight-card' data-glow><div class='insight-label'>{T('quick_overview')}</div><div class='insight-body'>\"{ov_snip}\"</div></div><div class='insight-card' style='margin-top:1rem' data-glow><div class='insight-label'>{T('primary_insight')}</div><div class='insight-body'>💡 {fi}</div></div>", unsafe_allow_html=True)

        st.markdown(f"<div style='margin-top:2rem'><h2 class='synthesis-title'>{T('synthesis')}</h2><div class='kp-grid'>", unsafe_allow_html=True)
        combined_kps = syn_kps if syn_kps else kps
        for i, pt in enumerate(combined_kps, 1):
            st.markdown(f"<div class='kp-item' data-glow><div class='kp-num'>{i}</div><div class='kp-text'>{pt}</div></div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        
    with tab2:
        for title, key in [("📖 General Overview", "general_overview"), ("🧠 Key Concepts", "key_concepts"), ("🎓 Exam Preparation", "exam_prep")]:
            st.markdown(f"<div class='exec-summary-card' style='margin-top:1rem;' data-glow><div class='exec-summary-title'>{title}</div><div class='exec-summary-body'>", unsafe_allow_html=True)
            st.markdown(_format_ai_data(result.get(key, 'No data generated.')))
            st.markdown("</div></div>", unsafe_allow_html=True)
        
    with tab3:
        for p, k in [("70%", "reduction_70"), ("30%", "reduction_30"), ("10%", "reduction_10")]:
            st.markdown(f"<div class='exec-summary-card' style='margin-top:1rem;' data-glow><div class='exec-summary-title'>✂️ {p} Reduction</div><div class='exec-summary-body'>", unsafe_allow_html=True)
            st.markdown(_format_ai_data(result.get(k, 'No data generated.')))
            st.markdown("</div></div>", unsafe_allow_html=True)

    # 🚀 NOTICE: Outside the tabs entirely. This section downloads the FULL master report.
    st.markdown("<hr style='border-color:rgba(68,72,82,0.15);margin:2rem 0'>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; margin-bottom: 1.5rem;'><span style='font-size: 0.9rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #a7abb6;'>📥 Download Complete Report</span></div>", unsafe_allow_html=True)
    
    ec1, ec2, ec3, ec4 = st.columns(4)
    
    pdf_out = result.get("pdf_file", "")
    if pdf_out and os.path.exists(pdf_out):
        with open(pdf_out, "rb") as f: ec1.download_button(f"📄 Full {T('pdf')}", f.read(), file_name="complete_summary.pdf", mime="application/pdf", use_container_width=True)
            
    word_out = result.get("word_file", "")
    if word_out and os.path.exists(word_out):
        with open(word_out, "rb") as f: ec2.download_button(f"📝 Full {T('word')}", f.read(), file_name="complete_summary.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            
    json_out = result.get("json_file", "")
    if json_out and os.path.exists(json_out):
        with open(json_out, "rb") as f: ec3.download_button(f"🗃 Full {T('json')}", f.read(), file_name="complete_summary.json", mime="application/json", use_container_width=True)

    if ec4.button(T("new_summary"), use_container_width=True, key="new_sum_btn"): st.session_state.current_result = None; st.rerun()

def _push_history(result, source_type):
    if result and "error" not in result:
        # 1. Local Backup
        st.session_state.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": result, 
            "type": source_type
        })
        
        # 2. Secure Supabase Insert via Admin Helper
        if BACKEND == "supabase" and st.session_state.user_id:
            try:
                from auth_supabase import add_history_entry
                add_history_entry(
                    user_id=st.session_state.user_id,
                    entry_type=source_type,
                    overall_summary=result.get("executive_summary", ""),
                    overview=result.get("quick_overview", ""),
                    keypoints=result.get("key_points_found", [])
                )
            except Exception as e:
                print(f"DB Write error: {e}")

def main():
    p = st.session_state.page
    if not st.session_state.logged_in:
        if p == "register":   page_register()
        elif p == "forgot":   page_forgot()
        elif p == "reset_pw": page_reset_pw()
        else:                 page_login()
    else:
        if p == "profile":    page_profile()
        elif p == "history":  page_history()
        elif p == "analytics":page_analytics()
        else:                 page_app()

if __name__ == "__main__":
    main()