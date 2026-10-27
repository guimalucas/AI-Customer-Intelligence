"""Enriquece feedbacks e retoma somente os registros ainda não concluídos."""

import argparse
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
COLUMNS = [
    "id", "feedback", "categoria", "assunto", "sentimento", "urgencia",
    "resumo", "possivel_causa", "acao_recomendada", "status", "erro",
]


def processar(entrada: Path, saida: Path, analisar=None) -> tuple[int, int]:
    origem = pd.read_csv(entrada)
    if not {"id", "feedback"}.issubset(origem) or origem["id"].duplicated().any():
        raise ValueError("A entrada deve ter colunas id e feedback, com IDs únicos.")

    if saida.exists():
        anteriores = pd.read_csv(saida).to_dict("records")
        ids_entrada = set(origem["id"])
        # Conserva somente a última tentativa de cada ID ainda presente na entrada.
        atuais = {r["id"]: r for r in anteriores if r["id"] in ids_entrada}
    else:
        atuais = {}

    textos_atuais = origem.set_index("id")["feedback"].to_dict()
    concluidos = {
        id_ for id_, r in atuais.items()
        if r.get("status") == "sucesso" and r.get("feedback") == textos_atuais[id_]
    }
    pendentes = origem.loc[~origem["id"].isin(concluidos)]
    if not pendentes.empty and analisar is None:
        # A chave só é exigida se houver alguma chamada à API.
        from analyzer import analisar_feedback
        analisar = analisar_feedback

    for _, linha in pendentes.iterrows():
        id_, feedback = linha["id"], linha["feedback"]
        try:
            analise = analisar(feedback)
            resultado = {
                "id": id_, "feedback": feedback,
                "categoria": analise.categoria.value, "assunto": analise.assunto.value,
                "sentimento": analise.sentimento.value, "urgencia": analise.urgencia.value,
                "resumo": analise.resumo, "possivel_causa": analise.possivel_causa,
                "acao_recomendada": analise.acao_recomendada,
                "status": "sucesso", "erro": None,
            }
        except Exception as exc:
            resultado = {key: None for key in COLUMNS}
            resultado.update(id=id_, feedback=feedback, status="erro", erro=str(exc))

        atuais[id_] = resultado
        saida.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([atuais[id_] for id_ in origem["id"] if id_ in atuais],
                     columns=COLUMNS).to_csv(saida, index=False, encoding="utf-8-sig")

    sucessos = sum(r["status"] == "sucesso" for r in atuais.values())
    erros = sum(r["status"] == "erro" for r in atuais.values())
    return sucessos, erros


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=BASE / "data/customer_feedback.csv")
    parser.add_argument("--output", type=Path, default=BASE / "data/feedback_enriched.csv")
    args = parser.parse_args()
    sucessos, erros = processar(args.input, args.output)
    print(f"Processamento finalizado: {sucessos} sucessos; {erros} erros.")


if __name__ == "__main__":
    main()
