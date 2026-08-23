import pandas as pd




df_pred = pd.read_csv("data/feedback_enriched.csv")

df_true = pd.read_csv("data/generation_metadata.csv")




df_avaliacao = df_true.merge(
    df_pred,
    on="id",
    how="inner"
)




df_avaliacao["categoria_correta"] = (
    df_avaliacao["categoria_geracao"]
    == df_avaliacao["categoria"]
)

df_avaliacao["assunto_correto"] = (
    df_avaliacao["assunto_geracao"]
    == df_avaliacao["assunto"]
)




acuracia_categoria = df_avaliacao["categoria_correta"].mean()

acuracia_assunto = df_avaliacao["assunto_correto"].mean()




print("\n===== AVALIAÇÃO DO CLASSIFICADOR =====")

print(f"\nTotal de feedbacks avaliados: {len(df_avaliacao)}")

print(
    f"Acurácia de categoria: "
    f"{acuracia_categoria * 100:.2f}%"
)

print(
    f"Acurácia de assunto: "
    f"{acuracia_assunto * 100:.2f}%"
)




erros_categoria = df_avaliacao[
    df_avaliacao["categoria_correta"] == False
]

erros_assunto = df_avaliacao[
    df_avaliacao["assunto_correto"] == False
]


print(f"\nErros de categoria: {len(erros_categoria)}")
print(f"Erros de assunto: {len(erros_assunto)}")



df_avaliacao.to_csv(
    "data/evaluation_results.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nResultados salvos em data/evaluation_results.csv")

print("\n===== ERROS DE CATEGORIA =====")

for _, linha in erros_categoria.iterrows():
    print("\nID:", linha["id"])
    print("Feedback:", linha["feedback"])
    print("Esperado:", linha["categoria_geracao"])
    print("LLM:", linha["categoria"])


print("\n===== ERROS DE ASSUNTO =====")

for _, linha in erros_assunto.iterrows():
    print("\nID:", linha["id"])
    print("Feedback:", linha["feedback"])
    print("Esperado:", linha["assunto_geracao"])
    print("LLM:", linha["assunto"])