# 연구원 질의 대응 하이브리드 검색 및 지식 추출 (Retrieval)
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# 한국어 질문
#researcher_query = "C-N 결합 형성 반응에서 pyrazole을 합성할 때 어떤 조건을 사용했어?"

# 영어 질문
researcher_query = "What conditions were used to synthesize pyrazole in the C-N bond formation reaction?"

def step3_search_knowledge(user_query, db_path="faiss_material_index"):

    # step2 와 반드시 동일한 모델 사용 (다르면 벡터 차원 불일치 에러)
    # embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # 1. 로컬에 저장된 FAISS 인덱스를 메모리에 역추적 로드
    vector_db = FAISS.load_local(
        db_path, embedding_model, allow_dangerous_deserialization=True
    )

    # 2. 유사도 기반 탑-K(k=2) 지식 검색 메소드 호출
    search_results = vector_db.similarity_search_with_score(user_query, k=2)

    # 3. 추출된 논문 조각 본문들을 하나의 컨텍스트 블록 스트림으로 병합
    compiled_contexts = []
    for doc, score in search_results:
        print(f"  - chunk_id: {doc.metadata['chunk_id']} | 유사도 점수: {score:.4f}")
        compiled_contexts.append(doc.page_content)

    final_context_block = "\n\n".join(compiled_contexts)
    print(">> 완료: 질문과 가장 연관성 높은 논문 후보 문단 추출 완료.")
    return final_context_block

retrieved_knowledge = step3_search_knowledge(
    user_query=researcher_query,
    db_path="faiss_material_index"
)

print("\n===== 추출된 지식 블록 =====")
print(retrieved_knowledge)