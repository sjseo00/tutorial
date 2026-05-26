# 변환된 마크다운 논문 원문의 의미 단위 고속 청킹
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import json


def step1_execute_chunking(markdown_path):
    
    # 1. 사전에 컨버팅 완료된 마크다운 PDF 파싱 결과물 로드
    with open(markdown_path, "r", encoding="utf-8") as f:
        raw_markdown = f.read()
            
    # 2. 텍스트 분할기 생성 및 소재 논문 특화 파라미터 세팅
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,        # 소재 논문 문맥 유지를 위한 최적 청크 크기
        chunk_overlap=120,     # 문단 단절 방지를 위한 중첩 영역
        length_function=len
    )
    
    # 3. 분할 알고리즘 call 및 LangChain Document 객체화
    chunks = text_splitter.split_text(raw_markdown)
    document_objects = [
        Document(
            page_content=chunk, 
            metadata={"source": markdown_path, "chunk_id": idx}
        ) 
        for idx, chunk in enumerate(chunks)
    ]
    
    print(f">> 완료: {len(document_objects)}개의 고유 지식 청크 생성.")
    return document_objects

document_chunks = step1_execute_chunking(markdown_path="12_llm_ready_input.md") 


output = [
    {
        "chunk_id": doc.metadata["chunk_id"],
        "length": len(doc.page_content),
        "content": doc.page_content,
        "source": doc.metadata["source"]
    }
    for doc in document_chunks
]

with open("chunks_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"저장 완료: chunks_output.json")


