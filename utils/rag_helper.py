import math
from collections import defaultdict
from typing import List, Dict

import faiss
import numpy as np
import torch
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from utils.settings import RagSettings


# from sklearn.cluster import DBSCAN

class SimpleRAG:
    def __init__(self, setting: RagSettings):
        self._index = faiss.IndexFlatL2(setting.dim)
        self._dim = setting.dim
        self._embeddings = []
        self._tokenizer = AutoTokenizer.from_pretrained(setting.tokenizer)
        self._model = AutoModel.from_pretrained(setting.model)
        self._model.eval()

    def _encode(self, docs: List[str]) -> np.ndarray:
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

    def kmeans(self, docs: List[str]) -> List[List[int]]:
        embeddings = self._encode(docs).astype(np.float32)
        kmeans = faiss.Kmeans(self._dim, max(int(math.sqrt(len(docs)) / 2), 1), niter=20, verbose=True)
        kmeans.train(embeddings)
        D, I = kmeans.index.search(embeddings, 1)
        x: Dict[int, List[int]] = defaultdict(list)
        for i in range(len(I)):
            x[I[i][0]].append(i)
        return list(x.values())

    # def dbscan(self, docs: List[str], eps=0.5, min_samples=5) -> List[List[int]]:
    #     # 将文档编码为向量
    #     vectors = self._encode(docs)
    #
    #     # 使用DBSCAN进行聚类
    #     clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(vectors)
    #     labels = clustering.labels_
    #
    #     # 根据标签整理聚类结果
    #     clusters = {}
    #     for idx, label in enumerate(labels):
    #         if label not in clusters:
    #             clusters[label] = []
    #         clusters[label].append(idx)
    #
    #     # 转换为所需格式
    #     result = [clusters[i] for i in sorted(clusters.keys())]
    #
    #     return result
