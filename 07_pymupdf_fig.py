import fitz
import os

# [1] 단일 PDF 파일 내부 모든 이미지 객체 탐색 및 개별 분리 저장
def extract_figures_from_single_pdf(pdf_path, output_dir="./extracted_figures"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    figure_counter = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)  # 페이지 내부 고유 이미지 메타 리스트 조회
        
        for img_idx, img_meta in enumerate(image_list):
            xref = img_meta[0]  # 이미지 객체 고유 참조 번호(XREF) 확보
            base_image = doc.extract_image(xref)  # 원본 이미지 바이너리 데이터 추출
            image_bytes = base_image["image"]  # 바이트 스트림 데이터
            image_ext = base_image["ext"]      # 원본 파일 확장자 (png, jpeg 등)
            
            figure_counter += 1
            file_name = f"fig_single_p{page_num+1}_{img_idx+1}.{image_ext}"
            full_save_path = os.path.join(output_dir, file_name)
            
            # 물리적 이미지 파일 최종 생성
            with open(full_save_path, "wb") as img_f:
                img_f.write(image_bytes)
    print(f"[단건 이미지 분리 완료] 총 {figure_counter}개의 Figure 파일이 {output_dir}에 생성되었습니다.")

extract_figures_from_single_pdf('./example_papers/double_column.pdf')