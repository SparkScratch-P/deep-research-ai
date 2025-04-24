import tkinter as tk
from tkinter import filedialog, messagebox
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient, InvalidAPIKeyError
import requests
from markdown2 import markdown
import re

# 🔐 API Keys
GEMINI_API_KEY = "AIzaSyBSkA0V5nvGoK-NJl_G_VAx89ZcpuO-iyM"
TAVILY_API_KEY = "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"

# 🔧 API Config
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
gemini_llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", google_api_key=GEMINI_API_KEY)


# 🌐 Agent 1 - Research
def research_agent(query: str) -> str:
    print("🔍 Research Agent Activated")
    try:
        result = tavily_client.search(query=query, include_answer=True)
        answer = result.get("answer", "")
        docs = "\n".join([doc.get("content", "") for doc in result.get("results", [])])
        return f"{answer}\n\n{docs}".strip()
    except InvalidAPIKeyError:
        return "❌ Error: Invalid or missing API key."


# ✍️ Agent 2 - Drafting
def drafting_agent(data: dict) -> str:
    query = data["query"]
    research_context = data["research"]
    prompt = f"""
You are a highly intelligent AI expert. Use the context below to answer the user's query clearly and comprehensively.

=== CONTEXT ===
{research_context}

=== QUERY ===
{query}

=== ANSWER ===
"""
    response = gemini_llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


# 🧠 State
class ResearchState(dict):
    query: str
    research: str
    answer: str


builder = StateGraph(ResearchState)
builder.add_node("ResearchAgent",
                 RunnableLambda(lambda state: {"query": state["query"], "research": research_agent(state["query"])}))
builder.add_node("AnswerAgent", RunnableLambda(
    lambda state: {"query": state["query"], "research": state["research"], "answer": drafting_agent(state)}))
builder.set_entry_point("ResearchAgent")
builder.add_edge("ResearchAgent", "AnswerAgent")
builder.add_edge("AnswerAgent", END)
graph = builder.compile()


def run_deep_research_system(user_query: str):
    result = graph.invoke({"query": user_query})
    return result["answer"]


def fetch_web_data(url: str) -> str:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"❌ Error fetching URL. HTTP {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


