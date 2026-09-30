#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gera um arquivo .tex contendo TODOS os Programas de Disciplina listados
no JSON (campo "Disciplinas").  Mantém o layout oficial PROGRAD / UFOP.
"""
# bash python json2tex2.py disciplinas_bia.json ./LaTeXSource/ufop_prog.tex [--no-escape]
import json, re, sys
from pathlib import Path
from textwrap import dedent

# ------------------------------------------------------------------ #
# 1. PREÂMBULO  (vai só uma vez)                                     #
# ------------------------------------------------------------------ #
PREAMBLE = dedent(r"""
\documentclass[11pt]{article}
\usepackage{ifthen}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{geometry}
\geometry{a4paper,margin=2cm}
\usepackage{longtable,graphicx,multirow,enumitem,tabularx,setspace,ragged2e}
\setlist{nosep,leftmargin=*}
\renewcommand\arraystretch{1.15}
% Caixa de seleção
\newcommand{\chk}[1]{\ifx#1X\setlength\fboxsep{1pt}\fbox{\rule{1.3ex}{0pt}X}%
\else\setlength\fboxsep{1pt}\fbox{\rule{1.3ex}{0pt}\rule{1.3ex}{0pt}}\fi}
\pagestyle{empty}
\begin{document}
""").lstrip()

# ------------------------------------------------------------------ #
# 2. BLOCO de uma única disciplina (place-holders entre {{...}})     #
# ------------------------------------------------------------------ #
DISCIPLINA = dedent(r"""
\begin{center}
\begin{tabular}{lccr}
 \multirow{3}{*}{\includegraphics[height=2.7cm]{brasao.png}} &
 \multicolumn{2}{c}{\bfseries UNIVERSIDADE FEDERAL DE OURO PRETO} &
 \ \ \ \ \multirow{3}{*}{\includegraphics[height=2.7cm]{ufop.png}} \\
 & \multicolumn{2}{c}{\bfseries PRÓ-REITORIA DE GRADUAÇÃO} & \\
 & \multicolumn{2}{c}{} & \\
 & \multicolumn{2}{c}{\Large\bfseries PROGRAMA DE DISCIPLINA} & \\
\end{tabular}
\end{center}

\begin{center}
\begin{longtable}{|p{4cm}|p{4cm}|p{4cm}|p{4cm}|}
\hline
\multicolumn{3}{|p{12cm}|}{Nome do Componente Curricular em Português:} &
\multicolumn{1}{p{4cm}|}{Código:} \\ 
\multicolumn{3}{|p{12cm}|}{\textbf{{{NOME_PTBR}}}} &
\textbf{{{CODIGO}}}\\ 
\multicolumn{3}{|p{12cm}|}{Nome do Componente Curricular em Inglês:} & \\ 
\multicolumn{3}{|p{12cm}|}{\textbf{{{NOME_ENUS}}}} & \\ 
\hline
\multicolumn{3}{|p{12cm}|}{Nome e Sigla do Departamento} & Unidade Acadêmica: \\ 
\multicolumn{3}{|p{12cm}|}{{{DEPARTAMENTO}}} & {{{UNIDADE}}} \\ 
\hline
\multicolumn{4}{|p{16cm}|}{Modalidade de Oferta:
[{{PRESENCIAL}}] presencial \hspace{0.6cm}
[{{SEMI}}] semipresencial \hspace{0.6cm}
[{{DISTANCIA}}] à distância}\\
\hline
\multicolumn{2}{|p{8cm}|}{Carga horária semestral} &
\multicolumn{2}{p{8cm}|}{Carga horária semanal}\\
\hline
\multicolumn{1}{|p{4cm}|}{Total} &
\multicolumn{1}{p{4cm}|}{Extensionista} &
\multicolumn{1}{p{4cm}|}{Teórica} &
\multicolumn{1}{p{4cm}|}{Prática} \\ 
\multicolumn{1}{|p{4cm}|}{{{CH_TOTAL}}\,horas} &
\multicolumn{1}{p{4cm}|}{{{CH_EXT}}\;horas} &
\multicolumn{1}{p{4cm}|}{{{CH_TEO}}\;horas/aula} &
\multicolumn{1}{p{4cm}|}{{{CH_PRA}}\;horas/aula} \\ 
\hline
\multicolumn{4}{|p{16cm}|}{Ementa:}\\
\multicolumn{4}{|p{16cm}|}{}\\
\multicolumn{4}{|p{\dimexpr 16cm + 6\tabcolsep\relax}|}{{{EMENTA}}}\\
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{4}{|p{16cm}|}{Conteúdo programático:}\\*
{{CONTEUDO}}
{{PERFIL_OBJ_BLOCK}}
\hline
\multicolumn{4}{|p{16cm}|}{Bibliografia Básica:}\\*
{{BIB_BASICA}}
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{4}{|p{16cm}|}{Bibliografia Complementar:}\\*
{{BIB_COMP}}
\hline
\end{longtable}
\end{center}

