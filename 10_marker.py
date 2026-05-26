from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
import torch

def transform_pdf_to_markdown_single(pdf_path, output_md_name="converted_output.md"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"사용 디바이스: {device.upper()}")

    artifact_dict = create_model_dict()

    converter = PdfConverter(
        artifact_dict=artifact_dict,
        config={"device": device}  # GPU 지정
    )
    rendered = converter(pdf_path)
    extracted_text, metadata, associated_images = text_from_rendered(rendered)

    with open(output_md_name, "w", encoding="utf-8") as md_file:
        md_file.write(extracted_text)
    print(f"[변환 완료] {output_md_name}")

transform_pdf_to_markdown_single('./example_papers/single_column.pdf')