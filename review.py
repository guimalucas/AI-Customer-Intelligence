"""Prepara amostra cega e estratificada de textos para revisão por pessoas."""

import argparse
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent


def preparar_amostra(textos: Path, metadados: Path, saida: Path,
                     por_categoria: int = 6, semente: int = 4587) -> pd.DataFrame:
    origem = pd.read_csv(textos)
    geracao = pd.read_csv(metadados)
    if por_categoria < 1 or origem["id"].duplicated().any() or geracao["id"].duplicated().any():
        raise ValueError("Amostra inválida: IDs devem ser únicos e tamanho positivo.")
    selecionados = geracao.groupby("categoria_geracao", group_keys=False).sample(
        n=por_categoria, random_state=semente
    )[["id"]]
    amostra = origem.merge(selecionados, on="id", validate="one_to_one").sort_values("id")
    if len(amostra) != len(selecionados):
        raise ValueError("Alguns IDs selecionados não existem no arquivo de feedbacks.")
    # O revisor só vê o texto; os rótulos da geração e do modelo ficam ocultos.
    for coluna in ("categoria_revisada", "assunto_revisado", "sentimento_revisado",
                   "urgencia_revisada", "anotador", "observacao"):
        amostra[coluna] = ""
    saida.parent.mkdir(parents=True, exist_ok=True)
    amostra.to_csv(saida, index=False, encoding="utf-8-sig")
    return amostra


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--texts", type=Path, default=BASE / "data/customer_feedback.csv")
    parser.add_argument("--metadata", type=Path, default=BASE / "data/generation_metadata.csv")
    parser.add_argument("--output", type=Path, default=BASE / "data/revisao_manual_template.csv")
    parser.add_argument("--per-category", type=int, default=6)
    args = parser.parse_args()
    amostra = preparar_amostra(args.texts, args.metadata, args.output, args.per_category)
    print(f"{len(amostra)} textos separados para revisão cega; rótulos ainda não preenchidos.")


if __name__ == "__main__":
    main()
