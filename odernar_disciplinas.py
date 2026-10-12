#!/usr/bin/env python3
"""Ordena lexicograficamente, pelo código, as disciplinas de um arquivo JSON.

Aceita os dois esquemas usados no projeto:
  - português: chave "Código"
  - inglês:    chave "Code"

O arquivo de entrada pode ter um destes formatos:
  - uma lista de disciplinas;
  - um objeto com uma chave que contém a lista, como {"Disciplinas": [...]}
    (a mesma estrutura é preservada na saída);
  - um único objeto de disciplina (tratado como uma lista de um elemento).

Uso:
    python ordenar_disciplinas.py entrada.json
    python ordenar_disciplinas.py entrada.json -o saida.json
"""

import argparse
import json
import sys
from pathlib import Path

CHAVES_CODIGO = ("Código", "Code")


def obter_codigo(disciplina: dict, indice: int) -> str:
    for chave in CHAVES_CODIGO:
        if chave in disciplina:
            return str(disciplina[chave]).strip()
    nome = disciplina.get("Nome (ptBR)") or disciplina.get("Name (Portuguese)") or "?"
    raise KeyError(
        f"Disciplina na posição {indice} ('{nome}') não possui "
        f"nenhuma das chaves de código {CHAVES_CODIGO}."
    )


def carregar(caminho: Path):
    """Retorna (lista_de_disciplinas, chave_do_invólucro ou None)."""
    with caminho.open(encoding="utf-8") as f:
        dados = json.load(f)
    if isinstance(dados, list):
        return dados, None
    if isinstance(dados, dict):
        if any(c in dados for c in CHAVES_CODIGO):
            return [dados], None
        listas = [k for k, v in dados.items() if isinstance(v, list)]
        if len(listas) == 1 and len(dados) == 1:
            return dados[listas[0]], listas[0]
        raise ValueError(
            "Objeto de nível superior não reconhecido: esperava uma disciplina "
            "ou um único campo contendo a lista de disciplinas."
        )
    raise ValueError("O JSON deve conter uma lista de disciplinas ou um objeto.")


def ordenar(disciplinas: list) -> list:
    indexadas = [(obter_codigo(d, i), d) for i, d in enumerate(disciplinas)]
    # sorted é estável: disciplinas com o mesmo código mantêm a ordem original
    return [d for _, d in sorted(indexadas, key=lambda par: par[0])]


def avisar_duplicatas(disciplinas: list) -> None:
    vistos = {}
    for i, d in enumerate(disciplinas):
        codigo = obter_codigo(d, i)
        vistos.setdefault(codigo, []).append(i)
    for codigo, posicoes in vistos.items():
        if len(posicoes) > 1:
            print(
                f"Aviso: código {codigo} repetido nas posições {posicoes}.",
                file=sys.stderr,
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ordena disciplinas de um JSON pelo código (ordem lexicográfica)."
    )
    parser.add_argument("entrada", type=Path, help="JSON de disciplinas")
    parser.add_argument(
        "-o",
        "--saida",
        type=Path,
        default=None,
        help="JSON de saída (padrão: <entrada>_ordenado.json)",
    )
    args = parser.parse_args()

    saida = args.saida or args.entrada.with_name(
        f"{args.entrada.stem}_ordenado{args.entrada.suffix}"
    )

    try:
        disciplinas, involucro = carregar(args.entrada)
        avisar_duplicatas(disciplinas)
        resultado = ordenar(disciplinas)
        conteudo = {involucro: resultado} if involucro else resultado
    except (OSError, ValueError, KeyError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    with saida.open("w", encoding="utf-8") as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"{len(resultado)} disciplinas ordenadas em {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())