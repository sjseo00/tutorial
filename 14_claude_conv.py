import anthropic, base64, json, re

def extract_numerical_data_from_figure(image_png_path):
    with open(image_png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    strict_json_prompt = (
        "너는 소재 연구 전문 데이터 엔지니어다. 첨부된 이미지 그래프를 정밀 판독하여 "
        "주요 피크(Peak) 또는 데이터 포인트 좌표를 역산해라. "
        "반드시 오직 하단 지정을 따르는 표준 JSON 형식 문자열로만 응답해라. 사설 금지.\n"
        'Schema: {"graph_title": str, "unit": str, "datapoints": [{"x": float, "y": float}]}'
    )

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
            {"type": "text", "text": strict_json_prompt}
        ]}]
    )

    raw = re.sub(r"```[a-z]*|```", "", message.content[0].text).strip()
    print("[단건 그래프 수치 복원 완료]")
    result = json.loads(raw)
    
    # JSON 파일 저장
    out_path = image_png_path.replace(".png", ".json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {out_path} 저장 완료")
    return result

extract_numerical_data_from_figure('./img_extract/figure.png')