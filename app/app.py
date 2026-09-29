import streamlit as st
import streamlit.components.v1 as components

from src.catalogo.ler_xml import ler_xml
from src.catalogo.metadados import obter_detalhes_tabela
from src.catalogo.relacionamentos import gerar_mermaid


arquivo_xml = "dados/probd_sda.client.xml"

df_colunas, df_relacionamentos = ler_xml(
    arquivo_xml
)


tabelas = sorted(
    df_colunas["tabela"].unique()
)


st.set_page_config(
    page_title="Catálogo do Datalake",
    layout="wide"
)


st.title("Catálogo do Datalake")


tabela = st.selectbox(
    "Selecione uma tabela",
    tabelas,
    index=tabelas.index("tb_estabelecimento")
)


detalhes = obter_detalhes_tabela(
    df_colunas,
    df_relacionamentos,
    tabela
)


st.header(tabela)


coluna1, coluna2 = st.columns(2)


with coluna1:
    st.subheader("Chave primária")

    st.dataframe(
        detalhes["chaves_primarias"],
        hide_index=True,
        use_container_width=True
    )


with coluna2:
    st.subheader("Resumo")

    st.metric(
        "Colunas",
        len(detalhes["colunas"])
    )

    st.metric(
        "Referências",
        len(detalhes["referencias"])
    )

    st.metric(
        "Referenciada pela PK",
        len(detalhes["referenciada_por_pk"])
    )


st.divider()


st.subheader("Colunas")

st.dataframe(
    detalhes["colunas"],
    hide_index=True,
    use_container_width=True
)


st.divider()


coluna1, coluna2 = st.columns(2)


with coluna1:
    st.subheader("Referências")

    referencias = detalhes["referencias"][
        [
            "tabela_destino",
            "coluna_origem",
            "coluna_destino",
            "foreign_key"
        ]
    ]

    st.dataframe(
        referencias,
        hide_index=True,
        use_container_width=True
    )


with coluna2:
    st.subheader("Referenciada pela PK")

    referenciada_por = detalhes[
        "referenciada_por_pk"
    ][
        [
            "tabela_origem",
            "coluna_origem",
            "coluna_destino",
            "foreign_key"
        ]
    ]

    st.dataframe(
        referenciada_por,
        hide_index=True,
        use_container_width=True
    )


st.divider()


st.subheader("Mapa de relacionamentos")


mermaid = gerar_mermaid(
    df_colunas,
    df_relacionamentos,
    tabela
)


html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">

    <script type="module">
        import mermaid from
        "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

        mermaid.initialize({{
            startOnLoad: true
        }});
    </script>
</head>

<body>

<div class="mermaid">

{mermaid}

</div>

</body>
</html>
"""


components.html(
    html,
    height=700,
    scrolling=True
)