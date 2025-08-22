#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gera um arquivo .tex contendo TODOS os Programas de Disciplina listados
no JSON (campo "Disciplinas").  Mantém o layout oficial PROGRAD / UFOP.
"""
# bash python json2tex2.py disciplinas_bia.json ./LaTeXSource/ufop_prog.tex
import json, sys
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
\setlist{noitemsep,leftmargin=*}
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
[{{PRESENCIAL}}] presencial \hspace{1cm}
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
\multicolumn{4}{|p{16cm}|}{{{EMENTA}}}\\
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{4}{|p{16cm}|}{Conteúdo programático:}\\
\multicolumn{4}{|p{16cm}|}{%
\begin{enumerate}{{CONTEUDO}}\end{enumerate}}\\
{{PERFIL_OBJ_BLOCK}}
\hline
\multicolumn{4}{|p{16cm}|}{Bibliografia Básica:}\\
\multicolumn{4}{|p{16cm}|}{%
\begin{itemize}{{BIB_BASICA}}\end{itemize}}\\
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{4}{|p{16cm}|}{Bibliografia Complementar:}\\
\multicolumn{4}{|p{16cm}|}{%
\begin{itemize}{{BIB_COMP}}\end{itemize}}\\
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
def lista_para_itens(seq, cmd="item"):
    """Converte lista Python em \item A \item B ..."""
    return "\n".join(f"\\{cmd} {x}" for x in seq)

def mc4(text):
    """Uma linha de \multicolumn que ocupa 4 colunas com p{16cm}."""
    return r"\multicolumn{4}{|p{16cm}|}{" + text + r"}\\"


def render_disciplina(d):
    """Substitui placeholders no bloco DISCIPLINA por valores da disciplina d."""
    pres = "X" if d["Modalidade"].lower().startswith("presencial") else " "
    dist = "X" if "distância" in d["Modalidade"].lower() else " "

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
            perfil_obj_lines.append(mc4(f"Perfil da Comunidade: {perfil}"))
        if objx:
            perfil_obj_lines.append(mc4(f"Objetivos Extensionistas: {objx}"))
        perfil_obj_lines.append(mc4(""))
    perfil_obj_block = "\n".join(perfil_obj_lines)

    mapa = {
        "NOME_PTBR": d["Nome (ptBR)"],
        "NOME_ENUS": d["Nome (enUS)"],
        "CODIGO":    d["Código"],
        "DEPARTAMENTO": d["Departamento"],
        "UNIDADE":   d["Unidade Acadêmica"],
        "PRESENCIAL": pres,
        "DISTANCIA":  dist,
        "CH_TOTAL": ch_get("Total"),
        "CH_EXT":   ch_get("Extensionista"),
        "CH_TEO":   ch_get("Teórica"),
        "CH_PRA":   ch_get("Prática"),
        "EMENTA":   d["Ementa"],
        "CONTEUDO": lista_para_itens(d["Conteúdo Programático"]),
        "BIB_BASICA": lista_para_itens(d["Bibliografia Básica"]),
        "BIB_COMP":   lista_para_itens(d["Bibliografia Complementar"]),
        "PERFIL_OBJ_BLOCK": perfil_obj_block if perfil_obj_lines else "\multicolumn{4}{|p{16cm}|}{}\\\\",
    }

    bloco = DISCIPLINA
    for k, v in mapa.items():
        bloco = bloco.replace(f"{{{{{k}}}}}", v)
    return bloco


def main():
    if len(sys.argv) not in (2, 3):
        print("Uso: python json2todas_tex.py entrada.json [saida.tex]")
        sys.exit(1)

    in_path  = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) == 3 else in_path.with_suffix(".tex")
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
