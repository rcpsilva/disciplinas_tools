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
\geometry{a4paper,margin=2.5cm}
\usepackage{enumitem,tabularx,setspace,ragged2e}

\newcommand{\chk}[1]{\ifx#1X\setlength\fboxsep{1pt}\fbox{\rule{1.2ex}{0pt}X}%
\else\setlength\fboxsep{1pt}\fbox{\rule{1.2ex}{0pt}\rule{1.2ex}{0pt}}\fi}

\setlist{noitemsep,leftmargin=*}
\renewcommand\arraystretch{1.15}

\begin{document}
\begin{center}
\bfseries UNIVERSIDADE FEDERAL DE OURO PRETO\\
PRÓ-REITORIA DE GRADUAÇÃO\\[1.2em]
{\Large\bfseries PROGRAMA DE DISCIPLINA}\\[2em]
\end{center}

\begin{flushleft}
\begin{tabularx}{\textwidth}{@{}lX@{}}
\textbf{Nome do Componente Curricular em português:} & {{NOME_PTBR}}\\
\textbf{Nome do Componente Curricular em inglês:}    & {{NOME_ENUS}}\\
\textbf{Código:}                                     & {{CODIGO}}\\
\textbf{Nome e sigla do departamento:}               & {{DEPARTAMENTO}}\\
\textbf{Unidade Acadêmica:}                          & {{UNIDADE}}\\
\end{tabularx}
\end{flushleft}

\vspace{0.8em}
\noindent\textbf{Modalidade de oferta:}\hspace{1.5em}
\chk{PRESENCIAL} presencial \hspace{2.5cm}
\chk{DISTANCIA}  a distância

\vspace{1.5em}
\noindent%
\begin{minipage}[t]{0.48\textwidth}
\raggedright\textbf{Carga horária semestral}\par
\vspace{0.3em}\small
Total\\ {{CH_TOTAL}}\medskip\\
Extensionista\\ {{CH_EXT}}\medskip\\
Teórica\\ {{CH_TEO}}\medskip\\
Prática\\ {{CH_PRA}}
\end{minipage}\hfill
\begin{minipage}[t]{0.48\textwidth}
\raggedright\textbf{Carga horária semanal}\par
\vspace{0.3em}\small
\strut
\end{minipage}

\section*{Ementa}
{{EMENTA}}

\section*{Conteúdo programático}
\begin{enumerate}
{{CONTEUDO}}
\end{enumerate}

\section*{Bibliografia básica}
\begin{itemize}
{{BIB_BASICA}}
\end{itemize}

\section*{Bibliografia complementar}
\begin{itemize}
{{BIB_COMP}}
\end{itemize}

\end{document}
""").lstrip()


def main():
    if len(sys.argv) != 2:
        print("Uso: python json2disciplina_tex.py disciplina.json")
        sys.exit(1)

    jpath = Path(sys.argv[1])
    data  = json.loads(jpath.read_text(encoding="utf-8"))

    pres = "X" if data["Modalidade"].lower().startswith("presencial") else ""
    dist = "X" if "distân" in data["Modalidade"].lower() else ""

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
