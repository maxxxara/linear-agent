from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from uuid import uuid4
from pydantic import BaseModel
from src.graph.utils.prompts import MEMORY_ANALYSIS_PROMPT
from typing import Optional
from langchain_core.documents import Document
from datetime import datetime

class MemoryAnalysis(BaseModel):
    memory_context: Optional[str] = None
    should_save: bool

class MemoryService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.vector_store = Chroma(
            collection_name="user_memory",
            collection_metadata={"hnsw:space": "cosine"},
            create_collection_if_not_exists=True,
            embedding_function=self.embeddings,
            persist_directory="./chroma_db",  
        )
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.COMPARE_MEMORY_THRESHOLD = 0.7
        self.RETURN_MEMORY_THRESHOLD = 0.5

    async def _find_similar_memory(self, message: str) -> bool:
        results = await self.vector_store.asimilarity_search_with_relevance_scores(
            message,
            k=1
        )
        if not results or len(results) == 0:
            return False
        _, similarity_score = results[0]
        return similarity_score > self.COMPARE_MEMORY_THRESHOLD

    async def _pick_possible_memory(self, message: str) -> MemoryAnalysis:
        prompt = MEMORY_ANALYSIS_PROMPT.format(message=message)
        response = await self.llm.with_structured_output(MemoryAnalysis).ainvoke(prompt)
        return response
    
    def _get_all_memories(self) -> list[Document]:
        return self.vector_store.get()

    async def extract_and_save_memory(self, message: str):
        memory_analysis = await self._pick_possible_memory(message)
        if memory_analysis.should_save and memory_analysis.memory_context:
            similar_memory = await self._find_similar_memory(memory_analysis.memory_context)
            if similar_memory:
                print("Same memory found")
            else:
                document_1 = Document(
                    page_content=memory_analysis.memory_context,
                    metadata={"timestamp": datetime.now().isoformat()},
                    id=1,
                )
                documents = [
                    document_1,
                ]
                uuids = [str(uuid4()) for _ in range(len(documents))]

                await self.vector_store.aadd_documents(documents=documents, ids=uuids)
        else:
            print("Memory not saved")

    async def get_relevant_memories(self, message: str) -> str:
        memories = await self.vector_store.asimilarity_search_with_relevance_scores(message, k=3)
        filtered_memories = [(doc, score) for doc, score in memories if score > self.RETURN_MEMORY_THRESHOLD]
        
        if filtered_memories:
            return "\n".join(f"- {doc.page_content}" for doc, _ in filtered_memories)
        else:
            return None


def get_memory_manager() -> MemoryService:
    return MemoryService()
