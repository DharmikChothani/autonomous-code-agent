from typing import Annotated, TypedDict
import operator


class AgentState(TypedDict):

    task: str

    plan: list

    current_step: int

    generated_code: str
    test_code: str

    execution_result: str
    test_result: str

    review: str

    critic_result: str
    reflection: str

    quality_score: float

    status: str
    error: str

    retry_count: int

    final_report: str

    events: Annotated[
        list,
        operator.add
    ]