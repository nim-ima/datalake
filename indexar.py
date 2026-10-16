import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET


def indexar(pasta):
    arquivos = sorted(Path(pasta).glob("*.xml"))
    if not arquivos:
        raise SystemExit(f"Nenhum XML encontrado em {Path(pasta).resolve()}")
    tabelas, rels = {}, {}
    for xml in arquivos:
        for t in ET.parse(xml).getroot().iter("table"):
            schema, nome = t.get("schema"), t.get("name")
            chave = f"{schema}.{nome}"
            colunas = t.findall("column")
            if chave in tabelas and len(tabelas[chave]["colunas"]) >= len(colunas):
                continue  # já temos uma versão igual ou mais completa
            pks = {p.get("column") for p in t.findall("primaryKey")}
            tabelas[chave] = {
                "schema": schema, "nome": nome, "datalake": f"{schema}_{nome}",
                "obs": t.get("remarks") or "",
                "colunas": [{
                    "nome": c.get("name"), "tipo": c.get("type"),
                    "pk": c.get("name") in pks, "nulo": c.get("nullable") == "true",
                    "obs": c.get("remarks") or "",
                } for c in colunas],
            }
            for c in colunas:
                for p in c.findall("parent"):  # cada FK aparece uma vez como <parent>
                    pai = f'{p.get("schema") or schema}.{p.get("table")}'
                    k = (p.get("foreignKey"), chave, pai)
                    r = rels.setdefault(k, {
                        "fk": p.get("foreignKey"), "filho": chave, "pai": pai,
                        "pares": [], "implied": p.get("implied") == "true",
                    })
                    r["pares"].append([c.get("name"), p.get("column")])
            por_nome = defaultdict(list)
            for chave, t in tabelas.items():
                por_nome[t["nome"]].append(chave)

            for r in rels.values():
                if r["pai"] in tabelas:
                    continue
                cand = por_nome.get(r["pai"].split(".", 1)[1], [])
                if len(cand) == 1:
                    r["pai"] = cand[0]          # resolvido para o schema certo
                elif len(cand) > 1:
                    r["candidatos"] = cand      # mesmo nome em mais de um schema
    return tabelas, list(rels.values())


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "dicionario"
    tabelas, rels = indexar(pasta)
    Path("catalogo.json").write_text(
        json.dumps({"tabelas": tabelas, "relacoes": rels}, ensure_ascii=False),
        encoding="utf-8",
    )
    print("tabelas por schema:", dict(Counter(t["schema"] for t in tabelas.values())))
    print(len(rels), "relações,", sum(r["implied"] for r in rels), "implícitas")
    orfas = [r for r in rels if r["pai"] not in tabelas]
    ambiguas = [r for r in orfas if "candidatos" in r]
    print(len(orfas) - len(ambiguas), "sem pai em nenhum XML;", len(ambiguas), "ambíguas")
    print(ambiguas[:3])