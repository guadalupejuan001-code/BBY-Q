"""C05 deterministic semantic contract tests; no native executable required."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import random
import string
import unittest

from integration.unified.common import C1
from .semantic import analyze, wire_decode, wire_encode, raw_roundtrip


def recover_topic(frame, role):
    for event in frame["events"]:
        for item in event["roles"]:
            if item["role"] == role:
                a, b = item["span"]["bytes"]
                return __import__("base64").b64decode(frame["current_raw_b64"])[a:b].decode("utf-8")
    return None


class SemanticContractTests(unittest.TestCase):
    def test_exact_utf8_roundtrip_whitespace_case_combining_marks_emojis(self):
        inputs = [
            "  ¡Hola, Ámbar!   \t¿Qué dices? 🦊\n",
            "si  Sí sí SI  no, NÓ; año ano ñ Niño ",
            "cafe\u0301  café  \U0001f9e0  🔥\u200d🔥",
            "  \t\n", "😀😀😀", "más  0000001,2300\t", "",
        ]
        for text in inputs:
            with self.subTest(text=text):
                frame = analyze(text, "Previo: Niña Ámbar. \n")
                raw, previous = raw_roundtrip(frame)
                self.assertEqual(raw, text.encode("utf-8"))
                self.assertEqual(previous, "Previo: Niña Ámbar. \n".encode("utf-8"))
                self.assertEqual(wire_decode(wire_encode(frame)), frame)
                self.assertEqual(frame["current_sha256"], sha256(raw).hexdigest())

    def test_token_ids_and_offsets_equal_original_c1(self):
        for sentence in ["Nara Atoyac Ñandú 137,05", "no definas memoria no interferencia",
                         "1.25 y 01,20", "Ámbar🏎️-XI"]:
            frame = analyze(sentence)
            old = C1.Codec(["<pad>"]).text(sentence)
            self.assertEqual([(x["id"], x["key"], x["start"], x["length"])
                              for x in frame["tokens"]],
                             [(x["id"], x["key"], x["start"], x["length"])
                              for x in old["tokens"]])
            raw = sentence.encode("utf-8")
            for t in frame["tokens"]:
                self.assertEqual(raw[t["start"]:t["start"] + t["length"]],
                                 t["raw"].encode("utf-8"))

    def test_prohibition_is_not_contrast_exclusion(self):
        no_define = analyze("no definas memoria")
        contrast = analyze("define memoria no interferencia")
        self.assertEqual(no_define["negations"][0]["kind"], "prohibition")
        self.assertEqual(no_define["events"][0]["polarity"], "prohibited")
        self.assertEqual(contrast["negations"][0]["kind"], "contrast_exclusion")
        self.assertEqual(contrast["events"][0]["polarity"], "not-negated-by-c05")
        self.assertEqual(recover_topic(contrast, "topic"), "memoria")
        mark = contrast["events"][0]["excluded_topics"][0]["bytes"]
        self.assertEqual("define memoria no interferencia".encode("utf-8")[mark[0]:mark[1]],
                         "interferencia".encode("utf-8"))

    def test_long_negation_scope_and_conjunction(self):
        value = analyze("No quiero que definas memoria, explica interferencia")
        self.assertEqual(value["negations"][0]["kind"], "prohibition")
        self.assertEqual(value["events"][0]["polarity"], "prohibited")
        self.assertEqual(value["events"][1]["polarity"], "not-negated-by-c05")
        self.assertEqual(value["events"][1]["verb"], "explain")

    def test_absence_does_not_invent_prohibited_instruction(self):
        r = analyze("sin datos no hay respuesta")
        self.assertEqual(r["negations"][0]["kind"], "absence")
        self.assertNotEqual(r["negations"][0]["kind"], "prohibition")

    def test_compositional_rule_roles_numbers_and_preserved_order(self):
        frame = analyze("guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3")
        self.assertEqual([v["verb"] for v in frame["events"]], ["store", "observe", "solve"])
        self.assertEqual(recover_topic(frame, "rule_name"), "Faro Azul")
        self.assertEqual(recover_topic(frame, "observation_name"), "Nara")
        self.assertEqual([x["decimal"] for x in frame["quantities"]], ["1", "88113", "3"])
        self.assertEqual([x["role"] for ev in frame["events"] for x in ev["roles"] if x["role"] in
                          ("sample", "position_from", "value")],
                         ["value", "sample", "position_from"])

    def test_entity_ownership_and_exact_name(self):
        frame = analyze("Recuerda que mi nave se llama Niña Ámbar")
        self.assertEqual(recover_topic(frame, "name_value"), "Niña Ámbar")
        self.assertTrue(any(v["role"] == "owner_speaker"
                            for e in frame["events"] for v in e["roles"]))

    def test_amounts_stay_decimal_and_lexically_distinct(self):
        frame = analyze("pago 000123,4500 y recibo 123.45 más 0,001 menos -27")
        amounts = frame["quantities"]
        self.assertEqual([a["lexeme"] for a in amounts],
                         ["000123,4500", "123.45", "0,001", "27"])
        self.assertEqual([a["decimal"] for a in amounts],
                         ["123.4500", "123.45", "0.001", "27"])
        self.assertTrue(amounts[-1]["negative"])
        self.assertEqual(amounts[0]["separator"], ",")
        self.assertEqual(amounts[1]["separator"], ".")
        self.assertNotEqual(wire_encode(analyze("valor 01")), wire_encode(analyze("valor 1")))

    def test_previous_context_reference_is_only_a_candidate(self):
        frame = analyze("repítelo", "define memoria")
        self.assertEqual(frame["references"][0]["status"], "unverified-candidate")
        self.assertIsNotNone(frame["references"][0]["candidate_in_previous"])
        without = analyze("repítelo", "hola")
        self.assertEqual(without["references"][0]["status"], "unresolved")
        multiple = analyze("repítelo", "define memoria y explica interferencia")
        self.assertEqual(multiple["references"][0]["status"], "unresolved")
        self.assertNotIn("resolved", frame["references"][0]["status"])

    def test_si_conditional_is_not_accented_affirmation(self):
        conditional = analyze("si alguien es clase cero entonces es alerta")
        self.assertEqual(conditional["logic_markers"][0]["kind"], "conditional-marker")
        self.assertEqual(analyze("sí, correcto")["logic_markers"][0]["kind"], "affirmative-marker")
        self.assertFalse(analyze("si no hay datos")["logic_markers"])

    def test_negative_number_does_not_turn_into_action_negation(self):
        frame = analyze("valor -30 y no definas algo")
        self.assertEqual(frame["quantities"][0]["lexeme"], "30")
        self.assertTrue(frame["quantities"][0]["negative"])
        self.assertEqual(frame["negations"][0]["kind"], "prohibition")

    def test_wire_detects_truncation_forgery_unknown_schema_and_corruption(self):
        frame = analyze("define memoria")
        full = wire_encode(frame)
        for tampered in [full[:-1], full + b"x", full[:44] + bytes([full[44] ^ 1]) + full[45:]]:
            with self.subTest(length=len(tampered)):
                with self.assertRaises(ValueError):
                    wire_decode(tampered)
        with self.assertRaises(ValueError):
            wire_decode(b"WRONG" + full[5:])
        forged = deepcopy(frame)
        forged["events"] = []
        # Even a valid SHA on a forged body must not permit fake semantics.
        with self.assertRaisesRegex(ValueError, "untrusted semantic annotations"):
            wire_decode(wire_encode(forged))
        with self.assertRaises(ValueError):
            wire_encode({**frame, "schema": "unknown"})

    def test_native_capacity_is_not_silently_increased(self):
        with self.assertRaises(ValueError):
            analyze("x " * 257)
        with self.assertRaises(ValueError):
            analyze("x", "palabra " * 65)
        with self.assertRaises(ValueError):
            analyze("z" * (C1.LIMITS["raw_bytes"] + 1))

    def test_holdout_compositional_cases_and_contrast_without_pair_collisions(self):
        rng = random.Random(2026110705)
        words = [a + b for a in "BCDFGHJKLMNPQRSTVWXYZ" for b in "aeio"]
        results = []
        for i in range(250):
            topic = rng.choice(words) + str(i)
            other = rng.choice(words) + str(i + 1000)
            left = analyze(f"no definas {topic}")
            right = analyze(f"define {topic} no {other}")
            self.assertEqual(left["events"][0]["polarity"], "prohibited")
            self.assertEqual(right["events"][0]["polarity"], "not-negated-by-c05")
            self.assertEqual(recover_topic(right, "topic"), topic)
            self.assertEqual(right["negations"][0]["kind"], "contrast_exclusion")
            self.assertNotEqual(wire_encode(left), wire_encode(right))
            self.assertEqual(raw_roundtrip(left)[0], f"no definas {topic}".encode("utf-8"))
            results.append(right["current_sha256"])
        self.assertEqual(len(set(results)), 250)


if __name__ == "__main__":
    unittest.main()
