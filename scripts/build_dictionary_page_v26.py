#!/usr/bin/env python3
"""Regenera a página pesquisável do dicionário mestre V2.6."""
from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv"
OUT = ROOT / "docs/dicionario-parametros.html"
COLUMNS = ["field", "modules", "definition", "formula_or_rule", "unit", "how_to_read", "does_not_mean", "unknown_rule"]


def cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return escape(str(value))


def main() -> None:
    frame = pd.read_csv(SOURCE).sort_values("field", kind="stable")
    rows = "".join(
        "<tr>" + "".join(f"<td>{cell(row[column])}</td>" for column in COLUMNS) + "</tr>"
        for _, row in frame.iterrows()
    )
    head = "".join(f"<th>{escape(column)}</th>" for column in COLUMNS)
    count = len(frame)
    document = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dicionário de parâmetros PIH MS V2.6</title><style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#eef4f8;color:#183448;line-height:1.6}}header{{background:linear-gradient(125deg,#083f67,#7b4ab4);color:#fff;padding:30px 5vw}}main{{max-width:1180px;margin:auto;padding:28px 5vw 60px}}.card{{background:#fff;border-radius:16px;padding:22px;margin:0 0 20px;box-shadow:0 5px 20px #163f5b18}}h2{{color:#58377f}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{text-align:left;padding:9px;border-bottom:1px solid #d8e3eb;vertical-align:top}}th{{background:#f0e8f7;color:#58377f;position:sticky;top:0}}.table-wrap{{overflow:auto;max-height:68vh;border:1px solid #d8e3eb;border-radius:10px}}a{{color:#0b5f97}}.search{{width:100%;box-sizing:border-box;padding:12px;border:1px solid #afc4d2;border-radius:9px;font:inherit;margin:8px 0 14px}}
</style><link rel="stylesheet" href="assets/css/documentation.css?v=260000"></head><body><header><small>PIH MS · V2.6 experimental</small><h1>Dicionário exaustivo</h1><p>{count:,} campos documentados e pesquisáveis</p></header><main><section class="card"><h2>Pesquisar campos</h2><p>Cada campo possui definição, regra, unidade, leitura permitida, leitura proibida e tratamento de UNKNOWN.</p><input class="search" id="q" type="search" placeholder="Campo, módulo, fórmula ou regra"><div id="count">{count:,} campos visíveis de {count:,}</div></section><section class="card"><div class="table-wrap"><table id="tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div><p><a href="data/dicionario_metricas_resultados_v1.csv" download>Baixar CSV completo</a></p></section><script>const q=document.getElementById('q'),rows=[...document.querySelectorAll('#tbl tbody tr')],count=document.getElementById('count');function f(){{const s=q.value.trim().toLowerCase();let n=0;rows.forEach(r=>{{const ok=!s||r.innerText.toLowerCase().includes(s);r.style.display=ok?'':'none';if(ok)n++}});count.textContent=n.toLocaleString('pt-BR')+' campos visíveis de {count:,}';}}q.addEventListener('input',f);</script></main><script src="assets/js/documentation.js?v=260000"></script></body></html>'''.replace("1,045", "1.045")
    OUT.write_text(document, encoding="utf-8")
    print(f"OK dicionário HTML · {count} campos")


if __name__ == "__main__":
    main()
