from anthropic import Anthropic
from search import step3_search_knowledge  # 함수만 import

researcher_query = "What conditions were used to synthesize pyrazole in the C-N bond formation reaction?"

retrieved_knowledge = step3_search_knowledge(
    user_query=researcher_query,
    db_path="faiss_material_index"
)

def step4_generate_answer(user_query, retrieved_context):
    client = Anthropic()

    system_prompt = (
        "당신은 신소재 전문 RAG 시스템입니다. 반드시 제공된 [논문 출처 정보]만을 "
        "기반으로 사실에 입각하여 답변하고, 모르는 것은 환각 없이 모른다고 하십시오."
    )
    user_message = f"""
[논문 출처 정보]
{retrieved_context}

[연구원 질문]
{user_query}
"""
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        temperature=0.0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


final_ai_report = step4_generate_answer(
    user_query=researcher_query,
    retrieved_context=retrieved_knowledge
)

print(final_ai_report)