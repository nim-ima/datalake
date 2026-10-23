import json
from pathlib import Path
 
HTML = r"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catálogo SIDAGRO</title>
<style>
:root{--bg:#fff;--fg:#1d2330;--mut:#6b7385;--bd:#dde1ea;--ac:#1f5fd1;--chip:#eef2fb}
@media (prefers-color-scheme:dark){:root{--bg:#14171f;--fg:#e6e9f2;--mut:#9aa3b8;--bd:#2b3140;--ac:#7aa7ff;--chip:#1e2433}}
body{margin:0;font:15px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--bd);padding:10px 16px;display:flex;gap:12px;align-items:center}
header a.home{font-weight:600;color:var(--fg);text-decoration:none}
#q{flex:1;padding:8px 10px;font-size:15px;border:1px solid var(--bd);border-radius:6px;background:var(--bg);color:var(--fg)}
main{max-width:1100px;margin:0 auto;padding:16px}
a{color:var(--ac);text-decoration:none} a:hover{text-decoration:underline}
table{border-collapse:collapse;width:100%;margin-bottom:20px}
th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--bd);vertical-align:top}
th{color:var(--mut);font-weight:500;font-size:13px}
h2{margin:.2em 0} h3{margin:1.2em 0 .4em}
.mut{color:var(--mut)} .prov{color:var(--mut);font-style:italic}
.chip{background:var(--chip);border-radius:4px;padding:1px 6px;font-size:12px;margin-left:4px}
button{cursor:pointer;font-size:12px;margin-left:8px;border:1px solid var(--bd);background:var(--bg);color:var(--fg);border-radius:4px;padding:2px 8px}
.scroll{overflow-x:auto}
.nota{white-space:pre-wrap;border-left:3px solid var(--ac);background:var(--chip);padding:8px 12px;border-radius:4px;margin:10px 0}
</style>
</head>
<body>
<header>
<a class="home" href="#">Catálogo</a>
<input id="q" autofocus placeholder="Buscar tabela ou coluna (ex.: id_log, core_tb_log_detalhe) e Enter para abrir">
</header>
<main id="m"></main>
<script>
const D = __DADOS__;
const T = D.tabelas, R = D.relacoes;
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
 
// ---- índices ----
const saindo = {}, entrando = {}, colFK = {}, porColuna = {}, pkSozinha = {};
for (const r of R) {
  (saindo[r.filho] ||= []).push(r);
  (entrando[r.pai] ||= []).push(r);
  for (const c of (r.candidatos || [])) (entrando[c] ||= []).push(r);
  for (const [c, cp] of r.pares) (colFK[r.filho + "|" + c] ||= []).push({ r, cp });
}
for (const [k, t] of Object.entries(T)) {
  const pks = t.colunas.filter(c => c.pk);
  for (const c of t.colunas) (porColuna[c.nome] ||= []).push(k);
  if (pks.length === 1) (pkSozinha[pks[0].nome] ||= []).push(k);
}
 
// ---- helpers ----
const lt = k => T[k]
  ? `<a href="#t/${encodeURIComponent(k)}">${esc(T[k].datalake)}</a>`
  : `<span class="mut" title="fora do índice">${esc(k)}</span>`;
const lc = n => `<a href="#c/${encodeURIComponent(n)}">${esc(n)}</a>`;
const alvos = r => r.candidatos
  ? r.candidatos.map(lt).join(' <span class="mut">ou</span> ')
  : lt(r.pai);
const chips = r => (r.implied ? '<span class="chip">implícita</span>' : "") +
                   (r.candidatos ? '<span class="chip">ambígua</span>' : "");
const provaveis = (k, nome) => /^id_/.test(nome) ? (pkSozinha[nome] || []).filter(x => x !== k) : [];
 
function liga(k, c) {
  const fks = colFK[k + "|" + c.nome] || [];
  if (fks.length) {
    return fks.map(({ r, cp }) => `→ ${alvos(r)}.${lc(cp)}${chips(r)}`).join("<br>");
  }
  if (c.pk) return "";
  const p = provaveis(k, c.nome);
  return p.length
    ? `<span class="prov">provável: ${p.slice(0, 6).map(lt).join(", ")}${p.length > 6 ? " …" : ""}</span>`
    : "";
}
 
