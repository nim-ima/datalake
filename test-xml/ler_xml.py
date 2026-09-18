import xml.etree.ElementTree as ET
import pandas as pd


arquivo_xml = "probd_sda.client.xml"

tree = ET.parse(arquivo_xml)
root = tree.getroot()

dados = []

for tabela in root.findall(".//table"):
    nome_tabela = tabela.get("name")

    colunas_pk = {
        pk.get("column")
        for pk in tabela.findall("primaryKey")
    }

    for coluna in tabela.findall("column"):
        nome_coluna = coluna.get("name")

        dados.append({
            "tabela": nome_tabela,
            "coluna": nome_coluna,
            "tipo": coluna.get("type"),
            "tamanho": coluna.get("size"),
            "nullable": coluna.get("nullable"),
            "primary_key": nome_coluna in colunas_pk,
            "descricao": coluna.get("remarks"),
        })

df = pd.DataFrame(dados)

print(df.head())
print()
print(f"Total de colunas: {len(df)}")
print(f"Total de tabelas: {df['tabela'].nunique()}")
print()
print("Colunas que são primary key:")
print(df[df["primary_key"]])