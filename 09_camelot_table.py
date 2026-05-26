import camelot
import os

def extract_lattice_tables_all(pdf_path):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    total_saved = 0

    # 전체 페이지 추출 (pages='all')
    print("Lattice 알고리즘 가동 (OpenCV 선 인식 기반)...")
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')

    if len(tables) == 0:
        print("추출된 표가 없습니다.")
        return

    # camelot은 페이지/표 번호를 parsing_report에 담아줌
    page_table_counter = {}  # 페이지별 표 번호 카운팅용

    for table in tables:
        page_num = table.parsing_report['page']
        
        # 페이지별 표 번호 누적
        page_table_counter[page_num] = page_table_counter.get(page_num, 0) + 1
        table_num = page_table_counter[page_num]

        accuracy = table.parsing_report['accuracy']
        output_csv = f"{base_name}_page{page_num}_table{table_num}.csv"

        table.df.to_csv(output_csv, index=False)
        print(f"[Page {page_num}] 표 {table_num} 저장 완료 → {output_csv} | 신뢰도: {accuracy}% | 크기: {table.df.shape}")
        total_saved += 1

    print(f"\n총 {total_saved}개 표 추출 완료")

extract_lattice_tables_all('./example_papers/single_column2.pdf')