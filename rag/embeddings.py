from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer as _ST

_MODEL_CACHE: dict[str, "_ST"] = {}


def get_model(model_name: str = "all-MiniLM-L6-v2") -> "_ST":
    if model_name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
    return _MODEL_CACHE[model_name]


def embed_texts(
    texts: list[str],
    model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 64,
    show_progress: bool = False,
) -> list[list[float]]:
    model = get_model(model_name)
    vecs = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
    )
    return vecs.tolist()


def embed_query(query: str, model_name: str = "all-MiniLM-L6-v2") -> list[float]:
    return embed_texts([query], model_name=model_name, batch_size=1)[0]
