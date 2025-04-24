import tkinter as tk
from tkinter import filedialog, messagebox
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient, InvalidAPIKeyError
import requests

# ✅ Direct API keys in this file
GEMINI_API_KEY = "AIzaSyBSkA0V5nvGoK-NJl_G_VAx89ZcpuO-iyM"
TAVILY_API_KEY = "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"  # Replace with your actual Tavily API key

# 🔧 Configure APIs
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

gemini_llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", google_api_key=GEMINI_API_KEY)

# 🌐 Agent 1: Web Research Agent using Tavily
def research_agent(query: str) -> str:
    print("🔍 Research Agent activated...")
    try:
        result = tavily_client.search(query=query, include_answer=True)
        answer = result.get("answer", "")
        docs = "\n".join([doc.get("content", "") for doc in result.get("results", [])])
        return f"{answer}\n\n{docs}".strip()
    except InvalidAPIKeyError:
        return "Error: The API key is invalid or missing. Please check your API key."

# ✍️ Agent 2: Answer Drafting Agent using Gemini
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

# 🧠 Define the state schema
class ResearchState(dict):
    query: str
    research: str
    answer: str

# 🧱 LangGraph: Define the graph
builder = StateGraph(ResearchState)

# Nodes
builder.add_node("ResearchAgent", RunnableLambda(lambda state: {"query": state["query"], "research": research_agent(state["query"])}))
builder.add_node("AnswerAgent", RunnableLambda(lambda state: {"query": state["query"], "research": state["research"], "answer": drafting_agent(state)}))

# Edges
builder.set_entry_point("ResearchAgent")
builder.add_edge("ResearchAgent", "AnswerAgent")
builder.add_edge("AnswerAgent", END)

# Build the graph
graph = builder.compile()

# 🚀 Run the system
def run_deep_research_system(user_query: str):
    result = graph.invoke({"query": user_query})
    return result["answer"]

# 🌐 Fetch Data from URL
def fetch_web_data(url: str) -> str:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error fetching data from {url}. HTTP Status: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# 📂 Read Data from File
def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# 🧪 Create the Tkinter UI
def create_ui():
    def on_query_submit():
        user_query = query_input.get("1.0", "end-1c").strip()

        if user_query:
            result = run_deep_research_system(user_query)
            result_text.delete("1.0", "end")
            result_text.insert("1.0", result)
        else:
            messagebox.showwarning("Input Error", "Please enter a query.")

    def on_file_open():
        file_path = filedialog.askopenfilename()
        if file_path:
            file_content = read_file(file_path)
            query_input.delete("1.0", "end")
            query_input.insert("1.0", file_content)

    def on_url_submit():
        url = url_input.get().strip()
        if url:
            web_data = fetch_web_data(url)
            query_input.delete("1.0", "end")
            query_input.insert("1.0", web_data)
        else:
            messagebox.showwarning("Input Error", "Please enter a valid URL.")

    # Create the main window
    root = tk.Tk()
    root.title("Deep Research AI System")
    root.geometry("800x600")
    root.configure(bg="#1e1e1e")  # Dark background for the futuristic look

    # Add a label
    label = tk.Label(root, text="Enter your research query:", font=("Helvetica", 14, "bold"), fg="#00ffff", bg="#1e1e1e")
    label.pack(pady=10)

    # Create a text box for input with holographic neon effect
    query_input = tk.Text(root, height=5, width=70, font=("Helvetica", 12), bg="#333333", fg="#00ffff", insertbackground='cyan', bd=0)
    query_input.pack(pady=10)
    query_input.config(highlightbackground="cyan", highlightthickness=2)

    # Frame to organize buttons in a row
    button_frame = tk.Frame(root, bg="#1e1e1e")
    button_frame.pack(pady=10)

    # Buttons for file, URL, and submit with neon glow effect
    file_button = tk.Button(button_frame, text="Upload File", command=on_file_open, font=("Helvetica", 12, "bold"), fg="cyan", bg="#1e1e1e", relief="flat", bd=0)
    file_button.pack(side=tk.LEFT, padx=5)

    url_button = tk.Button(button_frame, text="Fetch URL", command=on_url_submit, font=("Helvetica", 12, "bold"), fg="cyan", bg="#1e1e1e", relief="flat", bd=0)
    url_button.pack(side=tk.LEFT, padx=5)
    submit_button = tk.Button(button_frame, text="Ask", command=on_query_submit, font=("Helvetica", 12, "bold"), fg="cyan", bg="#1e1e1e", relief="flat", bd=0)
    submit_button.pack(side=tk.LEFT, padx=5)

    # Bind the Enter key to trigger the submit button
    root.bind('<Return>', lambda event: on_query_submit())

    # Create a text box to display the result with neon glow effect
    result_text = tk.Text(root, height=10, width=70, font=("Helvetica", 12), wrap="word", bg="#333333", fg="#00ffff", bd=0)
    result_text.pack(pady=10)
    result_text.config(highlightbackground="cyan", highlightthickness=2)

    # Holographic glowing effect for buttons (hover effect)
    def on_enter(button):
        button.config(fg="cyan", bg="#333333", relief="raised", bd=2)

    def on_leave(button):
        button.config(fg="cyan", bg="#1e1e1e", relief="flat", bd=0)

    file_button.bind("<Enter>", lambda e: on_enter(file_button))
    file_button.bind("<Leave>", lambda e: on_leave(file_button))

    url_button.bind("<Enter>", lambda e: on_enter(url_button))
    url_button.bind("<Leave>", lambda e: on_leave(url_button))

    submit_button.bind("<Enter>", lambda e: on_enter(submit_button))
    submit_button.bind("<Leave>", lambda e: on_leave(submit_button))

    root.mainloop()

# 🧪 Run the UI
if __name__ == "__main__":
    create_ui()
