from paperscraper.pubmed import get_and_dump_pubmed_papers
from paperscraper.arxiv import get_and_dump_arxiv_papers
from paperscraper.pdf import save_pdf
import json, os

# [1] 단건 수집 — 첫 번째 결과만 PDF 다운로드
def single_download_paperscraper(query_string, source="pubmed"):
    os.makedirs("./papers", exist_ok=True)
    safe_name = query_string.replace(' ', '_')
    jsonl_path = f"./papers/{safe_name}.jsonl"

    print(f"[단건 검색 시작] 키워드: {query_string}")
    get_and_dump_pubmed_papers([[query_string]], output_filepath=jsonl_path) if source == "pubmed" \
        else get_and_dump_arxiv_papers([[query_string]], output_filepath=jsonl_path)
    print(f"[JSONL 저장 완료] {jsonl_path}")

    with open(jsonl_path, "r", encoding="utf-8") as f:
        first_paper = json.loads(f.readline())

    print(f"[단건 추출] 제목: {first_paper.get('title')}")
    download_pdf(first_paper, "./papers", safe_name)

# [2] 배치 수집 — 상위 max_results건만 PDF 다운로드
def batch_download_paperscraper(keyword, max_results=3, source="pubmed"):
    os.makedirs("./batch_papers", exist_ok=True)

    print(f"\n[키워드: {keyword}] 검색 시작...")
    safe_name = keyword.replace(' ', '_')
    jsonl_path = f"./batch_papers/{safe_name}.jsonl"

    get_and_dump_pubmed_papers([[keyword]], output_filepath=jsonl_path) if source == "pubmed" \
        else get_and_dump_arxiv_papers([[keyword]], output_filepath=jsonl_path)
    print(f"[JSONL 저장 완료] {jsonl_path}")

    papers = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_results:
                break
            papers.append(json.loads(line))

    print(f"[추출 완료] {len(papers)}건 / 키워드: {keyword}")
    for paper in papers:
        safe_id = paper.get("doi", paper.get("title", keyword)).replace("/", "_")
        download_pdf(paper, "./batch_papers", safe_id)

# [유틸] PDF 다운로드
def download_pdf(paper, dirpath, filename):
    doi = paper.get("doi")
    if doi:
        filepath = f"{dirpath}/{filename}.pdf"
        save_pdf({"doi": doi}, filepath=filepath)
        print(f"[PDF 다운로드 완료] {filepath}")
    else:
        print(f"[PDF 스킵] DOI 없음 | 제목: {paper.get('title')}")

# 실행 예시
#single_download_paperscraper("perovskite AND synthesis", source="pubmed")
batch_download_paperscraper("perovskite AND synthesis", source="pubmed")