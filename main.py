from src.catalogo.mermaid import carregar, mermaid, salvar, vizinhas

tabelas, rels = carregar("dados/probd_sda.client.xml")

minhas = [l.strip() for l in open("tabelas.txt", encoding="utf-8")
          if l.strip() and not l.startswith("#")]
faltando = [t for t in minhas if t not in tabelas]
if faltando:
    raise SystemExit(f"Não encontradas no XML: {faltando}")

for t in minhas:
    ref, refd = vizinhas(rels, t)
    print(f"{t}\n  referencia:      {ref}\n  referenciada por: {refd}")

salvar(mermaid(tabelas, rels, minhas))