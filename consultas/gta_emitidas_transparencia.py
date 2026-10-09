# PORTAL TRANSPARÊNCIA - GTA emitidas:
# Com base a GTA emitidas - acumulada ao longo do ano, aproveitamos para rodar e atender à Comunicação IMA em publicar no Portal de Tranparência - GTA emitidas.    
#[https://drive.google.com/file/d/17FEy-PeWAGII0Wjxg3y95v4SEORmntxi/view?usp=sharing](https://drive.google.com/file/d/17FEy-PeWAGII0Wjxg3y95v4SEORmntxi/view?usp=sharing)

# ============================================================
# 1. DEPENDÊNCIAS
# ============================================================

import calendar
from pathlib import Path
import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name


# 2. CONFIGURAÇÕES
# ============================================================

ANOS = [2026]
MESES = [9]  # 1=JAN ... 12=DEZ
PASTA_RELATORIOS = Path("/content/drive/My Drive/Colab Notebooks/RELATORIOS")
ARQUIVO_REGIONAL = PASTA_RELATORIOS / "IBGE_SIDAGRO_CR_ESEC_MUNI_NEW.csv"
ARQUIVO_TRADE_TEMPLATE = "TRADE_{ano}.csv"
ARQUIVO_LOGO = PASTA_RELATORIOS / "logo_CIM.png" ### há um arquivo que contem a logo do NIM
SEPARADOR_TRADE = ";"
ENCODING = "utf-8"
SITUACAO_EXCLUIDA = "CANCELADA"

# ============================================================
# 3. DOMÍNIO: FINALIDADES, ESPÉCIES E NOMES DE EXIBIÇÃO
# ============================================================

FINALIDADES = [
    "CRIA",
    "ENGORDA",
    "REPRODUCAO",
    "ABATE",
    "ABATE SANITARIO",
    "RETORNO DE FRIGORIFICO",
    "AGLOMERACAO COM FINALIDADE COMERCIAL",
    "AGLOMERACAO SEM FINALIDADE COMERCIAL",
    "RETORNO DE AGLOMERACAO",
    "PESAGEM",
    "RETORNO A ORIGEM",
    "QUARENTENA",
    "TRABALHO",
    "PESQUISA",
    "COMERCIALIZACAO",
    "TRATAMENTO VETERINARIO",
    "ATENDIMENTO VETERINARIO",
    "POSTURA",
    "INCUBACAO",
    "RECRIA",
    "PRODUCAO APICOLA",
    "EXPORTACAO",
    "USO LABORATORIAL",
    "INDUSTRIALIZACAO",
]

FINALIDADES_EXIBICAO = {
    "CRIA": "CRIA",
    "ENGORDA": "ENGORDA",
    "REPRODUCAO": "REPRODUÇÃO",
    "ABATE": "ABATE",
    "ABATE SANITARIO": "ABATE SANITÁRIO",
    "RETORNO DE FRIGORIFICO": "RETORNO DE FRIGORÍFICO",
    "AGLOMERACAO COM FINALIDADE COMERCIAL": "AGLOMERAÇÃO COM FINALIDADE COMERCIAL",
    "AGLOMERACAO SEM FINALIDADE COMERCIAL": "AGLOMERAÇÃO SEM FINALIDADE COMERCIAL",
    "RETORNO DE AGLOMERACAO": "RETORNO DE AGLOMERAÇÃO",
    "PESAGEM": "PESAGEM",
    "RETORNO A ORIGEM": "RETORNO À ORIGEM",
    "QUARENTENA": "QUARENTENA",
    "TRABALHO": "TRABALHO",
    "PESQUISA": "PESQUISA",
    "COMERCIALIZACAO": "COMERCIALIZAÇÃO",
    "TRATAMENTO VETERINARIO": "TRATAMENTO VETERINÁRIO",
    "ATENDIMENTO VETERINARIO": "ATENDIMENTO VETERINÁRIO",
    "POSTURA": "POSTURA",
    "INCUBACAO": "INCUBAÇÃO",
    "RECRIA": "RECRIA",
    "PRODUCAO APICOLA": "PRODUÇÃO APÍCOLA",
    "EXPORTACAO": "EXPORTAÇÃO",
    "USO LABORATORIAL": "USO LABORATORIAL",
    "INDUSTRIALIZACAO": "INDUSTRIALIZAÇÃO",
}

ESPECIES = [
    "BOVINO",
    "BUBALINO",
    "GALINHA",
    "SUINO",
    "CAPRINO",
    "OVINO",
    "CODORNA",
    "RATITAS",
    "AVES NAO DESTINADAS A PRODUCAO DE CARNE OU OVOS (ORNAMENTAIS/SILVESTRES)",
    "EQUINO",
    "ASININO",
    "MUAR",
    "PEIXE E SEUS ALEVINOS",
    "ABELHAS AFRICANIZADAS",
    "ABELHAS MELIPONIDEAS",
    "LHAMA",
    "GANSO",
    "MARRECO",
    "PATO",
    "PERU",
    "GALINHA-D ANGOLA",
    "FAISAO/CHUKAR",
    "COELHO",
    "OUTRAS ESPECIES",
    "ANFIBIOS",
]

NOME_ABA_ESPECIE = {
    "BOVINO": "BOVINOS",
    "BUBALINO": "BUBALINOS",
    "SUINO": "SUÍNO",
    "AVES NAO DESTINADAS A PRODUCAO DE CARNE OU OVOS (ORNAMENTAIS/SILVESTRES)": "AVES ORNAMENTAIS",
    "ABELHAS MELIPONIDEAS": "ABELHAS MELIPONÍDEAS",
    "GALINHA-D ANGOLA": "GALINHA D'ANGOLA",
    "FAISAO/CHUKAR": "FAISÃO_CHUKAR",
    "OUTRAS ESPECIES": "OUTRAS ESPÉCIES",
    "ANFIBIOS": "ANFÍBIOS",
}

MESES_PT = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO",
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO",
}

# ============================================================
# 4. FUNÇÕES DE PREPARAÇÃO DOS DADOS
# ============================================================

def preparar_trade(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza os campos necessários ao relatório sem alterar o DataFrame original."""
    df = df.copy()

    for coluna in ("MUNICIPIO_ORIGEM", "MUNICIPIO_DESTINO"):
        if coluna in df.columns:
            df[coluna] = df[coluna].astype("string").str.strip()

    df["CODIGO_DO_MUNICIPIO_ORIGEM"] = pd.to_numeric(
        df["CODIGO_DO_MUNICIPIO_ORIGEM"],
        errors="coerce",
        downcast="signed",
    )

    df["TOTAL_DE_ANIMAIS"] = pd.to_numeric(
        df["TOTAL_DE_ANIMAIS"],
        errors="coerce",
    ).fillna(0)

    if ("year" not in df.columns or "month" not in df.columns) and "DATA" in df.columns:
        datas = pd.to_datetime(df["DATA"], errors="coerce")
        if "year" not in df.columns:
            df["year"] = datas.dt.year
        if "month" not in df.columns:
            df["month"] = datas.dt.month

    return df


def validar_colunas(df: pd.DataFrame, colunas: list[str], nome: str) -> None:
    """Interrompe a execução com mensagem clara se faltar alguma coluna obrigatória."""
    faltantes = [c for c in colunas if c not in df.columns]
    if faltantes:
        raise ValueError(f"{nome}: colunas obrigatórias ausentes: {faltantes}")


def periodo_mes(ano: int, mes: int) -> dict:
    """Retorna informações de calendário usadas no cabeçalho."""
    ultimo_dia = calendar.monthrange(ano, mes)[1]

    if mes == 12:
        proximo_ano, proximo_mes = ano + 1, 1
    else:
        proximo_ano, proximo_mes = ano, mes + 1

    return {
        "nome": MESES_PT[mes],
        "ultimo_dia": ultimo_dia,
        "mes_2d": f"{mes:02d}",
        "proximo_mes_2d": f"{proximo_mes:02d}",
        "proximo_ano": proximo_ano,
    }

# ============================================================
# 5. CONSOLIDAÇÃO POR ESPÉCIE E FINALIDADE
# ============================================================

def consolidar_finalidade(
    trade_especie: pd.DataFrame,
    finalidade: str,
) -> pd.DataFrame:
    """
    Consolida uma finalidade por município de origem:
    - GTAs: número de registros/guias
    - ANIMAIS: soma de TOTAL_DE_ANIMAIS
    """
    dados = trade_especie.loc[
        trade_especie["FINALIDADE_DE_TRANSITO"].eq(finalidade),
        ["CODIGO_DO_MUNICIPIO_ORIGEM", "TOTAL_DE_ANIMAIS"],
    ]

    if dados.empty:
        return pd.DataFrame(
            columns=["CODIGO_DO_MUNICIPIO_ORIGEM", "GTAs", "ANIMAIS"]
        )

    return (
        dados.groupby("CODIGO_DO_MUNICIPIO_ORIGEM", dropna=False)
        .agg(
            GTAs=("TOTAL_DE_ANIMAIS", "size"),
            ANIMAIS=("TOTAL_DE_ANIMAIS", "sum"),
        )
        .reset_index()
    )


def construir_tabela_especie(
    regional: pd.DataFrame,
    trade_mes: pd.DataFrame,
    especie: str,
) -> pd.DataFrame:
    """Monta a tabela completa de uma espécie, incluindo todas as finalidades."""
    base = (
        regional[["CODIGO_DO_MUNICIPIO_ORIGEM", "MUNICIPIO_IBGE"]]
        .drop_duplicates("CODIGO_DO_MUNICIPIO_ORIGEM")
        .copy()
    )
    base["ESPECIE"] = especie

    trade_especie = trade_mes.loc[trade_mes["ESPECIE"].eq(especie)]

    print(f"\n************ INÍCIO DA ANÁLISE: {especie} ************")

    for indice, finalidade in enumerate(FINALIDADES, start=1):
        resumo = consolidar_finalidade(trade_especie, finalidade)

        col_gta = f"F{indice:02d}_GTAs"
        col_animais = f"F{indice:02d}_ANIMAIS"

        if resumo.empty:
            base[col_gta] = 0
            base[col_animais] = 0
            print(f"{finalidade} - vazio")
            continue

        resumo = resumo.rename(columns={"GTAs": col_gta, "ANIMAIS": col_animais})
        base = base.merge(
            resumo[
                ["CODIGO_DO_MUNICIPIO_ORIGEM", col_gta, col_animais]
            ],
            on="CODIGO_DO_MUNICIPIO_ORIGEM",
            how="left",
        )
        base[[col_gta, col_animais]] = base[[col_gta, col_animais]].fillna(0)
        print(f"{finalidade} - com trânsito")

    colunas_numericas = [
        c for c in base.columns if c.endswith("_GTAs") or c.endswith("_ANIMAIS")
    ]
    total = {c: base[c].sum() for c in colunas_numericas}
    total.update(
        {
            "CODIGO_DO_MUNICIPIO_ORIGEM": "",
            "MUNICIPIO_IBGE": "",
            "ESPECIE": "TOTAL",
        }
    )
    base = pd.concat([base, pd.DataFrame([total])], ignore_index=True)

    print(f"************ TÉRMINO DA ANÁLISE: {especie} ************")
    return base


def cabecalho_exportacao() -> list[str]:
    """Cabeçalhos gravados na linha 6 do Excel."""
    colunas = ["CÓDIGO", "NOME", "ESPÉCIE"]
    for _ in FINALIDADES:
        colunas.extend(["GTAs", "ANIMAIS"])
    return colunas

# ============================================================
# 6. FORMATAÇÃO DO EXCEL
# ============================================================

def criar_formatos(workbook):
    """Centraliza todos os formatos usados nas abas."""
    return {
        "titulo_verde": workbook.add_format({
            "align": "center", "valign": "vcenter", "bold": True,
            "border": 1, "fg_color": "#99CC66"
        }),
        "titulo_laranja": workbook.add_format({
            "align": "center", "valign": "vcenter", "bold": True,
            "border": 1, "fg_color": "#FF9966"
        }),
        "titulo_cinza": workbook.add_format({
            "align": "center", "valign": "vcenter", "bold": True,
            "border": 1, "fg_color": "#999999"
        }),
        "titulo_azul": workbook.add_format({
            "align": "center", "valign": "vcenter", "bold": True,
            "border": 1, "fg_color": "#6699CC"
        }),
        "normal_central": workbook.add_format({
            "align": "center", "valign": "vcenter", "border": 1
        }),
        "normal_negrito": workbook.add_format({
            "align": "center", "valign": "vcenter", "border": 1, "bold": True
        }),
        "corpo_verde": workbook.add_format({"bg_color": "#CCFFCC", "border": 1}),
        "corpo_laranja": workbook.add_format({"bg_color": "#FFCC99", "border": 1}),
        "corpo_cinza": workbook.add_format({"bg_color": "#CCCCCC", "border": 1}),
        "corpo_azul": workbook.add_format({"bg_color": "#99CCFF", "border": 1}),
        "total": workbook.add_format({
            "bold": True, "border": 1, "bg_color": "#C0C0C0"
        }),
    }


def formatar_aba(
    writer: pd.ExcelWriter,
    nome_aba: str,
    ano: int,
    mes: int,
    numero_linhas_dados: int,
) -> None:
    """Aplica cabeçalhos, cores, larguras, bordas e identificação do período."""
    workbook = writer.book
    worksheet = writer.sheets[nome_aba]
    fmt = criar_formatos(workbook)

    periodo = periodo_mes(ano, mes)

    if ARQUIVO_LOGO.exists():
        worksheet.insert_image(
            "A1",
            str(ARQUIVO_LOGO),
            {"x_scale": 0.85, "y_scale": 0.85, "x_offset": 10, "y_offset": 2},
        )

    ultima_coluna = 2 + (2 * len(FINALIDADES))
    ultima_coluna_excel = xl_col_to_name(ultima_coluna)

    worksheet.merge_range("A1:B4", " ", fmt["normal_negrito"])
    worksheet.merge_range(
        f"G1:{ultima_coluna_excel}4", " ", fmt["normal_negrito"]
    )
    worksheet.merge_range(
        "C1:F1", "INSTITUTO MINEIRO DE AGROPECUÁRIA", fmt["normal_negrito"]
    )
    worksheet.merge_range(
        "C2:F2",
        "RELATÓRIO CONSOLIDADO DE TRÂNSITO DE ANIMAIS",
        fmt["normal_negrito"],
    )
    worksheet.merge_range("C3:D3", "Data de Emissão:", fmt["normal_negrito"])
    worksheet.merge_range("C4:D4", "Período de análise:", fmt["normal_negrito"])
    worksheet.merge_range(
        "E3:F3",
        f"01/{periodo['proximo_mes_2d']}/{periodo['proximo_ano']}",
        fmt["normal_central"],
    )
    worksheet.merge_range(
        "E4:F4",
        f"01/{periodo['mes_2d']}/{ano} a "
        f"{periodo['ultimo_dia']:02d}/{periodo['mes_2d']}/{ano}",
        fmt["normal_central"],
    )

    worksheet.merge_range("A5:B5", "MUNICÍPIO DE ORIGEM", fmt["titulo_verde"])
    worksheet.write("C5", " ", fmt["titulo_laranja"])

    for i, finalidade in enumerate(FINALIDADES):
        primeira_coluna = 3 + (i * 2)
        segunda_coluna = primeira_coluna + 1

        cel_ini = f"{xl_col_to_name(primeira_coluna)}5"
        cel_fim = f"{xl_col_to_name(segunda_coluna)}5"

        estilo_titulo = fmt["titulo_cinza"] if i % 2 == 0 else fmt["titulo_azul"]
        estilo_corpo = fmt["corpo_cinza"] if i % 2 == 0 else fmt["corpo_azul"]

        worksheet.merge_range(
            f"{cel_ini}:{cel_fim}",
            FINALIDADES_EXIBICAO[finalidade],
            estilo_titulo,
        )
        worksheet.set_column(primeira_coluna, segunda_coluna, 12, estilo_corpo)

    worksheet.write_row("A6", ["CÓDIGO", "NOME"], fmt["titulo_verde"])
    worksheet.write("C6", "ESPÉCIE", fmt["titulo_laranja"])

    for i in range(len(FINALIDADES)):
        primeira_coluna = 3 + (i * 2)
        estilo = fmt["titulo_cinza"] if i % 2 == 0 else fmt["titulo_azul"]
        worksheet.write_row(5, primeira_coluna, ["GTAs", "ANIMAIS"], estilo)

    worksheet.freeze_panes(6, 0)
    worksheet.set_column("A:A", 12, fmt["corpo_verde"])
    worksheet.set_column("B:B", 20, fmt["corpo_verde"])
    worksheet.set_column("C:C", 12, fmt["corpo_laranja"])

    # startrow=5 => cabeçalho técnico na linha 6; dados começam na linha 7.
    # O último registro da tabela é o TOTAL.
    linha_total_zero_based = 5 + numero_linhas_dados
    worksheet.set_row(linha_total_zero_based, cell_format=fmt["total"])


def escrever_aba(
    writer: pd.ExcelWriter,
    tabela: pd.DataFrame,
    especie: str,
    ano: int,
    mes: int,
) -> None:
    """Grava e formata uma aba de espécie."""
    nome_aba = NOME_ABA_ESPECIE.get(especie, especie)

    tabela.to_excel(
        writer,
        sheet_name=nome_aba,
        index=False,
        startrow=5,
    )

    formatar_aba(
        writer=writer,
        nome_aba=nome_aba,
        ano=ano,
        mes=mes,
        numero_linhas_dados=len(tabela),
    )

# ============================================================
# 7. CARREGAMENTO E VALIDAÇÃO DOS DADOS
# ============================================================

REGIONAL = pd.read_csv(
    ARQUIVO_REGIONAL,
    sep=",",
    encoding="utf-8-sig",
)

validar_colunas(
    REGIONAL,
    ["CODIGO_DO_MUNICIPIO_ORIGEM", "MUNICIPIO_IBGE"],
    "REGIONAL",
)

REGIONAL["CODIGO_DO_MUNICIPIO_ORIGEM"] = pd.to_numeric(
    REGIONAL["CODIGO_DO_MUNICIPIO_ORIGEM"],
    errors="coerce",
    downcast="signed",
)

print(f"Municípios na base REGIONAL: {len(REGIONAL):,}")

# ============================================================
# 8. EXECUÇÃO
# ============================================================

COLUNAS_TRADE_OBRIGATORIAS = [
    "CODIGO_DO_MUNICIPIO_ORIGEM",
    "MUNICIPIO_ORIGEM",
    "ESPECIE",
    "FINALIDADE_DE_TRANSITO",
    "TOTAL_DE_ANIMAIS",
    "SITUACAO",
]


for ano in ANOS:
    arquivo_trade = PASTA_RELATORIOS / ARQUIVO_TRADE_TEMPLATE.format(ano=ano)

    print(f"\nCarregando: {arquivo_trade}")
    trade = pd.read_csv(
        arquivo_trade,
        sep=SEPARADOR_TRADE,
        encoding=ENCODING,
    )

    trade = preparar_trade(trade)

    validar_colunas(
        trade,
        COLUNAS_TRADE_OBRIGATORIAS + ["year", "month"],
        f"TRADE_{ano}",
    )

    trade_ano = trade.loc[
        trade["SITUACAO"].ne(SITUACAO_EXCLUIDA)
        & trade["year"].eq(ano)
    ].copy()

    pasta_ano = PASTA_RELATORIOS / f"ANO_{ano}"
    pasta_ano.mkdir(parents=True, exist_ok=True)

    for mes in MESES:
        if mes not in MESES_PT:
            raise ValueError(f"Mês inválido: {mes}")

        periodo = periodo_mes(ano, mes)
        trade_mes = trade_ano.loc[trade_ano["month"].eq(mes)].copy()

        arquivo_saida = (
            pasta_ano
            / f"GTA_EMITIDAS_mes_{periodo['nome']}_ano_{ano}.xlsx"
        )

        print(
            "\n"
            + "*" * 28
            + f" {periodo['nome']} - {ano} "
            + "*" * 28
        )
        print(f"Registros válidos no mês: {len(trade_mes):,}")
        print(f"Saída: {arquivo_saida}")

        with pd.ExcelWriter(arquivo_saida, engine="xlsxwriter") as writer:
            for especie in ESPECIES:
                tabela = construir_tabela_especie(
                    regional=REGIONAL,
                    trade_mes=trade_mes,
                    especie=especie,
                )
                escrever_aba(
                    writer=writer,
                    tabela=tabela,
                    especie=especie,
                    ano=ano,
                    mes=mes,
                )

        print(f"\nArquivo concluído: {arquivo_saida}")