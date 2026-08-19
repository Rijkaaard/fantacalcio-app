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


# Funzione per impostare la squadra ed il ruolo selezionati dal click
def imposta_target(squadra, ruolo):
    st.session_state.target_squadra = squadra
    st.session_state.target_ruolo = ruolo


# --- SIDEBAR (PANNELLO INSERIMENTO) ---
st.sidebar.title("🔨 Assegna Giocatore")

# Calcola i giocatori già presi per escluderli
giocatori_presi = [a["Giocatore"] for a in st.session_state.acquisti]
df_disponibili = df_listone[~df_listone["Giocatore"].isin(giocatori_presi)]

# Filtro automatico per il ruolo selezionato cliccando sulla tabella
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


# --- AREA PRINCIPALE (TABELLONI INTERATTIVI) ---
st.title("⚽ Tabellone Asta Fantacalcio")


def render_squadra_table(nome_squadra):
    acquisti_sq = [
        a
        for a in st.session_state.acquisti
        if a["Squadra_Fanta"] == nome_squadra
    ]

    # Header Tabella
    st.markdown(
        f"""
        <div style="background-color: #2d2d2d; color: white; text-align: center; font-weight: bold; padding: 6px; border: 1px solid #444; border-bottom: none; text-transform: uppercase;">
            {nome_squadra}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Intestazione colonne
    c_r, c_n, c_c, c_d = st.columns([0.15, 0.45, 0.20, 0.20])
    c_r.markdown("**Ruolo**")
    c_n.markdown("**Nome**")
    c_c.markdown("**Costo**")
    c_d.markdown("**Diff.**")

    # Generazione righe slot per ruolo
    for ruolo, num_slots in SLOTS.items():
        giocatori_ruolo = [a for a in acquisti_sq if a["Ruolo"] == ruolo]

        for i in range(num_slots):
            col_ruolo, col_nome, col_costo, col_diff = st.columns(
                [0.15, 0.45, 0.20, 0.20]
            )

            col_ruolo.markdown(f"**{ruolo}**")

            if i < len(giocatori_ruolo):
                g = giocatori_ruolo[i]
                col_nome.write(g["Giocatore"])
                col_costo.write(str(g["Costo"]))

                diff = g["Costo"] - g["Prezzo_Medio"]
                if diff > 0:
                    col_diff.markdown(f":red[**+{diff}**]")
                elif diff < 0:
                    col_diff.markdown(f":green[**{diff}**]")
                else:
                    col_diff.write("0")
            else:
                # Pulsante per selezionare lo slot libero
                col_nome.button(
                    "➕ Seleziona",
                    key=f"btn_{nome_squadra}_{ruolo}_{i}",
                    on_click=imposta_target,
                    args=(nome_squadra, ruolo),
                )
                col_costo.write("-")
                col_diff.write("-")


# Disposizione tabelle affiancate a due a due
for i in range(0, 10, 2):
    c1, c2 = st.columns(2)

    with c1:
        render_squadra_table(FANTASQUADRE[i])
        st.divider()

    with c2:
        if i + 1 < 10:
            render_squadra_table(FANTASQUADRE[i + 1])
            st.divider()