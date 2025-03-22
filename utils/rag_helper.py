from typing import List

import faiss
import torch
from loguru import logger
from transformers import AutoTokenizer, AutoModel


class SimpleRAG:
    def __init__(self, tokenizer, model, dim):
        self._index = faiss.IndexFlatL2(dim)
        self._docs = []  # 存储原始JSON文档
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self._model = AutoModel.from_pretrained(model)
        self._model.eval()

    def _encode(self, docs: List[str]) -> torch.Tensor:
        encoded_input = self._tokenizer(docs, padding=True, truncation=True, return_tensors='pt',
                                        max_length=self._model.config.max_position_embeddings)
        for i, (input_ids, attention_mask) in enumerate(
                zip(encoded_input['input_ids'], encoded_input['attention_mask'])):
            real_token_count = attention_mask.sum().item()  # 计算非padding部分的token总数
            logger.debug(f'[JsonRAG] tokenized, length of input {i + 1} is {real_token_count}')
        with torch.no_grad():
            model_output = self._model(**encoded_input)
        text_embedding = model_output.last_hidden_state.mean(dim=1).numpy()
        return text_embedding

    def add(self, docs: List[str]):
        self._index.add(self._encode(docs))
        logger.info(f'[JsonRAG] add {len(docs)} docs to index')

    def query(self, query: str, k=3) -> List[int]:
        query_embedding = self._encode([query])
        D, I = self._index.search(query_embedding, k)
        for i, (d, j) in enumerate(zip(D[0], I[0])):
            logger.debug(f'[JsonRAG] similarity rank {i + 1}, distance: {d:.2f}, index: {j}')
        logger.info(f'[JsonRAG] query finished')
        return I[0]
