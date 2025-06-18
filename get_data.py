"""
Extrai informações de um “Programa de Disciplina” em PDF
e grava tudo num CSV, incluindo os quatro campos de
Carga Horária (Total, Extensionista, Teórica, Prática).

Dependências:
    pip install pdfplumber pandas
"""

import re
import pdfplumber
import pandas as pd


# ----------------------------------------------------------------------
# 1. Bloco auxiliar: pega as quatro cargas horárias mesmo com quebras
#    de linha ou variações de acentuação.
# ----------------------------------------------------------------------
def extract_carga_horaria(text: str) -> dict:
    """
    Retorna um dicionário com:
        • Carga Horária Total
        • Carga Horária Extensionista
        • Carga Horária Teórica
        • Carga Horária Prática
    O regex aceita quantas quebras de linha forem necessárias entre
    o rótulo (Total, Extensionista, Teórica, Prática) e o valor.
    """
    patt = re.compile(
        r"(Total|Extensionista|Te[oó]rica|Pr[aá]tica)"  # rótulo
        r"\s*[\r\n]+\s*"                                 # pula linhas/brancos
        r"(\d{1,3})\s*horas(/aula)?",                    # valor + unidade
        flags=re.IGNORECASE,
    )
    mapping = {
        "total": "Carga Horária Total",
        "extensionista": "Carga Horária Extensionista",
        "teórica": "Carga Horária Teórica",
        "teorica": "Carga Horária Teórica",   # sem acento
        "prática": "Carga Horária Prática",
        "pratica": "Carga Horária Prática",   # sem acento
    }

    resultado = {v: "" for v in mapping.values()}  # default vazio

    for rotulo, valor, aula in patt.findall(text):
        chave = mapping[rotulo.lower()]
        unidade = "horas/aula" if aula else "horas"
        resultado[chave] = f"{valor} {unidade}"

    return resultado


# ----------------------------------------------------------------------
# 2. Função principal: abre o PDF, extrai texto e monta o dicionário.
# ----------------------------------------------------------------------
def get_data_from_pdf(filename: str) -> dict:
    # Carrega o texto completo do PDF
    with pdfplumber.open(filename) as pdf:
        raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # Campos simples via regex
    campos_regex = {
        "Nome (ptBR)": r"Nome do Componente Curricular em português:\s*(.+)",
        "Nome (enUS)": r"Nome do Componente Curricular em inglês:\s*(.+)",
        "Código": r"Código:\s*(\w+)",
        "Departamento": r"Nome e sigla do departamento:\s*(.+)",
        "Unidade Acadêmica": r"Unidade Acadêmica:\s*(.+)",
        "Modalidade": (
            r"Modalidade de oferta:[^\n]*\[\s*[xX]\s*\]\s*"
            r"(presencial|a distância)"
        ),
        "Ementa": r"Ementa:(.*?)Conteúdo programático:",
        "Conteúdo Programático": r"Conteúdo programático:(.*?)Bibliografia básica:",
        "Bibliografia Básica": r"Bibliografia básica:(.*?)Bibliografia complementar:",
        "Bibliografia Complementar": r"Bibliografia complementar:(.*)",
    }

    dados = {}

    for campo, regex in campos_regex.items():
        m = re.search(regex, raw_text, flags=re.DOTALL | re.IGNORECASE)
        if m:
            valor = m.group(1).strip()

            # Normaliza listas longas em uma linha (conteúdo / bibliografia)
            if campo.startswith(("Conteúdo", "Bibliografia")):
                valor = re.sub(r"\s*[\r\n]+\s*", "; ", valor).strip("; ")
            else:
                valor = " ".join(valor.split())

            dados[campo] = valor
        else:
            dados[campo] = ""

    # Adiciona carga horária
    dados.update(extract_carga_horaria(raw_text))

    return dados


# ----------------------------------------------------------------------
# 3. Executa para um arquivo e gera CSV.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    PDF = "BCC101.pdf"          # troque aqui pelo nome desejado
    CSV = "disciplina.csv"      # nome do CSV de saída

    info = get_data_from_pdf(PDF)

    pd.DataFrame(info.items(), columns=["Campo", "Informação"]) \
      .to_csv(CSV, index=False, encoding="utf-8")

    print(f"CSV gerado com sucesso: {CSV}")
