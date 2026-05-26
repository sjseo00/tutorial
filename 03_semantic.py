import requests, os
import re
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

def resolve_pdf_url(url):
    """DOI URL을 실제 PDF URL로 변환 시도"""
    # 1. Unpaywall API로 무료 PDF URL 조회
    doi_match = re.search(r'10\.\d{4,}/\S+', url)
    if not doi_match:
        return None
    
    doi = doi_match.group(0)
    email = "your@email.com"
    unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    
    try:
        res = requests.get(unpaywall_url, timeout=10).json()
        if not res.get("is_oa"):
            print(f"[구독 논문] OA 아님: {doi}")
            return None
        
        # best_oa_location 먼저 확인
        best = res.get("best_oa_location", {})
        pdf_url = best.get("url_for_pdf")
        
        # ★ best에 pdf URL 없으면 oa_locations 전체에서 탐색
        if not pdf_url:
            for loc in res.get("oa_locations", []):
                if loc.get("url_for_pdf"):
                    pdf_url = loc["url_for_pdf"]
                    break
        
        if not pdf_url:
            print(f"[PDF 없음] OA이지만 PDF URL 없음: {doi}")
            return None
        
        return pdf_url

    except Exception as e:
        print(f"[Unpaywall 실패] {e}")
        return None

# [유틸] PDF 다운로드
def download_pdf(pdf_url, dirpath, paper_id):
    if "doi.org" in pdf_url:
        pdf_url = resolve_pdf_url(pdf_url)
    print("Converted " + pdf_url)
    if not pdf_url:
        print(f"[PDF 스킵] 무료 PDF 없음")
        return False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    res = requests.get(pdf_url, headers=headers, allow_redirects=True, timeout=30)

    if res.status_code == 200 and b"%PDF" in res.content[:10]:
        pdf_path = f"{dirpath}/{paper_id}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(res.content)
        print(f"[성공] {paper_id}.pdf")
        return True
    else:
        print(f"[실패] 상태코드: {res.status_code} | URL: {pdf_url}")
        return False
        
# 실행 예시
single_download_semantic("perovskite AND synthesis")
#batch_download_semantic("perovskite AND synthesis")
