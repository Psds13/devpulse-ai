import os
import asyncio
from typing import Dict, Any, List
from utils.logger import setup_logger
from openai import AsyncOpenAI

logger = setup_logger(__name__)

class AIService:
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY", "")
        self.is_simulated = not bool(self.api_key)
        
        if self.is_simulated:
            logger.info("AI_API_KEY not provided. Running AI Service in SIMULATION mode.")
        else:
            # We initialize AsyncOpenAI with the provided API Key.
            self.client = AsyncOpenAI(api_key=self.api_key)

    async def get_suggestions(self, file_name: str, patch_content: str, issues: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Sends the patch and found issues to an LLM to get code improvement suggestions.
        """
        if self.is_simulated:
            await asyncio.sleep(0.5) # Simulate network delay
            if not patch_content:
                return {}
            
            # Simple rule-based mock for demonstration
            suggestion = "Consider refactoring. Extract large logic into smaller functions. "
            if "TODO" in patch_content:
                suggestion += "Resolve TODO comments scattered in code. "
                
            return {file_name: f"[SIMULATED AI] {suggestion}"}
            
        else:
            logger.info(f"Using actual API key to call OpenAI for {file_name}")
            
            # Format static issues into a text block to feed as context for the AI
            issues_text = "\n".join([f"- [{iss['severity'].upper()}] {iss['type']}: {iss['message']}" for iss in issues])
            
            prompt = f"""
            You are a Senior Software Engineer acting as a Code Reviewer.
            Review the following code diff for the file '{file_name}'.
            
            Consider these static analysis issues found prior to your review:
            {issues_text if issues else "None"}
            
            Here is the code diff:
            ```diff
            {patch_content}
            ```
            
            Provide actionable, specific, and concise suggestions to improve the code. Focus on:
            - Best practices and clean code principles.
            - Performance, and potential bugs.
            - Provide a brief code snippet if recommending a specific refactoring.
            """
            
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini", # Fast, cost-efficient, great context windows
                    messages=[
                        {"role": "system", "content": "You are a senior code reviewer and software architect assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.2
                )
                
                suggestion = response.choices[0].message.content.strip()
                return {file_name: suggestion}
            except Exception as e:
                logger.error(f"Error calling OpenAI API for {file_name}: {e}")
                return {file_name: f"[AI ERROR] Failed to generate suggestions via OpenAI: {e}"}
