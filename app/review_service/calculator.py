from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

# Pydantic을 사용하여 원하는 JSON 출력 구조를 정의합니다.
class ReviewInterval(BaseModel):
    next_interval: int = Field(description="계산된 다음 복습 주기(일)")

# JSON 출력 파서를 생성합니다.
parser = JsonOutputParser(pydantic_object=ReviewInterval)

# 복습 주기 계산만을 위한 LLM을 초기화합니다.
calculator_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

# 프롬프트를 수정하여, '정답'인 경우의 계산 규칙에만 집중하도록 합니다.
review_prompt = ChatPromptTemplate.from_template(
    template="""
    당신은 인지 과학 및 에빙하우스의 망각 곡선 이론에 기반한 SRS(간헐적 반복 학습) 전문가입니다.
    사용자가 직전에 퀴즈를 **정답**으로 맞혔을 경우, 최적의 다음 복습 주기를 '일(day)' 단위로 계산해야 합니다.

    # 입력 데이터:
    - 현재 복습 주기 (일): {current_interval} (0보다 큰 값)

    # 계산 규칙:
    1.  사용자가 정답을 맞혔으므로, 현재 복습 주기를 1.6배에서 2.2배 사이로 늘립니다. 현재 주기가 길수록 증가율을 높게 적용할 수 있습니다.
    2.  계산된 다음 복습 주기는 반드시 정수여야 합니다. (소수점 이하는 버림)
    3.  최대 복습 주기는 60일을 넘지 않도록 합니다.
    4.  당신의 답변은 반드시 아래 JSON 형식에 맞춰야 합니다.

    {format_instructions}
    """,
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 프롬프트, LLM, JSON 파서를 연결하여 새로운 체인을 구성합니다.
review_chain = review_prompt | calculator_llm | parser

async def calculate_next_interval(is_correct: bool, current_interval: int) -> int:
    """AI를 호출하여 다음 복습 주기를 계산하는 함수"""

    # 규칙 1: 오답인 경우, 당일 복습을 위해 0을 반환합니다.
    if not is_correct:
        return 0

    # 규칙 2: 첫 정답인 경우(현재 주기가 0), 다음 복습일은 1일로 고정합니다.
    if current_interval == 0:
        return 1

    try:
        # 이제 이 코드는 is_correct가 true이고 current_interval > 0인 경우에만 실행됩니다.
        result_dict = await review_chain.ainvoke({
            "current_interval": current_interval
        })
        next_interval = result_dict['next_interval']
    except Exception as e:
        # AI 호출 또는 파싱 실패 시의 예외 처리
        print(f"Error during AI interval calculation: {e}")
        # 정답인 경우의 fallback 로직: 현재 주기에 1.6배를 하고, 최소 1일을 더합니다.
        fallback_interval = int(current_interval * 1.6)
        next_interval = max(fallback_interval, current_interval + 1)

    return next_interval