// ---- telas ----
function viewHome() {
  const por = {};
  for (const t of Object.values(T)) por[t.schema] = (por[t.schema] || 0) + 1;
  return `<h2>Catálogo do banco</h2>
    <p class="mut">${Object.keys(T).length} tabelas · ${R.length} relações. Digite um nome de tabela ou coluna acima.</p>
    <p>${Object.entries(por).map(([s, n]) => `<span class="chip">${esc(s)}: ${n}</span>`).join(" ")}</p>`;
}
 
function viewTabela(k) {
  const t = T[k];
  if (!t) return `<p>Tabela não encontrada: ${esc(k)}</p>`;
  const linhas = t.colunas.map(c => {
    const n = (entrando[k] || []).filter(r => r.pares.some(p => p[1] === c.nome)).length;
    return `<tr><td>${lc(c.nome)}</td><td class="mut">${esc(c.tipo)}</td>
      <td>${c.pk ? '<span class="chip">PK</span>' : ""}</td>
      <td>${liga(k, c)}${n ? `<div class="mut">← referenciada por ${n} relação(ões)</div>` : ""}</td>
      <td class="mut">${c.nota ? `<div class="nota">${esc(c.nota)}</div>` : ""}${esc(c.obs)}</td></tr>`;
  }).join("");
  const sai = (saindo[k] || []).map(r =>
    `<tr><td>${r.pares.map(p => lc(p[0])).join(", ")}</td>
     <td>→ ${alvos(r)} . ${r.pares.map(p => lc(p[1])).join(", ")}</td>
     <td class="mut">${esc(r.fk)}${chips(r)}</td></tr>`).join("");
  const ent = (entrando[k] || []).map(r =>
    `<tr><td>${lt(r.filho)}</td>
     <td>${r.pares.map(p => lc(p[0])).join(", ")} → ${r.pares.map(p => lc(p[1])).join(", ")}</td>
     <td class="mut">${esc(r.fk)}${chips(r)}</td></tr>`).join("");
  return `<h2>${esc(t.datalake)}<button data-c="${esc(t.datalake)}">copiar</button></h2>
    <div class="mut">${esc(t.schema)}.${esc(t.nome)}${t.obs ? " — " + esc(t.obs) : ""}</div>
    ${t.nota ? `<div class="nota">${esc(t.nota)}</div>` : ""}
    <h3>Colunas</h3>
    <div class="scroll"><table><tr><th>coluna</th><th>tipo</th><th></th><th>liga a</th><th>observação</th></tr>${linhas}</table></div>
    <h3>Aponta para (${(saindo[k] || []).length})</h3>
    <div class="scroll"><table>${sai || '<tr><td class="mut">nenhuma</td></tr>'}</table></div>
    <h3>É apontada por (${(entrando[k] || []).length})</h3>
    <div class="scroll"><table>${ent || '<tr><td class="mut">nenhuma</td></tr>'}</table></div>`;
}
 
function viewColuna(n) {
  const ks = (porColuna[n] || []).slice().sort((a, b) => {
    const pa = T[a].colunas.find(c => c.nome === n).pk, pb = T[b].colunas.find(c => c.nome === n).pk;
    return (pb - pa) || T[a].datalake.localeCompare(T[b].datalake);
  });
  const linhas = ks.map(k => {
    const c = T[k].colunas.find(c => c.nome === n);
    return `<tr><td>${lt(k)}</td><td class="mut">${esc(c.tipo)}</td>
      <td>${c.pk ? '<span class="chip">PK</span>' : ""}</td><td>${liga(k, c)}</td></tr>`;
  }).join("");
  return `<h2>${esc(n)}<button data-c="${esc(n)}">copiar</button></h2>
    <div class="mut">aparece em ${ks.length} tabela(s)</div>
    <div class="scroll"><table><tr><th>tabela</th><th>tipo</th><th></th><th>liga a</th></tr>${linhas}</table></div>`;
}
 
