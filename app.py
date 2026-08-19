import os
import pandas as pd
import streamlit as st

# ==============================================================================
# ⚙️ CONFIGURAZIONE PER 10 SQUADRE E SLOT ROSA
# ==============================================================================
BUDGET_INIZIALE = 500

# Personalizza qui i nomi dei 10 partecipanti
FANTASQUADRE = [
    "Squadra 1",
    "Squadra 2",
    "Squadra 3",
    "Squadra 4",
    "Squadra 5",
    "Squadra 6",
    "Squadra 7",
    "Squadra 8",
    "Squadra 9",
    "Squadra 10",
]

# Definizione slot per ruolo (Totale 25 giocatori)
SLOTS = {"P": 3, "D": 8, "C": 8, "A": 6}
# ==============================================================================

st.set_page_config(
    page_title="Asta Fantacalcio - 10 Squadre",
    page_icon="⚽",
    layout="wide",
)


# Caricamento e pulizia dati
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
    st.error("⚠️ File `fantalab_listone.csv` non trovato nella cartella!")
    st.stop()

# Memoria dell'Asta
if "acquisti" not in st.session_state:
    st.session_state.acquisti = []

if st.session_state.acquisti:
    df_acquisti = pd.DataFrame(st.session_state.acquisti)
else:
    df_acquisti = pd.DataFrame(
        columns=[
            "Giocatore",
            "Ruolo",
            "Squadra_SerieA",
            "Prezzo_Asta",
            "Squadra_Fanta",
        ]
    )

st.title("⚽ Asta Live Fantacalcio - 10 Partecipanti")

tab_asta, tab_rose, tab_listone = st.tabs(
    ["🔨 Assegna Giocatore", "📊 10 Rose & Crediti", "📋 Listone Completo"]
)

# --- TAB 1: ASSEGNAZIONE GIOCATORI ---
with tab_asta:
    giocatori_presi = df_acquisti["Giocatore"].tolist()
    df_liberi = df_listone[~df_listone["Giocatore"].isin(giocatori_presi)]

    st.subheader("Chiamata Calciatore")
    col_search, col_info = st.columns([2, 1])

    with col_search:
        giocatore_sel = st.selectbox(
            "Cerca giocatore:",
            options=sorted(df_liberi["Giocatore"].tolist()),
            index=None,
            placeholder="Scrivi il nome del calciatore...",
        )

    if giocatore_sel:
        info_g = df_liberi[df_liberi["Giocatore"] == giocatore_sel].iloc[0]

        with col_info:
            st.metric(
                label=f"{info_g['Ruolo']} - {info_g['Squadra']}",
                value=f"FM: {info_g['Prezzo Medio']} cr",
            )

        st.divider()
        c_team, c_price, c_btn = st.columns([2, 1, 1])

        with c_team:
            squadra_dest = st.selectbox(
                "Acquistato da:", options=FANTASQUADRE
            )

        with c_price:
            prezzo_acquisto = st.number_input(
                "Prezzo d'Asta (crediti):", min_value=1, value=1, step=1
            )

        with c_btn:
            st.write("")
            st.write("")

            # Controllo se la squadra ha già riempito lo slot per quel ruolo
            ruolo_g = info_g["Ruolo"]
            attuali_ruolo = len(
                df_acquisti[
                    (df_acquisti["Squadra_Fanta"] == squadra_dest)
                    & (df_acquisti["Ruolo"] == ruolo_g)
                ]
            )
            max_ruolo = SLOTS.get(ruolo_g, 0)

            if attuali_ruolo >= max_ruolo:
                st.error(
                    f"⚠️ {squadra_dest} ha già completato i {max_ruolo} slot per il ruolo {ruolo_g}!"
                )
            else:
                if st.button("✅ Confirm Acquisto", use_container_width=True):
                    st.session_state.acquisti.append(
                        {
                            "Giocatore": info_g["Giocatore"],
                            "Ruolo": info_g["Ruolo"],
                            "Squadra_SerieA": info_g["Squadra"],
                            "Prezzo_Asta": int(prezzo_acquisto),
                            "Squadra_Fanta": squadra_dest,
                        }
                    )
                    st.success(
                        f"**{info_g['Giocatore']}** a **{squadra_dest}** per **{prezzo_acquisto} cr**"
                    )
                    st.rerun()

    st.divider()
    st.subheader("📜 Ultimi Acquisti Effettuati")
    if not df_acquisti.empty:
        st.dataframe(
            df_acquisti[
                [
                    "Giocatore",
                    "Ruolo",
                    "Squadra_SerieA",
                    "Squadra_Fanta",
                    "Prezzo_Asta",
                ]
            ].iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )

        if st.button("↩️ Annulla Ultimo Acquisto"):
            st.session_state.acquisti.pop()
            st.rerun()
    else:
        st.info("Nessun giocatore assegnato.")


