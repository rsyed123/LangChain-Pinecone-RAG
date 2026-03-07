"""
Ingest a web page into Pinecone.
Usage: python ingest_url.py <url>
"""
import os
import sys
import uuid
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python ingest_url.py <url>")
    sys.exit(1)

url = sys.argv[1]
print(f"Fetching {url} ...")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers, timeout=15)
response.raise_for_status()

# Strip HTML tags, keep readable text
soup = BeautifulSoup(response.text, "html.parser")
for tag in soup(["script", "style", "nav", "footer", "header"]):
    tag.decompose()
text = soup.get_text(separator="\n", strip=True)

print(f"Extracted {len(text)} characters of text.")

# Chunk it
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=400)
chunks = splitter.split_documents([Document(page_content=text, metadata={"source": url})])
print(f"Split into {len(chunks)} chunks.")

# Upsert into Pinecone
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(os.environ["PINECONE_INDEX_NAME"])
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=os.environ["OPENAI_API_KEY"])
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

ids = [str(uuid.uuid4()) for _ in chunks]
vector_store.add_documents(chunks, ids=ids)
print(f"Done. {len(chunks)} chunks ingested from {url}")
