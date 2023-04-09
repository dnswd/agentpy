import datetime
import re

from pydantic import BaseModel
from typing import List, Dict, Tuple
from llms.chatGPT import ChatGPT
from tools.base import ToolInterface
from tools.python_repl import PythonREPLTool


FINAL_ANSWER_TOKEN = "Final Answer:"
OBSERVATION_TOKEN = "Observation:"
THOUGHT_TOKEN = "Orientation:"
PROMPT_TEMPLATE = """Today is {today} and you can use tools to get new information. Answer the question as best as you can using the following tools: 

{tool_description}
None: No actions needed

You are not given a goal but should create and alter a goal based on the previous actions you have taken. You will answer using the following format:

Question: the input question you must answer
Observation: comment of what to do next 
Orientation: orient the goal based on the observation
Action: the action to take, exactly one element of [None,{tool_names}]
Action Input: the input to the action
Observation: comment of what to do next based on the result of the action and the collection of information from previous actions
Orientation: refine the goal based on the observation
... (this Observation/Orientation/Action Input/Observation repeats N times, use it until you are sure of the answer)
Observation: I now know the final answer
Final Answer: your final answer to the original input question

Begin!

Question: {question}
Observation: {previous_responses}
"""


class Agent(BaseModel):
    llm: ChatGPT
    tools: List[ToolInterface]
    prompt_template: str = PROMPT_TEMPLATE
    max_loops: int = 15
    # The stop pattern is used, so the LLM does not hallucinate until the end
    stop_pattern: List[str] = [f'\n{OBSERVATION_TOKEN}', f'\n\t{OBSERVATION_TOKEN}']

    @property
    def tool_description(self) -> str:
        return "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])

    @property
    def tool_names(self) -> str:
        return ",".join([tool.name for tool in self.tools])

    @property
    def tool_by_names(self) -> Dict[str, ToolInterface]:
        return {tool.name: tool for tool in self.tools}

    def run(self, question: str):
        previous_responses = []
        num_loops = 0
        prompt = self.prompt_template.format(
                today = datetime.date.today(),
                tool_description=self.tool_description,
                tool_names=self.tool_names,
                question=question,
                previous_responses='{previous_responses}'
        )
        print(prompt.format(previous_responses=''))
        while num_loops < self.max_loops:
            num_loops += 1
            curr_prompt = prompt.format(previous_responses='\n'.join(previous_responses))
            generated, tool, tool_input = self.decide_next_action(curr_prompt)
            # print("======DEBUG=====")
            # print("generated:", generated)
            # print("tool:", tool)
            # print("tool_input:", tool_input)
            tool_result = None
            if tool is not None:
                if tool == 'Final Answer':
                    return tool_input
                if tool not in self.tool_by_names:
                    raise ValueError(f"Unknown tool: {tool}")
                tool_result = self.tool_by_names[tool].use(tool_input)
            generated += f"\n{OBSERVATION_TOKEN} {tool_result if tool_result is not None else ''}\n{THOUGHT_TOKEN}"
            print(generated)
            previous_responses.append(generated)

    def decide_next_action(self, prompt: str) -> str:
        generated = self.llm.generate(prompt, stop=self.stop_pattern)
        tool, tool_input = self._parse(generated)
        return generated, tool, tool_input

    def _parse(self, generated: str) -> Tuple[str, str]:
        if "final" in generated.lower() and "answer" in generated.lower():
            return "Final Answer", generated.strip()
        action_regex = r"Action: [\[]?(.*?)[\]]?"
        match = re.search(action_regex, generated, re.DOTALL)
        if not match:
            raise ValueError(f"Output of LLM is not parsable for next tool use: `{generated}`")
        tool = match.group(1).strip()
        if tool == "None":
            return None, None
        input_regex = r"Action Input:[\s]*(.*)"
        match = re.search(input_regex, generated, re.DOTALL)
        if not match:
            raise ValueError(f"Output of LLM is not parsable for next tool use: `{generated}`")
        tool_input = match.group(1).strip(" ").strip('"')
        return tool, tool_input


if __name__ == '__main__':
    agent = Agent(llm=ChatGPT(), tools=[PythonREPLTool()])
    result = agent.run("What is 7 * 9 - 34 in Python?")

    print(f"Final answer is {result}")
