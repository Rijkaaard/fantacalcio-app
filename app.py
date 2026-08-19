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
    acquisti_sq = [
        a
        for a in st.session_state.acquisti
        if a["Squadra_Fanta"] == nome_squadra
    ]

    rows = []
    for ruolo, num_slots in SLOTS.items():
        giocatori_ruolo = [a for a in acquisti_sq if a["Ruolo"] == ruolo]

        for i in range(num_slots):
            if i < len(giocatori_ruolo):
                g = giocatori_ruolo[i]
                nome = g["Giocatore"]
                costo = g["Costo"]
                diff = costo - g["Prezzo_Medio"]

                if diff > 0:
                    diff_td = f'<td style="padding: 2px 6px; text-align: right; color: #ff4d4d; font-weight: bold;">+{diff}</td>'
                elif diff < 0:
                    diff_td = f'<td style="padding: 2px 6px; text-align: right; color: #2eb82e; font-weight: bold;">{diff}</td>'
                else:
                    diff_td = '<td style="padding: 2px 6px; text-align: right; color: #aaa;">0</td>'

                costo_txt = str(costo)
            else:
                nome = ""
                costo_txt = ""
                diff_td = '<td style="padding: 2px 6px;"></td>'

            rows.append(
                f'<tr style="border-bottom: 1px solid #333;">'
                f'<td style="padding: 2px 6px; font-weight: bold; width: 12%; border-right: 1px solid #333;">{ruolo}</td>'
                f'<td style="padding: 2px 6px; width: 50%; border-right: 1px solid #333;">{nome}</td>'
                f'<td style="padding: 2px 6px; text-align: right; width: 18%; border-right: 1px solid #333;">{costo_txt}</td>'
                f"{diff_td}"
                f"</tr>"
            )

    table_rows = "".join(rows)

    html = f"""<table style="width:100%; border-collapse: collapse; border: 1px solid #444; font-size: 13px; font-family: sans-serif; background-color: #1a1a1a; color: #ffffff; margin-bottom: 25px;">
<thead>
<tr style="background-color: #2d2d2d; border-bottom: 1px solid #444;">
<th colspan="4" style="padding: 6px; font-size: 14px; text-align: center; text-transform: uppercase; letter-spacing: 1px; color: #ffffff;">{nome_squadra}</th>
</tr>
<tr style="background-color: #222222; border-bottom: 1px solid #444; font-size: 12px; color: #bbb;">
<th style="padding: 4px 6px; text-align: left; border-right: 1px solid #333;">Ruolo</th>
<th style="padding: 4px 6px; text-align: left; border-right: 1px solid #333;">Nome</th>
<th style="padding: 4px 6px; text-align: right; border-right: 1px solid #333;">Costo</th>
<th style="padding: 4px 6px; text-align: right;">Differenza</th>
</tr>
</thead>
<tbody>{table_rows}</tbody>
</table>"""
    return html


# Disposizione delle tabelle a due a due
for i in range(0, 10, 2):
    col1, col2 = st.columns(2)

    with col1:
        st.html(genera_html_tabella(FANTASQUADRE[i]))

    with col2:
        if i + 1 < 10:
            st.html(genera_html_tabella(FANTASQUADRE[i + 1]))