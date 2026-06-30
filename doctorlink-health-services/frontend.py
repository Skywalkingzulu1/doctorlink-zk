"""DoctorLink ZK Health Compliance — FastHTML Frontend."""

import json
from datetime import datetime

from fasthtml.common import *
from zk_service import ZKProofService, get_zk_service, ProofError
from ai_service import AIService, get_ai_service
from clinic_service import ClinicService, get_clinic_service

svc = get_zk_service()
ai = get_ai_service()
cs = get_clinic_service()

# ── App setup ─────────────────────────────────────────────────────

app, rt = fast_app(
    sessions=True,
    hdrs=(
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        Link(href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap", rel="stylesheet"),
        Script(src="https://cdn.tailwindcss.com"),
        Style("""
            :root {
                --bg-dark: #070b14;
                --bg-card: rgba(14, 20, 40, 0.55);
                --bg-card-hover: rgba(22, 32, 56, 0.8);
                --border-color: rgba(255, 255, 255, 0.05);
                --border-glow: rgba(139, 92, 246, 0.25);
                --text-main: #f0f2f8;
                --text-muted: #7886a0;
                --primary: #8b5cf6;
                --primary-glow: rgba(139, 92, 246, 0.5);
                --secondary: #06b6d4;
                --secondary-glow: rgba(6, 182, 212, 0.4);
                --accent: #06b6d4;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #f43f5e;
                --font-display: 'Outfit', sans-serif;
                --font-body: 'Plus Jakarta Sans', sans-serif;
            }
            *, *::before, *::after { box-sizing: border-box; }

            /* ── Animated background ── */
            body {
                font-family: var(--font-body);
                background: var(--bg-dark);
                color: var(--text-main);
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }
            body::before {
                content: '';
                position: fixed;
                inset: 0;
                z-index: -2;
                background:
                    radial-gradient(ellipse 60% 50% at 20% 10%, rgba(139,92,246,0.10), transparent 70%),
                    radial-gradient(ellipse 50% 40% at 80% 20%, rgba(6,182,212,0.07), transparent 70%),
                    radial-gradient(ellipse 40% 30% at 50% 80%, rgba(139,92,246,0.05), transparent 60%),
                    linear-gradient(160deg, #070b14 0%, #0c0f1e 30%, #0a0e18 60%, #070b14 100%);
                background-size: 200% 200%;
                animation: bgShift 20s ease-in-out infinite alternate;
            }
            @keyframes bgShift {
                0% { background-position: 0% 0%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 100%; }
            }

            /* ── Floating orbs ── */
            body::after {
                content: '';
                position: fixed;
                inset: 0;
                z-index: -1;
                pointer-events: none;
                overflow: hidden;
            }
            .orb {
                position: fixed;
                border-radius: 50%;
                filter: blur(80px);
                pointer-events: none;
                z-index: -1;
                opacity: 0.4;
                animation: orbFloat 25s ease-in-out infinite alternate;
            }
            .orb-1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(139,92,246,0.12), transparent 70%); left: -100px; top: -100px; animation-duration: 30s; }
            .orb-2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(6,182,212,0.08), transparent 70%); right: -80px; top: 30%; animation-duration: 25s; animation-delay: -5s; }
            .orb-3 { width: 600px; height: 600px; background: radial-gradient(circle, rgba(139,92,246,0.06), transparent 70%); left: 20%; bottom: -200px; animation-duration: 35s; animation-delay: -10s; }
            @keyframes orbFloat {
                0% { transform: translate(0, 0) scale(1); }
                25% { transform: translate(30px, -40px) scale(1.05); }
                50% { transform: translate(-20px, 20px) scale(0.95); }
                75% { transform: translate(40px, 30px) scale(1.02); }
                100% { transform: translate(-10px, -30px) scale(1); }
            }

            /* ── Subtle grid overlay ── */
            .grid-overlay {
                position: fixed;
                inset: 0;
                z-index: -1;
                pointer-events: none;
                background-image:
                    linear-gradient(rgba(139,92,246,0.015) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(139,92,246,0.015) 1px, transparent 1px);
                background-size: 60px 60px;
            }
            .scanline {
                position: fixed;
                inset: 0;
                z-index: -1;
                pointer-events: none;
                background: repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 2px,
                    rgba(255,255,255,0.008) 2px,
                    rgba(255,255,255,0.008) 4px
                );
            }

            /* ── Glass card with neon border glow ── */
            .glass-card {
                position: relative;
                background: var(--bg-card);
                backdrop-filter: blur(16px) saturate(150%);
                -webkit-backdrop-filter: blur(16px) saturate(150%);
                border: 1px solid var(--border-color);
                border-radius: 20px;
                transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                overflow: hidden;
            }
            .glass-card::before {
                content: '';
                position: absolute;
                inset: 0;
                border-radius: inherit;
                opacity: 0;
                transition: opacity 0.4s ease;
                background: linear-gradient(135deg, rgba(139,92,246,0.08), rgba(6,182,212,0.04));
                pointer-events: none;
            }
            .glass-card:hover {
                transform: translateY(-3px) scale(1.005);
                background: var(--bg-card-hover);
                border-color: rgba(139,92,246,0.2);
                box-shadow:
                    0 8px 32px rgba(0,0,0,0.25),
                    0 0 0 1px rgba(139,92,246,0.08),
                    0 0 40px rgba(139,92,246,0.06);
            }
            .glass-card:hover::before { opacity: 1; }

            /* ── Premium glass card (featured cards) ── */
            .glass-card-premium {
                position: relative;
                background: var(--bg-card);
                backdrop-filter: blur(16px) saturate(150%);
                -webkit-backdrop-filter: blur(16px) saturate(150%);
                border-radius: 20px;
                transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                overflow: hidden;
            }
            .glass-card-premium::before {
                content: '';
                position: absolute;
                inset: 0;
                border-radius: inherit;
                padding: 1.5px;
                background: conic-gradient(from var(--angle, 0deg), rgba(139,92,246,0.4), rgba(6,182,212,0.3), rgba(139,92,246,0.15), rgba(6,182,212,0.3), rgba(139,92,246,0.4));
                -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                -webkit-mask-composite: xor;
                mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                mask-composite: exclude;
                animation: rotateBorder 6s linear infinite;
                pointer-events: none;
            }
            .glass-card-premium::after {
                content: '';
                position: absolute;
                inset: 0;
                border-radius: inherit;
                opacity: 0;
                transition: opacity 0.4s ease;
                background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(6,182,212,0.05));
                pointer-events: none;
            }
            .glass-card-premium:hover {
                transform: translateY(-4px) scale(1.008);
                background: var(--bg-card-hover);
                box-shadow:
                    0 12px 48px rgba(0,0,0,0.3),
                    0 0 60px rgba(139,92,246,0.08);
            }
            .glass-card-premium:hover::after { opacity: 1; }
            @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
            @keyframes rotateBorder { to { --angle: 360deg; } }

            /* ── Gradient text ── */
            .gradient-text {
                background: linear-gradient(135deg, #f0f2f8, #a78bfa, #06b6d4);
                background-size: 200% 200%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: textShimmer 8s ease-in-out infinite alternate;
            }
            @keyframes textShimmer {
                0% { background-position: 0% 50%; }
                100% { background-position: 100% 50%; }
            }

            /* ── Gradient buttons ── */
            .gradient-btn {
                background: linear-gradient(135deg, var(--primary), #7c3aed);
                box-shadow: 0 4px 20px rgba(139,92,246,0.25);
                transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                position: relative;
                overflow: hidden;
            }
            .gradient-btn::before {
                content: '';
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            .gradient-btn:hover {
                box-shadow: 0 6px 28px rgba(139,92,246,0.45);
                transform: translateY(-2px);
            }
            .gradient-btn:hover::before { opacity: 1; }
            .gradient-btn:active { transform: translateY(0); }

            .gradient-accent {
                background: linear-gradient(135deg, var(--secondary), #0891b2);
                box-shadow: 0 4px 20px rgba(6,182,212,0.25);
                transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                position: relative;
                overflow: hidden;
            }
            .gradient-accent::before {
                content: '';
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            .gradient-accent:hover {
                box-shadow: 0 6px 28px rgba(6,182,212,0.45);
                transform: translateY(-2px);
            }
            .gradient-accent:hover::before { opacity: 1; }
            .gradient-accent:active { transform: translateY(0); }

            /* ── Base element resets (no DaisyUI) ── */
            input, textarea, select {
                background: rgba(255,255,255,0.05);
                border: 1px solid var(--border-color);
                color: var(--text-main);
                border-radius: 12px;
                font-family: var(--font-body);
                font-size: 0.875rem;
                padding: 0.625rem 1rem;
                transition: all 0.3s ease;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.15);
            }
            input::placeholder, textarea::placeholder {
                color: var(--text-muted);
                opacity: 0.5;
            }
            input:focus, textarea:focus, select:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 3px var(--border-glow), 0 0 20px rgba(139,92,246,0.06), inset 0 1px 3px rgba(0,0,0,0.15);
                outline: none;
                background: rgba(255,255,255,0.07);
            }
            button {
                font-family: var(--font-body);
                cursor: pointer;
            }
            table { border-collapse: separate; border-spacing: 0; }

            /* ── Chat bubbles ── */
            .chat-ai-bubble {
                background: rgba(139,92,246,0.08);
                border: 1px solid rgba(139,92,246,0.12);
                border-radius: 18px 18px 18px 4px;
                backdrop-filter: blur(8px);
            }
            .chat-user-bubble {
                background: linear-gradient(135deg, var(--primary), #6d28d9);
                border-radius: 18px 18px 4px 18px;
                box-shadow: 0 4px 16px rgba(139,92,246,0.2);
            }

            /* ── Nav bar ── */
            .nav-link {
                font-size: 0.875rem;
                font-weight: 500;
                padding: 0.375rem 0.875rem;
                border-radius: 10px;
                transition: all 0.25s ease;
                position: relative;
            }
            .nav-link::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 50%;
                width: 0;
                height: 2px;
                background: var(--primary);
                transition: all 0.3s ease;
                transform: translateX(-50%);
                border-radius: 1px;
            }
            .nav-link:hover::after { width: 60%; }
            .nav-link-active {
                color: white;
                background: rgba(139,92,246,0.12);
                box-shadow: inset 0 0 0 1px rgba(139,92,246,0.15);
            }
            .nav-link-active::after { width: 60%; }
            .nav-link-inactive {
                color: var(--text-muted);
            }
            .nav-link-inactive:hover {
                color: white;
                background: rgba(255,255,255,0.04);
            }

            /* ── Misc ── */
            .provider-badge { font-size: 0.65rem; letter-spacing: 0.05em; }
            .text-glow { text-shadow: 0 0 20px rgba(139,92,246,0.3), 0 0 40px rgba(139,92,246,0.1); }
            .border-glow { box-shadow: 0 0 0 1px rgba(139,92,246,0.15), 0 0 20px rgba(139,92,246,0.05); }

            /* ── Reduced motion ── */
            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }

            /* ── Table styling ── */
            .tbl th { color: var(--text-muted); font-weight: 500; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; padding: 0.75rem 1rem; }
            .tbl td { padding: 0.625rem 1rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255,255,255,0.03); }
            .tbl tr:last-child td { border-bottom: none; }

            /* ── Scrollbar ── */
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.2); border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.4); }
        """),
    ),
    htmlkw={"data_theme": "dark"},
)

# ── Components ────────────────────────────────────────────────────

def layout(title: str, *children):
    nav_links = [
        ("Dashboard", "/"),
        ("Patients", "/patients"),
        ("AI", "/ai"),
        ("Clinics", "/clinics"),
        ("Queue", "/queue"),
        ("On-Chain", "/onchain"),
    ]
    active = title.split(" —")[0].strip()
    return Titled(
        title,
        Div(cls="orb orb-1"),
        Div(cls="orb orb-2"),
        Div(cls="orb orb-3"),
        Div(cls="grid-overlay"),
        Div(cls="scanline"),
        Div(
            Div(
                A("DoctorLink", href="/", cls="font-display text-xl font-bold tracking-tight gradient-text"),
                Div(
                    *[A(label, href=href,
                        cls="nav-link" + (" nav-link-active" if active.lower() == label.lower() else " nav-link-inactive"))
                      for label, href in nav_links],
                    cls="flex gap-1",
                ),
                cls="flex items-center justify-between w-full px-6 py-3",
            ),
            cls="border-b border-[var(--border-color)] mb-6",
        ),
        Div(
            Div(*children, cls="max-w-4xl mx-auto"),
            cls="px-6 pb-12",
        ),
    )

def proof_card(title: str, proof: dict, status: str = None):
    return Div(
        Div(
            H3(title, cls="font-semibold font-display text-base"),
            P(f"Circuit: {proof.get('circuit', 'N/A')}", cls="text-sm text-[var(--text-muted)] mt-2"),
            P(f"Age verified: {proof.get('age_verified', 'N/A')}" if 'age_verified' in proof else None,
              cls="text-sm text-[var(--text-muted)]"),
            Div(
                Pre(json.dumps(proof.get("public_signals", {}), indent=2),
                    cls="text-xs text-[var(--text-muted)] p-3 rounded-lg bg-black/30 overflow-x-auto mt-3"),
            ) if proof.get("public_signals") else None,
            Div(
                Pre(proof.get("proof_hash", "N/A")[:64] + "...",
                    cls="text-xs text-[var(--text-muted)] font-mono mt-2"),
            ),
            P(status, cls="text-sm font-semibold mt-3 " + ("text-[var(--success)]" if "Submitted" in (status or "") else "text-[var(--danger)]")) if status else None,
            cls="p-5",
        ),
        cls="glass-card",
    )

def status_badge(ok: bool):
    return Span("On-chain" if ok else "Pending",
                cls="text-[10px] px-1.5 py-0.5 rounded-full " +
                ("bg-[var(--success)]/20 text-[var(--success)]" if ok else "bg-[var(--warning)]/20 text-[var(--warning)]"))

PROVIDER_COLORS = {"Netcare": "bg-cyan-500/20 text-cyan-400", "Mediclinic": "bg-green-500/20 text-green-400", "Life Healthcare": "bg-amber-500/20 text-amber-400", "Government": "bg-white/5 text-[var(--text-muted)]", "Private": "bg-violet-500/20 text-violet-400"}

def clinic_card(c: dict):
    provider = c.get("provider", "")
    badge_cls = PROVIDER_COLORS.get(provider, "bg-white/5 text-[var(--text-muted)]")
    return Div(
        Div(
            Div(
                Div(
                    H3(c.get("name", ""), cls="text-base font-semibold font-display leading-tight"),
                    Span(provider, cls=f"text-[10px] px-1.5 py-0.5 rounded-full ml-2 {badge_cls}"),
                    cls="flex items-start",
                ),
                Div(
                    *[Span(s, cls="text-[11px] px-2 py-0.5 rounded-md bg-white/5 text-[var(--text-muted)]") for s in c.get("services", [])[:4]],
                    cls="flex flex-wrap gap-1.5 mt-2",
                ),
                cls="mb-3",
            ),
            Div(
                Div(
                    Span(c.get("phone", ""), cls="text-sm font-medium text-[var(--secondary)]"),
                    cls="",
                ),
                Div(
                    A("Call", href=f"tel:{c.get('phone', '')}", cls="text-xs px-3 py-1.5 rounded-lg gradient-btn text-white font-medium"),
                    " ",
                    A("Directions",
                      href=f"https://www.google.com/maps/dir/?api=1&destination={c.get('lat',0)},{c.get('lng',0)}",
                      target="_blank", cls="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white transition-colors"),
                    cls="flex gap-2",
                ),
                cls="flex items-center justify-between flex-wrap gap-2",
            ),
            Div(
                P(f"{c.get('address', '')} · {c.get('city', '')}", cls="text-xs text-[var(--text-muted)] mt-2 truncate"),
                P(c.get("hours", ""), cls="text-xs text-[var(--text-muted)] opacity-60"),
                cls="mt-2",
            ),
            cls="p-4",
        ),
        cls="glass-card mb-3",
    )


def octoparse_status_badge():
    ost = cs.get_octoparse_status()
    if ost.get("connected"):
        return Span("Octoparse", cls="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--success)]/20 text-[var(--success)] ml-1")
    return Span("Octoparse", cls="text-[10px] px-1.5 py-0.5 rounded-full bg-white/5 text-[var(--text-muted)] ml-1")

# ── Routes ────────────────────────────────────────────────────────

@rt("/")
def get():
    return layout(
        "Dashboard — DoctorLink",
        # ── Hero Section ──
        Div(
            Div(
                H1("Private Health Compliance for", cls="text-3xl font-bold font-display leading-tight"),
                H1("Remote Mobile Clinics", cls="text-3xl font-bold font-display leading-tight gradient-text mt-1"),
                P("Verify patient age, vaccine status, and doctor licenses with zero-knowledge proofs — no internet required. Audit compliance on Stellar.", cls="text-sm text-[var(--text-muted)] mt-4 max-w-2xl"),
                cls="mb-8",
            ),
            # ── Why ZK callout ──
            Div(
                Div(
                    Span("Why Zero-Knowledge?", cls="font-semibold font-display text-sm"),
                    P("Prove a patient is over 18 without revealing their date of birth. Verify a doctor's license without transmitting the license number. ZK breaks the trade-off between privacy and compliance.", cls="text-sm text-[var(--text-muted)] mt-1"),
                    cls="p-4",
                ),
                cls="glass-card mb-8",
            ),
            # ── How It Works ──
            Div(
                H2("How It Works", cls="text-xl font-bold font-display mb-5"),
                Div(
                    *step_card("1", "Register", "Add patient or doctor data. The app stores it locally — nothing leaves your device.", "👤"),
                    *step_card("2", "Generate ZK Proof", "Select what to verify (age, vaccine, license). A zero-knowledge proof is generated on-device. The private data stays with you; only the proof is shared.", "🔐"),
                    *step_card("3", "Anchor on Stellar", "Submit the proof hash to Soroban. The verification record is permanently anchored on Stellar testnet — immutable, auditable, and privacy-preserving.", "⛓️"),
                    cls="grid grid-cols-1 md:grid-cols-3 gap-4",
                ),
                cls="mb-8",
            ),
            # ── Quick Actions ──
            Div(
                H2("Get Started", cls="text-xl font-bold font-display mb-5"),
                Div(
                    Div(
                        Div(
                            Span("Patients", cls="text-[10px] px-2 py-0.5 rounded-full bg-[var(--primary)]/15 text-[var(--primary)] font-medium tracking-wider"),
                            cls="mb-2",
                        ),
                        H3("Verify a Patient", cls="font-semibold font-display text-base mt-1"),
                        P("Check age eligibility, vaccine compliance, or issue token rewards.", cls="text-sm text-[var(--text-muted)] mt-1 mb-4"),
                        A("Patients & Doctors →", href="/patients",
                          cls="gradient-btn text-white px-4 py-2 rounded-lg text-sm font-medium inline-block"),
                        cls="p-5",
                    ),
                    cls="glass-card-premium",
                ),
                Div(
                    Div(
                        Div(
                            Span("Clinics", cls="text-[10px] px-2 py-0.5 rounded-full bg-[var(--secondary)]/15 text-[var(--secondary)] font-medium tracking-wider"),
                            cls="mb-2",
                        ),
                        H3("Find a Clinic", cls="font-semibold font-display text-base mt-1"),
                        P("Search the SA clinic directory or ask Dr. Link AI for a recommendation.", cls="text-sm text-[var(--text-muted)] mt-1 mb-4"),
                        A("Clinic Finder →", href="/ai/clinic-finder",
                          cls="gradient-accent text-white px-4 py-2 rounded-lg text-sm font-medium inline-block"),
                        " ",
                        A("AI Triage", href="/ai/triage",
                          cls="px-4 py-2 rounded-lg text-sm font-medium inline-block border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white transition-colors"),
                        cls="p-5",
                    ),
                    cls="glass-card-premium",
                ),
                Div(
                    Div(
                        Div(
                            Span("Stellar", cls="text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-[var(--text-muted)] font-medium tracking-wider"),
                            cls="mb-2",
                        ),
                        H3("On-Chain State", cls="font-semibold font-display text-base mt-1"),
                        P("View verifier contract records and DLHT token balances on Stellar testnet.", cls="text-sm text-[var(--text-muted)] mt-1 mb-4"),
                        A("On-Chain →", href="/onchain",
                          cls="px-4 py-2 rounded-lg text-sm font-medium inline-block border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white transition-colors"),
                        " ",
                        A("Sync Queue", href="/queue",
                          cls="px-4 py-2 rounded-lg text-sm font-medium inline-block border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white transition-colors"),
                        cls="p-5",
                    ),
                    cls="glass-card-premium",
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-5",
            ),
            # ── Footer summary ──
            Div(
                Div(
                    Span("Built for ", cls="text-xs text-[var(--text-muted)]"),
                    A("Stellar Hacks: Real-World ZK", href="https://dorahacks.io/hackathon/stellar-hacks-zk/detail",
                      target="_blank", cls="text-xs text-[var(--primary)] hover:underline"),
                    Span(" · Noir circuits · BN254 Groth16 · Soroban · Powered by Gemini 2.5 Flash Lite via OpenRouter", cls="text-xs text-[var(--text-muted)]"),
                    cls="text-center pt-8 border-t border-[var(--border-color)]",
                ),
            ),
        ),
    )

def step_card(num: str, title: str, desc: str, icon: str):
    return Div(
        Div(
            Span(icon, cls="text-2xl mb-2 block"),
            H3(f"{num}. {title}", cls="font-semibold font-display text-base"),
            P(desc, cls="text-sm text-[var(--text-muted)] mt-1 leading-relaxed"),
            cls="p-5",
        ),
        cls="glass-card",
    )

@rt("/patients")
def get():
    from models import Patient, Doctor, get_db
    db = next(get_db())
    patients = db.query(Patient).all()
    doctors = db.query(Doctor).all()
    return layout(
        "Patients — DoctorLink",
        Div(
            Div(
                H2("Patients", cls="text-2xl font-bold font-display mb-1"),
                P(f"{len(patients)} registered", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    Table(
                        Thead(Tr(Th("ID"), Th("Name"), Th("DOB"), Th("Actions"))),
                        Tbody(*[
                            Tr(
                                Td(str(p.id), cls="text-sm"),
                                Td(f"{p.first_name} {p.last_name}", cls="text-sm font-medium"),
                                Td(str(p.date_of_birth), cls="text-sm text-[var(--text-muted)]"),
                                Td(
                                    A("Prove Age ≥ 18", href=f"/verify/age/{p.id}",
                                      title="Generate ZK proof that age ≥ 18 without revealing DOB",
                                      cls="text-xs px-2 py-1 rounded gradient-btn text-white inline-block"),
                                    " ",
                                    A("Vaccine Proof", href=f"/verify/vaccine/{p.id}",
                                      title="Generate ZK proof of vaccination without revealing full history",
                                      cls="text-xs px-2 py-1 rounded border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white inline-block transition-colors"),
                                    " ",
                                    A("Reward DLHT", href=f"/reward/{p.id}",
                                      title="Mint DLHT compliance reward tokens",
                                      cls="text-xs px-2 py-1 rounded gradient-accent text-white inline-block"),
                                ),
                            ) for p in patients
                        ]),
                        cls="tbl w-full",
                    ),
                    cls="p-5",
                ),
                cls="glass-card-premium mb-6",
            ),
            Div(
                H2("Doctors", cls="text-2xl font-bold font-display mb-1"),
                P(f"{len(doctors)} registered", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    Table(
                        Thead(Tr(Th("ID"), Th("Name"), Th("License"), Th("Actions"))),
                        Tbody(*[
                            Tr(
                                Td(str(d.id), cls="text-sm"),
                                Td(f"{d.first_name} {d.last_name}", cls="text-sm font-medium"),
                                Td(d.license_number or "-", cls="text-sm text-[var(--text-muted)]"),
                                Td(
                                    A("Prove License (ZK)", href=f"/verify/license/{d.id}",
                                      title="Generate ZK proof of valid license without exposing license number",
                                      cls="text-xs px-2 py-1 rounded gradient-accent text-white inline-block"),
                                    " ",
                                    A("HPCSA Check", href=f"/hpcsa/{d.id}",
                                      title="Check HPCSA iRegister registration status",
                                      cls="text-xs px-2 py-1 rounded border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white inline-block transition-colors"),
                                ),
                            ) for d in doctors
                        ]),
                        cls="tbl w-full",
                    ),
                    cls="p-5",
                ),
                cls="glass-card-premium",
            ),
        ),
    )

@rt("/verify/age/{pid}")
def get(pid: int):
    from models import Patient, get_db
    db = next(get_db())
    p = db.query(Patient).filter(Patient.id == pid).first()
    if not p or not p.date_of_birth:
        return layout("Error", Div(P("Patient not found or missing DOB")))
    dob = p.date_of_birth.year
    cur = datetime.now().year
    proof = svc.generate_age_proof(dob, cur, 18)
    signals = proof["public_signals"]
    signals["circuit"] = "age_check"
    try:
        result = svc.submit_to_stellar(proof["proof_hash"], signals)
    except ProofError as e:
        result = {"success": False, "error": str(e)}
    return layout(
        "Age Verification — DoctorLink",
        Div(
            Div(
                H2("Age Verification", cls="text-2xl font-bold font-display mb-1"),
                P(f"{p.first_name} {p.last_name} — DOB: {p.date_of_birth}, Age: {cur - dob}", cls="text-sm text-[var(--text-muted)] mb-3"),
            ),
            # ── ZK explanation ──
            Div(
                Div(
                    Span("🔐 Zero-Knowledge Proof Generated", cls="font-semibold text-sm text-[var(--primary)]"),
                    P("A ZK proof was computed on-device proving age ≥ 18. The proof is sent to Stellar — ", cls="text-sm text-[var(--text-muted)] inline"),
                    Span("your date of birth never leaves this device.", cls="text-sm font-semibold text-[var(--accent)]"),
                    cls="p-4",
                ),
                cls="glass-card mb-5",
            ),
            proof_card("Proof Result", proof, "Submitted" if result.get("success") else "Failed"),
            Div(
                P(f"Tx: {result.get('tx_hash', 'N/A')}", cls="text-xs text-[var(--text-muted)] font-mono"),
                Div(
                    A("Stellar Explorer ↗",
                      href=f"https://stellar.expert/explorer/testnet/tx/{result.get('tx_hash', '')}",
                      target="_blank",
                      cls="text-xs text-[var(--accent)] hover:underline"),
                    cls="mt-1",
                ) if result.get("tx_hash") else None,
                cls="mt-4",
            ),
            Div(
                A("Patients", href="/patients",
                  cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

@rt("/verify/license/{did}")
def get(did: int):
    from models import Doctor, get_db
    db = next(get_db())
    d = db.query(Doctor).filter(Doctor.id == did).first()
    if not d or not d.license_number:
        return layout("Error", Div(P("Doctor or license not found")))

    hpcsa = svc.check_hpcsa(d.license_number, d.last_name or "", d.first_name or "")
    hpcsa_status = hpcsa.get("status", "Unknown")
    hpcsa_ok = hpcsa.get("found", False) and hpcsa.get("is_active", False)

    proof = svc.generate_license_proof(d.license_number, did)
    signals = proof["public_signals"]
    signals["circuit"] = "license_verify"
    try:
        result = svc.submit_to_stellar(proof["proof_hash"], signals)
    except ProofError as e:
        result = {"success": False, "error": str(e)}
    return layout(
        "License Verification — DoctorLink",
        Div(
            Div(
                H2("License Verification", cls="text-2xl font-bold font-display mb-1"),
                P(f"{d.first_name} {d.last_name} — #{d.license_number}", cls="text-sm text-[var(--text-muted)] mb-3"),
            ),
            # ── ZK explanation ──
            Div(
                Div(
                    Span("🔐 Zero-Knowledge License Proof", cls="font-semibold text-sm text-[var(--primary)]"),
                    P("A ZK proof was computed proving the doctor holds a valid registered license. ", cls="text-sm text-[var(--text-muted)] inline"),
                    Span("The license number is never transmitted.", cls="text-sm font-semibold text-[var(--accent)]"),
                    cls="p-4",
                ),
                cls="glass-card mb-5",
            ),
            Div(
                Div(
                    Div(
                        H3("HPCSA iRegister", cls="font-semibold text-sm"),
                        P(f"Status: {hpcsa_status}", cls="font-medium mt-1 " + ("text-[var(--success)]" if hpcsa_ok else "text-[var(--warning)]")),
                        P(f"Source: {hpcsa.get('source', '-')}", cls="text-xs text-[var(--text-muted)] mt-1"),
                        P(f"Name: {hpcsa.get('full_name', '-')}", cls="text-xs text-[var(--text-muted)]"),
                        P(f"Register: {hpcsa.get('register', '-')}", cls="text-xs text-[var(--text-muted)]"),
                        cls="p-4",
                    ),
                    cls="glass-card-premium mb-5",
                ) if hpcsa else None,
                proof_card("ZK Proof", proof, "Submitted" if result.get("success") else "Failed"),
            ),
            Div(
                P(f"Tx: {result.get('tx_hash', 'N/A')}", cls="text-xs text-[var(--text-muted)] font-mono"),
            ) if result.get("tx_hash") else None,
            Div(
                A("Patients", href="/patients",
                  cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

@rt("/hpcsa/{did}")
def get(did: int):
    from models import Doctor, get_db
    db = next(get_db())
    d = db.query(Doctor).filter(Doctor.id == did).first()
    if not d:
        return layout("Error", Div(P("Doctor not found")))
    hpcsa = svc.check_hpcsa(d.license_number or "", d.last_name or "", d.first_name or "")
    return layout(
        "HPCSA — DoctorLink",
        Div(
            Div(
                H2("HPCSA iRegister", cls="text-2xl font-bold font-display mb-1"),
                P(f"{d.first_name} {d.last_name} — #{d.license_number}", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    Pre(json.dumps({k: v for k, v in hpcsa.items() if v}, indent=2),
                        cls="text-xs text-[var(--text-muted)] p-3 rounded-lg bg-black/30 overflow-x-auto"),
                    cls="p-5",
                ),
                cls="glass-card-premium",
            ),
            Div(
                A("Patients", href="/patients",
                  cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

@rt("/verify/vaccine/{pid}")
def get(pid: int):
    from models import Patient, get_db
    db = next(get_db())
    p = db.query(Patient).filter(Patient.id == pid).first()
    if not p:
        return layout("Error", Div(P("Patient not found")))
    from models import Vaccination
    v = db.query(Vaccination).filter(Vaccination.patient_id == pid).first()
    vtype = v.vaccine_name if v else "COVID-19"
    proof = svc.generate_vaccine_proof(pid, vtype)
    signals = proof["public_signals"]
    signals["circuit"] = "vaccine_status"
    try:
        result = svc.submit_to_stellar(proof["proof_hash"], signals)
    except ProofError as e:
        result = {"success": False, "error": str(e)}
    return layout(
        "Vaccine — DoctorLink",
        Div(
            Div(
                H2("Vaccine Verification", cls="text-2xl font-bold font-display mb-1"),
                P(f"{p.first_name} {p.last_name} — {vtype}", cls="text-sm text-[var(--text-muted)] mb-3"),
            ),
            # ── ZK explanation ──
            Div(
                Div(
                    Span("🔐 Zero-Knowledge Vaccine Proof", cls="font-semibold text-sm text-[var(--primary)]"),
                    P("A ZK proof was computed confirming the patient's vaccination record matches the required type. ", cls="text-sm text-[var(--text-muted)] inline"),
                    Span("The full medical history remains private.", cls="text-sm font-semibold text-[var(--accent)]"),
                    cls="p-4",
                ),
                cls="glass-card mb-5",
            ),
            proof_card("Proof Generated", proof, "Submitted" if result.get("success") else "Failed"),
            Div(
                P(f"Tx: {result.get('tx_hash', 'N/A')}", cls="text-xs text-[var(--text-muted)] font-mono mt-4"),
            ) if result.get("tx_hash") else None,
            Div(
                A("Patients", href="/patients",
                  cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

@rt("/reward/{pid}")
def get(pid: int):
    from models import Patient, get_db
    db = next(get_db())
    p = db.query(Patient).filter(Patient.id == pid).first()
    if not p:
        return layout("Error", Div(P("Patient not found")))
    result = svc.reward_tokens("GCLJMFKL3CFWJKZS6UM5BF5KWG67UMVL7TCSDAM4L3JIFWNMV3LSIFL7", 10)
    import subprocess as sp
    bal_cmd = (
        f'stellar contract invoke --id CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT '
        f'--network testnet --source-account funded -- balance '
        f'--id GCLJMFKL3CFWJKZS6UM5BF5KWG67UMVL7TCSDAM4L3JIFWNMV3LSIFL7'
    )
    bal_out = sp.run(["wsl", "bash", "-l", "-c", bal_cmd], capture_output=True, text=True, timeout=30)
    balance = bal_out.stdout.strip().strip('"')
    return layout(
        "Reward — DoctorLink",
        Div(
            Div(
                H2("Token Reward", cls="text-2xl font-bold font-display mb-1"),
                P(f"{p.first_name} {p.last_name}", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    Div(
                        H3("Reward Sent" if result.get("success") else "Failed", cls="font-semibold font-display text-base"),
                        P(f"DLHT Balance: {balance}", cls="text-2xl font-bold text-[var(--accent)] mt-2"),
                        P(f"Tx: {result.get('tx_hash', 'N/A')}", cls="text-xs text-[var(--text-muted)] font-mono mt-2"),
                        cls="p-5",
                    ),
                    cls="glass-card-premium",
                ) if result.get("success") else Div(
                    P("Failed to reward tokens", cls="text-sm text-[var(--text-muted)]"),
                ),
            ),
            Div(
                A("Patients", href="/patients",
                  cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

@rt("/queue")
def get():
    from models import StellarSyncQueue, get_db
    db = next(get_db())
    items = db.query(StellarSyncQueue).all()
    return layout(
        "Queue — DoctorLink",
        Div(
            Div(
                H2("Sync Queue", cls="text-2xl font-bold font-display mb-1"),
                P(f"{len(items)} item(s) pending sync", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    Div(
                        A("Sync All to Stellar", href="/sync/all",
                          cls="gradient-btn text-white px-4 py-2 rounded-lg text-sm font-medium inline-block"),
                        cls="mb-4",
                    ),
                    Div(
                        *[Div(
                            Div(
                                Span(f"#{i.id}", cls="text-xs text-[var(--text-muted)]"),
                                Span(i.entity_type, cls="text-sm font-medium ml-3"),
                                Span(i.proof_hash[:20] + "...", cls="text-xs text-[var(--text-muted)] ml-3 font-mono"),
                                Span("Synced" if i.status == "synced" else "Pending",
                                     cls="text-xs ml-auto px-2 py-0.5 rounded-full " + ("bg-[var(--success)]/20 text-[var(--success)]" if i.status == "synced" else "bg-[var(--warning)]/20 text-[var(--warning)]")),
                                cls="flex items-center gap-2 py-2 px-3 rounded-lg bg-white/[0.02]",
                            ),
                        ) for i in items] if items else Div(
                            P("No items in queue.", cls="text-sm text-[var(--text-muted)] text-center py-6"),
                        ),
                    ),
                    cls="p-5",
                ),
                cls="glass-card-premium",
            ),
            Div(
                A("Dashboard", href="/", cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

@rt("/sync/all")
def get():
    from models import StellarSyncQueue, get_db
    db = next(get_db())
    pending = db.query(StellarSyncQueue).filter(StellarSyncQueue.status == "pending").all()
    count = 0
    circuit_map = {
        "doctor_verification": "license_verify",
        "contraceptive_eligibility": "age_check",
    }
    for item in pending:
        try:
            signals = item.public_signals or {}
            signals["circuit"] = circuit_map.get(item.entity_type, "age_check")
            r = svc.submit_to_stellar(item.proof_hash, signals)
            if r.get("success"):
                item.status = "synced"
                item.tx_hash = r.get("tx_hash")
                count += 1
        except Exception:
            pass
    db.commit()
    return layout(
        "Sync Complete — DoctorLink",
        Div(
            Div(
                H2("Sync Complete", cls="text-2xl font-bold font-display mb-1"),
                P(f"{count} item(s) synced, {len(pending) - count} failed", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    P(f"{count} item(s) synced to Stellar", cls="text-lg font-semibold"),
                    cls="p-5",
                ),
                cls="glass-card-premium",
            ),
            Div(
                A("Queue", href="/queue",
                  cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

@rt("/onchain")
def get():
    import subprocess as sp
    cmd_ver = (
        'stellar contract invoke --id CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2 '
        '--network testnet --source-account funded -- get_last_verification'
    )
    cmd_bal = (
        'stellar contract invoke --id CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT '
        '--network testnet --source-account funded -- balance '
        '--id GCLJMFKL3CFWJKZS6UM5BF5KWG67UMVL7TCSDAM4L3JIFWNMV3LSIFL7'
    )
    ver_out = sp.run(["wsl", "bash", "-l", "-c", cmd_ver], capture_output=True, text=True, timeout=30)
    bal_out = sp.run(["wsl", "bash", "-l", "-c", cmd_bal], capture_output=True, text=True, timeout=30)

    try:
        ver_data = json.loads(ver_out.stdout)
    except (json.JSONDecodeError, ValueError):
        ver_data = {"error": ver_out.stderr[:200]}

    balance = bal_out.stdout.strip().strip('"')

    return layout(
        "On-Chain — DoctorLink",
        Div(
            Div(
                H2("Stellar Contract State", cls="text-2xl font-bold font-display mb-1"),
                P("Live view of deployed Soroban contracts on testnet", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    Div(
                        Span("Contract", cls="text-[10px] px-2 py-0.5 rounded-full bg-[var(--primary)]/15 text-[var(--primary)] font-medium tracking-wider uppercase text-xs"),
                        cls="mb-3",
                    ),
                    H3("Verifier", cls="font-semibold font-display text-base"),
                    P("CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2",
                      cls="text-xs text-[var(--text-muted)] mt-1 font-mono"),
                    Pre(json.dumps(ver_data, indent=2),
                        cls="text-xs text-[var(--text-muted)] p-3 rounded-lg bg-black/40 overflow-x-auto mt-3 border border-white/5"),
                    cls="p-5",
                ),
                cls="glass-card-premium mb-5",
            ),
            Div(
                Div(
                    Div(
                        Span("Token", cls="text-[10px] px-2 py-0.5 rounded-full bg-[var(--secondary)]/15 text-[var(--secondary)] font-medium tracking-wider uppercase text-xs"),
                        cls="mb-3",
                    ),
                    H3("DoctorLink Health Token", cls="font-semibold font-display text-base"),
                    P("CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT",
                      cls="text-xs text-[var(--text-muted)] mt-1 mb-4 font-mono"),
                    Div(
                        Span("DLHT Balance", cls="text-sm text-[var(--text-muted)]"),
                        Span(f"{balance}", cls="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[var(--accent)] to-[var(--primary)] ml-3"),
                        cls="flex items-baseline gap-2",
                    ),
                    cls="p-5",
                ),
                cls="glass-card-premium",
            ),
            Div(
                A("Refresh", href="/onchain",
                  cls="gradient-btn text-white px-4 py-2 rounded-lg text-sm font-medium inline-block"),
                " ",
                A("Dashboard", href="/",
                  cls="px-4 py-2 rounded-lg text-sm font-medium inline-block border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

# ── AI Assistant Routes ───────────────────────────────────────────

@rt("/ai")
def get(session=None):
    return layout(
        "AI — DoctorLink",
        Div(
            Div(
                H2("AI Assistant", cls="text-2xl font-bold font-display mb-1"),
                P("Find clinics, assess symptoms, and learn about DoctorLink.", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    Div(
                        Div(
                            Span("Search", cls="text-[10px] px-2 py-0.5 rounded-full bg-[var(--primary)]/15 text-[var(--primary)] font-medium tracking-wider"),
                            cls="mb-3",
                        ),
                        H3("Clinic Finder", cls="font-semibold font-display text-base"),
                        P("Search for clinics by location.", cls="text-sm text-[var(--text-muted)] mt-1"),
                        A("Search", href="/ai/clinic-finder", cls="gradient-btn text-white px-4 py-2 rounded-lg text-sm font-medium inline-block mt-4"),
                        " ",
                        A("Directory", href="/clinics", cls="px-4 py-2 rounded-lg text-sm font-medium inline-block mt-4 border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white transition-colors"),
                        cls="p-5",
                    ),
                    cls="glass-card-premium",
                ),
                Div(
                    Div(
                        Div(
                            Span("Diagnosis", cls="text-[10px] px-2 py-0.5 rounded-full bg-[var(--secondary)]/15 text-[var(--secondary)] font-medium tracking-wider"),
                            cls="mb-3",
                        ),
                        H3("Patient Triage", cls="font-semibold font-display text-base"),
                        P("Describe your symptoms for a step-by-step assessment.", cls="text-sm text-[var(--text-muted)] mt-1"),
                        A("Start", href="/ai/triage", cls="gradient-accent text-white px-4 py-2 rounded-lg text-sm font-medium inline-block mt-4"),
                        cls="p-5",
                    ),
                    cls="glass-card-premium",
                ),
                Div(
                    Div(
                        Div(
                            Span("Chat", cls="text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-[var(--text-muted)] font-medium tracking-wider"),
                            cls="mb-3",
                        ),
                        H3("General Chat", cls="font-semibold font-display text-base"),
                        P("Ask about DoctorLink, ZK health compliance, or health info.", cls="text-sm text-[var(--text-muted)] mt-1"),
                        A("Chat", href="/ai/chat", cls="px-4 py-2 rounded-lg text-sm font-medium inline-block mt-4 border border-[var(--border-color)] text-[var(--text-muted)] hover:text-white transition-colors"),
                        cls="p-5",
                    ),
                    cls="glass-card-premium",
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-5",
            ),
        ),
    )


def _chat_bubble(msg: dict, idx: int):
    is_user = msg.get("role") == "user"
    clinics = msg.get("clinics", [])
    if is_user:
        return Div(
            Div(msg.get("content", ""), cls="chat-user-bubble text-sm text-white px-4 py-2.5 max-w-[80%]"),
            cls="flex justify-end mb-2",
        )
    return Div(
        Div(
            Div(
                Span("Dr. Link", cls="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] ml-1 mb-1 block"),
                Div(
                    P(msg.get("content", ""), cls="text-sm leading-relaxed"),
                    *[clinic_card(c) for c in clinics],
                    cls="space-y-2",
                ),
                cls="chat-ai-bubble px-4 py-3 max-w-[85%]",
            ),
            cls="flex flex-col items-start mb-2",
        ),
    )


def _chat_page(title: str, session_key: str, session, form_action: str,
               placeholder: str, input_name: str = "message", button_text: str = "Send",
               subtitle: str = ""):
    history = session.get(session_key, [])
    error = session.pop("_chat_error", None)
    return layout(
        title,
        Div(
            Div(
                H2(title, cls="text-2xl font-bold font-display mb-1"),
                P(subtitle, cls="text-sm text-[var(--text-muted)] mb-6") if subtitle else None,
            ),
            Div(
                Div(
                    Div(
                        *[_chat_bubble(m, i) for i, m in enumerate(history)],
                        cls="space-y-1",
                    ) if history else Div(
                        P("Start a conversation below.", cls="text-sm text-[var(--text-muted)] text-center py-8"),
                    ),
                    Div(
                        P(error, cls="text-sm text-[var(--danger)]"),
                    ) if error else None,
                    cls="p-4",
                ),
                Div(
                    Form(
                        Div(
                            Input(name=input_name, placeholder=placeholder, required=True,
                                  cls="input-glass px-4 py-2.5 w-full text-sm"),
                            Button(button_text, type="submit", cls="gradient-btn text-white px-5 py-2.5 rounded-lg text-sm font-medium ml-2 border-0 cursor-pointer"),
                            A("Clear", href=f"{form_action}/clear", cls="text-xs text-[var(--text-muted)] hover:text-white ml-3 transition-colors"),
                            cls="flex items-center gap-0",
                        ),
                        method="post",
                    ),
                    cls="p-4 pt-0",
                ),
                cls="glass-card-premium",
            ),
            Div(
                A("Dashboard", href="/", cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )

@rt("/ai/clinic-finder")
def get(session, q: str = ""):
    results = cs.search_by_location(q) if q else []
    if results:
        session["_clinic_context"] = results[:3]
    history = session.get("clinic_history", [])
    return layout(
        "Clinic Finder — DoctorLink",
        Div(
            Div(
                H2("Find a Clinic", cls="text-2xl font-bold font-display mb-1"),
                P("Search by location or ask Dr. Link for a recommendation.", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            Div(
                Div(
                    Form(
                        Div(
                            Input(name="q", placeholder="Search city or area... e.g. Soweto, Cape Town",
                                  value=q, cls="input-glass px-4 py-3 w-full text-sm"),
                            Button("Search", type="submit", cls="gradient-btn text-white px-6 py-3 rounded-lg text-sm font-medium ml-2 border-0 cursor-pointer"),
                            cls="flex",
                        ),
                        method="get",
                    ),
                    cls="p-4",
                ),
                cls="glass-card-premium mb-6",
            ),
            Div(
                Div(
                    Span(f"{len(results)} clinic{'' if len(results)==1 else 's'} found",
                         cls="text-sm text-[var(--text-muted)]"),
                    cls="mb-3",
                ) if results else None,
                *[clinic_card(c) for c in results],
            ) if results else (
                Div(
                    Div(
                        H3("No results yet", cls="text-lg font-semibold text-[var(--text-muted)]"),
                        P("Type a location above to find nearby clinics.", cls="text-sm text-[var(--text-muted)] opacity-60 mt-1"),
                        cls="text-center py-12",
                    ),
                ) if not q else
                Div(
                    Div(
                        H3("No clinics found", cls="text-lg font-semibold text-[var(--text-muted)]"),
                        P(f"No results for \"{q}\". Try a different area.", cls="text-sm text-[var(--text-muted)] opacity-60 mt-1"),
                        cls="text-center py-12",
                    ),
                )
            ),
            Div(
                Div(
                    Div(
                        Span("Ask Dr. Link", cls="font-semibold font-display"),
                        Span("AI-powered", cls="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[var(--text-muted)] ml-2"),
                        cls="flex items-center mb-3",
                    ),
                    Div(
                        *[_chat_bubble(m, i) for i, m in enumerate(history)],
                        cls="max-h-72 overflow-y-auto",
                        style="min-height: 60px;",
                    ) if history else Div(
                        P("Ask Dr. Link about clinic hours, services, or which clinic suits your needs.",
                          cls="text-sm text-[var(--text-muted)] text-center py-4"),
                    ),
                    Form(
                        Div(
                            Input(name="message", placeholder="Ask Dr. Link...",
                                  required=True, cls="input-glass px-4 py-2.5 w-full text-sm"),
                            Button("Send", type="submit", cls="gradient-btn text-white px-5 py-2.5 rounded-lg text-sm font-medium ml-2 border-0 cursor-pointer"),
                            A("Clear", href="/ai/clinic-finder/clear", cls="text-xs text-[var(--text-muted)] hover:text-white ml-3 transition-colors"),
                            cls="flex items-center mt-3",
                        ),
                        method="post",
                    ),
                    cls="p-4",
                ),
                cls="glass-card-premium mt-6",
            ),
            Div(
                A("AI Home", href="/ai", cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )


@rt("/ai/clinic-finder")
def post(session, message: str):
    history = session.get("clinic_history", [])
    history.append({"role": "user", "content": message})
    context = session.get("_clinic_context", [])
    if context:
        lines = "\n".join(f"- {c['name']} ({c['city']}) — {c['phone']}" for c in context)
        history.append({"role": "system", "content": f"Nearby clinics:\n{lines}"})
    result = ai.clinic_finder(history)
    if result.get("ok"):
        entry = {"role": "assistant", "content": result["reply"]}
        clinics = result.get("clinics", [])
        if clinics:
            entry["clinics"] = clinics
        history.append(entry)
    else:
        history.append({"role": "assistant", "content": "Sorry, I'm unavailable right now. Try again shortly."})
    session["clinic_history"] = history
    return get(session)


@rt("/ai/clinic-finder/clear")
def get(session):
    session.pop("clinic_history", None)
    session.pop("_clinic_context", None)
    return get(session)


@rt("/ai/triage")
def get(session):
    return _chat_page(
        "Patient Triage", "triage_history", session,
        form_action="/ai/triage",
        placeholder="Describe your symptoms...",
        button_text="Assess",
        subtitle="Describe your symptoms. I'll ask follow-up questions to determine the right care level.",
    )


@rt("/ai/triage")
def post(session, message: str):
    history = session.get("triage_history", [])
    history.append({"role": "user", "content": message})
    result = ai.triage(history)
    if result.get("ok"):
        history.append({"role": "assistant", "content": result["reply"]})
        session.pop("_chat_error", None)
    else:
        session["_chat_error"] = "The AI assistant is temporarily unavailable. Please try again."
    session["triage_history"] = history
    return _chat_page(
        "Patient Triage", "triage_history", session,
        form_action="/ai/triage",
        placeholder="Describe your symptoms...",
        button_text="Assess",
        subtitle="Describe your symptoms. I'll ask follow-up questions to determine the right care level.",
    )


@rt("/ai/triage/clear")
def get(session):
    session.pop("triage_history", None)
    session.pop("_chat_error", None)
    return _chat_page(
        "Patient Triage", "triage_history", session,
        form_action="/ai/triage",
        placeholder="Describe your symptoms...",
        button_text="Assess",
        subtitle="Describe your symptoms. I'll ask follow-up questions to determine the right care level.",
    )


@rt("/ai/chat")
def get(session):
    return _chat_page(
        "General Chat", "chat_history", session,
        form_action="/ai/chat",
        placeholder="Ask about DoctorLink, ZK compliance, or health info...",
        button_text="Send",
        subtitle="Ask about DoctorLink, ZK health compliance, or general health information.",
    )


@rt("/ai/chat")
def post(session, message: str):
    history = session.get("chat_history", [])
    history.append({"role": "user", "content": message})
    result = ai.chat(history, system_prompt="general")
    if result.get("ok"):
        history.append({"role": "assistant", "content": result["reply"]})
        session.pop("_chat_error", None)
    else:
        session["_chat_error"] = "The AI assistant is temporarily unavailable. Please try again."
    session["chat_history"] = history
    return _chat_page(
        "General Chat", "chat_history", session,
        form_action="/ai/chat",
        placeholder="Ask about DoctorLink, ZK compliance, or health info...",
        button_text="Send",
        subtitle="Ask about DoctorLink, ZK health compliance, or general health information.",
    )


@rt("/ai/chat/clear")
def get(session):
    session.pop("chat_history", None)
    session.pop("_chat_error", None)
    return _chat_page(
        "General Chat", "chat_history", session,
        form_action="/ai/chat",
        placeholder="Ask about DoctorLink, ZK compliance, or health info...",
        button_text="Send",
        subtitle="Ask about DoctorLink, ZK health compliance, or general health information.",
    )


@rt("/clinics")
def get():
    all_clinics = cs.all_clinics()
    return layout(
        "Clinics — DoctorLink",
        Div(
            Div(
                H2("SA Clinic Directory", cls="text-2xl font-bold font-display mb-1"),
                P(f"{len(all_clinics)} clinics from Octoparse seed data", cls="text-sm text-[var(--text-muted)] mb-6"),
            ),
            *[clinic_card(c) for c in all_clinics],
            Div(
                A("Dashboard", href="/", cls="text-xs text-[var(--text-muted)] hover:text-white transition-colors"),
                cls="mt-6 text-center",
            ),
        ),
    )


@rt("/api/clinics/search")
def get(q: str = ""):
    all_cs = cs.search_by_location(q) if q else cs.all_clinics()
    return json.dumps(all_cs)

# ── Start ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("frontend:app", host="0.0.0.0", port=8001, reload=True)
