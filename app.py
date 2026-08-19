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

st.set_page_config(
    page_title="FantaLab - Tabellone Asta",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 🎨 STILE CSS FANTA-LAB DARK NEON (CONTENITORI NATIVI STYLED)
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
        padding-top: 1.2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* Styling del box/contenitore nativo Streamlit */
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

    /* Mini-lista squadre a sinistra */
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

    /* Griglia 10 colonne tabellone */
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

    /* Barre dei ruoli */
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

    /* Celle giocatori */
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
# CARICAMENTO DATI E MEMORIA SESSIONE
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


# Funzione Calcolo Statistiche Squadra
def get_squadra_stats(nome_squadra):
    acquisti = [
        a
        for a in st.session_state.acquisti
        if a["Squadra_Fanta"] == nome_squadra
    ]
    spesi = sum(a["Costo"] for a in acquisti)
    rimasti = BUDGET_INIZIALE - spesi
    tot_giocatori = len(acquisti)
    slot_mancanti = TOTALE_SLOTS - tot_giocatori

    max_offerta = rimasti - (slot_mancanti - 1) if slot_mancanti > 0 else 0
    return rimasti, tot_giocatori, max_offerta, acquisti


# ==============================================================================
# 1. PANNELLO SUPERIORE (PANNELLO SQUADRE E ASSEGNAZIONE)
# ==============================================================================
c_left, c_right = st.columns([1.2, 3])

# Mini-lista squadre a sinistra
with c_left:
    with st.container(border=True):
        st.markdown(
            '<div class="card-title">SQUADRE & BUDGET</div>',
            unsafe_allow_html=True,
        )
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

# Form Inserimento/Assegnazione al centro
with c_right:
    with st.container(border=True):
        st.markdown(
            '<div class="card-title">ASSEGNA GIOCATORE</div>',
            unsafe_allow_html=True,
        )

        ruolo_selezionato = st.radio(
            "Filtra Ruolo",
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
            btn_conferma = st.button(
                "✅ CONFERMA", use_container_width=True, type="primary"
            )

        # Validazione e Assegnazione
        if giocatore_selezionato and btn_conferma:
            info_g = df_filtrati[
                df_filtrati["Giocatore"] == giocatore_selezionato
            ].iloc[0]
            ruolo_g = info_g["Ruolo"]

            rimasti, tot_giocatori, max_offerta, acquisti_sq = (
                get_squadra_stats(sq_dest)
            )
            giocatori_ruolo = len(
                [a for a in acquisti_sq if a["Ruolo"] == ruolo_g]
            )
            max_slot_ruolo = SLOTS[ruolo_g]

            # Controlli bloccanti
            if giocatori_ruolo >= max_slot_ruolo:
                st.error(
                    f"❌ **{sq_dest.split(' - ')[0]}** ha già completato lo slot per il ruolo **{ruolo_g}** ({max_slot_ruolo}/{max_slot_ruolo})!"
                )
            elif costo_asta > max_offerta:
                st.error(
                    f"❌ Offerta troppo alta per **{sq_dest.split(' - ')[0]}**! Offerta Max consentita: **{max_offerta} FM** (Budget rimasto: {rimasti} FM)."
                )
            else:
                st.session_state.acquisti.append(
                    {
                        "Giocatore": info_g["Giocatore"],
                        "Ruolo": info_g["Ruolo"],
                        "Costo": int(costo_asta),
                        "Prezzo_Medio": int(info_g["Prezzo_Numerico"]),
                        "Squadra_Fanta": sq_dest,
                    }
                )
                st.success(
                    f"✅ **{info_g['Giocatore']}** assegnato a **{sq_dest.split(' - ')[0]}** per **{costo_asta} FM**!"
                )
                st.rerun()

        # Informazioni Calciatore Selezionato
        if giocatore_selezionato:
            info_g = df_filtrati[
                df_filtrati["Giocatore"] == giocatore_selezionato
            ].iloc[0]
            st.info(
                f"**Ruolo:** {info_g['Ruolo']} | **Squadra Serie A:** {info_g['Squadra']} | **Prezzo Medio (FM):** {int(info_g['Prezzo_Numerico'])}"
            )


# ==============================================================================
# 2. TABELLONE 10 COLONNE ORIZZONTALI (ROSE SQUADRE)
# ==============================================================================
def render_board():
    cols_html = []

    for sq in FANTASQUADRE:
        rim, tot, max_off, acquisti_sq = get_squadra_stats(sq)
        nome_team = sq.split(" - ")[0]

        col_content = [
            f"""
        <div class="team-column">
            <div class="team-header">
                <div class="team-header-name">{nome_team}</div>
                <div class="team-header-budget">🟡 {rim}</div>
                <div class="team-header-sub">
                    <span>MAX: {max_off if max_off > 0 else 0}</span>
                    <span>{tot}/25</span>
                </div>
            </div>
        """
        ]

        # Genera sezioni per Ruoli (P, D, C, A)
        for ruolo, num_slots in SLOTS.items():
            role_css = f"role-{ruolo.lower()}"
            giocatori_r = [a for a in acquisti_sq if a["Ruolo"] == ruolo]

            # Calcolo percentuale del budget iniziale (500) speso per questo reparto
            speso_ruolo = sum(g["Costo"] for g in giocatori_r)
            pct_budget = round((speso_ruolo / BUDGET_INIZIALE) * 100, 1)

            pct_str = (
                f"{int(pct_budget)}%"
                if pct_budget.is_integer()
                else f"{pct_budget}%"
            )

            col_content.append(
                f'<div class="role-bar {role_css}"><span>{ruolo}</span><span>{pct_str}</span></div>'
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
            const inputField = doc.querySelector('input[placeholder="🔍 Cerca calciatore..."]');
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