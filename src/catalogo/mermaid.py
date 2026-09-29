import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def carregar(xml_path):
    """Retorna (tabelas, rels). Lê só <parent>: cada FK aparece uma vez."""
    raiz = ET.parse(xml_path).getroot()
    tabelas, rels = {}, {}
    for t in raiz.iter("table"):
        nome = t.get("name")
        pks = {p.get("column") for p in t.findall("primaryKey")}
        cols = []
        for c in t.findall("column"):
            cn = c.get("name")
            pais = c.findall("parent")
            cols.append({
                "nome": cn, "tipo": c.get("type"), "pk": cn in pks,
                "fk": bool(pais), "obs": (c.get("remarks") or "").replace('"', "'"),
            })
            for p in pais:
                k = (p.get("foreignKey"), nome, p.get("table"))
                r = rels.setdefault(k, {
                    "filho": nome, "pai": p.get("table"), "cols": [],
                    "implied": p.get("implied") == "true",
                    "opcional": c.get("nullable") == "true",
                })
                r["cols"].append(cn)
        tabelas[nome] = cols
    return tabelas, list(rels.values())


def vizinhas(rels, tabela):
    """(tabelas que ela referencia, tabelas que a referenciam)."""
    ref = sorted({r["pai"] for r in rels if r["filho"] == tabela})
    refd = sorted({r["filho"] for r in rels if r["pai"] == tabela})
    return ref, refd


def mermaid(tabelas, rels, selecionadas):
    """Selecionadas mostram colunas; vizinhas aparecem como caixas vazias."""
    sel = set(selecionadas)
    linhas = ["erDiagram"]
    for r in rels:
        if r["filho"] in sel or r["pai"] in sel:
            esq = "|o" if r["opcional"] else "||"
            lig = ".." if r["implied"] else "--"
            linhas.append(
                f'    {r["pai"]} {esq}{lig}o{{ {r["filho"]} : "{", ".join(r["cols"])}"'
            )
    for t in sorted(sel):
        linhas.append(f"    {t} {{")
        for c in tabelas[t]:
            chaves = ", ".join(k for k, ativo in (("PK", c["pk"]), ("FK", c["fk"])) if ativo)
            obs = f' "{c["obs"]}"' if c["obs"] else ""
            linhas.append(f'        {c["tipo"]} {c["nome"]} {chaves}{obs}'.rstrip())
        linhas.append("    }")
    return "\n".join(linhas)


def salvar(texto, pasta="docs"):
    Path(pasta).mkdir(exist_ok=True)
    Path(pasta, "diagrama.md").write_text(f"```mermaid\n{texto}\n```\n", encoding="utf-8")
    Path(pasta, "diagrama.html").write_text(
        '<!doctype html><meta charset="utf-8"><pre class="mermaid">' + texto + "</pre>"
        '<script type="module">'
        "import m from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';"
        "m.initialize({startOnLoad:true});</script>",
        encoding="utf-8",
    )