function viewBusca(q) {
  q = q.trim().toLowerCase();
  const rank = s => (s === q ? 0 : s.startsWith(q) ? 1 : 2);
  const tabs = Object.entries(T)
    .filter(([k, t]) => t.datalake.toLowerCase().includes(q) || t.nome.toLowerCase().includes(q) ||
                        (t.obs || "").toLowerCase().includes(q) || (t.nota || "").toLowerCase().includes(q))
    .sort((a, b) => rank(a[1].datalake.toLowerCase()) - rank(b[1].datalake.toLowerCase()) ||
                    a[1].datalake.localeCompare(b[1].datalake))
    .slice(0, 40);
  const cols = Object.keys(porColuna)
    .filter(n => n.toLowerCase().includes(q))
    .sort((a, b) => rank(a.toLowerCase()) - rank(b.toLowerCase()) || a.localeCompare(b))
    .slice(0, 40);
  const obs = Object.entries(T)
    .flatMap(([k, t]) => t.colunas.filter(c => ((c.nota || "") + " " + (c.obs || "")).toLowerCase().includes(q)).map(c => [k, c]))
    .slice(0, 30);
  return `<h3>Tabelas (${tabs.length})</h3>
    <p>${tabs.map(([k]) => lt(k) + (T[k].nota ? ' <span class="chip">nota</span>' : "")).join("<br>") || '<span class="mut">nenhuma</span>'}</p>
    <h3>Colunas (${cols.length})</h3>
    <p>${cols.map(n => `${lc(n)} <span class="mut">${porColuna[n].length} tabela(s)</span>`).join("<br>") ||
      '<span class="mut">nenhuma</span>'}</p>
    <h3>Nas observações (${obs.length})</h3>
    <p>${obs.map(([k, c]) => `${lt(k)}.${lc(c.nome)} <span class="mut">— ${esc(c.nota || c.obs)}</span>`).join("<br>") ||
      '<span class="mut">nenhuma</span>'}</p>`;
}
 
// ---- navegação ----
function render() {
  $("#q").value = "";
  const h = decodeURIComponent(location.hash.slice(1));
  const i = h.indexOf("/");
  const tipo = i < 0 ? h : h.slice(0, i), arg = i < 0 ? "" : h.slice(i + 1);
  $("#m").innerHTML = tipo === "t" ? viewTabela(arg) : tipo === "c" ? viewColuna(arg) : viewHome();
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", render);
 
$("#q").addEventListener("input", e => {
  const v = e.target.value;
  if (v.trim()) $("#m").innerHTML = viewBusca(v); else render();
});
$("#q").addEventListener("keydown", e => {
  if (e.key !== "Enter") return;
  const q = e.target.value.trim().toLowerCase();
  if (!q) return;
  const t = Object.entries(T).find(([k, x]) => x.datalake.toLowerCase() === q || k.toLowerCase() === q);
  if (t) { location.hash = "#t/" + encodeURIComponent(t[0]); return; }
  const c = Object.keys(porColuna).find(n => n.toLowerCase() === q);
  if (c) { location.hash = "#c/" + encodeURIComponent(c); }
});
 
document.addEventListener("click", e => {
  const b = e.target.closest("[data-c]");
  if (!b) return;
  const txt = b.dataset.c;
  (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).catch(() => {
    const a = document.createElement("textarea");
    a.value = txt; document.body.appendChild(a); a.select(); document.execCommand("copy"); a.remove();
  });
  b.textContent = "copiado";
  setTimeout(() => { b.textContent = "copiar"; }, 1200);
});
 
render();
</script>
</body>
</html>
"""
 
 
def main():
    dados = Path("catalogo.json").read_text(encoding="utf-8")
    json.loads(dados)  # valida o JSON
    html = HTML.replace("__DADOS__", dados.replace("</", "<\\/"))
    Path("catalogo.html").write_text(html, encoding="utf-8")
    print("gerado: catalogo.html")
 
 
if __name__ == "__main__":
    main()
 