import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from pipeline import processar
from evaluation import avaliar
from review import preparar_amostra


def enum(value):
    return SimpleNamespace(value=value)


class PipelineTests(unittest.TestCase):
    def test_resume_retries_errors_without_repeating_successes(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            entrada, saida = base / "feedback.csv", base / "out.csv"
            pd.DataFrame({"id": [1, 2], "feedback": ["um", "dois"]}).to_csv(entrada, index=False)
            chamadas = []

            def analisar(texto):
                chamadas.append(texto)
                if texto == "dois" and len(chamadas) == 2:
                    raise RuntimeError("falha temporária")
                return SimpleNamespace(
                    categoria=enum("pix"), assunto=enum("erro_ao_realizar_pix"),
                    sentimento=enum("negativo"), urgencia=enum("media"),
                    resumo="erro", possivel_causa="indefinida",
                    acao_recomendada="contatar suporte",
                )

            self.assertEqual(processar(entrada, saida, analisar), (1, 1))
            self.assertEqual(processar(entrada, saida, analisar), (2, 0))
            self.assertEqual(chamadas, ["um", "dois", "dois"])
            self.assertEqual(len(pd.read_csv(saida)), 2)

            # Mesmo ID com texto alterado precisa de uma nova classificação.
            pd.DataFrame({"id": [1, 2], "feedback": ["um corrigido", "dois"]}).to_csv(
                entrada, index=False
            )
            self.assertEqual(processar(entrada, saida, analisar), (2, 0))
            self.assertEqual(chamadas[-1], "um corrigido")

    def test_missing_prediction_counts_as_error(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            refs, pred, out = (base / name for name in ("ref.csv", "pred.csv", "eval.csv"))
            pd.DataFrame({"id": [1, 2], "categoria_geracao": ["pix"] * 2,
                          "assunto_geracao": ["erro"] * 2}).to_csv(refs, index=False)
            pd.DataFrame({"id": [1], "categoria": ["pix"], "assunto": ["erro"],
                          "status": ["sucesso"]}).to_csv(pred, index=False)
            resultado = avaliar(refs, pred, out)
            self.assertEqual(resultado["processados"], 1)
            self.assertEqual(resultado["acuracia_categoria"], 0.5)
            self.assertEqual(resultado["macro_f1_categoria"], 2 / 3)

    def test_blind_review_requires_labels_and_unchanged_text(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            texts, metadata, template, predictions, output = (
                base / name for name in ("texts.csv", "meta.csv", "review.csv", "pred.csv", "eval.csv")
            )
            pd.DataFrame({"id": [1, 2], "feedback": ["texto A", "texto B"]}).to_csv(texts, index=False)
            pd.DataFrame({"id": [1, 2], "categoria_geracao": ["pix", "boleto"]}).to_csv(
                metadata, index=False
            )
            review = preparar_amostra(texts, metadata, template, por_categoria=1)
            self.assertFalse({"categoria_geracao", "categoria"} & set(review.columns))
            pd.DataFrame({"id": [1, 2], "feedback": ["texto A", "texto B"],
                          "categoria": ["pix", "boleto"], "status": ["sucesso"] * 2}).to_csv(
                predictions, index=False
            )
            with self.assertRaisesRegex(ValueError, "preenchidas"):
                avaliar(template, predictions, output, "revisada", ("categoria",))

            review["categoria_revisada"] = ["pix", "boleto"]
            review.to_csv(template, index=False)
            self.assertEqual(1.0, avaliar(template, predictions, output, "revisada",
                                          ("categoria",))["acuracia_categoria"])
            review.loc[0, "feedback"] = "texto alterado"
            review.to_csv(template, index=False)
            with self.assertRaisesRegex(ValueError, "texto mudou"):
                avaliar(template, predictions, output, "revisada", ("categoria",))


if __name__ == "__main__":
    unittest.main()
