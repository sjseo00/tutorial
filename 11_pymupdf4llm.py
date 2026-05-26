import pymupdf4llm
import json

# [1] 단일 파일 대상 통째 변환 및 LLM 프롬프트 임베딩 연동용 마크다운 생성
def prepare_single_pdf_for_llm(pdf_path):
    print("LLM 포맷 최적화 모드로 마크다운 변환 엔진 구동...")
    # 내부 마크다운 래퍼가 동작하여 제목, 강조 기호 등을 표준화 구조로 변환
    structured_markdown_string = pymupdf4llm.to_markdown(pdf_path)
    
    output_filename = "llm_ready_input.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(structured_markdown_string)
    print(f"[단건 변환 완료] {output_filename} 마크다운 파일 물리 생성 성공.")
    return structured_markdown_string


prepare_single_pdf_for_llm('./example_papers/single_column.pdf')