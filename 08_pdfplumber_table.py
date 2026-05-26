import pdfplumber
import pandas as pd
import os

def extract_all_tables_from_pdf(pdf_path):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    total_saved = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            if not tables:
                print(f"[Page {page_num}] 표 없음, 스킵")
                continue

            for table_num, raw_table in enumerate(tables, start=1):
                if not raw_table or len(raw_table) < 2:
                    print(f"[Page {page_num}] 표 {table_num}: 데이터 부족, 스킵")
                    continue

                header = raw_table[0]
                data_rows = raw_table[1:]

                df = pd.DataFrame(data_rows, columns=header)

                # 파일명: {원본파일명}_page{페이지번호}_table{표번호}.csv
                output_csv = f"{base_name}_page{page_num}_table{table_num}.csv"
                df.to_csv(output_csv, index=False, encoding="utf-8-sig")
                print(f"[Page {page_num}] 표 {table_num} 저장 완료 → {output_csv} (형태: {df.shape})")
                total_saved += 1

    print(f"\n총 {total_saved}개 표 추출 완료")

extract_all_tables_from_pdf('./example_papers/double_column.pdf')