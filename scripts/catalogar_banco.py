import getpass
import sqlite3

from impala.dbapi import connect


host = "dlmg.prodemge.gov.br"
port = 21051
banco = "db_dlsidagro_staging"

arquivo_catalogo = "catalogo.db"


usuario = input("Usuário LDAP: ")
senha = getpass.getpass("Senha LDAP: ")


print()
print("Conectando ao Impala...")

conn_impala = connect(
    host=host,
    port=port,
    database=banco,
    auth_mechanism="LDAP",
    user=usuario,
    password=senha,
    use_ssl=True,
)

print("Conexão estabelecida.")


conn_sqlite = sqlite3.connect(
    arquivo_catalogo
)


cursor_impala = conn_impala.cursor()
cursor_sqlite = conn_sqlite.cursor()


cursor_sqlite.execute("""
    CREATE TABLE IF NOT EXISTS colunas (
        banco TEXT,
        tabela TEXT,
        ordem INTEGER,
        coluna TEXT,
        tipo TEXT,
        comentario TEXT
    )
""")


cursor_sqlite.execute("""
    DELETE FROM colunas
""")


cursor_sqlite.execute("""
    CREATE INDEX IF NOT EXISTS idx_colunas_nome
    ON colunas (coluna)
""")


print()
print("Buscando tabelas...")

cursor_impala.execute("SHOW TABLES")

tabelas = [
    linha[0]
    for linha in cursor_impala.fetchall()
]


print(f"{len(tabelas)} tabelas encontradas.")
print()


for numero, tabela in enumerate(tabelas, start=1):

    print(
        f"[{numero}/{len(tabelas)}] "
        f"{tabela}"
    )

    cursor_impala.execute(
        f"DESCRIBE `{tabela}`"
    )

    colunas = cursor_impala.fetchall()

    for ordem, coluna in enumerate(colunas, start=1):

        nome_coluna = coluna[0]
        tipo = coluna[1]

        comentario = (
            coluna[2]
            if len(coluna) > 2
            else None
        )

        cursor_sqlite.execute(
            """
            INSERT INTO colunas (
                banco,
                tabela,
                ordem,
                coluna,
                tipo,
                comentario
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                banco,
                tabela,
                ordem,
                nome_coluna,
                tipo,
                comentario,
            )
        )


conn_sqlite.commit()


cursor_impala.close()
cursor_sqlite.close()

conn_impala.close()
conn_sqlite.close()


print()
print("===================================")
print("Catálogo criado com sucesso.")
print(f"Arquivo: {arquivo_catalogo}")
print("===================================")