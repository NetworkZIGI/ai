__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os

from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
import os
from utils import bedrock
from langchain.embeddings import BedrockEmbeddings

os.environ["AWS_DEFAULT_REGION"] = "us-east-1"  
os.environ["AWS_PROFILE"] = "zigi-bedrock"

# PDF 파일 경로 목록
pdf_files = [
    "./data/visa-kor.pdf",
    "./data/card.pdf",
    "./data/network.pdf"
]

# 로더, 텍스트 분할기 및 임베딩 초기화
text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=600)

boto3_bedrock = bedrock.get_bedrock_client(
    # IAM User에 Bedrock에 대한 권한이 없이 Role을 Assume하는 경우
    # assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None), 
    region=os.environ.get("AWS_DEFAULT_REGION", None)
)

bedrock_embeddings = BedrockEmbeddings(client=boto3_bedrock, model_id="amazon.titan-embed-text-v1")

texts = []

# 각 PDF 파일에 대해 작업 수행
for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    documents = loader.load()
    texts.extend(text_splitter.split_documents(documents))

#벡터 DB 생성
docsearch = Chroma.from_documents(texts, bedrock_embeddings,persist_directory="./zigi_chromadb")
print("Vector DB에 데이터를 저장 완료했습니다")
