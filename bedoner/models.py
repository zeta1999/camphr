"""The models module defines functions to create spacy models."""
import os
from pathlib import Path

import bedoner.lang.juman as juman
import bedoner.lang.mecab as mecab
import mojimoji
from bedoner.lang.pytt_mixin import PyttJuman
from bedoner.pipelines.date_ner import DateRuler
from bedoner.pipelines.person_ner import create_person_ruler
from bedoner.pipelines.pytt_model import PyttBertModel
from bedoner.pipelines.pytt_ner import PyttBertForNamedEntityRecognition
from bedoner.pipelines.wordpiecer import PyttWordPiecer
from spacy.vocab import Vocab

__dir__ = Path(__file__).parent

pytt_bert_dir = str(__dir__ / "../data/bert-ja-juman")


def juman_nlp() -> juman.Japanese:
    return juman.Japanese(
        Vocab(), meta={"tokenizer": {"preprocessor": mojimoji.han_to_zen}}
    )


def bert_wordpiecer() -> mecab.Japanese:
    nlp = PyttJuman(Vocab(), meta={"tokenizer": {"preprocessor": mojimoji.han_to_zen}})
    w = PyttWordPiecer.from_pretrained(Vocab(), pytt_bert_dir)
    nlp.add_pipe(w)
    return nlp


def bert_model():
    nlp = bert_wordpiecer()
    bert = PyttBertModel.from_pretrained(Vocab(), pytt_bert_dir)
    nlp.add_pipe(bert)
    return nlp


def bert_ner(**cfg):
    nlp = bert_model()
    ner = PyttBertForNamedEntityRecognition.from_pretrained(
        Vocab(), pytt_bert_dir, **cfg
    )
    nlp.add_pipe(ner)
    return nlp


def date_ruler(name="date_ruler") -> mecab.Japanese:
    nlp = mecab.Japanese(
        meta={"name": name, "requirements": ["mecab-python3", "regex"]}
    )
    nlp.add_pipe(DateRuler(nlp))
    return nlp


def person_ruler(name="person_ruler") -> mecab.Japanese:
    user_dic = os.path.expanduser("~/.bedoner/user.dic")
    if not os.path.exists(user_dic):
        raise ValueError(
            """User dictionary not found. See bedoner/scripts/person_dictionary and create user dictionary."""
        )

    nlp = mecab.Japanese(
        meta={
            "tokenizer": {"userdic": user_dic, "assets": "./jinmei/"},
            "name": name,
            "requirements": ["mecab-python3", "regex"],
        }
    )
    nlp.add_pipe(create_person_ruler(nlp))
    return nlp