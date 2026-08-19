import base64
import json
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
TOTALE_SLOTS = sum(SLOTS.values())  # 25 giocatori
BUDGET_INIZIALE = 500

MAPPA_CODICI_LOGHI = {
    "ATALANTA": "ATA", "BOLOGNA": "BOL", "CAGLIARI": "CAG", "COMO": "COM",
    "EMPOLI": "EMP", "FIORENTINA": "FIO", "GENOA": "GEN", "INTER": "INT",
    "JUVENTUS": "JUV", "LAZIO": "LAZ", "LECCE": "LEC", "MILAN": "MIL",
    "MONZA": "MON", "NAPOLI": "NAP", "PARMA": "PAR", "ROMA": "ROM",
    "SALERNITANA": "SAL", "SAMPDORIA": "SAM", "SASSUOLO": "SAS",
    "SPEZIA": "SPE", "TORINO": "TOR", "UDINESE": "UDI", "VENEZIA": "VEN",
    "VERONA": "VER",
}

st.set_page_config(
    page_title="FantaLab - Tabellone Asta",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 💾 GESTIONE SALVATAGGIO PERSISTENTE
# ==============================================================================
DATA_FILE = "fanta_asta_data.json"

def load_saved_acquisti():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_acquisti():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.acquisti, f, ensure_ascii=False, indent=2)

if "acquisti" not in st.session_state:
    st.session_state.acquisti = load_saved_acquisti()

# --- TRIGGER RIMOZIONE SILENZIOSA (SENZA REFRESH BROWSER) ---
st.markdown('<style>div[data-testid="stTextInput"]:has(input[aria-label="TriggerRimozione"]) { display: none; }</style>', unsafe_allow_html=True)
st.text_input("TriggerRimozione", key="trigger_rimozione", label_visibility="collapsed")

if st.session_state.get("trigger_rimozione"):
    giocatore_da_rimuovere = st.session_state.trigger_rimozione
    st.session_state.acquisti = [a for a in st.session_state.acquisti if a["Giocatore"] != giocatore_da_rimuovere]
    save_acquisti()
    st.session_state.trigger_rimozione = ""
    st.rerun()

