from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq 
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import os 
from dotenv import load_dotenv

load_dotenv()

os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

template = """Question: {question}
Answer: Let's think step by step."""

prompt = PromptTemplate(template=template, input_variables=["question"])

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    # other params...
)

#llm = ChatOpenAI(
#    api_key=getenv("OPENROUTER_API_KEY"),
#    base_url=getenv("OPENROUTER_BASE_URL"),
#    model="openai/gpt-5",
#)

llm_chain = LLMChain(prompt=prompt, llm=llm)
