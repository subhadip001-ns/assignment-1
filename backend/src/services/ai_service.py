import os
import re
from typing import Iterator

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from ..ai.tools import (
    fetch_all_courses as fetch_courses_tool,
    enroll_into_course as enroll_tool,
    unenroll_from_course as unenroll_tool,
    add_numbers as add_numbers_tool,
    search_course_information as search_course_information_tool
)
from ..ai.prompts import SYSTEM_PROMPT


def fix_markdown_formatting(text: str) -> str:
    """
    Post-process markdown text to ensure proper line breaks and formatting.
    Fixes common issues like headers without blank lines, lists without spacing, etc.
    """
    if not text:
        return text
    
    # Fix: text.## Header -> text.\n\n## Header (most critical fix)
    # This handles cases where headers are concatenated directly after text
    text = re.sub(r'([^\n\s])(#{1,6}\s+)', r'\1\n\n\2', text)
    
    # Fix: text.## Header (with any whitespace) -> text.\n\n## Header
    text = re.sub(r'([^\n])\s*(#{1,6}\s+)', r'\1\n\n\2', text)
    
    # Ensure headers have blank lines after them
    # Pattern: ## Headertext -> ## Header\n\ntext
    text = re.sub(r'(#{1,6}[^\n]+)\n([^\n#\s\-*])', r'\1\n\n\2', text)
    
    # Fix: text.- item or text.* item -> text.\n\n- item
    text = re.sub(r'([^\n\s])\s*([-*]\s)', r'\1\n\n\2', text)
    
    # Ensure list items have proper spacing (if there's a newline but no blank line)
    # Pattern: text\n- item -> text\n\n- item
    text = re.sub(r'([^\n])\n([-*]\s)', r'\1\n\n\2', text)
    
    # Ensure code blocks have blank lines before and after
    # Pattern: text```code```text -> text\n\n```code```\n\ntext
    text = re.sub(r'([^\n\s])(```)', r'\1\n\n\2', text)
    text = re.sub(r'(```[^`]*```)([^\n\s])', r'\1\n\n\2', text)
    
    # Fix paragraphs: ensure proper spacing between sentences and sections
    # Split into lines and process intelligently
    lines = text.split('\n')
    result = []
    prev_was_empty = False
    prev_line_was_special = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        is_header = stripped.startswith('#')
        is_list_item = stripped.startswith('-') or stripped.startswith('*')
        is_code_block = stripped.startswith('```')
        is_table_row = '|' in stripped and stripped.count('|') >= 2
        is_special = is_header or is_list_item or is_code_block or is_table_row
        
        if not stripped:
            # Empty line
            if not prev_was_empty:
                result.append('')
            prev_was_empty = True
            prev_line_was_special = False
        elif is_special:
            # Special markdown element
            if not prev_was_empty and not prev_line_was_special and result:
                # Add blank line before special elements
                result.append('')
            result.append(line)
            prev_was_empty = False
            prev_line_was_special = True
        else:
            # Regular paragraph line
            if result and result[-1] and not prev_was_empty:
                prev_line = result[-1].strip()
                # If previous line was a paragraph (not special), ensure spacing
                if not (prev_line.startswith('#') or prev_line.startswith('-') or 
                       prev_line.startswith('*') or prev_line.startswith('```') or
                       '|' in prev_line):
                    # Check if we need spacing (if line ends with punctuation or is a sentence)
                    if prev_line and prev_line[-1] in '.!?':
                        result.append('')
            result.append(line)
            prev_was_empty = False
            prev_line_was_special = False
    
    text = '\n'.join(result)
    
    # Clean up multiple consecutive blank lines (max 2)
    text = re.sub(r'\n{3,}', r'\n\n', text)
    
    # Remove blank lines at the very start
    text = text.lstrip('\n')
    
    # Ensure trailing newline
    if text and not text.endswith('\n'):
        text += '\n'
    
    return text


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
        self.tools = [add_numbers_tool, fetch_courses_tool, enroll_tool, unenroll_tool, search_course_information_tool]

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
                    elif tool_call["name"] == "unenroll_from_course":
                        result = unenroll_tool.invoke(tool_call["args"])
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    elif tool_call["name"] == "search_course_information":
                        result = search_course_information_tool.invoke(tool_call["args"])
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
            import html
            error_msg = html.escape(str(e))
            return f"<h2>Error</h2><p><strong>An error occurred:</strong> <code>{error_msg}</code></p>"

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
                    elif tool_call["name"] == "unenroll_from_course":
                        result = unenroll_tool.invoke(tool_call["args"])
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
            # Collect all chunks for post-processing
            complete_response = ""
            for chunk in self.llm.stream(messages):
                if chunk.content:
                    complete_response += chunk.content
                    # Yield chunks immediately for real-time streaming
                    yield chunk.content
            
            # After streaming completes, apply markdown formatting fixes
            # and send a final correction chunk if needed
            formatted_response = fix_markdown_formatting(complete_response)
            
            # If formatting changed the response, send the corrected version
            # The frontend can use this to update the final rendered markdown
            if formatted_response != complete_response:
                # Calculate the difference and send correction
                # For now, we'll send a special marker that frontend can use
                # But actually, ReactMarkdown should handle incremental updates
                # So we'll just ensure the prompt generates correct markdown
                pass

        except Exception as e:
            import html
            error_msg = html.escape(str(e))
            yield f"<h2>Error</h2><p><strong>An error occurred:</strong> <code>{error_msg}</code></p>"


# Singleton instance
ai_service = AIService()
