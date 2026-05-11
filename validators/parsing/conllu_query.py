"""CoNLL-U query primitives — re-exported from atu_method.

The universal Token/Sentence types and loader live in
`atu_method.parsing.conllu_query`. This module exists for import-path
compatibility within readers-bofm; new readers-bofm code should prefer
importing from `atu_method.parsing.conllu_query` directly.
"""
from atu_method.parsing.conllu_query import *  # noqa: F401,F403
from atu_method.parsing.conllu_query import (  # explicit re-exports
    Token,
    Sentence,
    load_conllu,
)

__all__ = ["Token", "Sentence", "load_conllu"]
