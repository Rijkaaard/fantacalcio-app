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

MAPPA_NOME_CODICE_FANTA = {s['nome']: s['codice'] for s in SQUADRE_INFO}

query_params = st.query_params
is_tv_mode = query_params.get("vista") == "tv"

page_title_str = "Asta | Tabellone TV" if is_tv_mode else "Asta | Admin"

icona_path = "logo_icon.png"
page_icon_param = icona_path if os.path.exists(icona_path) else "⚽"

st.set_page_config(
    page_title=page_title_str,
    page_icon=page_icon_param,
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
# 🎨 STILE CSS - VIOLA DARK CYBERPUNK (COORDINATO ALL'HEADER)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Sfondo principale: Viola Notte Profondo */
    html, body, [class*="css"], .stApp {
        background-color: #090514 !important;
        color: #f8fafc;
        font-family: 'Inter', sans-serif !important;
    }

    .stMainBlockContainer {
        padding-top: 0.8rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    /* Allineamento colonne e contenitore flessibile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        align-items: stretch !important;
    }

    [data-testid="stColumn"] {
        display: flex !important;
        flex-direction: column !important;
    }

    [data-testid="stColumn"] > div {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }

    .classifica-container [data-testid="stVerticalBlockBorderWrapper"] {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* Card/Widget dell'interfaccia */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #110a24 !important;
        border: 1px solid #231342 !important;
        border-radius: 8px !important;
        padding: 10px 14px 16px 14px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5) !important;
        margin-bottom: 6px !important;
    }

    .card-title {
        font-size: 11px;
        font-weight: 700;
        color: #c084fc;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .board-grid {
        display: grid;
        grid-template-columns: repeat(10, minmax(120px, 1fr));
        gap: 6px;
        width: 100%;
        overflow-x: auto;
        padding-bottom: 15px;
        padding-top: 2px;
    }

    .team-column {
        background: transparent !important;
        border: none !important;
        display: flex;
        flex-direction: column;
    }

    .team-header {
        background: url('https://img.freepik.com/premium-vector/abstract-violet-light-arrow-direction-geometric-hexagon-mesh-design-modern-futuristic-background_33869-2361.jpg?semt=ais_test_b&w=740&q=80') center/cover no-repeat !important;
        padding: 6px 4px;
        text-align: center;
        border-radius: 6px 6px 0 0;
        border-bottom: 2px solid #3b1660;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.4);
    }
    
    .team-logo-container {
        width: 38px;
        height: 38px;
        margin: 0 auto 3px auto;
        background: transparent !important;
        border: none !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .fanta-team-logo {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }

    .team-header-name {
        font-size: 9px;
        font-weight: 700;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 1px;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
    }
    .team-header-budget {
        font-size: 13px;
        font-weight: 800;
        color: #facc15;
        margin: 1px 0;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
    }
    .team-header-sub {
        display: flex;
        justify-content: space-between;
        font-size: 7.5px;
        color: #cbd5e1;
        padding: 0 2px;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
    }

    /* Barre dei Ruoli FantaLab */
    .role-bar {
        font-size: 8.5px;
        font-weight: 700;
        padding: 3px 5px;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
        margin-top: 2px;
        margin-bottom: 2px;
    }
    .role-p { 
        background: linear-gradient(135deg, #78350f 0%, #d97706 35%, #b45309 50%, #f59e0b 70%, #92400e 100%); 
        border-top: 1px solid #fcd34d; 
        border-bottom: 1px solid #451a03; 
    }
    .role-d { 
        background: linear-gradient(135deg, #14532d 0%, #22c55e 35%, #15803d 50%, #4ade80 70%, #166534 100%); 
        border-top: 1px solid #86efac; 
        border-bottom: 1px solid #052e16; 
    }
    .role-c { 
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 35%, #1d4ed8 50%, #60a5fa 70%, #1e40af 100%); 
        border-top: 1px solid #93c5fd; 
        border-bottom: 1px solid #172554; 
    }
    .role-a { 
        background: linear-gradient(135deg, #881337 0%, #f43f5e 35%, #be123c 50%, #fda4af 70%, #9f1239 100%); 
        border-top: 1px solid #fecdd3; 
        border-bottom: 1px solid #4c0519; 
    }

    .badge-ruolo-p { background-color: #ea580c; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 11px; }
    .badge-ruolo-d { background-color: #16a34a; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 11px; }
    .badge-ruolo-c { background-color: #2563eb; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 11px; }
    .badge-ruolo-a { background-color: #e11d48; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 11px; }

    .player-preview-box {
        background: #170d30;
        border: 1px solid #321a5c;
        border-radius: 6px;
        padding: 8px 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 6px;
        margin-bottom: 4px;
    }

    .player-cell {
        height: 22px;
        width: 100%;
        background: transparent;
        border: 1px solid rgba(192, 132, 252, 0.2) !important;
        border-radius: 3px !important;
        margin: 2px 0;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 4px;
        font-size: 9.5px;
    }

    .player-cell-filled {
        border: 1px solid rgba(0, 0, 0, 0.5) !important;
        border-radius: 3px !important;
    }

    .player-cell-p { background: linear-gradient(90deg, #2a1205 0%, #ea580c 50%, #7c2d12 100%) !important; }
    .player-cell-d { background: linear-gradient(90deg, #0a1811 0%, #0d381e 50%, #0c1f13 100%) !important; }
    .player-cell-c { background: linear-gradient(90deg, #09131f 0%, #0f2c4a 50%, #0c1a2b 100%) !important; }
    .player-cell-a { background: linear-gradient(90deg, #1c0a10 0%, #441220 50%, #210a12 100%) !important; }

    .player-cell-left {
        display: flex;
        align-items: center;
        gap: 3px;
        overflow: hidden;
        max-width: 88px;
    }

    .player-team-logo {
        width: 12px;
        height: 12px;
        object-fit: contain;
        flex-shrink: 0;
    }

    .player-cell-name {
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-weight: 600;
    }

    .player-cell-right {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        font-weight: 700;
        color: #ffffff !important;
    }

    .deal-box-single {
        background: #150b2c;
        border: 1px solid #28144d;
        border-radius: 6px;
        padding: 10px 6px;
        height: 105px;
        margin-top: 6px;
        margin-bottom: 6px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        text-align: center;
    }
    .deal-rank-title {
        font-size: 9.5px;
        font-weight: 800;
        text-transform: uppercase;
        line-height: 1;
    }
    .deal-player-name {
        font-size: 11px;
        font-weight: 800;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
        line-height: 1.2;
    }
    .deal-logos-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        height: 22px;
    }
    .deal-logo-img {
        width: 22px;
        height: 22px;
        object-fit: contain;
    }
    .deal-arrow {
        color: #c084fc;
        font-size: 11px;
        font-weight: bold;
    }
    .deal-price-info {
        font-size: 9px;
        font-weight: 700;
        line-height: 1;
    }

    .ranking-row {
        background: #140a2b;
        border: 1px solid #251249;
        border-radius: 5px;
        padding: 6px 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 4px;
        font-size: 11px;
    }
    .ranking-info {
        font-weight: 600;
        color: #ffffff;
    }
    .ranking-sub {
        font-size: 9.5px;
        color: #a78bfa;
        margin-left: 4px;
    }
    .ranking-badge {
        background: #0d061c;
        color: #facc15;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid #2a1452;
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


# ==============================================================================
# 1. PANNELLO SUPERIORE A WIDGET SEPARATI
# ==============================================================================
@st.fragment
def render_control_panel():
    st.session_state.acquisti = load_saved_acquisti()

    col_gestione, col_classifica = st.columns([1.3, 1])

    giocatori_presi = {a["Giocatore"] for a in st.session_state.acquisti}
    df_disponibili = df_listone[~df_listone["Giocatore"].isin(giocatori_presi)]

    with col_gestione:
        # WIDGET 1: AGGIUNGI CALCIATORE
        with st.container(border=True):
            st.markdown('<div class="card-title">➕ AGGIUNGI / ASSEGNA CALCIATORE</div>', unsafe_allow_html=True)

            col_f_ruolo, col_f_sa = st.columns(2)
            
            with col_f_ruolo:
                ruoli_scelti = st.multiselect(
                    "Filtra per Ruoli",
                    options=["P", "D", "C", "A"],
                    default=[],
                    placeholder="Tutti i ruoli",
                    key="sel_filtro_ruolo"
                )
            
            with col_f_sa:
                squadre_sa_list = sorted(df_disponibili["Squadra_SerieA"].dropna().unique().tolist()) if "Squadra_SerieA" in df_disponibili.columns else []
                squadre_sa_scelte = st.multiselect(
                    "Filtra per Squadre Serie A",
                    options=squadre_sa_list,
                    default=[],
                    placeholder="Tutte le squadre",
                    key="sel_filtro_sa"
                )

            df_filtrati = df_disponibili.copy()
            if ruoli_scelti:
                df_filtrati = df_filtrati[df_filtrati["Ruolo"].isin(ruoli_scelti)]
            if squadre_sa_scelte:
                df_filtrati = df_filtrati[df_filtrati["Squadra_SerieA"].isin(squadre_sa_scelte)]

            col_g, col_sq, col_costo, col_btn = st.columns([2.5, 2, 1, 1.2])

            with col_g:
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
                    
                    st.session_state.search_version += 1
                    st.rerun()

            if giocatore_selezionato and not btn_conferma:
                info_g = df_listone[df_listone["Giocatore"] == giocatore_selezionato].iloc[0]
                squadra_serie_a = str(info_g.get("Squadra_SerieA", info_g.get("Squadra", ""))).strip()
                ruolo_g = info_g["Ruolo"]
                badge_class = f"badge-ruolo-{ruolo_g.lower()}"
                
                logo_b64 = get_logo_base64_cached(squadra_serie_a)
                logo_html = f'<img src="{logo_b64}" style="width:24px; height:24px; object-fit:contain; vertical-align:middle;" />' if logo_b64 else ""
                
                st.markdown(
                    f'<div class="player-preview-box">'
                    f'{logo_html}'
                    f'<span style="font-size: 13px; font-weight: 700; color: #ffffff;">{info_g["Giocatore"]}</span>'
                    f'<span class="{badge_class}">{ruolo_g}</span>'
                    f'<span style="margin-left: auto; font-size: 11px; color: #facc15; font-weight: 700;">Prezzo Medio: {int(info_g["Prezzo_Numerico"])} FM</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        # WIDGET 2: RIMUOVI / SVINCOLA CALCIATORE
        with st.container(border=True):
            st.markdown('<div class="card-title">🗑️ SVINCOLA / RIMUOVI CALCIATORE</div>', unsafe_allow_html=True)

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

        # CALCOLO TOP 3 AFFARI
        acquisti_validi = [
            a for a in st.session_state.acquisti 
            if a.get("Prezzo_Medio", 0) > 0 and a["Costo"] != a["Prezzo_Medio"]
        ]

        migliori_affari = sorted(
            [a for a in acquisti_validi if (a["Prezzo_Medio"] - a["Costo"]) > 0],
            key=lambda x: (x["Prezzo_Medio"] - x["Costo"]),
            reverse=True
        )[:3]

        peggiori_affari = sorted(
            [a for a in acquisti_validi if (a["Prezzo_Medio"] - a["Costo"]) < 0],
            key=lambda x: (x["Prezzo_Medio"] - x["Costo"])
        )[:3]

        def render_deal_box(deal_data, label_rank, price_color):
            if not deal_data:
                return f'''
                <div class="deal-box-single">
                    <div class="deal-rank-title" style="color:{price_color};">{label_rank}</div>
                    <div style="font-size:10px; color:#64748b;">- N/D -</div>
                    <div class="deal-price-info" style="color:transparent;">.</div>
                </div>
                '''
            
            g_nome = deal_data["Giocatore"]
            ruolo = deal_data.get("Ruolo", "")
            costo = deal_data["Costo"]
            p_medio = deal_data["Prezzo_Medio"]

            sq_sa = deal_data.get("Squadra_SerieA", "")
            logo_sa_b64 = get_logo_base64_cached(sq_sa)
            logo_sa_html = f'<img src="{logo_sa_b64}" class="deal-logo-img" alt="{sq_sa}">' if logo_sa_b64 else '⚽'

            sq_fanta_full = deal_data.get("Squadra_Fanta", "")
            nome_fanta = sq_fanta_full.split(" - ")[0]
            codice_fanta = MAPPA_NOME_CODICE_FANTA.get(nome_fanta, nome_fanta)
            logo_fanta_b64 = get_logo_base64_cached(codice_fanta)
            logo_fanta_html = f'<img src="{logo_fanta_b64}" class="deal-logo-img" alt="{codice_fanta}">' if logo_fanta_b64 else f'<strong style="font-size:9px; color:#f8fafc;">{codice_fanta}</strong>'

            ruolo_str = f" ({ruolo})" if ruolo else ""

            return f'''
            <div class="deal-box-single">
                <div class="deal-rank-title" style="color:{price_color};">{label_rank}</div>
                <div class="deal-player-name">{g_nome}<span style="color:#94a3b8; font-weight:600;">{ruolo_str}</span></div>
                <div class="deal-logos-row">{logo_sa_html} <span class="deal-arrow">➜</span> {logo_fanta_html}</div>
                <div class="deal-price-info" style="color:{price_color};">Pagato: {costo} FM <span style="color:#94a3b8; font-size:8px; font-weight:normal;">(Medio: {p_medio})</span></div>
            </div>
            '''

        # WIDGET 3 & 4: TOP 3 MIGLIORI E PEGGIORI AFFARI
        col_top_best, col_top_worst = st.columns(2)

        with col_top_best:
            with st.container(border=True):
                st.markdown('<div class="card-title" style="color: #22c55e;">🌟 TOP 3 MIGLIORI AFFARI</div>', unsafe_allow_html=True)
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    item_1 = migliori_affari[0] if len(migliori_affari) > 0 else None
                    st.markdown(render_deal_box(item_1, "🥇 1° MIGLIORE", "#22c55e"), unsafe_allow_html=True)
                with col_m2:
                    item_2 = migliori_affari[1] if len(migliori_affari) > 1 else None
                    st.markdown(render_deal_box(item_2, "🥈 2° MIGLIORE", "#22c55e"), unsafe_allow_html=True)
                with col_m3:
                    item_3 = migliori_affari[2] if len(migliori_affari) > 2 else None
                    st.markdown(render_deal_box(item_3, "🥉 3° MIGLIORE", "#22c55e"), unsafe_allow_html=True)

        with col_top_worst:
            with st.container(border=True):
                st.markdown('<div class="card-title" style="color: #ef4444;">⚠️ TOP 3 PEGGIORI AFFARI</div>', unsafe_allow_html=True)
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    item_p1 = peggiori_affari[0] if len(peggiori_affari) > 0 else None
                    st.markdown(render_deal_box(item_p1, "🥇 1° PEGGIORE", "#ef4444"), unsafe_allow_html=True)
                with col_p2:
                    item_p2 = peggiori_affari[1] if len(peggiori_affari) > 1 else None
                    st.markdown(render_deal_box(item_p2, "🥈 2° PEGGIORE", "#ef4444"), unsafe_allow_html=True)
                with col_p3:
                    item_p3 = peggiori_affari[2] if len(peggiori_affari) > 2 else None
                    st.markdown(render_deal_box(item_p3, "🥉 3° PEGGIORE", "#ef4444"), unsafe_allow_html=True)

    # Colonna Destra: Widget Classifica Crediti
    with col_classifica:
        st.markdown('<div class="classifica-container">', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="card-title">🏆 CLASSIFICA CREDITI</div>', unsafe_allow_html=True)

            dati_classifica = []
            for s_info in SQUADRE_INFO:
                sq_full = f"{s_info['nome']} - {s_info['mister']}"
                rimasti, tot_giocatori, max_off, acquisti_sq = get_squadra_stats(sq_full)
                dati_classifica.append({
                    "Squadra": s_info['nome'],
                    "Mister": s_info['mister'],
                    "Crediti": rimasti,
                    "Rosa": f"{tot_giocatori}/{TOTALE_SLOTS}"
                })
            
            dati_classifica = sorted(dati_classifica, key=lambda x: x["Crediti"], reverse=True)

            for idx, item in enumerate(dati_classifica, start=1):
                st.markdown(
                    f'<div class="ranking-row">'
                    f'<div>'
                    f'<span style="font-weight: 700; color: #c084fc; margin-right: 6px;">{idx}.</span>'
                    f'<span class="ranking-info">{item["Squadra"]}</span>'
                    f'<span class="ranking-sub">({item["Mister"]})</span>'
                    f'</div>'
                    f'<div style="display: flex; align-items: center; gap: 8px;">'
                    f'<span style="font-size: 9.5px; color: #94a3b8;">{item["Rosa"]}</span>'
                    f'<span class="ranking-badge">🟡 {item["Crediti"]}</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        st.markdown('</div>', unsafe_allow_html=True)

if not is_tv_mode:
    render_control_panel()

# ==============================================================================
# 2. TABELLONE FRAGMENT
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
                    cell_role_class = f"player-cell-{ruolo.lower()}"

                    col_content.append(
                        f'<div class="player-cell player-cell-filled {cell_role_class}">'
                        f'<div class="player-cell-left">'
                        f'{logo_html}'
                        f'<span class="player-cell-name">{nome_g}</span>'
                        f'</div>'
                        f'<div class="player-cell-right">'
                        f'<span class="player-cell-cost">{costo}</span>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    col_content.append('<div class="player-cell"><span class="player-cell-name" style="color:#2a1752;">-</span></div>')

        col_content.append("</div>")
        cols_html.append("".join(col_content))

    st.markdown(f'<div class="board-grid">{"".join(cols_html)}</div>', unsafe_allow_html=True)


render_board_fragment()