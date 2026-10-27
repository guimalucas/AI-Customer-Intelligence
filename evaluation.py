"""Compara os rótulos do modelo com os rótulos usados na geração sintética."""

import argparse
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent


def avaliar(referencias: Path, predicoes: Path, saida: Path) -> dict:
    esperado = pd.read_csv(referencias)
    previsto = pd.read_csv(predicoes)
    if esperado["id"].duplicated().any() or previsto["id"].duplicated().any():
        raise ValueError("IDs duplicados invalidam a avaliação.")

    avaliacao = esperado.merge(
        previsto, on="id", how="left", validate="one_to_one", indicator=True
    )
    # Falhas e ausências contam como erros; o inner join anterior as omitia.
    valido = (avaliacao["_merge"] == "both") & (avaliacao["status"] == "sucesso")
    for campo in ("categoria", "assunto"):
        avaliacao[f"{campo}_correto"] = (
            valido & (avaliacao[f"{campo}_geracao"] == avaliacao[campo])
        )
    metrics = {
        "total": len(avaliacao),
        "processados": int(valido.sum()),
        "acuracia_categoria": float(avaliacao["categoria_correto"].mean()),
        "acuracia_assunto": float(avaliacao["assunto_correto"].mean()),
    }
    saida.parent.mkdir(parents=True, exist_ok=True)
    avaliacao.drop(columns="_merge").to_csv(saida, index=False, encoding="utf-8-sig")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", type=Path, default=BASE / "data/generation_metadata.csv")
    parser.add_argument("--predictions", type=Path, default=BASE / "data/feedback_enriched.csv")
    parser.add_argument("--output", type=Path, default=BASE / "data/evaluation_results.csv")
    args = parser.parse_args()
    metrics = avaliar(args.references, args.predictions, args.output)
    print(f"Avaliados: {metrics['total']}; processados: {metrics['processados']}")
    print(f"Acurácia de categoria: {metrics['acuracia_categoria']:.2%}")
    print(f"Acurácia de assunto: {metrics['acuracia_assunto']:.2%}")


if __name__ == "__main__":
    main()
