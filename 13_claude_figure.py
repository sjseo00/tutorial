import anthropic, base64, json, os, re
import fitz  # pip install pymupdf

client = anthropic.Anthropic()

def b64(path): return base64.b64encode(open(path,"rb").read()).decode()

def process(pdf_path, out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    n = 0

    for i, page in enumerate(doc):
        # 페이지 → JPEG (임시)
        jpg = f"{out_dir}/_p{i+1}.jpg"
        page.get_pixmap(dpi=200).save(jpg)

        # Claude → figure bbox 감지
        resp = client.messages.create(
            model="claude-opus-4-5", max_tokens=1024,
            messages=[{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":"image/jpeg","data":b64(jpg)}},
                {"type":"text","text":(
                    "이 페이지에서 figure(차트/그래프/플롯)를 모두 찾아 bbox를 반환해줘. "
                    '형식: [{"label":"name","bbox":[x,y,w,h]}] '
                    "x,y,w,h는 0~1 비율. figure 없으면 []. JSON만 반환."
                )}
            ]}]
        )
        raw = re.sub(r"```[a-z]*|```","",resp.content[0].text).strip()
        try: regions = json.loads(raw)
        except: os.remove(jpg); continue

        # bbox → 크롭 PNG 저장
        r = page.rect
        for reg in regions:
            x,y,w,h = reg["bbox"]
            clip = fitz.Rect(x*r.width, y*r.height, (x+w)*r.width, (y+h)*r.height)
            dst = f"{out_dir}/p{i+1:03d}_{reg['label']}.png"
            page.get_pixmap(dpi=200, clip=clip).save(dst)
            print(f"✓ {dst}")
            n += 1

        os.remove(jpg)

    print(f"\n완료: figure {n}개 → {out_dir}/")

process("./example_papers/double_column.pdf")