def markdown_to_pretty_text(markdown_text: str) -> str:
    formatted_text = ""
    lines = markdown_text.split("\n")

    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Handle code blocks (```):
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            formatted_text += "\n" + ("─" * 50) + "\n" if in_code_block else "\n" + ("─" * 50) + "\n"
            continue
        if in_code_block:
            formatted_text += line + "\n"
            continue

        # Headers
        if stripped.startswith("# "):
            header = stripped[2:].strip().upper()
            formatted_text += f"\n\n{'=' * 50}\n{header}\n{'=' * 50}\n"
        elif stripped.startswith("## "):
            header = stripped[3:].strip().upper()
            formatted_text += f"\n\n{'-' * 40}\n{header}\n{'-' * 40}\n"
        elif stripped.startswith("### "):
            header = stripped[4:].strip().capitalize()
            formatted_text += f"\n\n{header}\n{'-' * len(header)}\n"
        else:
            # Bold
            line = re.sub(r"\*\*(.*?)\*\*", lambda m: m.group(1).upper(), line)
            # Italic
            line = re.sub(r"\*(.*?)\*", lambda m: m.group(1).capitalize(), line)
            # Inline code
            line = re.sub(r"`(.*?)`", lambda m: f"[{m.group(1)}]", line)
            # Strip HTML tags
            line = re.sub(r"<[^>]+>", "", line)
            formatted_text += line + "\n"

    return formatted_text.strip()


# 🧪 UI
def create_ui():
    def on_query_submit():
        user_query = query_input.get("1.0", "end-1c").strip()
        if user_query:
            processing_label.config(text="🔄 Processing...")
            root.update_idletasks()
            result = run_deep_research_system(user_query)

            # Convert Markdown to plain text with styling using the new function
            plain_text_result = markdown(result, extras=["strip-html", "fenced-code-blocks", "tables"])
            formatted_text = markdown_to_pretty_text(plain_text_result)

            # Use the formatted text for display
            plain_text_result = formatted_text.strip()
            # Clear previous content
            result_text.delete("1.0", "end")

            # Implement typewriter effect for plain text content
            delay = 5  # Set delay for normal typing speed
            for char in plain_text_result:
                result_text.insert(tk.END, char)
                result_text.update()
                result_text.after(delay)

            processing_label.config(text="")
        else:
            messagebox.showwarning("⚠️ Input Missing", "Please enter a query.")

    def on_file_open():
        file_path = filedialog.askopenfilename()
        if file_path:
            file_content = read_file(file_path)
            query_input.delete("1.0", "end")
            query_input.insert("1.0", file_content)

    def on_url_submit():
        url = url_input.get().strip()
        if url:
            processing_label.config(text="🔄 Fetching URL...")
            root.update_idletasks()
            web_data = fetch_web_data(url)
            query_input.delete("1.0", "end")
            query_input.insert("1.0", web_data)
            processing_label.config(text="")
        else:
            messagebox.showwarning("⚠️ URL Missing", "Please enter a URL.")

    def typewriter_effect(text):
        result_text.delete("1.0", "end")
        delay = 5  # Set delay for normal typing speed
        for i in range(len(text)):
            result_text.insert(tk.END, text[i])  # Fix: Insert text normally (left-to-right)
            result_text.update()
            result_text.after(delay)
        result_text.insert(tk.END, "\n")  # Add a newline after typing completes

    root = tk.Tk()
    root.title("🤖 Deep Research AI System")
    root.attributes("-fullscreen", True)  # Set full screen
    root.configure(bg="#0a0f1f")

    futuristic_font = ("Lucida Console", 12)
    title_font = ("Orbitron", 22, "bold")

    # 🪩 Title
    title_label = tk.Label(root, text="🌌 DEEP RESEARCH AI ASSISTANT 🌌", font=title_font,
                           fg="#00ffff", bg="#0a0f1f")
    title_label.pack(pady=(30, 10))

    # ✍️ Query Input
    query_input = tk.Text(root, height=6, width=85, font=futuristic_font, bg="#111827", fg="#00ffff",
                          insertbackground="cyan", bd=0, highlightbackground="#00ffff", highlightthickness=2)
    query_input.pack(pady=(10, 15))

    # 🌐 URL + Upload Row
    url_frame = tk.Frame(root, bg="#0a0f1f")
    url_frame.pack(pady=5)

    url_input = tk.Entry(url_frame, width=50, font=futuristic_font, bg="#0f172a", fg="#00ffff",
                         insertbackground="cyan", highlightbackground="#00ffff", highlightthickness=1, bd=0)
    url_input.pack(side=tk.LEFT, padx=5)

    url_button = tk.Button(url_frame, text="🌐 Fetch URL", command=on_url_submit,
                           font=futuristic_font, fg="#00ffff", bg="#111827", relief="flat")
    url_button.pack(side=tk.LEFT, padx=5)

    file_button = tk.Button(url_frame, text="📂 Upload File", command=on_file_open,
                            font=futuristic_font, fg="#00ffff", bg="#111827", relief="flat")
    file_button.pack(side=tk.LEFT, padx=5)

    # 🎯 Action Buttons
    btn_frame = tk.Frame(root, bg="#0a0f1f")
    btn_frame.pack(pady=10)

    def on_enter_key(event):
        on_query_submit()

    root.bind('<Return>', on_enter_key)

    submit_button = tk.Button(btn_frame, text="🚀 Ask AI", command=on_query_submit,
                              font=futuristic_font, fg="#00ffff", bg="#111827", relief="flat")
    submit_button.pack(side=tk.LEFT, padx=10)

    # 🧠 Output Display
    result_text = tk.Text(root, height=18, width=85, font=futuristic_font, wrap="word", bg="#111827",
                          fg="#00ffff", bd=0, highlightbackground="#00ffff", highlightthickness=2)
    result_text.pack(pady=(20, 10))

    # ⏳ Processing status
    global processing_label
    processing_label = tk.Label(root, text="", font=("Lucida Console", 10),
                                fg="#00ffff", bg="#0a0f1f")
    processing_label.pack(pady=(0, 15))

    root.mainloop()


# 🚀 Launch App
if __name__ == "__main__":
    create_ui()
