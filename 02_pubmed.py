import requests, time, os
from xml.etree import ElementTree as ET

# [1] 단건 수집 — 키워드 검색 후 XML 저장 + 오픈액세스 PDF 다운로드
def single_download_pubmed(query_string):
    os.makedirs("./papers", exist_ok=True)
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    # 키워드로 PMID 1건 검색
    s_params = {"db": "pubmed", "term": query_string, "retmax": 1, "retmode": "json"}
    id_list = requests.get(search_url, params=s_params).json() \
                      .get("esearchresult", {}).get("idlist", [])

    if not id_list:
        print(f"[검색 실패] '{query_string}'에 해당하는 논문 없음")
        return

    pmid = id_list[0]
    print(f"[단건 검색 완료] 키워드: {query_string} | PMID: {pmid}")

    # XML 저장
    params = {"db": "pubmed", "id": pmid, "retmode": "xml"}
    response = requests.get(fetch_url, params=params)
    print(response.text)
    xml_path = f"./papers/{pmid}.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"[XML 저장 완료] {xml_path}")

    # 오픈액세스 PDF 다운로드 시도
    pmc_id = extract_pmc_id(response.text)
    if pmc_id:
        download_pmc_pdf(pmc_id, "./papers", pmid)
    else:
        print(f"[PDF 스킵] PMID: {pmid} | 오픈액세스 아님")


# [2] 배치 수집 — 키워드 검색 후 XML 저장 + 오픈액세스 PDF 다운로드
def batch_download_pubmed(keyword, max_results=3):
    os.makedirs("./batch_papers", exist_ok=True)
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


    s_params = {"db": "pubmed", "term": keyword, "retmax": max_results, "retmode": "json"}
    id_list = requests.get(search_url, params=s_params).json() \
                      .get("esearchresult", {}).get("idlist", [])
    print(f"\n[키워드: {keyword}] 매칭 PMID: {id_list}")

    for pmid in id_list:
        params = {"db": "pubmed", "id": pmid, "retmode": "xml"}
        response = requests.get(fetch_url, params=params)

        # XML 저장
        xml_path = f"./batch_papers/{pmid}.xml"
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"[XML 저장 완료] {pmid}.xml")

        # 오픈액세스 PDF 다운로드 시도
        pmc_id = extract_pmc_id(response.text)
        if pmc_id:
            download_pmc_pdf(pmc_id, "./batch_papers", pmid)
        else:
            print(f"[PDF 스킵] PMID: {pmid} | 오픈액세스 아님")

        time.sleep(0.3)  # NCBI Rate Limit 준수

# [유틸] XML에서 PMC ID 추출
def extract_pmc_id(xml_text):
    try:
        root = ET.fromstring(xml_text)
        # ArticleIdList 내 IdType="pmc" 항목 탐색
        for article_id in root.iter("ArticleId"):
            if article_id.attrib.get("IdType") == "pmc":
                return article_id.text  # 예: "PMC1234567"
    except ET.ParseError:
        pass
    return None

# [유틸] PMC PDF 다운로드
def download_pmc_pdf(pmc_id, dirpath, pmid):
    # 1. OA API로 Open Access 여부 확인
    oa_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
    r = requests.get(oa_url, params={"id": pmc_id}, timeout=15)

    # tgz 링크가 없으면 구독 논문 → 다운로드 불가
    if "href=" not in r.text:
        print(f"[실패] PMID: {pmid} | 구독 논문 (OA 아님)")
        return False

    # 2. AWS S3에서 PDF 직접 다운로드 (버전 1~3 순서로 시도)
    for v in ["1", "2", "3"]:
        s3_url = f"https://pmc-oa-opendata.s3.amazonaws.com/{pmc_id}.{v}/{pmc_id}.{v}.pdf"
        res = requests.get(s3_url, timeout=60)

        if res.status_code == 200 and b"%PDF" in res.content[:10]:
            pdf_path = f"{dirpath}/{pmid}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(res.content)
            print(f"[성공] {pmid}.pdf | {pmc_id} (v{v})")
            return True

    print(f"[실패] PMID: {pmid} | S3 PDF 없음")
    return False
    
# 실행 예시
#single_download_pubmed("perovskite AND synthesis")
batch_download_pubmed("perovskite AND synthesis")
