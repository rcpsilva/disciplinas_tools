#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gera um arquivo .tex contendo TODOS os Programas de Disciplina listados
no JSON (campo "Disciplinas"), em INGLES (rotulos, cabecalho e babel).
Mantem o layout oficial PROGRAD / UFOP de json2tex2.py.

Uso:
    python json2tex2_en.py eletivas_bacharelado_IA_en.json [saida.tex] [--no-escape]

O JSON pode usar as chaves em portugues (as mesmas de json2tex2.py) ou as
chaves em ingles listadas em ALIASES. O conteudo (ementa, bibliografia etc.)
e' impresso como esta no JSON, portanto deve ja estar em ingles.
"""
import json, re, sys
from pathlib import Path
from textwrap import dedent

# ------------------------------------------------------------------ #
# 1. PREAMBLE (emitted once)                                         #
# ------------------------------------------------------------------ #
PREAMBLE = dedent(r"""
\documentclass[11pt]{article}
\usepackage{ifthen}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}
\usepackage{geometry}
\geometry{a4paper,margin=2cm}
\usepackage{longtable,graphicx,multirow,enumitem,tabularx,setspace,ragged2e}
\setlist{nosep,leftmargin=*}
\renewcommand\arraystretch{1.15}
\pagestyle{empty}
\begin{document}
""").lstrip()

# ------------------------------------------------------------------ #
# 2. One course block (placeholders between {{...}})                  #
# ------------------------------------------------------------------ #
DISCIPLINA = dedent(r"""
\begin{center}
\begin{tabular}{lccr}
 \multirow{3}{*}{\includegraphics[height=2.7cm]{brasao.png}} &
 \multicolumn{2}{c}{\bfseries FEDERAL UNIVERSITY OF OURO PRETO} &
 \ \ \ \ \multirow{3}{*}{\includegraphics[height=2.7cm]{ufop.png}} \\
 & \multicolumn{2}{c}{\bfseries DEAN'S OFFICE FOR UNDERGRADUATE STUDIES} & \\
 & \multicolumn{2}{c}{} & \\
 & \multicolumn{2}{c}{\Large\bfseries COURSE PROGRAM} & \\
\end{tabular}
\end{center}

\begin{center}
\begin{longtable}{|p{4cm}|p{4cm}|p{4cm}|p{4cm}|}
\hline
\multicolumn{3}{|p{12cm}|}{Course Name in English:} &
\multicolumn{1}{p{4cm}|}{Code:} \\ 
\multicolumn{3}{|p{12cm}|}{\textbf{{{NOME_ENUS}}}} &
\textbf{{{CODIGO}}}\\ 
\multicolumn{3}{|p{12cm}|}{Course Name in Portuguese:} & \\ 
\multicolumn{3}{|p{12cm}|}{\textbf{{{NOME_PTBR}}}} & \\ 
\hline
\multicolumn{3}{|p{12cm}|}{Department Name and Acronym:} & Academic Unit: \\ 
\multicolumn{3}{|p{12cm}|}{{{DEPARTAMENTO}}} & {{{UNIDADE}}} \\ 
\hline
\multicolumn{4}{|p{16cm}|}{Delivery Mode:
[{{PRESENCIAL}}] in person \hspace{0.6cm}
[{{SEMI}}] blended \hspace{0.6cm}
[{{DISTANCIA}}] distance learning}\\
\hline
\multicolumn{2}{|p{8cm}|}{Semester workload} &
\multicolumn{2}{p{8cm}|}{Weekly workload}\\
\hline
\multicolumn{1}{|p{4cm}|}{Total} &
\multicolumn{1}{p{4cm}|}{Extension} &
\multicolumn{1}{p{4cm}|}{Theoretical} &
\multicolumn{1}{p{4cm}|}{Practical} \\ 
\multicolumn{1}{|p{4cm}|}{{{CH_TOTAL}}\,hours} &
\multicolumn{1}{p{4cm}|}{{{CH_EXT}}\;hours} &
\multicolumn{1}{p{4cm}|}{{{CH_TEO}}\;class hours} &
\multicolumn{1}{p{4cm}|}{{{CH_PRA}}\;class hours} \\ 
\hline
\multicolumn{4}{|p{16cm}|}{Course Description:}\\
\multicolumn{4}{|p{16cm}|}{}\\
\multicolumn{4}{|p{\dimexpr 16cm + 6\tabcolsep\relax}|}{{{EMENTA}}}\\
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{4}{|p{16cm}|}{Course Content:}\\*
{{CONTEUDO}}
{{PERFIL_OBJ_BLOCK}}
\hline
\multicolumn{4}{|p{16cm}|}{Basic Bibliography:}\\*
{{BIB_BASICA}}
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{4}{|p{16cm}|}{Complementary Bibliography:}\\*
{{BIB_COMP}}
\hline
\end{longtable}
\end{center}

\clearpage
""").lstrip()

ENDDOC = r"\end{document}"

# ------------------------------------------------------------------ #
# 3. Chaves aceitas no JSON (portugues, como no original, ou ingles)  #
# ------------------------------------------------------------------ #
ALIASES = {
    "name_pt":  ("Nome (ptBR)", "Name (ptBR)", "Name (Portuguese)"),
    "name_en":  ("Nome (enUS)", "Name (enUS)", "Name (English)"),
    "code":     ("Código", "Code"),
    "dept":     ("Departamento", "Department"),
    "unit":     ("Unidade Acadêmica", "Academic Unit"),
    "modality": ("Modalidade", "Modality"),
    "workload": ("Carga Horária", "Workload", "Credit Hours"),
    "syllabus": ("Ementa", "Syllabus", "Course Description"),
    "content":  ("Conteúdo Programático", "Course Content", "Program Content"),
    "basic":    ("Bibliografia Básica", "Basic Bibliography"),
    "compl":    ("Bibliografia Complementar", "Complementary Bibliography",
                 "Supplementary Bibliography"),
    "profile":  ("Perfil", "Community Profile"),
    "ext_obj":  ("Objetivo Extencionista", "Objetivo Extensionista",
                 "Extension Objectives"),
}
WORKLOAD_KEYS = {
    "total": ("Total",),
    "ext":   ("Extensionista", "Extension"),
    "theo":  ("Teórica", "Theoretical"),
    "prac":  ("Prática", "Practical"),
}

ESCAPE = True
_ESC = re.compile(r"(?<!\\)([&%#_])")


def esc(s):
    """Escapa & % # _ que ainda nao estejam escapados (URLs, autores com &)."""
    s = "" if s is None else str(s)
    return _ESC.sub(r"\\\1", s) if ESCAPE else s


def get(d, key, default=""):
    for k in ALIASES[key]:
        if k in d and d[k] is not None:
            return d[k]
    return default


def mc4(text):
    return r"\multicolumn{4}{|p{\dimexpr 16cm + 6\tabcolsep\relax}|}{" + text + r"}\\"


def list_rows(seq, env):
    """Uma linha de longtable por item, para a tabela poder quebrar de pagina
    entre itens (uma unica celula gigante nao quebra e deixa a pagina vazia)."""
    seq = [x for x in (seq or []) if str(x).strip()]
    if not seq:
        return mc4(r"\begin{itemize}\item[] (none listed)\end{itemize}")
    rows = []
    for i, x in enumerate(seq, 1):
        opt = f"[start={i}]" if env == "enumerate" else ""
        rows.append(mc4(f"\\begin{{{env}}}{opt}\\item {esc(x)}\\end{{{env}}}"))
    return "\n".join(rows)


def render_disciplina(d):
    mod = str(get(d, "modality")).lower()
    blended = any(t in mod for t in ("semi", "blended", "hybrid"))
    dist = (not blended) and any(t in mod for t in
                                 ("distância", "distancia", "distance", "remote", "online"))
    pres = (not blended) and any(t in mod for t in
                                 ("presencial", "in person", "in-person", "on-site"))
    mark = lambda b: "X" if b else " "

    wl = get(d, "workload", {})
    wl = wl if isinstance(wl, dict) else {}
    def wl_get(k):
        for name in WORKLOAD_KEYS[k]:
            if name in wl:
                return esc(wl[name])
        return ""

    perfil = get(d, "profile")
    perfil = perfil.strip() if isinstance(perfil, str) else ""
    objx = get(d, "ext_obj")
    objx = objx.strip() if isinstance(objx, str) else ""

    if perfil or objx:
        lines = [mc4("")]
        if perfil:
            lines.append(mc4(f"Community Profile: {esc(perfil)}"))
        if objx:
            lines.append(mc4(f"Extension Objectives: {esc(objx)}"))
        lines.append(mc4(""))
        perfil_obj_block = "\n".join(lines)
    else:
        perfil_obj_block = mc4("")

    mapa = {
        "NOME_PTBR": esc(get(d, "name_pt")),
        "NOME_ENUS": esc(get(d, "name_en")),
        "CODIGO": esc(get(d, "code")),
        "DEPARTAMENTO": esc(get(d, "dept")),
        "UNIDADE": esc(get(d, "unit")),
        "PRESENCIAL": mark(pres),
        "SEMI": mark(blended),
        "DISTANCIA": mark(dist),
        "CH_TOTAL": wl_get("total"),
        "CH_EXT": wl_get("ext"),
        "CH_TEO": wl_get("theo"),
        "CH_PRA": wl_get("prac"),
        "EMENTA": esc(get(d, "syllabus")),
        "CONTEUDO": list_rows(get(d, "content", []), "enumerate"),
        "BIB_BASICA": list_rows(get(d, "basic", []), "itemize"),
        "BIB_COMP": list_rows(get(d, "compl", []), "itemize"),
        "PERFIL_OBJ_BLOCK": perfil_obj_block,
    }

    bloco = DISCIPLINA
    for k, v in mapa.items():
        bloco = bloco.replace(f"{{{{{k}}}}}", v)
    return bloco


def main():
    global ESCAPE
    args = [a for a in sys.argv[1:] if a != "--no-escape"]
    if "--no-escape" in sys.argv[1:]:
        ESCAPE = False
    if len(args) not in (1, 2):
        print("Usage: python json2tex2_en.py input.json [output.tex] [--no-escape]")
        sys.exit(1)

    in_path = Path(args[0])
    out_path = Path(args[1]) if len(args) == 2 else in_path.with_suffix(".tex")
    dados = json.loads(in_path.read_text(encoding="utf-8"))

    # JSON com uma unica disciplina e' embrulhado em lista
    disciplinas = dados.get("Disciplinas", dados.get("Courses", dados.get("Electives", [dados])))

    corpo = "".join(render_disciplina(d) for d in disciplinas)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(PREAMBLE + corpo + ENDDOC, encoding="utf-8")
    print("Generated:", out_path)


if __name__ == "__main__":
    main()
