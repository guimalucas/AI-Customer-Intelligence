"""Avalia classificações contra rótulos de geração ou de revisão independente."""

import argparse
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
CAMPOS = ("categoria", "assunto", "sentimento", "urgencia")


def metricas_por_classe(avaliacao: pd.DataFrame, campos: tuple[str, ...],
                       sufixo_referencia: str) -> pd.DataFrame:
    """Conta ausências e falhas como falsos negativos da classe esperada."""
    valido = (avaliacao["_merge"] == "both") & (avaliacao["status"] == "sucesso")
    linhas = []
    for campo in campos:
        coluna = f"{campo}_{sufixo_referencia}"
        referencia = avaliacao[coluna]
        previsao = avaliacao[campo].where(valido)
        classes = sorted(set(referencia.dropna()) | set(previsao.dropna()))
        for classe in classes:
            suporte = int(referencia.eq(classe).sum())
            previstos = int(previsao.eq(classe).sum())
            acertos = int((referencia.eq(classe) & previsao.eq(classe)).sum())
            precisao = acertos / previstos if previstos else 0.0
            revocacao = acertos / suporte if suporte else 0.0
            f1 = 2 * acertos / (suporte + previstos) if suporte + previstos else 0.0
            linhas.append({"campo": campo, "classe": classe, "suporte": suporte,
                           "previstos": previstos, "acertos": acertos,
                           "precisao": precisao, "revocacao": revocacao, "f1": f1})
    return pd.DataFrame(linhas)


def avaliar(referencias: Path, predicoes: Path, saida: Path,
            sufixo_referencia: str = "geracao",
            campos: tuple[str, ...] = ("categoria", "assunto"),
            saida_classes: Path | None = None) -> dict:
    if sufixo_referencia not in ("geracao", "revisada") or not campos or any(
        campo not in CAMPOS for campo in campos
    ):
        raise ValueError("Escolha campos conhecidos e uma referência de geração ou revisão.")
    esperado = pd.read_csv(referencias)
    previsto = pd.read_csv(predicoes)
    referencias_necessarias = {f"{campo}_{sufixo_referencia}" for campo in campos}
    if not {"id", *referencias_necessarias}.issubset(esperado.columns):
        raise ValueError("Faltam ID ou colunas de referência para os campos escolhidos.")
    if not {"id", "status", *campos}.issubset(previsto.columns):
        raise ValueError("Faltam ID, status ou campos classificados nas previsões.")
    if esperado["id"].duplicated().any() or previsto["id"].duplicated().any():
        raise ValueError("IDs duplicados invalidam a avaliação.")
    if esperado.empty or esperado[list(referencias_necessarias)].isna().any().any():
        raise ValueError("As referências precisam estar preenchidas antes da avaliação.")

    avaliacao = esperado.merge(
        previsto, on="id", how="left", validate="one_to_one", indicator=True,
        suffixes=("_referencia", ""),
    )
    if "feedback_referencia" in avaliacao and (
        avaliacao.loc[avaliacao["_merge"] == "both", "feedback_referencia"]
        != avaliacao.loc[avaliacao["_merge"] == "both", "feedback"]
    ).any():
        raise ValueError("O texto mudou desde a revisão; não compare rótulos desatualizados.")
    # Falhas e ausências entram no denominador da respectiva classe.
    valido = (avaliacao["_merge"] == "both") & (avaliacao["status"] == "sucesso")
    for campo in campos:
        avaliacao[f"{campo}_correto"] = (
            valido & (avaliacao[f"{campo}_{sufixo_referencia}"] == avaliacao[campo])
        )
    por_classe = metricas_por_classe(avaliacao, campos, sufixo_referencia)
    metrics: dict = {
        "total": len(avaliacao),
        "processados": int(valido.sum()),
    }
    for campo in campos:
        metrics[f"acuracia_{campo}"] = float(avaliacao[f"{campo}_correto"].mean())
        metrics[f"macro_f1_{campo}"] = float(
            por_classe.loc[por_classe["campo"] == campo, "f1"].mean()
        )
    saida.parent.mkdir(parents=True, exist_ok=True)
    avaliacao.drop(columns="_merge").to_csv(saida, index=False, encoding="utf-8-sig")
    if saida_classes is not None:
        saida_classes.parent.mkdir(parents=True, exist_ok=True)
        por_classe.to_csv(saida_classes, index=False, encoding="utf-8-sig")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", type=Path, default=BASE / "data/generation_metadata.csv")
    parser.add_argument("--predictions", type=Path, default=BASE / "data/feedback_enriched.csv")
    parser.add_argument("--output", type=Path, default=BASE / "data/evaluation_results.csv")
    parser.add_argument("--reference-suffix", choices=("geracao", "revisada"), default="geracao")
    parser.add_argument("--fields", nargs="+", choices=CAMPOS, default=("categoria", "assunto"))
    args = parser.parse_args()
    metrics = avaliar(args.references, args.predictions, args.output,
                      sufixo_referencia=args.reference_suffix, campos=tuple(args.fields),
                      saida_classes=args.output.with_name(args.output.stem + "_classes.csv"))
    print(f"Avaliados: {metrics['total']}; processados: {metrics['processados']}")
    for campo in args.fields:
        print(f"{campo}: acurácia {metrics[f'acuracia_{campo}']:.2%}; "
              f"F1 macro {metrics[f'macro_f1_{campo}']:.2%}")


if __name__ == "__main__":
    main()
