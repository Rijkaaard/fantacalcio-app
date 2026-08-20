import base64
import json
import os
import pandas as pd
import streamlit as st

# ==============================================================================
# ⚙️ CONFIGURAZIONE SQUADRE ED ELEMENTI
# ==============================================================================
SQUADRE_INFO = [
    {"nome": "INPSWICH DOWN", "mister": "LOLLO", "codice": "INP"},
    {"nome": "CAZZATHE", "mister": "SIMO", "codice": "CAZ"},
    {"nome": "JOGA BENITO", "mister": "TAVE", "codice": "JOG"},
    {"nome": "LAMINCHIADURA", "mister": "FEDE", "codice": "LAM"},
    {"nome": "LEI3SWEET DREAMS", "mister": "SAMU", "codice": "LEI"},
    {"nome": "MINORENNI FC", "mister": "VERRA", "codice": "MIN"},
    {"nome": "REBECCA LAZIALE", "mister": "LUCIO", "codice": "REB"},
    {"nome": "SALISBURRO", "mister": "STACCHIO", "codice": "SAL"},
    {"nome": "TEL-AVIV FC", "mister": "JACO", "codice": "TEL"},
    {"nome": "VILLASBURREAL", "mister": "NICO", "codice": "VIL"},
]

FANTASQUADRE = [f"{s['nome']} - {s['mister']}" for s in SQUADRE_INFO]
SLOTS = {"P": 3, "D": 8, "C": 8, "A": 6}
TOTALE_SLOTS = sum(SLOTS.values())
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
# 🧼 PULIZIA INTERFACCIA CSS
# ==============================================================================
hide_st_style = """
    <style>
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {padding-top: 0px !important;}
    [data-testid="stStatusWidget"] {
        display: none !important;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

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

if "search_version" not in st.session_state:
    st.session_state.search_version = 0

# ==============================================================================
# 🎨 STILE CSS COMPATTO (OTTIMIZZATO PER SPAZIATURA E PULIZIA)
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
        padding-top: 1rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #120d24 !important;
        border: 1px solid #282045 !important;
        border-radius: 12px !important;
        padding: 8px 10px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 6px !important;
    }

    .card-title {
        font-size: 11px;
        font-weight: 800;
        color: #a78bfa;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }

    .team-mini-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 2px 6px;
        margin-bottom: 2px;
        background: #1b1533;
        border-radius: 4px;
        font-size: 9px;
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
        grid-template-columns: repeat(10, minmax(125px, 1fr));
        gap: 6px;
        width: 100%;
        overflow-x: auto;
        padding-bottom: 15px;
        padding-left: 2px;
        padding-right: 2px;
    }

    .team-column {
        background: #110d21;
        border: 1px solid #231b3e;
        border-radius: 8px;
        overflow: hidden;
    }

    .team-header {
        background: #191233;
        padding: 6px 4px;
        text-align: center;
        border-bottom: 1px solid #2d2252;
    }
    
    .team-logo-container {
        width: 50px;
        height: 50px;
        margin: 0 auto 4px auto;
        background: transparent !important;
        border: none !important;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .fanta-team-logo {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 0px !important;
        background: transparent !important;
        border: none !important;
    }

    .team-header-name {
        font-size: 9px;
        font-weight: 800;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
    }
    .team-header-budget {
        font-size: 13px;
        font-weight: 800;
        color: #fbbf24;
        margin: 1px 0;
    }
    .team-header-sub {
        display: flex;
        justify-content: space-between;
        font-size: 7px;
        color: #9ca3af;
        padding: 0 2px;
    }

    .role-bar {
        font-size: 9px;
        font-weight: 800;
        padding: 2px 5px;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
    }
    .role-p { background-color: #d97706; }
    .role-d { background-color: #15803d; }
    .role-c { background-color: #1d4ed8; }
    .role-a { background-color: #be123c; }

    .player-cell {
        height: 22px;
        background: #16102b;
        border-bottom: 1px solid #21183c;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 4px;
        font-size: 9.5px;
    }
    .player-cell:nth-child(even) {
        background: #130e26;
    }

    .player-cell-left {
        display: flex;
        align-items: center;
        gap: 3px;
        overflow: hidden;
        max-width: 90px;
    }

    .player-team-logo {
        width: 12px;
        height: 12px;
        object-fit: contain;
        flex-shrink: 0;
    }

    .player-cell-name {
        color: #e2e8f0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .player-cell-right {
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# CARICAMENTO DATI E CACHE LOGHI
# ==============================================================================
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
def load_all_logos():
    logos = {}
    if not os.path.exists("loghi"):
        return logos
    for filename in os.listdir("loghi"):
        if filename.lower().endswith(("png", "jpg", "jpeg", "webp", "svg")):
            name_without_ext = os.path.splitext(filename)[0].upper()
            path = os.path.join("loghi", filename)
            try:
                ext = filename.split(".")[-1].lower()
                mime_type = "image/png" if ext == "png" else f"image/{ext}"
                with open(path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                logos[name_without_ext] = f"data:{mime_type};base64,{encoded_string}"
            except Exception:
                pass
    return logos

ALL_LOGOS = load_all_logos()

def get_logo_base64_cached(squadra):
    if not squadra or pd.isna(squadra):
        return ""
    sq_str = str(squadra).strip().upper()
    codice = MAPPA_CODICI_LOGHI.get(sq_str, sq_str)
    
    if codice in ALL_LOGOS:
        return ALL_LOGOS[codice]
    if sq_str in ALL_LOGOS:
        return ALL_LOGOS[sq_str]
    return ""

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

df_listone = load_data("fantalab_listone.csv")

if df_listone is None:
    st.error("⚠️ File `fantalab_listone.csv` non trovato!")
    st.stop()


def get_squadra_stats(nome_squadra):
    acquisti = [a for a in st.session_state.acquisti if a["Squadra_Fanta"] == nome_squadra]
    spesi = sum(a["Costo"] for a in acquisti)
    rimasti = BUDGET_INIZIALE - spesi
    tot_giocatori = len(acquisti)
    slot_mancanti = TOTALE_SLOTS - tot_giocatori

    max_offerta = rimasti - (slot_mancanti - 1) if slot_mancanti > 0 else 0
    return rimasti, tot_giocatori, max_offerta, acquisti


query_params = st.query_params
is_tv_mode = query_params.get("vista") == "tv"

# ==============================================================================
# 1. PANNELLO SUPERIORE ISOLATO IN UN FRAGMENT
# ==============================================================================
@st.fragment
def render_control_panel():
    st.session_state.acquisti = load_saved_acquisti()
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
            st.markdown('<div class="card-title">GESTIONE ASTA LIBERA & FILTRI</div>', unsafe_allow_html=True)

            tab_assegna, tab_svincola = st.tabs(["➕ Assegna Calciatore", "🗑️ Svincola / Rimuovi"])

            giocatori_presi = {a["Giocatore"] for a in st.session_state.acquisti}
            df_disponibili = df_listone[~df_listone["Giocatore"].isin(giocatori_presi)]

            with tab_assegna:
                f_col1, f_col2 = st.columns([1, 1])
                with f_col1:
                    filtro_ruolo = st.selectbox("Filtra per Ruolo", options=["Tutti", "P", "D", "C", "A"], label_visibility="collapsed", index=0, key="ctrl_ruolo")
                with f_col2:
                    squadre_sa_list = sorted(df_disponibili["Squadra_SerieA"].dropna().unique().tolist()) if "Squadra_SerieA" in df_disponibili.columns else []
                    filtro_sa = st.selectbox("Filtra per Squadra Serie A", options=["Tutte le squadre"] + squadre_sa_list, label_visibility="collapsed", index=0, key="ctrl_sa")

                df_filtrati = df_disponibili.copy()
                if filtro_ruolo != "Tutti":
                    df_filtrati = df_filtrati[df_filtrati["Ruolo"] == filtro_ruolo]
                if filtro_sa != "Tutte le squadre":
                    df_filtrati = df_filtrati[df_filtrati["Squadra_SerieA"] == filtro_sa]

                col_g, col_sq, col_costo, col_btn = st.columns([2.5, 2, 1, 1.2])

                with col_g:
                    # Utilizziamo una chiave dinamica con la versione per azzerare la ricerca correttamente senza eccezioni
                    giocatore_selezionato = st.selectbox(
                        "Cerca Calciatore",
                        options=sorted(df_filtrati["Giocatore"].tolist()),
                        index=None,
                        placeholder="🔍 Cerca calciatore...",
                        label_visibility="collapsed",
                        key=f"search_box_{st.session_state.search_version}",
                    )

                with col_sq:
                    sq_dest = st.selectbox(
                        "Aggiudicato a", 
                        options=FANTASQUADRE, 
                        label_visibility="collapsed",
                        key="ctrl_dest"
                    )

                with col_costo:
                    costo_asta = st.number_input("Costo", min_value=1, value=1, step=1, label_visibility="collapsed", key="ctrl_costo")

                with col_btn:
                    btn_conferma = st.button("✅ CONFERMA", use_container_width=True, type="primary", key="ctrl_btn_conf")

                if giocatore_selezionato and btn_conferma:
                    info_g = df_listone[df_listone["Giocatore"] == giocatore_selezionato].iloc[0]
                    ruolo_g = info_g["Ruolo"]
                    squadra_sa = str(info_g.get("Squadra_SerieA", info_g.get("Squadra", ""))).strip()

                    rimasti, _, max_offerta, acquisti_sq = get_squadra_stats(sq_dest)
                    giocatori_ruolo = len([a for a in acquisti_sq if a["Ruolo"] == ruolo_g])
                    max_slot_ruolo = SLOTS[ruolo_g]

                    if giocatori_ruolo >= max_slot_ruolo:
                        st.error(f"❌ Questa squadra ha già completato i slot per il ruolo **{ruolo_g}** ({max_slot_ruolo}/{max_slot_ruolo})!")
                    elif costo_asta > max_offerta:
                        st.error(f"❌ Offerta troppo alta! Offerta Max consentita: **{max_offerta} FM**.")
                    else:
                        nuovo_acquisto = {
                            "Giocatore": info_g["Giocatore"],
                            "Ruolo": ruolo_g,
                            "Costo": int(costo_asta),
                            "Prezzo_Medio": int(info_g["Prezzo_Numerico"]),
                            "Squadra_SerieA": squadra_sa,
                            "Squadra_Fanta": sq_dest,
                        }
                        st.session_state.acquisti.append(nuovo_acquisto)
                        save_acquisti()
                        st.success(f"✅ **{info_g['Giocatore']}** assegnato a **{sq_dest.split(' - ')[0]}** per {int(costo_asta)} FM!")
                        
                        # Incrementa la versione per resettare la selectbox pulita al prossimo rerun
                        st.session_state.search_version += 1
                        st.rerun()

                if giocatore_selezionato and not btn_conferma:
                    info_g = df_listone[df_listone["Giocatore"] == giocatore_selezionato].iloc[0]
                    squadra_serie_a = str(info_g.get("Squadra_SerieA", info_g.get("Squadra", ""))).strip()
                    logo_path = get_logo_path(squadra_serie_a)

                    if logo_path:
                        col_logo, col_info = st.columns([0.12, 0.88])
                        with col_logo:
                            st.image(logo_path, width=42)
                        with col_info:
                            st.info(f"**Ruolo:** {info_g['Ruolo']} | **Squadra Serie A:** {squadra_serie_a} | **Prezzo Medio:** {int(info_g['Prezzo_Numerico'])}")
                    else:
                        st.info(f"**Ruolo:** {info_g['Ruolo']} | **Squadra Serie A:** {squadra_serie_a} | **Prezzo Medio:** {int(info_g['Prezzo_Numerico'])}")

            with tab_svincola:
                if st.session_state.acquisti:
                    col_del_g, col_del_btn = st.columns([3, 1])
                    with col_del_g:
                        lista_acquistati = sorted([a["Giocatore"] for a in st.session_state.acquisti])
                        g_da_eliminare = st.selectbox("Seleziona Calciatore da rimuovere", options=lista_acquistati, label_visibility="collapsed", key="ctrl_del_box")
                    with col_del_btn:
                        if st.button("❌ RIMUOVI", type="primary", use_container_width=True, key="ctrl_btn_del"):
                            st.session_state.acquisti = [a for a in st.session_state.acquisti if a["Giocatore"] != g_da_eliminare]
                            save_acquisti()
                            st.success(f"Rimosso con successo.")
                    
                    st.markdown("---")
                    
                    with st.expander("⚠️ Area Pericolosa: Reset Totale"):
                        st.warning("Attenzione: questo comando cancellerà **tutti** i calciatori acquistati da tutte le squadre, riportando l'asta allo stato iniziale.")
                        conferma_reset = st.checkbox("Conferma di voler eliminare TUTTI i calciatori", key="chk_reset_totale")
                        if st.button("🗑️ RIMUOVI TUTTI I CALCIATORI", type="primary", use_container_width=True, key="btn_reset_totale"):
                            if conferma_reset:
                                st.session_state.acquisti = []
                                save_acquisti()
                                st.success("Tutti i calciatori sono stati rimossi con successo!")
                                st.rerun()
                            else:
                                st.error("Devi spuntare la casella di conferma per procedere con il reset totale.")
                else:
                    st.info("Nessun calciatore ancora assegnato.")

if not is_tv_mode:
    render_control_panel()

# ==============================================================================
# 2. TABELLONE FRAGMENT (AGGIORNAMENTO AUTOMATICO OGNI 5 SECONDI)
# ==============================================================================
@st.fragment(run_every=5)
def render_board_fragment():
    st.session_state.acquisti = load_saved_acquisti()
    
    cols_html = []

    for s_info in SQUADRE_INFO:
        sq = f"{s_info['nome']} - {s_info['mister']}"
        rim, tot, max_off, acquisti_sq = get_squadra_stats(sq)
        nome_team = s_info['nome']
        max_val = max_off if max_off > 0 else 0
        
        logo_fanta_html = ""
        if is_tv_mode:
            fanta_logo_b64 = get_logo_base64_cached(s_info['codice'])
            if fanta_logo_b64:
                logo_fanta_html = f'<div class="team-logo-container"><img src="{fanta_logo_b64}" class="fanta-team-logo" alt="{s_info["codice"]}"></div>'
        
        col_content = [
            f'<div class="team-column">'
            f'<div class="team-header">'
            f'{logo_fanta_html}'
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
            giocatori_r = sorted(giocatori_r, key=lambda x: x.get("Prezzo_Medio", 0), reverse=True)

            speso_ruolo = sum(g["Costo"] for g in giocatori_r)
            pct_budget = round((speso_ruolo / BUDGET_INIZIALE) * 100, 1)
            pct_str = f"{int(pct_budget)}%" if pct_budget.is_integer() else f"{pct_budget}%"

            col_content.append(f'<div class="role-bar {role_css}"><span>{ruolo}</span><span>{pct_str}</span></div>')

            for i in range(num_slots):
                if i < len(giocatori_r):
                    g = giocatori_r[i]
                    nome_g = g["Giocatore"]
                    sq_sa = g.get("Squadra_SerieA", "")
                    logo_b64 = get_logo_base64_cached(sq_sa)
                    logo_html = f'<img src="{logo_b64}" class="player-team-logo" alt="{sq_sa}">' if logo_b64 else ""

                    costo = g["Costo"]
                    prezzo_medio = g.get("Prezzo_Medio", 0)

                    if costo < prezzo_medio:
                        colore_prezzo = "#22c55e"
                    elif costo > prezzo_medio:
                        colore_prezzo = "#ef4444"
                    else:
                        colore_prezzo = "#fbbf24"

                    col_content.append(
                        f'<div class="player-cell">'
                        f'<div class="player-cell-left">'
                        f'{logo_html}'
                        f'<span class="player-cell-name">{nome_g}</span>'
                        f'</div>'
                        f'<div class="player-cell-right">'
                        f'<span class="player-cell-cost" style="color: {colore_prezzo};">{costo}</span>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    col_content.append('<div class="player-cell"><span class="player-cell-name" style="color:#374151;">-</span></div>')

        col_content.append("</div>")
        cols_html.append("".join(col_content))

    st.markdown(f'<div class="board-grid">{"".join(cols_html)}</div>', unsafe_allow_html=True)


render_board_fragment()