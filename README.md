# Feedbacks bancários com classificação estruturada

Classifiquei 120 mensagens bancárias **sintéticas** com uma LLM. Cada registro recebe categoria, assunto, sentimento, urgência, resumo, possível causa e ação sugerida. O [notebook](01_customer_feedback_analysis.ipynb) mostra as distribuições e examina os casos em que a classificação divergiu do rótulo usado para criar o texto.

O pipeline valida a combinação entre categoria e assunto, salva as respostas à medida que chegam e retoma uma execução interrompida sem repetir registros concluídos.

## Exemplo

> “Não consigo fazer pix, aparece erro toda vez que confirmo.”

O resultado foi `pix / erro_ao_realizar_pix`, sentimento `negativo` e urgência `alta`. A possível causa e a ação sugerida são texto gerado a partir da mensagem, não uma verificação do que ocorreu no banco.

## Fluxo

1. [`pipeline.py`](pipeline.py) lê `data/customer_feedback.csv` e confere quais IDs já foram concluídos. Se o texto de um ID mudar, ele é processado novamente.
2. [`analyzer.py`](analyzer.py) envia o texto à API da OpenAI e solicita uma resposta estruturada.
3. [`models.py`](models.py) define os valores permitidos e rejeita combinações impossíveis, como `boleto / erro_ao_realizar_pix`.
4. O pipeline salva cada tentativa em `data/feedback_enriched.csv`. Erros ficam registrados e podem ser retomados.
5. [`evaluation.py`](evaluation.py) compara categoria e assunto com os rótulos da geração e calcula precisão, revocação e F1 por classe. IDs ausentes ou com erro permanecem no denominador.

## Resultados nos 120 textos

| Comparação com o rótulo de geração | Acertos |
|---|---:|
| Categoria | 119/120 (99,17%) |
| Assunto | 118/120 (98,33%) |

No **ID 13**, a mensagem diz que houve falha “ao efetuar o pagamento”, sem informar que era um boleto, embora esse seja o rótulo da geração. No **ID 66**, o Pix que “não conclui” recebeu o assunto `pix_em_processamento` em vez de `erro_ao_realizar_pix`. Os dois textos e as classificações aparecem no notebook.

O [relatório por classe](data/evaluation_results_classes.csv) informa o tamanho de cada grupo: `boleto` teve **14 acertos em 15 textos**; alguns assuntos aparecem apenas uma ou duas vezes.

Os rótulos de referência acompanharam a criação dos textos. Os percentuais acima medem concordância **nesta base sintética**, sem revisão humana independente; não são uma taxa de acerto para mensagens reais. A amostra concentra reclamações, e a taxonomia aceita apenas as categorias listadas em [`models.py`](models.py). Sentimento, urgência, causas e ações sugeridas não foram comparados com respostas anotadas por pessoas.

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

### Revisão manual

`python review.py` gera [`data/revisao_manual_template.csv`](data/revisao_manual_template.csv) com 36 textos, seis por categoria de geração. A planilha mostra **somente os textos**: as colunas `categoria_revisada`, `assunto_revisado`, `sentimento_revisado` e `urgencia_revisada` estão vazias para preenchimento sem consultar os rótulos originais nem as previsões. O campo `observacao` serve para registrar textos ambíguos ou fora das categorias.

Com as colunas preenchidas, a comparação é executada assim:

```bash
python evaluation.py --references data/revisao_manual_template.csv \
  --reference-suffix revisada --fields categoria assunto sentimento urgencia \
  --output data/revisao_manual_resultados.csv
```

O avaliador recusa rótulos vazios ou textos alterados após a revisão. O arquivo incluído no repositório é apenas o formulário, sem respostas humanas.

Para classificar textos novos, crie um `.env` com `OPENAI_API_KEY=sua_chave`, adicione IDs e feedbacks ao CSV de entrada e rode `python pipeline.py`. O pipeline só exige a chave quando encontra registros pendentes. Chamadas novas podem ter custo.

**Lucas Guimarães** · Engenharia da Computação, FIAP
