from pydantic import BaseModel, model_validator
from enum import Enum

class Urgencia(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class Sentimento(str, Enum):
    MUITO_POSITIVO = "muito_positivo"
    POSITIVO = "positivo"
    NEUTRO = "neutro"
    NEGATIVO = "negativo"
    MUITO_NEGATIVO = "muito_negativo"

class Categoria(str, Enum):
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    APLICATIVO = "aplicativo"
    BOLETO = "boleto"
    EMPRESTIMO = "emprestimo"
    ATENDIMENTO = "atendimento"

class Assunto(str, Enum):
    # PIX
    PIX_ESTORNADO = "pix_estornado"
    PIX_NAO_RECONHECIDO = "pix_nao_reconhecido"
    PIX_NAO_RECEBIDO = "pix_nao_recebido"
    PROBLEMA_CHAVE_PIX = "problema_chave_pix"
    ERRO_AO_REALIZAR_PIX = "erro_ao_realizar_pix"
    PIX_EM_PROCESSAMENTO = "pix_em_processamento"

    # CARTÃO
    CARTAO_BLOQUEADO = "cartao_bloqueado"
    PROBLEMA_LIMITE = "problema_limite"
    COMPRA_RECUSADA = "compra_recusada"
    COMPRA_NAO_RECONHECIDA = "compra_nao_reconhecida"
    COBRANCA_DUPLICADA = "cobranca_duplicada"
    PROBLEMA_FATURA = "problema_fatura"

    # APLICATIVO
    PROBLEMA_LOGIN = "problema_login"
    PROBLEMA_DOCUMENTO = "problema_documento"
    PROBLEMA_RECONHECIMENTO_FACIAL = "problema_reconhecimento_facial"
    ERRO_APLICATIVO = "erro_aplicativo"
    DUVIDA_APLICATIVO = "duvida_aplicativo"

    # BOLETO
    PAGAMENTO_NAO_RECONHECIDO = "pagamento_nao_reconhecido"
    ERRO_AO_PAGAR = "erro_ao_pagar"
    BOLETO_VENCIDO = "boleto_vencido"
    PAGAMENTO_DUPLICADO = "pagamento_duplicado"
    COBRANCA_INCORRETA = "cobranca_incorreta"

    # EMPRÉSTIMO
    PARCELA_INCORRETA = "parcela_incorreta"
    COBRANCA_INDEVIDA = "cobranca_indevida"
    DIFICULDADE_CONTRATACAO = "dificuldade_contratacao"
    PROBLEMA_QUITACAO = "problema_quitacao"
    DUVIDA_JUROS = "duvida_juros"
    RENEGOCIACAO = "renegociacao"

    # ATENDIMENTO
    DIFICULDADE_SER_ATENDIDO = "dificuldade_ser_atendido"
    ATENDIMENTO_NAO_RESOLUTIVO = "atendimento_nao_resolutivo"
    RECLAMACAO_ATENDENTE = "reclamacao_atendente"
    ELOGIO_ATENDIMENTO = "elogio_atendimento"

class AnaliseFeedback (BaseModel):
    categoria: Categoria
    assunto: Assunto
    sentimento: Sentimento
    urgencia: Urgencia
    resumo: str
    possivel_causa: str
    acao_recomendada: str

    @model_validator(mode="after")
    def validar_categoria_assunto(self):
        assuntos_por_categoria = {
            Categoria.PIX: {
                Assunto.PIX_ESTORNADO,
                Assunto.PIX_NAO_RECONHECIDO,
                Assunto.PIX_NAO_RECEBIDO,
                Assunto.PROBLEMA_CHAVE_PIX,
                Assunto.ERRO_AO_REALIZAR_PIX,
                Assunto.PIX_EM_PROCESSAMENTO,
            },

            Categoria.CARTAO_CREDITO: {
                Assunto.CARTAO_BLOQUEADO,
                Assunto.PROBLEMA_LIMITE,
                Assunto.COMPRA_RECUSADA,
                Assunto.COMPRA_NAO_RECONHECIDA,
                Assunto.COBRANCA_DUPLICADA,
                Assunto.PROBLEMA_FATURA,
            },

            Categoria.APLICATIVO: {
                Assunto.PROBLEMA_LOGIN,
                Assunto.PROBLEMA_DOCUMENTO,
                Assunto.PROBLEMA_RECONHECIMENTO_FACIAL,
                Assunto.ERRO_APLICATIVO,
                Assunto.DUVIDA_APLICATIVO,
            },

            Categoria.BOLETO: {
                Assunto.PAGAMENTO_NAO_RECONHECIDO,
                Assunto.ERRO_AO_PAGAR,
                Assunto.BOLETO_VENCIDO,
                Assunto.PAGAMENTO_DUPLICADO,
                Assunto.COBRANCA_INCORRETA,
            },

            Categoria.EMPRESTIMO: {
                Assunto.PARCELA_INCORRETA,
                Assunto.COBRANCA_INDEVIDA,
                Assunto.DIFICULDADE_CONTRATACAO,
                Assunto.PROBLEMA_QUITACAO,
                Assunto.DUVIDA_JUROS,
                Assunto.RENEGOCIACAO,
            },

            Categoria.ATENDIMENTO: {
                Assunto.DIFICULDADE_SER_ATENDIDO,
                Assunto.ATENDIMENTO_NAO_RESOLUTIVO,
                Assunto.RECLAMACAO_ATENDENTE,
                Assunto.ELOGIO_ATENDIMENTO,
            },
        }

        if self.assunto not in assuntos_por_categoria[self.categoria]:
            raise ValueError(
                f"O assunto {self.assunto.value} não pertence à categoria {self.categoria.value}"
            )
        return self