# ==============================================================================
# 🎨 STILE CSS FANTA-LAB DARK NEON
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

    .stMainBlockContainer {
        padding-top: 3.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #120d24 !important;
        border: 1px solid #282045 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 10px !important;
    }

    .card-title {
        font-size: 13px;
        font-weight: 800;
        color: #a78bfa;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    .team-mini-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 10px;
        margin-bottom: 3px;
        background: #1b1533;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid #2a224a;
    }
    .team-mini-name {
        color: #d1d5db;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 120px;
    }
    .team-mini-budget {
        color: #fbbf24;
        font-weight: 700;
    }

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
        color: #9ca3af;
        padding: 0 4px;
    }

    .role-bar {
        font-size: 10px;
        font-weight: 800;
        padding: 3px 6px;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
    }
    .role-p { background-color: #d97706; }
    .role-d { background-color: #15803d; }
    .role-c { background-color: #1d4ed8; }
    .role-a { background-color: #be123c; }

    .player-cell {
        height: 24px;
        background: #16102b;
        border-bottom: 1px solid #21183c;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 5px;
        font-size: 10px;
        transition: background-color 0.2s ease;
    }
    .player-cell:nth-child(even) {
        background: #130e26;
    }

    .player-cell-left {
        display: flex;
        align-items: center;
        gap: 4px;
        overflow: hidden;
        max-width: 95px;
    }

    .player-team-logo {
        width: 14px;
        height: 14px;
        border-radius: 0px !important;
        object-fit: contain;
        flex-shrink: 0;
    }

    .player-cell-name {
        color: #e2e8f0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* --- STILI ANIMAZIONE RIMOZIONE HOVER --- */
    .player-cell-right {
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }

    .player-cell-cost {
        font-weight: 700;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        display: inline-block;
    }

    .delete-btn {
        opacity: 0;
        max-width: 0;
        margin-left: 0;
        color: #ef4444 !important;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 11px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
        white-space: nowrap;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    .delete-btn:hover {
        color: #dc2626 !important;
        transform: scale(1.3);
    }

    .player-cell:hover .delete-btn {
        opacity: 1;
        max-width: 20px;
        margin-left: 6px;
    }

    .player-cell:hover .player-cell-cost {
        transform: translateX(-2px);
    }

    stImage > img {
        border-radius: 0px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# CARICAMENTO DATI E CACHING
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

    colonna_prezzo = next((c for c in df.columns if c.lower().replace(" ", "").replace("_", "") in ["prezzomedio", "prezzo", "quotazione"]), None)
    if colonna_prezzo:
        df = df.rename(columns={colonna_prezzo: "Prezzo Medio"})

    colonna_squadra = next((c for c in df.columns if c.lower().replace(" ", "").replace("_", "") in ["squadra", "team", "club", "squadraseriea"]), None)
    if colonna_squadra:
        df = df.rename(columns={colonna_squadra: "Squadra_SerieA"})

    df["Prezzo_Numerico"] = pd.to_numeric(df["Prezzo Medio"], errors="coerce").fillna(0)
    return df


@st.cache_data
def get_logo_path(squadra):
    if not squadra or pd.isna(squadra):
        return None

    sq_str = str(squadra).strip().upper()
    codice_squadra = MAPPA_CODICI_LOGHI.get(sq_str, sq_str)
    estensioni = ["png", "jpg", "jpeg", "webp", "svg"]

    for ext in estensioni:
        path = os.path.join("loghi", f"{codice_squadra}.{ext}")
        if os.path.exists(path):
            return path
        path_lower = os.path.join("loghi", f"{codice_squadra.lower()}.{ext}")
        if os.path.exists(path_lower):
            return path_lower

    return None


@st.cache_data
def get_logo_base64(path):
    if not path or not os.path.exists(path):
        return ""
    ext = path.split(".")[-1].lower()
    mime_type = "image/png" if ext == "png" else f"image/{ext}"
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_string}"


df_listone = load_data("fantalab_listone.csv")

if df_listone is None:
    st.error("⚠️ File `fantalab_listone.csv` non trovato!")
    st.stop()

giocatori_presi = {a["Giocatore"] for a in st.session_state.acquisti}
df_disponibili = df_listone[~df_listone["Giocatore"].isin(giocatori_presi)]


def get_squadra_stats(nome_squadra):
    acquisti = [a for a in st.session_state.acquisti if a["Squadra_Fanta"] == nome_squadra]
    spesi = sum(a["Costo"] for a in acquisti)
    rimasti = BUDGET_INIZIALE - spesi
    tot_giocatori = len(acquisti)
    slot_mancanti = TOTALE_SLOTS - tot_giocatori

    max_offerta = rimasti - (slot_mancanti - 1) if slot_mancanti > 0 else 0
    return rimasti, tot_giocatori, max_offerta, acquisti


# ==============================================================================
# 1. PANNELLO SUPERIORE (SQUADRE ED ASSEGNAZIONE)
# ==============================================================================
c_left, c_right = st.columns([1.2, 3])

with c_left:
    with st.container(border=True):
        st.markdown('<div class="card-title">SQUADRE & BUDGET</div>', unsafe_allow_html=True)
        for sq in FANTASQUADRE:
            rim, tot, _, _ = get_squadra_stats(sq)
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

with c_right:
    with st.container(border=True):
        st.markdown('<div class="card-title">ASSEGNA GIOCATORE</div>', unsafe_allow_html=True)

        ruolo_selezionato = st.radio(
            "Filtra Ruolo",
            options=["TUTTI", "P", "D", "C", "A"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if ruolo_selezionato != "TUTTI":
            df_filtrati = df_disponibili[df_disponibili["Ruolo"] == ruolo_selezionato]
        else:
            df_filtrati = df_disponibili

        col_g, col_sq, col_costo, col_btn = st.columns([2.5, 2, 1, 1.2])

        with col_g:
            giocatore_selezionato = st.selectbox(
                "Cerca Calciatore",
                options=sorted(df_filtrati["Giocatore"].tolist()),
                index=None,
                placeholder="🔍 Cerca calciatore...",
                label_visibility="collapsed",
                key="search_box",
            )

        with col_sq:
            sq_dest = st.selectbox(
                "Aggiudicato a",
                options=FANTASQUADRE,
                label_visibility="collapsed",
            )

        with col_costo:
            costo_asta = st.number_input(
                "Costo",
                min_value=1,
                value=1,
                step=1,
                label_visibility="collapsed",
            )

        with col_btn:
            btn_conferma = st.button("✅ CONFERMA", use_container_width=True, type="primary")

        if giocatore_selezionato and btn_conferma:
            info_g = df_filtrati[df_filtrati["Giocatore"] == giocatore_selezionato].iloc[0]
            ruolo_g = info_g["Ruolo"]
            squadra_sa = str(info_g.get("Squadra_SerieA", info_g.get("Squadra", ""))).strip()

            rimasti, tot_giocatori, max_offerta, acquisti_sq = get_squadra_stats(sq_dest)
            giocatori_ruolo = len([a for a in acquisti_sq if a["Ruolo"] == ruolo_g])
            max_slot_ruolo = SLOTS[ruolo_g]

            if giocatori_ruolo >= max_slot_ruolo:
                st.error(f"❌ **{sq_dest.split(' - ')[0]}** ha già completato lo slot per il ruolo **{ruolo_g}** ({max_slot_ruolo}/{max_slot_ruolo})!")
            elif costo_asta > max_offerta:
                st.error(f"❌ Offerta troppo alta per **{sq_dest.split(' - ')[0]}**! Offerta Max consentita: **{max_offerta} FM** (Budget rimasto: {rimasti} FM).")
            else:
                st.session_state.acquisti.append(
                    {
                        "Giocatore": info_g["Giocatore"],
                        "Ruolo": info_g["Ruolo"],
                        "Costo": int(costo_asta),
                        "Prezzo_Medio": int(info_g["Prezzo_Numerico"]),
                        "Squadra_SerieA": squadra_sa,
                        "Squadra_Fanta": sq_dest,
                    }
                )
                save_acquisti()
                st.success(f"✅ **{info_g['Giocatore']}** assegnato a **{sq_dest.split(' - ')[0]}** per **{costo_asta} FM**!")
                st.rerun()

        if giocatore_selezionato:
            info_g = df_filtrati[df_filtrati["Giocatore"] == giocatore_selezionato].iloc[0]
            squadra_serie_a = str(info_g.get("Squadra_SerieA", info_g.get("Squadra", ""))).strip()
            logo_path = get_logo_path(squadra_serie_a)

            if logo_path:
                col_logo, col_info = st.columns([0.12, 0.88])
                with col_logo:
                    st.image(logo_path, width=42)
                with col_info:
                    st.info(f"**Ruolo:** {info_g['Ruolo']} | **Squadra Serie A:** {squadra_serie_a} | **Prezzo Medio (FM):** {int(info_g['Prezzo_Numerico'])}")
            else:
                st.info(f"**Ruolo:** {info_g['Ruolo']} | **Squadra Serie A:** {squadra_serie_a} | **Prezzo Medio (FM):** {int(info_g['Prezzo_Numerico'])}")


# ==============================================================================
# 2. TABELLONE 10 COLONNE ORIZZONTALI (ROSE SQUADRE)
# ==============================================================================
def render_board():
    cols_html = []

    for sq in FANTASQUADRE:
        rim, tot, max_off, acquisti_sq = get_squadra_stats(sq)
        nome_team = sq.split(" - ")[0]
        max_val = max_off if max_off > 0 else 0
        
        col_content = [
            f'<div class="team-column">'
            f'<div class="team-header">'
            f'<div class="team-header-name">{nome_team}</div>'
            f'<div class="team-header-budget">🟡 {rim}</div>'
            f'<div class="team-header-sub">'
            f'<span>MAX: {max_val}</span>'
            f'<span>{tot}/25</span>'
            f'</div></div>'
        ]

        for ruolo, num_slots in SLOTS.items():
            role_css = f"role-{ruolo.lower()}"
            giocatori_r = [a for a in acquisti_sq if a["Ruolo"] == ruolo]

            speso_ruolo = sum(g["Costo"] for g in giocatori_r)
            pct_budget = round((speso_ruolo / BUDGET_INIZIALE) * 100, 1)
            pct_str = f"{int(pct_budget)}%" if pct_budget.is_integer() else f"{pct_budget}%"

            col_content.append(f'<div class="role-bar {role_css}"><span>{ruolo}</span><span>{pct_str}</span></div>')

            for i in range(num_slots):
                if i < len(giocatori_r):
                    g = giocatori_r[i]
                    nome_g = g["Giocatore"]
                    nome_escaped = nome_g.replace("'", "\\'")
                    sq_sa = g.get("Squadra_SerieA", "")
                    logo_p = get_logo_path(sq_sa)
                    logo_b64 = get_logo_base64(logo_p) if logo_p else ""
                    logo_html = f'<img src="{logo_b64}" class="player-team-logo" alt="{sq_sa}">' if logo_b64 else ""

                    costo = g["Costo"]
                    prezzo_medio = g.get("Prezzo_Medio", 0)

                    if costo < prezzo_medio:
                        colore_prezzo = "#22c55e"
                    elif costo > prezzo_medio:
                        colore_prezzo = "#ef4444"
                    else:
                        colore_prezzo = "#fbbf24"

                    delete_onclick = f"window.parent.silentlyRemovePlayer('{nome_escaped}')"
                    col_content.append(
                        f'<div class="player-cell">'
                        f'<div class="player-cell-left">'
                        f'{logo_html}'
                        f'<span class="player-cell-name">{nome_g}</span>'
                        f'</div>'
                        f'<div class="player-cell-right">'
                        f'<span class="player-cell-cost" style="color: {colore_prezzo};">{costo}</span>'
                        f'<a href="javascript:void(0)" onclick="{delete_onclick}" class="delete-btn" title="Rimuovi {nome_g}">✖</a>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    col_content.append('<div class="player-cell"><span class="player-cell-name" style="color:#374151;">-</span></div>')

        col_content.append("</div>")
        cols_html.append("".join(col_content))

    return f'<div class="board-grid">{"".join(cols_html)}</div>'


st.markdown(render_board(), unsafe_allow_html=True)

if st.session_state.acquisti:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↩️ Annulla Ultimo Acquisto", use_container_width=True):
        st.session_state.acquisti.pop()
        save_acquisti()
        st.rerun()

# --- JAVASCRIPT PONTE PER RIMOZIONE SILENZIOSA + AUTO-FOCUS ---
components.html(
    """
<script>
window.parent.silentlyRemovePlayer = function(playerName) {
    const doc = window.parent.document;
    const input = doc.querySelector('input[aria-label="TriggerRimozione"]');
    if (input) {
        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(input, playerName);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }
};

if (!window.parent._fantalab_keydown_attached) {
    window.parent._fantalab_keydown_attached = true;
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        if (doc.activeElement.tagName !== 'INPUT' && doc.activeElement.tagName !== 'TEXTAREA') {
            if (e.key.length === 1 || e.key === 'Backspace') {
                const inputField = doc.querySelector('input[placeholder="🔍 Cerca calciatore..."]');
                if (inputField) {
                    inputField.focus();
                }
            }
        }
    });
}
</script>
""",
    height=0,
)