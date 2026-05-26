# 분할 청크 고차원 임베딩 및 로컬 FAISS Vector DB 적재
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import json

def step2_build_vector_db(json_path="chunks_output.json", db_path="faiss_material_index"):
    
    # 0. JSON 파일에서 청크 로드 및 Document 객체 복원
    print(f">> '{json_path}' 파일에서 청크 로드 중...")
    with open(json_path, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)
    
    document_chunks = [
        Document(
            page_content=item["content"],
            metadata={"source": item["source"], "chunk_id": item["chunk_id"]}
        )
        for item in chunks_data
    ]
    print(f">> {len(document_chunks)}개 청크 복원 완료.")

    # 1. 고성능 text-embedding-3-small 모델 call (OpenAI API 키 필요)
    # embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    
    embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True})
    
    # 2. 대량의 텍스트 청크를 임베딩 벡터로 변환 및 FAISS 인덱싱 동시 실행
    print(">> 고속 매트릭스 변환 및 인덱스 트리 생성 중...")
    vector_db = FAISS.from_documents(document_chunks, embedding_model)
    
    # 3. 로컬 디스크로 벡터 데이터베이스 물리 저장 메소드 호출
    vector_db.save_local(db_path)
    print(f">> 완료: 로컬 디스크 '{db_path}' 적재 완료.")
    return vector_db

vector_db = step2_build_vector_db(json_path="chunks_output.json", db_path="faiss_material_index")