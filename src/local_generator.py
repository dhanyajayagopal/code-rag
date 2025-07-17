from transformers import pipeline
from typing import List
from .models import SearchResult

class LocalCodeQAGenerator:
    def __init__(self):
        """Initialize local text generation model"""
        self.generator = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-medium",
            device=-1
        )
    
    def answer_question(self, question: str, search_results: List[SearchResult]) -> str:
        """Generate an answer using local model"""
        
        context_parts = []
        for result in search_results[:2]:
            context_parts.append(f"Code from {result.chunk.file_path}:\n{result.chunk.content}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""Question: {question}

Relevant code:
{context}

Answer: Based on the code, """
        
        try:
            response = self.generator(
                prompt,
                max_length=len(prompt.split()) + 100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
            
            full_response = response[0]['generated_text']
            answer = full_response[len(prompt):].strip()
            
            return answer if answer else "I can find the relevant code but need more context to provide a detailed explanation."
            
        except Exception as e:
            return f"Error generating answer: {e}"