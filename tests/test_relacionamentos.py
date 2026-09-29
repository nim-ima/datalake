from src.catalogo.ler_xml import ler_xml
from src.catalogo.relacionamentos import (
    obter_referencias,
    obter_referenciada_por_pk,
)


arquivo_xml = "dados/probd_sda.client.xml"


def carregar_dados():
    return ler_xml(arquivo_xml)


def test_referencias_tb_estabelecimento():
    df_colunas, df_relacionamentos = carregar_dados()

    referencias = obter_referencias(
        df_relacionamentos,
        "tb_estabelecimento"
    )

    assert len(referencias) == 10


def test_referenciada_por_pk_tb_estabelecimento():
    df_colunas, df_relacionamentos = carregar_dados()

    referenciada_por_pk = obter_referenciada_por_pk(
        df_colunas,
        df_relacionamentos,
        "tb_estabelecimento"
    )

    assert len(referenciada_por_pk) == 11


def test_pk_tb_estabelecimento():
    df_colunas, _ = carregar_dados()

    pk = df_colunas[
        (df_colunas["tabela"] == "tb_estabelecimento")
        & (df_colunas["primary_key"])
    ]

    assert len(pk) == 1
    assert pk.iloc[0]["coluna"] == "id_estabelecimento"