import anthropic
import base64

# [1] 단일 로컬 PDF 파일 바이너리의 Claude Vision Direct 전송 및 특정 물성 질의 (Single Call)
def query_claude_vision_single(pdf_path):
    # 1단계: 원본 PDF 파일을 읽어 무손실 Base64 텍스트 스트림 데이터로 사전 인코딩 처리
    with open(pdf_path, "rb") as pdf_file:
        encoded_pdf_string = base64.b64encode(pdf_file.read()).decode("utf-8")

    print("Anthropic Claude 멀티모달 API 커넥션 수립 및 도큐먼트 전송 중...")
    client = anthropic.Anthropic()

    # 2단계: PDF 전체를 마크다운으로 변환해달라는 프롬프트로 교체
    markdown_conversion_prompt = (
        "이 PDF 문서 전체를 마크다운 형식으로 변환해줘. "
        "제목은 #, 소제목은 ##, 본문은 그대로 유지하고, "
        "표는 마크다운 테이블로, 강조 텍스트는 **볼드** 또는 *이탤릭*으로 표현해줘. "
        "코드 블록이 있으면 ``` 로 감싸줘. 변환된 마크다운만 출력해줘."
    )

    # 3단계: 클로드 전용 도큐먼트 소스 블록 구조체 형식에 맞추어 API 페이로드 전송
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": encoded_pdf_string
                    }
                },
                {
                    "type": "text",
                    "text": markdown_conversion_prompt
                }
            ]
        }]
    )

    structured_markdown_string = response.content[0].text

    # 4단계: 마크다운 파일로 저장
    output_filename = "llm_ready_input.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(structured_markdown_string)
    print(f"[단건 변환 완료] {output_filename} 마크다운 파일 물리 생성 성공.")

    return structured_markdown_string


query_claude_vision_single('./example_papers/double_column.pdf')