import requests, os
from semanticscholar import SemanticScholar

# [1] 단건 수집 — 키워드 검색 후 XML 저장 + 오픈액세스 PDF 다운로드
def single_download_semantic(query_string):
    os.makedirs("./papers", exist_ok=True)
    sch = SemanticScholar()

    # 키워드로 1건 검색
    results = sch.search_paper(query_string, limit=1, fields=['title', 'openAccessPdf'])
    if not results:
        print(f"[검색 실패] '{query_string}'에 해당하는 논문 없음")
        return

    paper = results[0]
    print(f"[단건 검색 완료]")
    print(f" - 제목: {paper.title}")
    print(f" - URL: {paper.openAccessPdf.get('url')}")
    print(f" - Abstract: {paper.abstract}")
    print(f" - Published: {paper.year}")
    
    # 오픈액세스 PDF 다운로드 시도
    pdf_url = paper.openAccessPdf.get('url') if paper.openAccessPdf else None
    if pdf_url:
        download_pdf(pdf_url, "./papers", paper.paperId)
    else:
        print(f"[PDF 스킵] 오픈액세스 아님 | 제목: {paper.title}")

# [2] 배치 수집 — 키워드 검색 후 PDF 일괄 다운로드
def batch_download_semantic(keyword, max_results=3):
    os.makedirs("./batch_papers", exist_ok=True)
    sch = SemanticScholar()

    results = sch.search_paper(keyword, limit=max_results, fields=['title', 'openAccessPdf'])
    print(f"\n[키워드: {keyword}] 검색 결과: {len(results)}건")

    for paper in results:
        pdf_url = paper.openAccessPdf.get('url') if paper.openAccessPdf else None
        if pdf_url:
            download_pdf(pdf_url, "./batch_papers", paper.paperId)
        else:
            print(f"[PDF 스킵] 오픈액세스 아님 | 제목: {paper.title}")

# [유틸] PDF 다운로드
def download_pdf(pdf_url, dirpath, paper_id):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(pdf_url, headers=headers, allow_redirects=True)

    if response.status_code == 200 and b"%PDF" in response.content[:10]:
        safe_id = paper_id.replace("/", "_")
        pdf_path = f"{dirpath}/{safe_id}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        print(f"[PDF 다운로드 성공] {safe_id}.pdf")
    else:
        print(f"[PDF 다운로드 실패] 상태코드: {response.status_code} | URL: {pdf_url}")

# 실행 예시
single_download_semantic("perovskite AND synthesis")
#batch_download_semantic("perovskite AND synthesis")