import xml.etree.ElementTree as ET
import pandas as pd


arquivo_xml = "probd_sda.client.xml"

tree = ET.parse(arquivo_xml)
root = tree.getroot()

dados_colunas = []
dados_relacionamentos = []


for tabela in root.findall(".//table"):
    nome_tabela = tabela.get("name")

    colunas_pk = {
        pk.get("column")
        for pk in tabela.findall("primaryKey")
    }

    for coluna in tabela.findall("column"):
        nome_coluna = coluna.get("name")

        dados_colunas.append({
            "tabela": nome_tabela,
            "coluna": nome_coluna,
            "tipo": coluna.get("type"),
            "tamanho": coluna.get("size"),
            "nullable": coluna.get("nullable"),
            "primary_key": nome_coluna in colunas_pk,
            "descricao": coluna.get("remarks"),
        })

        for parent in coluna.findall("parent"):
            dados_relacionamentos.append({
                "tabela_origem": nome_tabela,
                "coluna_origem": nome_coluna,
                "tabela_destino": parent.get("table"),
                "coluna_destino": parent.get("column"),
                "foreign_key": parent.get("foreignKey"),
                "on_delete_cascade": parent.get("onDeleteCascade"),
            })


df_colunas = pd.DataFrame(dados_colunas)
df_relacionamentos = pd.DataFrame(dados_relacionamentos)


print("========== COLUNAS ==========")
print(df_colunas.head())

print()
print(f"Total de colunas: {len(df_colunas)}")
print(f"Total de tabelas: {df_colunas['tabela'].nunique()}")

print()
print("========== RELACIONAMENTOS ==========")
print(df_relacionamentos.head())

print()
print(f"Total de relacionamentos: {len(df_relacionamentos)}")


print()
print("========== TB_EXPLORACAO ==========")

print("\nColunas:")
print(
    df_colunas[
        df_colunas["tabela"] == "tb_exploracao"
    ]
)

print("\nRelacionamentos:")
print(
    df_relacionamentos[
        df_relacionamentos["tabela_origem"] == "tb_exploracao"
    ]
)

def gerar_mermaid(tabelas):
    linhas = ["erDiagram"]

    relacionamentos = df_relacionamentos[
        (
            (
                df_relacionamentos["tabela_origem"] == "tb_exploracao"
            )
            |
            (
                df_relacionamentos["tabela_destino"] == "tb_exploracao"
            )
        )
        &
        (
            df_relacionamentos["tabela_origem"].isin(tabelas)
            &
            df_relacionamentos["tabela_destino"].isin(tabelas)
        )
    ]

    for tabela in tabelas:
        dados_tabela = df_colunas[
            df_colunas["tabela"] == tabela
        ]

        if dados_tabela.empty:
            continue

        linhas.append(f"    {tabela} {{")

        fks = set(
            relacionamentos[
                relacionamentos["tabela_origem"] == tabela
            ]["coluna_origem"]
        )

        for _, coluna in dados_tabela.iterrows():
            nome = coluna["coluna"]
            tipo = coluna["tipo"]

            chave = ""

            if coluna["primary_key"]:
                chave = " PK"
            elif nome in fks:
                chave = " FK"

            if chave:
                linhas.append(
                    f"        {tipo} {nome}{chave}"
                )

        linhas.append("    }")

    for _, relacionamento in relacionamentos.iterrows():
        origem = relacionamento["tabela_origem"]
        destino = relacionamento["tabela_destino"]
        foreign_key = relacionamento["foreign_key"]

        linhas.append(
            f"    {origem} }}o--|| {destino} : {foreign_key}"
        )

    return "\n".join(linhas)


tabelas_mapa = [
    "tb_exploracao",
    "tb_atualizacao_cadastral_produtor_nucleo",
    "tb_propriedade",
    "tb_exploracao_produtor",
    "tb_nucleo"
]

def encontrar_relacionamentos(tabela):
    relacionamentos = df_relacionamentos[
        (df_relacionamentos["tabela_origem"] == tabela)
        | (df_relacionamentos["tabela_destino"] == tabela)
    ]

    referencias = relacionamentos[
        relacionamentos["tabela_origem"] == tabela
    ]

    referenciada_por = relacionamentos[
        relacionamentos["tabela_destino"] == tabela
    ]

    return referencias, referenciada_por


referencias, referenciada_por = encontrar_relacionamentos(
    "tb_exploracao"
)

print()
print("========== TB_EXPLORACAO ==========")

print()
print("REFERENCIA:")
print(
    referencias[
        [
            "tabela_destino",
            "coluna_origem",
            "coluna_destino",
            "foreign_key"
        ]
    ].to_string(index=False)
)

print()
print("REFERENCIADA POR:")
print(
    referenciada_por[
        [
            "tabela_origem",
            "coluna_origem",
            "coluna_destino",
            "foreign_key"
        ]
    ].to_string(index=False)
)

mermaid = gerar_mermaid(tabelas_mapa)


#html = f"""
#<!DOCTYPE html>
#<html lang="pt-BR">
#<head>
#    <meta charset="UTF-8">
#    <title>Mapa do banco</title>
#
#    <script type="module">
#        import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
#
#        mermaid.initialize({{
#            startOnLoad: true
#        }});
#    </script>
#</head>
#
#<body>
#
#    <h1>Mapa do banco</h1>
#
#    <div class="mermaid">
#
#{mermaid}
#
#    </div>
#
#</body>
#</html>
#"""
#
#
#with open("diagrama.html", "w", encoding="utf-8") as arquivo:
#    arquivo.write(html)
#
#
#print()
#print("Diagrama criado: diagrama.html")