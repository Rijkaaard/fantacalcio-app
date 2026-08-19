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

# Memoria degli acquisti
if "acquisti" not in st.session_state:
    st.session_state.acquisti = []

# --- SIDEBAR (PANNELLO DI INSERIMENTO A SINISTRA) ---
st.sidebar.title("🔨 Assegna Giocatore")

# Calcola i giocatori già presi per escluderli dalla ricerca
giocatori_presi = [a["Giocatore"] for a in st.session_state.acquisti]
df_disponibili = df_listone[~df_listone["Giocatore"].isin(giocatori_presi)]

# Ricerca del giocatore con completamento automatico
giocatore_selezionato = st.sidebar.selectbox(
    "Cerca Nome Giocatore:",
    options=sorted(df_disponibili["Giocatore"].tolist()),
    index=None,
    placeholder="Inizia a scrivere il nome...",
)

if giocatore_selezionato:
    info_g = df_disponibili[
        df_disponibili["Giocatore"] == giocatore_selezionato
    ].iloc[0]

    st.sidebar.info(
        f"**Ruolo:** {info_g['Ruolo']} | **Squadra:** {info_g['Squadra']}\n\n"
        f"**Prezzo Medio (FM):** {int(info_g['Prezzo_Numerico'])}"
    )

    squadra_dest = st.sidebar.selectbox("Fantasquadra:", options=FANTASQUADRE)
    costo_asta = st.sidebar.number_input(
        "Costo d'acquisto:", min_value=1, value=1, step=1
    )

    # Verifica se la squadra ha posto per quel ruolo
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
            f"❌ {squadra_dest} ha già coperto tutti i {max_slot} slot per il ruolo {ruolo_g}!"
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

# --- AREA PRINCIPALE: TABELLONI DELLE 10 SQUADRE ---
st.title("⚽ Tabellone Asta Fantacalcio")


def genera_html_tabella(nome_squadra):
    """Genera la tabella in stile Excel esattamente come richiesto"""
    acquisti_sq = [
        a
        for a in st.session_state.acquisti
        if a["Squadra_Fanta"] == nome_squadra
    ]

    html = f"""
    <table style="width:100%; border-collapse: collapse; border: 1px solid #333; font-family: sans-serif; font-size: 13px; margin-bottom: 25px;">
        <thead>
            <tr style="background-color: #e6e6e6; color: black; font-weight: bold; text-align: center; border-bottom: 1px solid #333;">
                <th colspan="4" style="padding: 6px; font-size: 15px; text-transform: uppercase;">{nome_squadra}</th>
            </tr>
            <tr style="background-color: #f2f2f2; color: black; border-bottom: 1px solid #333; text-align: left;">
                <th style="padding: 4px 8px; width: 15%; border-right: 1px solid #ccc;">Ruolo</th>
                <th style="padding: 4px 8px; width: 45%; border-right: 1px solid #ccc;">Nome</th>
                <th style="padding: 4px 8px; width: 20%; text-align: right; border-right: 1px solid #ccc;">Costo</th>
                <th style="padding: 4px 8px; width: 20%; text-align: right;">Differenza</th>
            </tr>
        </thead>
        <tbody>
    """

    for ruolo, num_slots in SLOTS.items():
        giocatori_ruolo = [a for a in acquisti_sq if a["Ruolo"] == ruolo]

        for i in range(num_slots):
            if i < len(giocatori_ruolo):
                g = giocatori_ruolo[i]
                nome = g["Giocatore"]
                costo = g["Costo"]
                diff = costo - g["Prezzo_Medio"]

                # Formattazione differenza con i colori verde/rosso
                if diff > 0:
                    diff_txt = f"+{diff}"
                    diff_style = "color: red; font-weight: bold;"
                elif diff < 0:
                    diff_txt = f"{diff}"
                    diff_style = "color: green; font-weight: bold;"
                else:
                    diff_txt = "0"
                    diff_style = "color: black;"

                costo_txt = str(costo)
            else:
                nome = ""
                costo_txt = ""
                diff_txt = ""
                diff_style = ""

            html += f"""
            <tr style="border-bottom: 1px solid #e0e0e0;">
                <td style="padding: 3px 8px; font-weight: bold; border-right: 1px solid #ccc;">{ruolo}</td>
                <td style="padding: 3px 8px; border-right: 1px solid #ccc;">{nome}</td>
                <td style="padding: 3px 8px; text-align: right; border-right: 1px solid #ccc;">{costo_txt}</td>
                <td style="padding: 3px 8px; text-align: right; {diff_style}">{diff_txt}</td>
            </tr>
            """

    html += "</tbody></table>"
    return html


# Disposizione delle tabelle a due a due (2 colonne per riga)
for i in range(0, 10, 2):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            genera_html_tabella(FANTASQUADRE[i]), unsafe_allow_html=True
        )

    with col2:
        if i + 1 < 10:
            st.markdown(
                genera_html_tabella(FANTASQUADRE[i + 1]), unsafe_allow_html=True
            )