import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# ⚙️ CONFIGURAZIONE SQUADRE ED ELEMENTI
# ==============================================================================
SQUADRE_INFO = [
    {"nome": "INPSWICH DOWN", "mister": "LOLLO"},
    {"nome": "CAZZATHE", "mister": "SIMO"},
    {"nome": "JOGA BENITO", "mister": "TAVE"},
    {"nome": "LAMINCHIADURA", "mister": "FEDE"},
    {"nome": "LEI3SWEET DREAMS", "mister": "SAMU"},
    {"nome": "MINORENNI FC", "mister": "VERRA"},
    {"nome": "REBECCA LAZIALE", "mister": "LUCIO"},
    {"nome": "SALISBURRO", "mister": "STACCHIO"},
    {"nome": "TEL-AVIV FC", "mister": "JACO"},
    {"nome": "VILLASBURREAL", "mister": "NICO"},
]

FANTASQUADRE = [f"{s['nome']} - {s['mister']}" for s in SQUADRE_INFO]
SLOTS = {"P": 3, "D": 8, "C": 8, "A": 6}
BUDGET_INIZIALE = 500

st.set_page_config(
    page_title="FantaLab - Asta Fantacalcio",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 🎨 STILE CSS FANTA-LAB DARK / NEON
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        background-color: #0c0919 !important;
        color: #e2e8f0;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Hide standard sidebar header padding */
    .stMainBlockContainer {
        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* Cards container upper section */
    .fantalab-card {
        background: linear-gradient(145deg, #161129, #100c21);
        border: 1px solid #282045;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        height: 100%;
    }

    /* Left teams mini list */
    .team-mini-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 10px;
        margin-bottom: 4px;
        background: #1b1533;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid #2a224a;
    }
    .team-mini-name {
        color: #d1d5db;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 110px;
    }
    .team-mini-budget {
        color: #fbbf24;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 3px;
    }

    /* Center player area */
    .player-avatar-box {
        width: 90px;
        height: 90px;
        background: radial-gradient(circle, #3b2d6b 0%, #171031 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        border: 2px solid #8b5cf6;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
    }

    .role-badge-btn {
        background: #251a4a;
        color: #a78bfa;
        border: 1px solid #4c1d95;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
    }

    /* Call Box */
    .call-box {
        background: linear-gradient(135deg, #2e2111 0%, #1c1524 100%);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-top: 10px;
    }
    .call-title {
        color: #fef3c7;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 8px;
    }

    /* Right stat card */
    .stat-card-box {
        background: linear-gradient(135deg, #1b113d 0%, #0d1b3e 100%);
        border: 1px solid #3b82f6;
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
    }
    .stat-text {
        font-size: 16px;
        font-weight: 600;
        color: #e0e7ff;
        line-height: 1.5;
    }
    .stat-highlight {
        color: #fbbf24;
        font-weight: 800;
    }

    /* Navigation Bar */
    .fantalab-navbar {
        display: flex;
        justify-content: center;
        gap: 8px;
        background: #130f24;
        padding: 8px;
        border-radius: 30px;
        border: 1px solid #261d47;
        margin: 15px 0;
        overflow-x: auto;
    }
    .nav-item {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        color: #9ca3af;
        background: transparent;
        border: none;
        white-space: nowrap;
    }
    .nav-item.active {
        background: #7c3aed;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(124, 58, 237, 0.5);
    }

    /* Board 10 columns Grid */
    .board-grid {
        display: grid;
        grid-template-columns: repeat(10, minmax(130px, 1fr));
        gap: 6px;
        width: 100%;
        overflow-x: auto;
    }

    .team-column {
        background: #110d21;
        border: 1px solid #231b3e;
        border-radius: 10px;
        overflow: hidden;
    }

    .team-header {
        background: #191233;
        padding: 8px 6px;
        text-align: center;
        border-bottom: 1px solid #2d2252;
    }
    .team-header-name {
        font-size: 10px;
        font-weight: 800;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .team-header-budget {
        font-size: 14px;
        font-weight: 800;
        color: #fbbf24;
        margin: 2px 0;
    }
    .team-header-sub {
        display: flex;
        justify-content: space-between;
        font-size: 8px;
        color: #6b7280;
        padding: 0 4px;
    }

    /* Role headers in board */
    .role-bar {
        font-size: 10px;
        font-weight: 800;
        padding: 3px 6px;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
    }
    .role-p { background-color: #d97706; } /* Portieri Arancio */
    .role-d { background-color: #15803d; } /* Difensori Verde */
    .role-c { background-color: #1d4ed8; } /* Centrocampisti Blu */
    .role-a { background-color: #be123c; } /* Attaccanti Rosso */

    /* Player cell in board */
    .player-cell {
        height: 22px;
        background: #16102b;
        border-bottom: 1px solid #21183c;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 5px;
        font-size: 10px;
    }
    .player-cell:nth-child(even) {
        background: #130e26;
    }
    .player-cell-name {
        color: #e2e8f0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 80px;
    }
    .player-cell-cost {
        color: #fbbf24;
        font-weight: 700;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# DATA LOAD & STATE
# ==============================================================================
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_csv(file_path)
        if len(df.columns) == 1 and ";" in df.columns[0]:
            df = pd.read_csv(file_path, sep=";")
    except Exception:
        df = pd.read_csv(file_path, sep=";")

    df.columns = df.columns.str.strip()
    colonna_prezzo = None
    for col in df.columns:
        if col.lower().replace(" ", "").replace("_", "") in [
            "prezzomedio",
            "prezzo",
            "quotazione",
        ]:
            colonna_prezzo = col
            break

    if colonna_prezzo:
        df = df.rename(columns={colonna_prezzo: "Prezzo Medio"})

    df["Prezzo_Numerico"] = pd.to_numeric(
        df["Prezzo Medio"], errors="coerce"
    ).fillna(0)
    return df


df_listone = load_data("fantalab_listone.csv")

if df_listone is None:
    st.error("⚠️ File `fantalab_listone.csv` non trovato!")
    st.stop()

if "acquisti" not in st.session_state:
    st.session_state.acquisti = []

giocatori_presi = [a["Giocatore"] for a in st.session_state.acquisti]
df_disponibili = df_listone[~df_listone["Giocatore"].isin(giocatori_presi)]


# Calcolo Budget per Squadra
def get_squadra_stats(nome_squadra):
    acquisti = [
        a
        for a in st.session_state.acquisti
        if a["Squadra_Fanta"] == nome_squadra
    ]
    spesi = sum(a["Costo"] for a in acquisti)
    rimasti = BUDGET_INIZIALE - spesi
    tot_giocatori = len(acquisti)
    return rimasti, tot_giocatori, acquisti


# ==============================================================================
# 1. TOP DASHBOARD (3 COLONNE COME NELLO SCREENSHOT)
# ==============================================================================
c_left, c_center, c_right = st.columns([1.2, 2, 1.8])

# --- SQUADRE MINI LIST (LEFT) ---
with c_left:
    st.markdown('<div class="fantalab-card">', unsafe_allow_html=True)
    for sq in FANTASQUADRE:
        rim, tot, _ = get_squadra_stats(sq)
        nome_breve = sq.split(" - ")[0]
        st.markdown(
            f"""
            <div class="team-mini-row">
                <span class="team-mini-name">{nome_breve}</span>
                <span class="team-mini-budget">🟡 {rim}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# --- PANNELLO ASTA / RICERCA (CENTER) ---
with c_center:
    st.markdown('<div class="fantalab-card">', unsafe_allow_html=True)

    # Avatar Silhouette + Filtri
    col_av, col_filt = st.columns([1, 2.5])
    with col_av:
        st.markdown(
            """
            <div class="player-avatar-box">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="#6b7280">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_filt:
        ruolo_selezionato = st.radio(
            "Ruolo",
            options=["TUTTI", "P", "D", "C", "A"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if ruolo_selezionato != "TUTTI":
            df_filtrati = df_disponibili[
                df_disponibili["Ruolo"] == ruolo_selezionato
            ]
        else:
            df_filtrati = df_disponibili

        giocatore_selezionato = st.selectbox(
            "Cerca Giocatore",
            options=sorted(df_filtrati["Giocatore"].tolist()),
            index=None,
            placeholder="🔍 CERCA GIOCATORE...",
            label_visibility="collapsed",
            key="search_box",
        )

    # Box chiamata o assegnazione
    if giocatore_selezionato:
        info_g = df_filtrati[
            df_filtrati["Giocatore"] == giocatore_selezionato
        ].iloc[0]

        st.markdown(
            f"""
            <div class="call-box" style="border-color:#8b5cf6; background:linear-gradient(135deg, #1e1b4b 0%, #110d21 100%);">
                <div style="font-size:16px; font-weight:800; color:#a78bfa;">{info_g['Giocatore']}</div>
                <div style="font-size:12px; color:#9ca3af;">{info_g['Ruolo']} | {info_g['Squadra']} | Prezzo Medio: {int(info_g['Prezzo_Numerico'])} FM</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ca1, ca2, ca3 = st.columns([1.5, 1, 1])
        with ca1:
            sq_dest = st.selectbox(
                "A", options=FANTASQUADRE, label_visibility="collapsed"
            )
        with ca2:
            costo = st.number_input(
                "Costo",
                min_value=1,
                value=1,
                step=1,
                label_visibility="collapsed",
            )
        with ca3:
            if st.button("ASSEGNA", use_container_width=True):
                st.session_state.acquisti.append(
                    {
                        "Giocatore": info_g["Giocatore"],
                        "Ruolo": info_g["Ruolo"],
                        "Costo": int(costo),
                        "Prezzo_Medio": int(info_g["Prezzo_Numerico"]),
                        "Squadra_Fanta": sq_dest,
                    }
                )
                st.rerun()
    else:
        st.markdown(
            """
            <div class="call-box">
                <div class="call-title">È il tuo turno di chiamata!</div>
                <div style="display:flex; gap:10px; justify-content:center;">
                    <span style="background:#374151; color:#9ca3af; padding:6px 16px; border-radius:8px; font-size:12px; font-weight:700;">ASSEGNA</span>
                    <span style="background:#374151; color:#9ca3af; padding:6px 16px; border-radius:8px; font-size:12px; font-weight:700;">CHIAMA</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# --- STAT WIDGET (RIGHT) ---
with c_right:
    st.markdown(
        """
        <div class="stat-card-box">
            <div class="stat-text">
                <span class="stat-highlight">Ravaglia F.</span> è il <span class="stat-highlight">10°</span> portiere di Serie A per percentuale di partite con voto ≥ 6 (<span class="stat-highlight">88%</span>)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 2. BARRA NAVIGAZIONE CENTRALE
# ==============================================================================
st.markdown(
    """
    <div class="fantalab-navbar">
        <button class="nav-item active">👕 Rosa Squadre</button>
        <button class="nav-item">📊 Fasce Giocatori</button>
        <button class="nav-item">📑 Recap Asta</button>
        <button class="nav-item">💡 Guida all'Asta</button>
        <button class="nav-item">⚽ Partite</button>
        <button class="nav-item">⚔️ Avversari</button>
        <button class="nav-item">🧮 Stima Rosa/Budget</button>
        <button class="nav-item">📈 Analisi Asta</button>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 3. TABELLONE 10 COLONNE ORIZZONTALI (STILE FANTALAB)
# ==============================================================================
def render_board():
    cols_html = []

    for sq in FANTASQUADRE:
        rim, tot, acquisti_sq = get_squadra_stats(sq)
        nome_team = sq.split(" - ")[0]

        col_content = [
            f"""
        <div class="team-column">
            <div class="team-header">
                <div class="team-header-name">{nome_team}</div>
                <div class="team-header-budget">🟡 {rim}</div>
                <div class="team-header-sub">
                    <span>MAX: {rim - (25 - tot) + 1 if (25-tot)>0 else rim}</span>
                    <span>{tot}/25</span>
                </div>
            </div>
        """
        ]

        # Genera sezioni per Ruoli (P, D, C, A)
        for ruolo, num_slots in SLOTS.items():
            role_css = f"role-{ruolo.lower()}"
            giocatori_r = [a for a in acquisti_sq if a["Ruolo"] == ruolo]
            pct = int((len(giocatori_r) / num_slots) * 100)

            col_content.append(
                f'<div class="role-bar {role_css}"><span>{ruolo}</span><span>{pct}%</span></div>'
            )

            for i in range(num_slots):
                if i < len(giocatori_r):
                    g = giocatori_r[i]
                    col_content.append(
                        f"""
                        <div class="player-cell">
                            <span class="player-cell-name">{g['Giocatore']}</span>
                            <span class="player-cell-cost">{g['Costo']}</span>
                        </div>
                        """
                    )
                else:
                    col_content.append(
                        '<div class="player-cell"><span class="player-cell-name" style="color:#374151;">-</span></div>'
                    )

        col_content.append("</div>")
        cols_html.append("".join(col_content))

    grid_wrapper = f'<div class="board-grid">{"".join(cols_html)}</div>'
    return grid_wrapper


st.markdown(render_board(), unsafe_allow_html=True)

# Tasto Annulla in basso
if st.session_state.acquisti:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↩️ Annulla Ultimo Acquisto", use_container_width=True):
        st.session_state.acquisti.pop()
        st.rerun()

# --- JAVASCRIPT SCORCIATOIA TASTIERA ---
components.html(
    """
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if (doc.activeElement.tagName !== 'INPUT' && doc.activeElement.tagName !== 'TEXTAREA') {
        if (e.key.length === 1 || e.key === 'Backspace') {
            const inputField = doc.querySelector('input[placeholder="🔍 CERCA GIOCATORE..."]');
            if (inputField) {
                inputField.focus();
            }
        }
    }
});
</script>
""",
    height=0,
)