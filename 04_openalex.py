import requests, os

# [1] 단건 수집 — 키워드 검색 후 오픈액세스 PDF 다운로드
def single_download_openalex(query_string):
    os.makedirs("./papers", exist_ok=True)

    paper = fetch_openalex(query_string, per_page=1)
    if not paper:
        print(f"[검색 실패] '{query_string}'에 해당하는 논문 없음")
        return

    print(f"[단건 검색 완료] 제목: {paper.get('display_name')}")
    download_openalex_pdf(paper, "./papers")

# [2] 배치 수집 — 키워드 검색 후 PDF 일괄 다운로드
def batch_download_openalex(keyword, max_results=10):
    os.makedirs("./batch_papers", exist_ok=True)

    print(f"\n[키워드: {keyword}] 검색 시작...")
    papers = fetch_openalex(keyword, per_page=max_results, single=False)

    for paper in papers:
        print(f"[검색 완료] 제목: {paper.get('display_name')}")
        download_openalex_pdf(paper, "./batch_papers")

# [유틸] OpenAlex API 검색
def fetch_openalex(query_string, per_page=1, single=True):
    base_url = "https://api.openalex.org/works"
    params = {
        "filter": f"display_name.search:{query_string},is_oa:true",
        "per_page": per_page
    }
    headers = {"User-Agent": "mailto:researcher@institution.ac.kr"}

    results = requests.get(base_url, params=params, headers=headers).json().get("results", [])
    return results[0] if (single and results) else results

# [유틸] PDF 다운로드
def download_openalex_pdf(paper, dirpath):
    # OA 정보에서 PDF URL 추출
    oa_url = paper.get("open_access", {}).get("oa_url")
    if not oa_url or not oa_url.endswith(".pdf"):
        print(f"[PDF 스킵] 직접 PDF URL 없음 | DOI: {paper.get('doi')}")
        return

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(oa_url, headers=headers, allow_redirects=True)

    if response.status_code == 200 and b"%PDF" in response.content[:10]:
        safe_id = paper.get("id", "unknown").split("/")[-1]  # "W2741809807"
        pdf_path = f"{dirpath}/{safe_id}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        print(f"[PDF 다운로드 성공] {safe_id}.pdf")
    else:
        print(f"[PDF 다운로드 실패] 상태코드: {response.status_code} | URL: {oa_url}")

# 실행 예시
#single_download_openalex("perovskite AND synthesis")
batch_download_openalex("perovskite AND synthesis")