#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
json2disciplina_tex.py  –  Gera disciplina.tex no formato da PROGRAD
(versão corrigida: \chk{X} / \chk{})
"""

import json, sys
from pathlib import Path
from textwrap import dedent

TEMPLATE = dedent(r"""
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{geometry}
\usepackage{longtable} 
\usepackage{graphicx}
\usepackage{multirow}
\geometry{a4paper,margin=2cm}
\usepackage{enumitem,tabularx,setspace,ragged2e}

\newcommand{\chk}[1]{\ifx#1X\setlength\fboxsep{1pt}\fbox{\rule{1.2ex}{0pt}X}%
\else\setlength\fboxsep{1pt}\fbox{\rule{1.2ex}{0pt}\rule{1.2ex}{0pt}}\fi}

\setlist{noitemsep,leftmargin=*}
\renewcommand\arraystretch{1.15}

\begin{document}
\pagestyle{empty}

\begin{center}
\begin{tabular}{lccr}
 \multirow{3}{*}{\includegraphics[height=2.7cm]{brasao.png}} & \multicolumn{2}{c}{\bfseries UNIVERSIDADE FEDERAL DE OURO PRETO} & \ \ \ \ \ \multirow{3}{*}{\includegraphics[height=2.7cm]{ufop.png}} \\
 & \multicolumn{2}{c}{\bfseries PRÓ-REITORIA DE GRADUAÇÃO} & \\
 & \multicolumn{2}{c}{} & \\
 & \multicolumn{2}{c}{\Large\bfseries PROGRAMA DE DISCIPLINA} & \\
\end{tabular}
\end{center}

\begin{center}
\begin{longtable}{|p{4cm}|p{4cm}|p{4cm}|p{4cm}|}  % repeats {c|} 18 times
\hline
\multicolumn{3}{|p{12cm}|}{Nome do Componente Currigcular em Português:} & \multicolumn{1}{p{4cm}|}{Código:} \\ 
\multicolumn{3}{|p{12cm}|}{\textbf{{{NOME_PTBR}}}} &  \textbf{{{CODIGO}}}\\ 
\multicolumn{3}{|p{12cm}|}{Nome do Componente Currigcular em Inglês:} &  \\ 
\multicolumn{3}{|p{12cm}|}{\textbf{{{NOME_ENUS}}}} &  \\ 
\hline
\multicolumn{3}{|p{12cm}|}{Nome e Sigla do Departamento} & Unidade Acadêmica: \\ 
\multicolumn{3}{|p{12cm}|}{Departamento de Computação (DECOM)} & ICEB \\ 
\hline
\multicolumn{4}{|p{16cm}|}{Modalidade de Oferta: [{{PRESENCIAL}}] presencial \hspace{1cm} [{{DISTANCIA}}] à distância}\\
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{2}{|p{8cm}|}{Carga horária semestral} & \multicolumn{2}{p{8cm}|}{Carga horária semanal}\\
\multicolumn{2}{|p{8cm}|}{} & \multicolumn{2}{p{8cm}|}{}\\
\hline
\multicolumn{1}{|p{4cm}|}{Total} & \multicolumn{1}{p{4cm}|}{Extencionista} &  \multicolumn{1}{p{4cm}|}{Teórica} &  \multicolumn{1}{p{4cm}|}{Prática} \\
\multicolumn{1}{|p{4cm}|}{{{CH_TOTAL}} horas} & \multicolumn{1}{p{4cm}|}{{{CH_EXT}} horas} &  \multicolumn{1}{p{4cm}|}{{{CH_TEO}} horas/aula} &  \multicolumn{1}{p{4cm}|}{{{CH_PRA}} horas/aula} \\
\hline
\multicolumn{4}{|p{16cm}|}{Ementa:}\\
\multicolumn{4}{|p{16cm}|}{{{EMENTA}}}\\
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{4}{|p{16cm}|}{Conteúdo programático:}\\
\multicolumn{4}{|p{16cm}|}{\begin{enumerate}
{{CONTEUDO}}
\end{enumerate}}\\
\multicolumn{4}{|p{16cm}|}{}\\
\hline
\multicolumn{4}{|p{16cm}|}{Bibliografia Básica:}\\
\multicolumn{4}{|p{16cm}|}{\begin{itemize}
{{BIB_BASICA}}
\end{itemize}}\\
\multicolumn{4}{|p{16cm}|}{} \\
\hline
\multicolumn{4}{|p{16cm}|}{Bibliografia Complementar:}\\
\multicolumn{4}{|p{16cm}|}{\begin{itemize}
{{BIB_COMP}}
\end{itemize}}\\
\multicolumn{4}{|p{16cm}|}{} \\
\hline
\end{longtable}
\end{center}


\end{document}

""").lstrip()


def main():
    if len(sys.argv) != 2:
        print("Uso: python json2disciplina_tex.py disciplina.json")
        sys.exit(1)

    jpath = Path(sys.argv[1])
    data  = json.loads(jpath.read_text(encoding="utf-8"))

    pres = "x" if data["Modalidade"].lower().startswith("presencial") else " "
    dist = "x" if "distân" in data["Modalidade"].lower() else " "

    def join_list(lst, cmd="item"):
        return "\n".join(f"\\{cmd} {x}" for x in lst)

    ch = data.get("Carga Horária", {})
    def ch_get(k): return ch.get(k, "")

    repl = {
        "NOME_PTBR": data["Nome (ptBR)"],
        "NOME_ENUS": data["Nome (enUS)"],
        "CODIGO":    data["Código"],
        "DEPARTAMENTO": data["Departamento"],
        "UNIDADE":   data["Unidade Acadêmica"],
        "PRESENCIAL": pres,
        "DISTANCIA":  dist,
        "CH_TOTAL": ch_get("Total"),
        "CH_EXT":   ch_get("Extensionista"),
        "CH_TEO":   ch_get("Teórica"),
        "CH_PRA":   ch_get("Prática"),
        "EMENTA":   data["Ementa"],
        "CONTEUDO": join_list(data["Conteúdo Programático"]),
        "BIB_BASICA": join_list(data["Bibliografia Básica"]),
        "BIB_COMP":   join_list(data["Bibliografia Complementar"]),
    }

    tex = TEMPLATE
    for k, v in repl.items():
        tex = tex.replace(f"{{{{{k}}}}}", v)

    tpath = jpath.with_suffix(".tex")
    tpath.write_text(tex, encoding="utf-8")
    print("LaTeX salvo em:", tpath)


if __name__ == "__main__":
    main()
