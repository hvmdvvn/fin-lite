from sentence_transformers import SentenceTransformer
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device=device,
)


def embed_text(text: str):
    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()