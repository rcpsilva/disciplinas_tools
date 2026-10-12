#!/usr/bin/env python3
"""Ordena lexicograficamente, pelo código, as disciplinas de um arquivo JSON.

Aceita os dois esquemas usados no projeto:
  - português: chave "Código"
  - inglês:    chave "Code"

O arquivo de entrada pode ser uma lista de disciplinas ou um único objeto
(tratado como uma lista de um elemento). A saída é sempre uma lista.

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


def carregar(caminho: Path) -> list:
    with caminho.open(encoding="utf-8") as f:
        dados = json.load(f)
    if isinstance(dados, dict):
        return [dados]
    if isinstance(dados, list):
        return dados
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
        disciplinas = carregar(args.entrada)
        avisar_duplicatas(disciplinas)
        resultado = ordenar(disciplinas)
    except (OSError, ValueError, KeyError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    with saida.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"{len(resultado)} disciplinas ordenadas em {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())