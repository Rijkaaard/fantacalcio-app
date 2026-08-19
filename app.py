import os
import pandas as pd
import streamlit as st

# ==============================================================================
# ⚙️ CONFIGURAZIONE SQUADRE ED ELEMENTI
# ==============================================================================
FANTASQUADRE = [f"SQUADRA {i+1}" for i in range(10)]

# Slot fissi per ruolo (Totale 25 righe per tabella)
SLOTS = {"P": 3, "D": 8, "C": 8, "A": 6}

st.set_page_config(
    page_title="Tabellone Asta Fantacalcio",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Caricamento e preparazione del Listone
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

# Memoria dell'applicazione
if "acquisti" not in st.session_state:
    st.session_state.acquisti = []

if "target_squadra" not in st.session_state:
    st.session_state.target_squadra = FANTASQUADRE[0]

if "target_ruolo" not in st.session_state:
    st.session_state.target_ruolo = "TUTTI"


def imposta_target(squadra, ruolo):
    st.session_state.target_squadra = squadra
    st.session_state.target_ruolo = ruolo


# --- SIDEBAR (PANNELLO INSERIMENTO A SINISTRA) ---
st.sidebar.title("🔨 Assegna Giocatore")

# Calcola i giocatori già presi per escluderli
giocatori_presi = [a["Giocatore"] for a in st.session_state.acquisti]
df_disponibili = df_listone[~df_listone["Giocatore"].isin(giocatori_presi)]

# Filtro automatico per il ruolo selezionato
ruolo_selezionato = st.sidebar.radio(
    "Filtro Ruolo:",
    options=["TUTTI", "P", "D", "C", "A"],
    index=["TUTTI", "P", "D", "C", "A"].index(st.session_state.target_ruolo),
    horizontal=True,
)

if ruolo_selezionato != "TUTTI":
    df_filtrati = df_disponibili[
        df_disponibili["Ruolo"] == ruolo_selezionato
    ]
else:
    df_filtrati = df_disponibili

# Ricerca del giocatore
giocatore_selezionato = st.sidebar.selectbox(
    "Cerca Nome Giocatore:",
    options=sorted(df_filtrati["Giocatore"].tolist()),
    index=None,
    placeholder=f"Scrivi un nome ({ruolo_selezionato})...",
)

squadra_dest = st.sidebar.selectbox(
    "Fantasquadra:",
    options=FANTASQUADRE,
    index=FANTASQUADRE.index(st.session_state.target_squadra),
)

if giocatore_selezionato:
    info_g = df_filtrati[
        df_filtrati["Giocatore"] == giocatore_selezionato
    ].iloc[0]

    st.sidebar.info(
        f"**Ruolo:** {info_g['Ruolo']} | **Squadra:** {info_g['Squadra']}\n\n"
        f"**Prezzo Medio (FM):** {int(info_g['Prezzo_Numerico'])}"
    )

    costo_asta = st.sidebar.number_input(
        "Costo d'acquisto:", min_value=1, value=1, step=1
    )

    ruolo_g = info_g["Ruolo"]
    presi_ruolo = len(
        [
            a
            for a in st.session_state.acquisti
            if a["Squadra_Fanta"] == squadra_dest and a["Ruolo"] == ruolo_g
        ]
    )
    max_slot = SLOTS[ruolo_g]

    if presi_ruolo >= max_slot:
        st.sidebar.error(
            f"❌ {squadra_dest} ha già coperto i {max_slot} slot per il ruolo {ruolo_g}!"
        )
    else:
        if st.sidebar.button("✅ Inserisci in Rosa", use_container_width=True):
            st.session_state.acquisti.append(
                {
                    "Giocatore": info_g["Giocatore"],
                    "Ruolo": info_g["Ruolo"],
                    "Costo": int(costo_asta),
                    "Prezzo_Medio": int(info_g["Prezzo_Numerico"]),
                    "Squadra_Fanta": squadra_dest,
                }
            )
            st.rerun()

st.sidebar.divider()
if st.session_state.acquisti:
    if st.sidebar.button("↩️ Annulla Ultimo Inserimento"):
        st.session_state.acquisti.pop()
        st.rerun()


# --- AREA PRINCIPALE (TABELLONI STILE EXCEL INTERATTIVI) ---
st.title("⚽ Tabellone Asta Fantacalcio")

# Stile CSS per mantenere la tabella uguale al formato Excel precedente
st.markdown(
    """
    <style>
    div[data-testid="column"] button {
        background: transparent !important;
        border: none !important;
        color: #888888 !important;
        text-align: left !important;
        padding: 0px 4px !important;
        height: auto !important;
        min-height: 24px !important;
        font-size: 13px !important;
        box-shadow: none !important;
    }
    div[data-testid="column"] button:hover {
        color: #4da6ff !important;
        background-color: #2b2b2b !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def render_squadra_table(nome_squadra):
    acquisti_sq = [
        a
        for a in st.session_state.acquisti
        if a["Squadra_Fanta"] == nome_squadra
    ]

    # Header Tabella (Titolo Squadra)
    st.markdown(
        f"""
        <div style="background-color: #2d2d2d; color: #ffffff; text-align: center; font-weight: bold; padding: 6px; border: 1px solid #444; border-bottom: 1px solid #444; text-transform: uppercase; font-size: 14px; letter-spacing: 1px;">
            {nome_squadra}
        </div>
        <div style="display: flex; background-color: #222222; border: 1px solid #444; border-top: none; border-bottom: 1px solid #333; font-size: 12px; color: #bbb; font-weight: bold; padding: 4px 0;">
            <div style="width: 15%; padding-left: 6px; border-right: 1px solid #333;">Ruolo</div>
            <div style="width: 45%; padding-left: 6px; border-right: 1px solid #333;">Nome</div>
            <div style="width: 20%; text-align: right; padding-right: 6px; border-right: 1px solid #333;">Costo</div>
            <div style="width: 20%; text-align: right; padding-right: 6px;">Differenza</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Righe della tabella
    for ruolo, num_slots in SLOTS.items():
        giocatori_ruolo = [a for a in acquisti_sq if a["Ruolo"] == ruolo]

        for i in range(num_slots):
            c_r, c_n, c_c, c_d = st.columns([0.15, 0.45, 0.20, 0.20])

            # Ruolo
            c_r.markdown(
                f"<div style='font-size:13px; font-weight:bold; padding:2px 0 0 6px;'>{ruolo}</div>",
                unsafe_allow_html=True,
            )

            if i < len(giocatori_ruolo):
                g = giocatori_ruolo[i]

                # Nome Giocatore
                c_n.markdown(
                    f"<div style='font-size:13px; padding:2px 0 0 6px;'>{g['Giocatore']}</div>",
                    unsafe_allow_html=True,
                )

                # Costo
                c_c.markdown(
                    f"<div style='font-size:13px; text-align:right; padding:2px 6px 0 0;'>{g['Costo']}</div>",
                    unsafe_allow_html=True,
                )

                # Differenza (+X rosso / -X verde / 0 grigio)
                diff = g["Costo"] - g["Prezzo_Medio"]
                if diff > 0:
                    diff_html = f"<span style='color: #ff4d4d; font-weight: bold;'>+{diff}</span>"
                elif diff < 0:
                    diff_html = f"<span style='color: #2eb82e; font-weight: bold;'>{diff}</span>"
                else:
                    diff_html = "<span style='color: #aaa;'>0</span>"

                c_d.markdown(
                    f"<div style='font-size:13px; text-align:right; padding:2px 6px 0 0;'>{diff_html}</div>",
                    unsafe_allow_html=True,
                )

            else:
                # Slot Libero: Bottone trasparente che simula la riga vuota della tabella
                c_n.button(
                    "--- (Libero)",
                    key=f"btn_{nome_squadra}_{ruolo}_{i}",
                    on_click=imposta_target,
                    args=(nome_squadra, ruolo),
                )
                c_c.markdown(
                    "<div style='font-size:13px; text-align:right; color:#555; padding:2px 6px 0 0;'>-</div>",
                    unsafe_allow_html=True,
                )
                c_d.markdown(
                    "<div style='font-size:13px; text-align:right; color:#555; padding:2px 6px 0 0;'>-</div>",
                    unsafe_allow_html=True,
                )

            # Bordo separatore riga
            st.markdown(
                "<div style='border-bottom: 1px solid #2a2a2a; margin-bottom: 1px;'></div>",
                unsafe_allow_html=True,
            )


# Disposizione a due tabelle affiancate per riga
for i in range(0, 10, 2):
    col1, col2 = st.columns(2)

    with col1:
        render_squadra_table(FANTASQUADRE[i])
        st.write("")

    with col2:
        if i + 1 < 10:
            render_squadra_table(FANTASQUADRE[i + 1])
            st.write("")