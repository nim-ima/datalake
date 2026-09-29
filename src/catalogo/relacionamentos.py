def obter_referencias(df_relacionamentos, tabela):
    return df_relacionamentos[
        df_relacionamentos["tabela_origem"] == tabela
    ].copy()


def obter_referenciada_por_pk(
    df_colunas,
    df_relacionamentos,
    tabela
):
    pk = df_colunas[
        (df_colunas["tabela"] == tabela)
        & (df_colunas["primary_key"])
    ][
        ["tabela", "coluna"]
    ].rename(
        columns={
            "tabela": "tabela_destino",
            "coluna": "coluna_destino"
        }
    )

    referenciada_por = df_relacionamentos[
        df_relacionamentos["tabela_destino"] == tabela
    ]

    return referenciada_por.merge(
        pk,
        on=[
            "tabela_destino",
            "coluna_destino"
        ],
        how="inner"
    )


def gerar_mermaid(
    df_colunas,
    df_relacionamentos,
    tabela
):
    referencias = obter_referencias(
        df_relacionamentos,
        tabela
    )

    referenciada_por_pk = obter_referenciada_por_pk(
        df_colunas,
        df_relacionamentos,
        tabela
    )

    tabelas = {tabela}

    tabelas.update(
        referencias["tabela_destino"]
    )

    tabelas.update(
        referenciada_por_pk["tabela_origem"]
    )

    relacionamentos = df_relacionamentos[
        (
            df_relacionamentos["tabela_origem"].isin(tabelas)
        )
        &
        (
            df_relacionamentos["tabela_destino"].isin(tabelas)
        )
    ]

    linhas = ["erDiagram"]

    for nome_tabela in tabelas:
        dados_tabela = df_colunas[
            df_colunas["tabela"] == nome_tabela
        ]

        if dados_tabela.empty:
            continue

        linhas.append(
            f"    {nome_tabela} {{"
        )

        fks = set(
            relacionamentos[
                relacionamentos["tabela_origem"] == nome_tabela
            ]["coluna_origem"]
        )

        for _, coluna in dados_tabela.iterrows():
            if (
                not coluna["primary_key"]
                and coluna["coluna"] not in fks
            ):
                continue

            chave = ""

            if coluna["primary_key"]:
                chave = " PK"
            elif coluna["coluna"] in fks:
                chave = " FK"

            linhas.append(
                f"        {coluna['tipo']} "
                f"{coluna['coluna']}{chave}"
            )

        linhas.append("    }")

    relacionamentos = relacionamentos.drop_duplicates(
        subset=[
            "tabela_origem",
            "coluna_origem",
            "tabela_destino",
            "coluna_destino",
        ]
    )

    for _, relacionamento in relacionamentos.iterrows():
        linhas.append(
            f"    "
            f"{relacionamento['tabela_origem']} "
            f"}}o--|| "
            f"{relacionamento['tabela_destino']} "
            f": "
            f"{relacionamento['foreign_key']}"
        )

    return "\n".join(linhas)