\clearpage
""").lstrip()

# ------------------------------------------------------------------ #
# 3. FIM do documento                                                #
# ------------------------------------------------------------------ #
ENDDOC = r"\end{document}"


# ---------- Funções auxiliares ------------------------------------ #
ESCAPE = True
_ESC = re.compile(r"(?<!\\)([&%#_])")


def esc(s):
    """Escapa & % # _ ainda não escapados (URLs, autores com &, etc.)."""
    s = "" if s is None else str(s)
    return _ESC.sub(r"\\\1", s) if ESCAPE else s


def mc4(text):
    return r"\multicolumn{4}{|p{\dimexpr 16cm + 6\tabcolsep\relax}|}{" + text + r"}\\"


def lista_linhas(seq, env):
    """Uma linha da longtable por item. Uma única célula gigante não quebra
    entre páginas e deixa a página anterior vazia; com uma linha por item a
    quebra acontece entre os itens. A numeração é preservada via start=."""
    seq = [x for x in (seq or []) if str(x).strip()]
    if not seq:
        return mc4(r"\begin{itemize}\item[] (nenhum item informado)\end{itemize}")
    linhas = []
    for i, x in enumerate(seq, 1):
        opt = f"[start={i}]" if env == "enumerate" else ""
        linhas.append(mc4(f"\\begin{{{env}}}{opt}\\item {esc(x)}\\end{{{env}}}"))
    return "\n".join(linhas)


def render_disciplina(d):
    """Substitui placeholders no bloco DISCIPLINA por valores da disciplina d."""
    mod = d.get("Modalidade", "").lower()
    semi = "semi" in mod
    pres = "X" if (not semi and "presencial" in mod) else " "
    dist = "X" if (not semi and ("distância" in mod or "distancia" in mod)) else " "
    semi = "X" if semi else " "

    ch = d.get("Carga Horária", {})
    def ch_get(k): return ch.get(k, "")

    # Campos opcionais
    perfil = d.get("Perfil", "")
    perfil = perfil.strip() if isinstance(perfil, str) else ""

    objx = (d.get("Objetivo Extencionista") or d.get("Objetivo Extensionista") or "")
    objx = objx.strip() if isinstance(objx, str) else ""

    # Monta bloco apenas se houver conteúdo
    perfil_obj_lines = []
    if perfil or objx:
        perfil_obj_lines.append(mc4(""))
        if perfil:
            perfil_obj_lines.append(mc4(f"Perfil da Comunidade: {esc(perfil)}"))
        if objx:
            perfil_obj_lines.append(mc4(f"Objetivos Extensionistas: {esc(objx)}"))
        perfil_obj_lines.append(mc4(""))
    perfil_obj_block = "\n".join(perfil_obj_lines)

    mapa = {
        "NOME_PTBR": esc(d["Nome (ptBR)"]),
        "NOME_ENUS": esc(d["Nome (enUS)"]),
        "CODIGO":    esc(d["Código"]),
        "DEPARTAMENTO": esc(d["Departamento"]),
        "UNIDADE":   esc(d["Unidade Acadêmica"]),
        "PRESENCIAL": pres,
        "SEMI":       semi,
        "DISTANCIA":  dist,
        "CH_TOTAL": esc(ch_get("Total")),
        "CH_EXT":   esc(ch_get("Extensionista")),
        "CH_TEO":   esc(ch_get("Teórica")),
        "CH_PRA":   esc(ch_get("Prática")),
        "EMENTA":   esc(d["Ementa"]),
        "CONTEUDO":   lista_linhas(d.get("Conteúdo Programático"), "enumerate"),
        "BIB_BASICA": lista_linhas(d.get("Bibliografia Básica"), "itemize"),
        "BIB_COMP":   lista_linhas(d.get("Bibliografia Complementar"), "itemize"),
        "PERFIL_OBJ_BLOCK": perfil_obj_block if perfil_obj_lines else mc4(""),
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
        print("Uso: python json2tex2.py entrada.json [saida.tex] [--no-escape]")
        sys.exit(1)

    in_path  = Path(args[0])
    out_path = Path(args[1]) if len(args) == 2 else in_path.with_suffix(".tex")
    dados = json.loads(in_path.read_text(encoding="utf-8"))

    # Se o JSON antigo (uma única disciplina) for usado,
    # embrulhamos em lista para reutilizar o mesmo fluxo.
    disciplinas = dados.get("Disciplinas", [dados])

    corpo = "".join(render_disciplina(d) for d in disciplinas)

    tex_final = PREAMBLE + corpo + ENDDOC

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tex_final, encoding="utf-8")
    print("Gerado:", out_path)


if __name__ == "__main__":
    main()