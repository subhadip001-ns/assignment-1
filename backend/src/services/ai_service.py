import os
from typing import Iterator

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from ..ai.tools import (
    fetch_all_courses as fetch_courses_tool,
    enroll_into_course as enroll_tool,
    add_numbers as add_numbers_tool,
    search_course_information as search_course_information_tool
)
from ..ai.prompts import SYSTEM_PROMPT


class AIService:
    def __init__(self, is_streaming: bool = False):
        # Initialize Groq LLM with streaming enabled
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="meta-llama/llama-4-scout-17b-16e-instruct",  # Using a supported Groq model
            temperature=0.2,
            streaming=is_streaming,
            # reasoning_effort="low"
        )

        # Define tools
        self.tools = [add_numbers_tool, fetch_courses_tool, enroll_tool, search_course_information_tool]

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
            print("AI Message: ", ai_msg.content)

            # Check if the AI wants to use tools
            if ai_msg.tool_calls:
                print("Tool Calls: ", ai_msg.tool_calls)
                # Execute the tools
                tool_results = []
                for tool_call in ai_msg.tool_calls:
                    if tool_call["name"] == "add_numbers_tool":
                        result = add_numbers_tool.invoke(tool_call["args"])
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    elif tool_call["name"] == "fetch_courses_tool":
                        result = fetch_courses_tool.invoke(tool_call["args"])
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    elif tool_call["name"] == "enroll_tool":
                        result = enroll_tool.invoke(tool_call["args"])
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
        Streaming chat method with real LLM streaming and tool support
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
            # Use the LLM with tools for decision making (same as chat method)
            ai_msg = self.llm_with_tools.invoke(messages)

            print("AI Message: ", ai_msg.content)
            print("Tool Calls: ", ai_msg.tool_calls)

            if ai_msg.tool_calls:
                # Execute the tools
                tool_results = []
                for tool_call in ai_msg.tool_calls:
                    if tool_call["name"] == "add_numbers":
                        result = add_numbers_tool.invoke(tool_call["args"])
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    elif tool_call["name"] == "fetch_all_courses":
                        result = fetch_courses_tool.invoke(tool_call["args"])
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    elif tool_call["name"] == "enroll_into_course":
                        result = enroll_tool.invoke(tool_call["args"])
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    elif tool_call["name"] == "search_course_information":
                        result = search_course_information_tool.invoke(tool_call["args"])
                        print("Result: ", result)
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))

                # Add tool results to messages
                messages.extend([ai_msg] + tool_results)

            # Stream the final response from LLM
            for chunk in self.llm.stream(messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            yield f"Error: {str(e)}"


# Singleton instance
ai_service = AIService()
