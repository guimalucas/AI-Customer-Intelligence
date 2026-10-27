# Feedbacks bancários: classificação estruturada com LLM

Uma caixa de entrada cheia de reclamações é difícil de resumir com uma planilha. Neste projeto, usei uma LLM para transformar 120 feedbacks **sintéticos** em campos que podem ser filtrados: categoria, assunto, sentimento, urgência, resumo, possível causa e ação sugerida.

O foco está no caminho do dado: validar a saída do modelo, continuar uma execução interrompida e conferir onde a classificação divergiu dos rótulos usados para criar os exemplos. Não é uma avaliação de atendimento bancário real.

## Um registro do conjunto

> “Não consigo fazer pix, aparece erro toda vez que confirmo.”

Foi classificado como `pix / erro_ao_realizar_pix`, sentimento `negativo` e urgência `alta`. O modelo também gerou um resumo, uma possível causa e uma ação. Esses últimos campos são sugestões, não diagnósticos verificados.

## Como funciona

1. [`pipeline.py`](pipeline.py) lê `data/customer_feedback.csv` e confere quais IDs já foram concluídos. Se o texto de um ID mudar, ele é processado novamente.
2. [`analyzer.py`](analyzer.py) envia o texto à API da OpenAI e solicita uma resposta estruturada.
3. [`models.py`](models.py) define os valores permitidos e rejeita combinações impossíveis, como `boleto / erro_ao_realizar_pix`.
4. O pipeline salva cada tentativa em `data/feedback_enriched.csv`. Erros ficam registrados e podem ser retomados.
5. [`evaluation.py`](evaluation.py) compara categoria e assunto com os rótulos da geração. IDs sem resultado ou com erro contam no denominador. O [notebook](01_customer_feedback_analysis.ipynb) explora as distribuições e os casos divergentes.

## O que os 120 exemplos mostraram

| Comparação com o rótulo de geração | Acertos |
|---|---:|
| Categoria | 119/120 (99,17%) |
| Assunto | 118/120 (98,33%) |

Há dois casos que merecem leitura. No ID 13, o texto diz apenas que houve falha “ao efetuar o pagamento”; o rótulo de geração era boleto, mas a mensagem não explicita esse meio de pagamento. No ID 66, uma transferência Pix que não concluiu foi classificada como `pix_em_processamento` em vez de `erro_ao_realizar_pix`.

Os rótulos foram definidos **durante a geração dos próprios textos**, sem anotadores independentes. Portanto, essas porcentagens medem concordância neste conjunto pequeno e sintético. Não indicam acurácia em mensagens reais.

## Rodar localmente

```bash
git clone https://github.com/guimalucas/AI-Customer-Intelligence.git
cd AI-Customer-Intelligence
python -m venv .venv
# Ative o ambiente virtual no seu sistema.
pip install -r requirements.txt
python evaluation.py
python -m unittest discover -s tests -v
jupyter notebook
```

Abra o notebook a partir da raiz do repositório. A avaliação e os gráficos usam os CSVs já incluídos e **não fazem chamadas à API**.

Para classificar textos novos, crie um `.env` com `OPENAI_API_KEY=sua_chave`, adicione IDs e feedbacks ao CSV de entrada e rode `python pipeline.py`. O pipeline só exige a chave quando encontra registros pendentes. Chamadas novas podem ter custo.

## Limites

A taxonomia é fechada; problemas fora das categorias atuais precisam de outro tratamento. O conjunto favorece reclamações e não representa a frequência dos assuntos de uma instituição. Sentimento, urgência, causas e ações ainda precisam de avaliação com dados anotados por pessoas antes de qualquer uso operacional.

**Lucas Guimarães** · Engenharia da Computação, FIAP
