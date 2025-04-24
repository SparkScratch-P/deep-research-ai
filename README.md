# Deep Research AI System

The **Deep Research AI System** is a versatile tool that leverages advanced AI agents for **web research** and **answer drafting**. It integrates **Tavily**, a web crawling client, and **Gemini**, Google's generative AI model, to provide intelligent responses to user queries.

This system allows users to perform the following tasks:
- Fetch data from URLs or files.
- Perform web research through the **Tavily API**.
- Draft answers based on research context using the **Gemini API**.
- Use a futuristic, holographic Tkinter-based GUI to interact with the system.

## Key Features

- **Web Research Agent**: Uses **Tavily** to search the web and provide context-rich research results.
- **Answer Drafting Agent**: Uses **Gemini** to draft detailed answers based on the gathered research context.
- **Futuristic GUI**: Features a holographic neon effect with a sleek dark background.
- **File & URL Input**: Ability to input queries from a file or directly from a URL.

## Requirements

- Python 3.x
- Tkinter (for GUI)
- LangChain & LangGraph (for chaining AI agents)
- Tavily (for web crawling)
- Gemini (Google's generative AI)
- Requests (for HTTP requests)

### Install Dependencies

To get started, install the necessary Python packages. Run the following commands to install the dependencies:

```bash
pip install tkinter
pip install langchain
pip install langgraph
pip install langchain-google-genai
pip install tavily
pip install requests
