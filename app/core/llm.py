from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from .config import FAISS_INDEX_PATH, OPENAI_API_KEY

# LLM 모델
llm = ChatOpenAI(
    model="gpt-4", 
    temperature=0.4, 
    streaming=True,
    api_key=OPENAI_API_KEY
)

# 임베딩 모델
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# FAISS 벡터 스토어 로드 및 리트리버 생성
vector_store = FAISS.load_local(
    FAISS_INDEX_PATH, 
    embeddings, 
    allow_dangerous_deserialization=True
)
retriever = vector_store.as_retriever()
