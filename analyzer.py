import os
from dotenv import load_dotenv
from openai import OpenAI
from models import AnaliseFeedback

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY não encontrada.")

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
Você analisa feedbacks de clientes de uma instituição financeira.

Classifique o feedback seguindo rigorosamente o schema fornecido.

TAXONOMIA:

pix:
- pix_estornado
- pix_nao_reconhecido
- pix_nao_recebido
- problema_chave_pix
- erro_ao_realizar_pix
- pix_em_processamento

cartao_credito:
- cartao_bloqueado
- problema_limite
- compra_recusada
- compra_nao_reconhecida
- cobranca_duplicada
- problema_fatura

aplicativo:
- problema_login
- problema_documento
- problema_reconhecimento_facial
- erro_aplicativo
- duvida_aplicativo

boleto:
- pagamento_nao_reconhecido
- erro_ao_pagar
- boleto_vencido
- pagamento_duplicado
- cobranca_incorreta

emprestimo:
- parcela_incorreta
- cobranca_indevida
- dificuldade_contratacao
- problema_quitacao
- duvida_juros
- renegociacao

atendimento:
- dificuldade_ser_atendido
- atendimento_nao_resolutivo
- reclamacao_atendente
- elogio_atendimento

O assunto escolhido deve obrigatoriamente pertencer à categoria escolhida.

REGRAS DE SENTIMENTO:
- muito_positivo: satisfação intensa, entusiasmo ou elogio forte explícito.
- positivo: satisfação ou aprovação moderada.
- neutro: não demonstra claramente satisfação nem insatisfação.
- negativo: demonstra insatisfação ou frustração moderada.
- muito_negativo: demonstra raiva, indignação, desespero ou forte insatisfação explícita.

Não deduza o sentimento pela gravidade do problema.
Considere apenas como o cliente se expressa.

REGRAS DE URGÊNCIA:
- baixa: dúvida, elogio, solicitação informativa ou inconveniente menor.
- media: existe um problema real, mas os serviços financeiros essenciais continuam utilizáveis e não há risco financeiro imediato.
- alta: uma funcionalidade financeira importante está indisponível ou existe um problema financeiro relevante que exige resolução rápida.
- critica: existe possível fraude, transação não reconhecida, dinheiro indevidamente retirado ou retido, ou impossibilidade de acessar/utilizar o próprio dinheiro.

RESUMO:
- Retorne somente uma frase curta contendo o problema principal.

POSSÍVEL CAUSA:
- Retorne somente a principal causa plausível.
- Não invente detalhes técnicos sem evidências.
- Se não houver informação suficiente, informe que a causa específica não pode ser determinada.

AÇÃO RECOMENDADA:
- Retorne somente a principal ação recomendada.
- A resposta deve ser curta e acionável.
"""

def analisar_feedback(feedback: str) -> AnaliseFeedback:

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[{
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {"role": "user",
         "content": feedback}],
         text_format=AnaliseFeedback
    )

    return response.output_parsed