# --- TAB 2: TABELLE DELLE 10 ROSE ---
def genera_struttura_rosa(df_sq):
    """Genera una tabella fisso da 25 righe con slot coperti o liberi"""
    righe = []
    for ruolo, num_max in SLOTS.items():
        presi = df_sq[df_sq["Ruolo"] == ruolo].to_dict("records")
        for i in range(num_max):
            if i < len(presi):
                righe.append(
                    {
                        "Slot": f"{ruolo} #{i+1}",
                        "Giocatore": presi[i]["Giocatore"],
                        "Club Serie A": presi[i]["Squadra_SerieA"],
                        "Costo": f"{presi[i]['Prezzo_Asta']} cr",
                    }
                )
            else:
                righe.append(
                    {
                        "Slot": f"{ruolo} #{i+1}",
                        "Giocatore": "--- (Libero) ---",
                        "Club Serie A": "-",
                        "Costo": "-",
                    }
                )
    return pd.DataFrame(righe)


with tab_rose:
    st.subheader("📊 Panoramica Crediti & Slot")

    riepilogo = []
    for sq in FANTASQUADRE:
        df_sq = df_acquisti[df_acquisti["Squadra_Fanta"] == sq]
        speso = df_sq["Prezzo_Asta"].sum() if not df_sq.empty else 0
        rimanente = BUDGET_INIZIALE - speso

        n_p = len(df_sq[df_sq["Ruolo"] == "P"]) if not df_sq.empty else 0
        n_d = len(df_sq[df_sq["Ruolo"] == "D"]) if not df_sq.empty else 0
        n_c = len(df_sq[df_sq["Ruolo"] == "C"]) if not df_sq.empty else 0
        n_a = len(df_sq[df_sq["Ruolo"] == "A"]) if not df_sq.empty else 0

        riepilogo.append(
            {
                "Fantasquadra": sq,
                "Crediti Rimanenti": f"{rimanente} cr",
                "Spesi": f"{speso} cr",
                "Slot Totali": f"{len(df_sq)}/25",
                "Portieri": f"{n_p}/3",
                "Difensori": f"{n_d}/8",
                "Centrocampisti": f"{n_c}/8",
                "Attaccanti": f"{n_a}/6",
            }
        )

    st.dataframe(
        pd.DataFrame(riepilogo), use_container_width=True, hide_index=True
    )

    st.divider()
    st.subheader("📋 Rose Dettagliate delle 10 Squadre")

    # Visualizzazione a Tab individuali per ognuna delle 10 squadre
    tabs_squadre = st.tabs([f"🛡️ {sq}" for sq in FANTASQUADRE])

    for idx, sq in enumerate(FANTASQUADRE):
        with tabs_squadre[idx]:
            df_sq = df_acquisti[df_acquisti["Squadra_Fanta"] == sq]
            speso = df_sq["Prezzo_Asta"].sum() if not df_sq.empty else 0
            rimanente = BUDGET_INIZIALE - speso

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Budget Rimanente", f"{rimanente} cr")
            col_m2.metric("Crediti Spesi", f"{speso} cr")
            col_m3.metric("Giocatori Acquistati", f"{len(df_sq)} / 25")

            # Genera e mostra la tabella con esattamente 25 slot
            df_rosa_completa = genera_struttura_rosa(df_sq)
            st.dataframe(
                df_rosa_completa,
                use_container_width=True,
                hide_index=True,
                height=910,
            )

# --- TAB 3: LISTONE COMPLETO ---
with tab_listone:
    st.subheader("Stato del Listone Completo")
    df_merged = df_listone.copy()

    if not df_acquisti.empty:
        df_merged = df_merged.merge(
            df_acquisti[["Giocatore", "Squadra_Fanta", "Prezzo_Asta"]],
            on="Giocatore",
            how="left",
        )
        df_merged["Squadra_Fanta"] = df_merged["Squadra_Fanta"].fillna(
            "Libero"
        )
        df_merged["Prezzo_Asta"] = df_merged["Prezzo_Asta"].fillna("-")
    else:
        df_merged["Squadra_Fanta"] = "Libero"
        df_merged["Prezzo_Asta"] = "-"

    st.dataframe(
        df_merged[
            [
                "Giocatore",
                "Ruolo",
                "Squadra",
                "Prezzo Medio",
                "Squadra_Fanta",
                "Prezzo_Asta",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )