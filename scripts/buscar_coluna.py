import sqlite3
import sys


arquivo_catalogo = "catalogo.db"


if len(sys.argv) != 2:
    print("Uso: python scripts/buscar_coluna.py nome_da_coluna")
    sys.exit(1)


nome_coluna = sys.argv[1]


conn = sqlite3.connect(arquivo_catalogo)

cursor = conn.cursor()

cursor.execute(
    """
    SELECT
        tabela,
        coluna,
        tipo,
        comentario
    FROM colunas
    WHERE coluna = ?
    ORDER BY tabela
    """,
    (nome_coluna,)
)

resultados = cursor.fetchall()

conn.close()


if not resultados:
    print(f"Nenhuma ocorrência encontrada para: {nome_coluna}")
    sys.exit(0)


print()
print(f"Coluna: {nome_coluna}")
print(f"Ocorrências: {len(resultados)}")
print()

for tabela, coluna, tipo, comentario in resultados:
    print(f"Tabela:     {tabela}")
    print(f"Tipo:       {tipo}")
    print(f"Comentário: {comentario or '-'}")
    print("-" * 60)