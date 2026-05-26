import arxiv, os, requests
from concurrent.futures import ThreadPoolExecutor

# [1] 단일 논문 수집 (Single Processing)
def single_download_arxiv(query_string):
    # arXiv 클라이언트 인스턴스 생성
    client = arxiv.Client()
    # 검색 조건 설정 (정확한 매칭을 위해 쿼리 구성, 최대 1건 결과 요구)
    search = arxiv.Search(query=query_string, max_results=1)
    
    # 이터레이터로부터 첫 번째 검색 결과 획득
    paper = next(client.results(search))
    print(f"[단건 수집 완료]")
    print(f" - 제목: {paper.title}")
    print(f" - URL: {paper.pdf_url}")
    print(f" - Abstract: {paper.summary}")
    print(f" - Published: {paper.published}")
    
    # 지정 폴더에 PDF 파일 다운로드 수행
    os.makedirs("./papers", exist_ok=True)
    filepath = "./papers/single_arxiv_output.pdf"
    
    response = requests.get(paper.pdf_url)
    with open(filepath, "wb") as f:
        f.write(response.content)
    # 생성 파일: ./papers/single_arxiv_output.pdf

# [2] 다중 논문 일괄/병렬 수집 (Batch Processing)
def batch_download_arxiv(keyword):
    os.makedirs("./batch_papers", exist_ok=True)
    client = arxiv.Client()
    
    # 키워드별 상위 3건의 소재 관련 논문 검색
    search = arxiv.Search(query=keyword, max_results=3)
    for paper in client.results(search):
        safe_filename = f"{paper.get_short_id()}.pdf"
        filepath = f"./batch_papers/{safe_filename}"
        
        response = requests.get(paper.pdf_url)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"[배치 다운로드 성공] 파일명: {safe_filename} | 제목: {paper.title}")
        
# 실행 예시
#single_download_arxiv("perovskite AND synthesis")
batch_download_arxiv("perovskite AND synthesis")
