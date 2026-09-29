def obter_tabela(df_colunas, tabela):
    return df_colunas[
        df_colunas["tabela"] == tabela
    ].copy()


def obter_colunas(df_colunas, tabela):
    return df_colunas[
        df_colunas["tabela"] == tabela
    ][
        [
            "coluna",
            "tipo",
            "tamanho",
            "nullable",
            "primary_key",
            "descricao"
        ]
    ].copy()


def obter_chaves_primarias(df_colunas, tabela):
    return df_colunas[
        (df_colunas["tabela"] == tabela)
        & (df_colunas["primary_key"])
    ][
        ["coluna", "tipo"]
    ].copy()


def obter_detalhes_tabela(
    df_colunas,
    df_relacionamentos,
    tabela
):
    from src.catalogo.relacionamentos import (
        obter_referencias,
        obter_referenciada_por_pk,
    )

    return {
        "tabela": tabela,
        "colunas": obter_colunas(
            df_colunas,
            tabela
        ),
        "chaves_primarias": obter_chaves_primarias(
            df_colunas,
            tabela
        ),
        "referencias": obter_referencias(
            df_relacionamentos,
            tabela
        ),
        "referenciada_por_pk": obter_referenciada_por_pk(
            df_colunas,
            df_relacionamentos,
            tabela
        ),
    }