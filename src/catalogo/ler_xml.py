import xml.etree.ElementTree as ET

import pandas as pd


arquivo_xml = "probd_sda.client.xml"


def ler_xml(arquivo_xml):
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

    return df_colunas, df_relacionamentos