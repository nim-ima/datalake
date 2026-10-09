#Com base em GTA emitidas (todas as espécies);
# O arquivo trade_2020 foi tratado na demanda do Gilberto Coelho em python.

# ============================================================
# CONSOLIDAÇÃO DAS GTAs PARA EXPORTAÇÃO À SEAPA
# ============================================================

# Colunas usadas para identificar cada fluxo
colunas_agrupamento = [
    "CODIGO_DO_MUNICIPIO_ORIGEM",
    "MUNICIPIO_ORIGEM",
    "CODIGO_MUNICIPIO_DESTINO",
    "MUNICIPIO_DESTINO",
    "UF_DESTINO",
    "ESPECIE",
    "FINALIDADE_DE_TRANSITO",
    "year",
    "month",
]


# ============================================================
# 1. CONSOLIDAR GTAs
# ============================================================

df_trade_seapa = (
    trade_2020
    .groupby(
        colunas_agrupamento,
        as_index=False,
        dropna=False
    )
    .agg(
        N_GTA=("TOTAL_DE_ANIMAIS", "size"),
        TOTAL_DE_MACHOS=("TOTAL_DE_MACHOS", "sum"),
        TOTAL_DE_FEMEAS=("TOTAL_DE_FEMEAS", "sum"),
        TOTAL_DE_ANIMAIS=("TOTAL_DE_ANIMAIS", "sum"),
    )
    .rename(
        columns={
            "year": "ANO",
            "month": "MÊS",
        }
    )
)

# Conferência
display(df_trade_seapa.head())