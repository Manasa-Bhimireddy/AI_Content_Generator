import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

class GroqGenerator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
            logger.info("Groq client initialized successfully.")
        else:
            logger.warning("GROQ_API_KEY not found in environment variables. Groq content generation will fail until it is set.")

    def generate_content(self, topic: str, content_type: str, tone: str, keywords: str = "", retrieved_context: list = None) -> str:
        """
        Generates content using the Groq API.
        Enriches the prompt with retrieved context from similar past posts (RAG).
        """
        if not self.client:
            # Try reloading in case the environment was updated
            self.api_key = os.getenv("GROQ_API_KEY")
            if self.api_key:
                self.client = Groq(api_key=self.api_key)
            else:
                return "Error: GROQ_API_KEY is not configured. Please add your Groq API Key to the .env file in the root directory."

        # Select model (standard Groq models: llama-3.3-70b-versatile, llama3-8b-8192)
        model = "llama-3.3-70b-versatile"

        # Construct System Prompt based on content type and tone
        system_prompt = self._build_system_prompt(content_type, tone, keywords)

        # Construct User Prompt with topic and RAG context
        user_prompt = self._build_user_prompt(topic, content_type, tone, keywords, retrieved_context)

        try:
            logger.info(f"Requesting content from Groq using model {model}...")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=model,
                temperature=0.7,
                max_tokens=2048,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            # Try fallback to llama3-8b-8192
            try:
                fallback_model = "llama3-8b-8192"
                logger.info(f"Attempting fallback to {fallback_model}...")
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=fallback_model,
                    temperature=0.7,
                    max_tokens=2048,
                )
                return chat_completion.choices[0].message.content
            except Exception as fe:
                logger.error(f"Fallback model also failed: {fe}")
                return f"Error generating content via Groq: {str(e)}"

    def _build_system_prompt(self, content_type: str, tone: str, keywords: str) -> str:
        """
        Formulate a system prompt that sets constraints and style rules based on type and tone.
        """
        prompt = (
            "You are a professional, high-converting AI Content Copywriter. Your goal is to write copy "
            "that is highly engaging, grammatically perfect, and tailored precisely to the user's requirements.\n\n"
        )

        # Style guidelines based on content type
        prompt += "### FORMATTING RULES:\n"
        if content_type.lower() == "blog post":
            prompt += (
                "- Write a comprehensive, well-structured blog post.\n"
                "- Use clear, engaging headings (H1, H2, H3) in Markdown format.\n"
                "- Write an inviting introduction, highly informative body paragraphs with clear transitions, and a concise conclusion.\n"
                "- Keep paragraphs relatively short and highly readable (bullet points are welcome if it aids comprehension).\n"
            )
        elif content_type.lower() == "linkedin post":
            prompt += (
                "- Write a highly engaging LinkedIn post.\n"
                "- Begin with a strong hook to capture attention in the feed (first 2 lines are critical).\n"
                "- Use line breaks extensively to make it easily scannable on mobile and desktop.\n"
                "- Include bullet points or list formatting where appropriate.\n"
                "- Conclude with an engaging question or call-to-action (CTA) to encourage comments.\n"
                "- Add 3 to 5 highly relevant professional hashtags at the very end.\n"
            )
        elif content_type.lower() == "instagram caption":
            prompt += (
                "- Write a captivating Instagram caption.\n"
                "- Start with an attention-grabbing hook and emojis.\n"
                "- Keep the spacing neat and include fun, context-appropriate emojis throughout.\n"
                "- Keep paragraphs short and concise.\n"
                "- Include a clear call-to-action (e.g., 'Double tap if you agree', 'Link in bio', 'Share your thoughts below').\n"
                "- Include 5 to 10 relevant hashtags at the bottom.\n"
            )
        elif content_type.lower() == "twitter thread":
            prompt += (
                "- Write a Twitter (X) thread.\n"
                "- Break the content down into a series of tweets numbered sequentially (e.g., '1/', '2/', '3/', etc.).\n"
                "- Each individual tweet must strictly be under 280 characters.\n"
                "- The first tweet must contain a highly compelling hook to drive thread views.\n"
                "- Ensure the progression of ideas flows logically from tweet to tweet.\n"
                "- Conclude the final tweet with a summarizing thought or a call to action.\n"
            )
        else:
            prompt += (
                f"- Write the content in the format of a {content_type}.\n"
                "- Structure it cleanly using markdown.\n"
            )

        # Tone rules
        prompt += f"\n### TONE GUIDELINE: {tone.upper()}\n"
        if tone.lower() == "professional":
            prompt += "Maintain an authoritative, formal, polished, and objective voice. Use industry-standard terms, logical arguments, and avoid slang or excessive exclamation marks.\n"
        elif tone.lower() == "engaging":
            prompt += "Write in a friendly, conversational, and highly relatable style. Speak directly to the reader ('you'), ask rhetorical questions, and create a dialogue.\n"
        elif tone.lower() == "creative":
            prompt += "Be imaginative, use metaphors, storytelling, vivid imagery, and fresh vocabulary. Avoid clichés and think outside the box to deliver a unique perspective.\n"
        elif tone.lower() == "humorous":
            prompt += "Keep it light-hearted, witty, and fun. Incorporate subtle humor, clever puns, or clean jokes relevant to the topic without losing the core message.\n"
        elif tone.lower() == "informative":
            prompt += "Focus heavily on clear facts, step-by-step guidance, and educational explanations. Be direct, clear, structured, and easy to understand.\n"

        # Keyword rules
        if keywords:
            prompt += f"\n### KEYWORD REQUIREMENT:\n"
            prompt += f"You MUST organically integrate the following keywords/phrases: {keywords}. Make sure they fit naturally in the sentences and don't feel forced.\n"

        prompt += "\nRespond ONLY with the generated content itself. Do not include introductory notes like 'Sure, here is your post' or concluding conversational pleasantries."
        return prompt

    def _build_user_prompt(self, topic: str, content_type: str, tone: str, keywords: str, retrieved_context: list) -> str:
        """
        Formulate a user prompt incorporating topic, requirements, and RAG context.
        """
        prompt = f"Please generate a {content_type} about the following topic.\n"
        prompt += f"Topic: {topic}\n"
        if keywords:
            prompt += f"Keywords to incorporate: {keywords}\n"
        prompt += f"Desired Tone: {tone}\n\n"

        # RAG Context injection
        if retrieved_context:
            prompt += "--- RETRIEVED CONTEXT (Use this as reference to maintain style consistency or facts if relevant) ---\n"
            prompt += "Here is some content you previously generated that is related to this topic:\n\n"
            for idx, item in enumerate(retrieved_context):
                prompt += f"Context Item {idx+1}:\n"
                prompt += f"- Topic: {item['topic']}\n"
                prompt += f"- Type: {item['content_type']}\n"
                prompt += f"- Generated Content:\n{item['generated_content']}\n"
                prompt += "-" * 40 + "\n"
            prompt += "\nEnsure the new post is unique and does not simply copy the context, but rather builds upon it, maintains consistent writing patterns, or references it if helpful.\n"

        return prompt
