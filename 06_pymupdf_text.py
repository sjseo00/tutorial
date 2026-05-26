import fitz

# [1] 단일 논문 PDF 대상 고속 텍스트 추출 (Single File)
def extract_text_from_single_pdf(pdf_path):
    # PDF 문서 객체 할당
    doc = fitz.open(pdf_path)
    full_document_text = []
    
    # 전체 페이지를 순회하며 텍스트 추출
    for page_idx, page in enumerate(doc):
        page_text = page.get_text("text")  # 기본 텍스트 스트림 모드로 추출
        full_document_text.append(f"--- PAGE {page_idx+1} ---\n{page_text}")
        
    final_output = "\n".join(full_document_text)
    
    # 단건 파일 결과를 .txt 포맷으로 로컬에 출력
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(final_output)
    print(f"[단건 처리 완료] extracted_text.txt 파일 물리적 생성 완료 (글자수: {len(final_output)})")

extract_text_from_single_pdf("./example_papers/double_column.pdf")
