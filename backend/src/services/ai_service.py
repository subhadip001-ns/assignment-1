import os
from typing import Iterator

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from ..ai.tools import add_numbers
from ..ai.prompts import SYSTEM_PROMPT


class AIService:
    def __init__(self):
        # Initialize Groq LLM
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",  # Using a supported Groq model
            temperature=0.7
        )

        # Define tools
        self.tools = [add_numbers]

        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def chat(self, message: str, chat_history: list = None) -> str:
        """
        Non-streaming chat method
        """
        if chat_history is None:
            chat_history = []

        # Convert chat history to LangChain format
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # Add the current message
        messages.append(HumanMessage(content=message))

        try:
            # Use the LLM with tools
            ai_msg = self.llm_with_tools.invoke(messages)

            # Check if the AI wants to use tools
            if ai_msg.tool_calls:
                # Execute the tools
                tool_results = []
                for tool_call in ai_msg.tool_calls:
                    if tool_call["name"] == "add_numbers":
                        result = add_numbers.invoke(tool_call["args"])
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))

                # Add tool results to messages and get final response
                messages.extend([ai_msg] + tool_results)
                final_response = self.llm.invoke(messages)
                return final_response.content
            else:
                # No tools needed
                return ai_msg.content

        except Exception as e:
            return f"Error: {str(e)}"

    def chat_stream(self, message: str, chat_history: list = None) -> Iterator[str]:
        """
        Streaming chat method
        """
        if chat_history is None:
            chat_history = []

        # Convert chat history to LangChain format
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # Add the current message
        messages.append(HumanMessage(content=message))

        try:
            # For streaming, we'll simulate it by yielding chunks of the response
            response = self.chat(message, chat_history)

            # Yield the response in chunks for streaming effect
            words = response.split()
            current_chunk = ""

            for word in words:
                current_chunk += word + " "
                if len(current_chunk) >= 50:  # Yield every ~50 characters
                    yield current_chunk
                    current_chunk = ""

            if current_chunk:
                yield current_chunk

        except Exception as e:
            yield f"Error: {str(e)}"


# Singleton instance
ai_service = AIService()
