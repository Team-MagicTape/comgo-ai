from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .core.llm import llm, retriever
from .prompts import (
    router_prompt,
    explanation_prompt,
    direct_question_prompt,
    conversation_prompt,
)

# --- 전문가 체인 정의 ---
explanation_rag_chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, explanation_prompt))
direct_rag_chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, direct_question_prompt))
conversation_chain = conversation_prompt | llm | StrOutputParser()

# --- 라우터 및 브랜치 정의 ---
router = router_prompt | llm | StrOutputParser()

branch = RunnableBranch(
    (lambda x: "explanation_request" in x["topic"].lower(), explanation_rag_chain),
    (lambda x: "direct_question" in x["topic"].lower(), direct_rag_chain),
    conversation_chain,
)

# --- 전체 체인 통합 ---
full_chain = RunnablePassthrough.assign(topic=router) | branch
