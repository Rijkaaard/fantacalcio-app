import os
import pandas as pd
import streamlit as st

# 1. Configurazione della pagina
st.set_page_config(
    page_title="Fantacalcio - Asta & Listone",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. Caricamento e pulizia dati
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None

    # Tenta prima con la virgola, poi con il punto e virgola se fallisce
    try:
        df = pd.read_csv(file_path)
        if len(df.columns) == 1 and ";" in df.columns[0]:
            df = pd.read_csv(file_path, sep=";")
    except Exception:
        df = pd.read_csv(file_path, sep=";")

    # Rimuove spazi vuoti invisibili prima e dopo i nomi delle colonne
    df.columns = df.columns.str.strip()

    # Cerca la colonna del prezzo medio (gestisce differenze di maiuscole/spazi)
    colonna_prezzo = None
    for col in df.columns:
        if col.lower().replace(" ", "").replace("_", "") in [
            "prezzomedio",
            "prezzo",
            "quotazione",
        ]:
            colonna_prezzo = col
            break

    if colonna_prezzo is None:
        st.error(
            f"❌ Impossibile trovare la colonna del prezzo! Le colonne trovate nel tuo file CSV sono: `{list(df.columns)}`"
        )
        st.stop()

    # Rinomina la colonna trovata per uniformarla
    df = df.rename(columns={colonna_prezzo: "Prezzo Medio"})

    # Convertiamo i valori in numeri
    df["Prezzo_Numerico"] = pd.to_numeric(
        df["Prezzo Medio"], errors="coerce"
    ).fillna(0)

    return df

# Nome del file CSV nella stessa cartella
CSV_FILENAME = "fantalab_listone.csv"
df = load_data(CSV_FILENAME)

# Se il file non esiste, mostra un messaggio di errore
if df is None:
    st.error(
        f"⚠️ File `{CSV_FILENAME}` non trovato! "
        "Assicurati di aver salvato la tabella in un file `.csv` con questo nome nella stessa cartella di `app.py`."
    )
    st.stop()

# 3. Titolo Principale
st.title("⚽ Fantacalcio: Dashboard Listone & Asta")
st.markdown("Analizza i prezzi medi, filtra i giocatori e pianifica la tua rosa.")

# 4. Sidebar - Filtri
st.sidebar.header("🔍 Filtri Giocatori")

# Filtro Ricerca Testuale
search_name = st.sidebar.text_input(
    "Cerca Giocatore", placeholder="Es. Dimarco..."
)

# Filtro Ruolo
ruoli_disponibili = sorted(df["Ruolo"].unique().tolist())
selected_ruoli = st.sidebar.multiselect(
    "Ruolo",
    options=ruoli_disponibili,
    default=ruoli_disponibili,
    help="Seleziona uno o più ruoli (P, D, C, A)",
)

# Filtro Squadra
squadre_disponibili = sorted(df["Squadra"].unique().tolist())
selected_squadre = st.sidebar.multiselect(
    "Squadra", options=squadre_disponibili, default=squadre_disponibili
)

# Filtro Prezzo Medio (Slider)
max_price = int(df["Prezzo_Numerico"].max())
min_price = int(df["Prezzo_Numerico"].min())

price_range = st.sidebar.slider(
    "Range Prezzo Medio",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
)

# 5. Applicazione dei Filtri
df_filtered = df[
    (df["Ruolo"].isin(selected_ruoli))
    & (df["Squadra"].isin(selected_squadre))
    & (df["Prezzo_Numerico"] >= price_range[0])
    & (df["Prezzo_Numerico"] <= price_range[1])
]

if search_name:
    df_filtered = df_filtered[
        df_filtered["Giocatore"].str.contains(search_name, case=False, na=False)
    ]

# 6. Metriche in Evidenza
col1, col2, col3, col4 = st.columns(4)
col1.metric("Giocatori Trovati", len(df_filtered))
col2.metric(
    "Prezzo Medio Max",
    (
        f"{int(df_filtered['Prezzo_Numerico'].max())} cr"
        if not df_filtered.empty
        else "0 cr"
    ),
)
col3.metric(
    "Prezzo Medio Min",
    (
        f"{int(df_filtered['Prezzo_Numerico'].min())} cr"
        if not df_filtered.empty
        else "0 cr"
    ),
)
col4.metric(
    "Media Prezzo della Selezione",
    (
        f"{df_filtered['Prezzo_Numerico'].mean():.1f} cr"
        if not df_filtered.empty
        else "0 cr"
    ),
)

st.divider()

# 7. Layout Principale: Tabella e Calcolatore Rosa
tab1, tab2 = st.tabs(["📋 Listone Completo", "🛒 Calcolatore / Target Asta"])

with tab1:
    st.subheader("Listone Filtrato")

    # Ordinamento predefinito per Prezzo Medio decrescente
    df_display = df_filtered[
        ["Giocatore", "Ruolo", "Squadra", "Prezzo Medio", "Prezzo_Numerico"]
    ].sort_values(by="Prezzo_Numerico", ascending=False)

    # Mostra la tabella ordinabile
    st.dataframe(
        df_display[["Giocatore", "Ruolo", "Squadra", "Prezzo Medio"]],
        use_container_width=True,
        hide_index=True,
        height=500,
    )

    # Pulsante per scaricare i dati filtrati in CSV
    csv_download = df_display[
        ["Giocatore", "Ruolo", "Squadra", "Prezzo Medio"]
    ].to_csv(index=False)
    st.download_button(
        label="📥 Scarica Selezione (CSV)",
        data=csv_download,
        file_name="listone_filtrato.csv",
        mime="text/csv",
    )

with tab2:
    st.subheader("Simulatore Budget Asta")
    st.markdown(
        "Seleziona i calciatori che vorresti acquistare per valutare la spesa stimata totale."
    )

    # Multiselect per selezionare i target
    target_giocatori = st.multiselect(
        "Seleziona Giocatori Target",
        options=sorted(df["Giocatore"].tolist()),
        placeholder="Aggiungi calciatori alla tua lista obiettivi...",
    )

    if target_giocatori:
        df_targets = df[df["Giocatore"].isin(target_giocatori)].copy()
        spesa_totale = df_targets["Prezzo_Numerico"].sum()

        st.markdown(f"### 💰 Spesa Totale Stimata: **{int(spesa_totale)} crediti**")

        st.dataframe(
            df_targets[["Giocatore", "Ruolo", "Squadra", "Prezzo Medio"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nessun giocatore selezionato. Aggiungi qualcuno dal menu sopra!")