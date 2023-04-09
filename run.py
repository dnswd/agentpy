from agent import Agent
from llms import ChatGPT
from tools import HackerNewsSearchTool, PythonREPLTool, SerpAPITool

if __name__ == "__main__":
    # setup agent
    # build ask for prompt
    # run prompt
    prompt = input("Enter a question / task for the agent: ")
    agent = Agent(llm=ChatGPT(), tools=[HackerNewsSearchTool(crawl_urls=True), SerpAPITool()])
    result = agent.run(prompt)

    print(f"Final answer is {result}")
