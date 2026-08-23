import os
import pandas as pd

from analyzer import analisar_feedback


ARQUIVO_ENTRADA = "data/customer_feedback.csv"
ARQUIVO_SAIDA = "data/feedback_enriched.csv"



df = pd.read_csv(ARQUIVO_ENTRADA)

total = len(df)



if os.path.exists(ARQUIVO_SAIDA):

    df_resultados = pd.read_csv(ARQUIVO_SAIDA)

    resultados = df_resultados.to_dict("records")

    ids_processados = set(
        df_resultados.loc[
            df_resultados["status"] == "sucesso",
            "id"
        ]
    )

    print(
        f"Processamento anterior encontrado: "
        f"{len(ids_processados)} feedbacks concluídos."
    )

else:

    resultados = []
    ids_processados = set()

    print("Nenhum processamento anterior encontrado.")



for i, linha in df.iterrows():

    feedback_id = linha["id"]
    feedback = linha["feedback"]

    # Pula feedback já processado com sucesso
    if feedback_id in ids_processados:
        print(
            f"Pulando {i + 1}/{total} "
            f"(ID {feedback_id} já processado)"
        )
        continue

    print(f"Processando {i + 1}/{total}...")

    try:

        analise = analisar_feedback(feedback)

        resultado = {
            "id": feedback_id,
            "feedback": feedback,
            "categoria": analise.categoria.value,
            "assunto": analise.assunto.value,
            "sentimento": analise.sentimento.value,
            "urgencia": analise.urgencia.value,
            "resumo": analise.resumo,
            "possivel_causa": analise.possivel_causa,
            "acao_recomendada": analise.acao_recomendada,
            "status": "sucesso",
            "erro": None
        }

    except Exception as erro:

        resultado = {
            "id": feedback_id,
            "feedback": feedback,
            "categoria": None,
            "assunto": None,
            "sentimento": None,
            "urgencia": None,
            "resumo": None,
            "possivel_causa": None,
            "acao_recomendada": None,
            "status": "erro",
            "erro": str(erro)
        }

    resultados = [
        r for r in resultados
        if r["id"] != feedback_id
    ]

    # Adiciona resultado mais recente
    resultados.append(resultado)

    # Salva imediatamente
    pd.DataFrame(resultados).to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig"
    )



df_resultados = pd.DataFrame(resultados)

sucessos = (df_resultados["status"] == "sucesso").sum()
erros = (df_resultados["status"] == "erro").sum()

print("\nProcessamento finalizado.")
print(f"Sucessos: {sucessos}")
print(f"Erros: {erros}")