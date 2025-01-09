import json
import traceback

from model_configurations import get_model_configuration
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

gpt_chat_version = 'gpt-4o'
gpt_config = get_model_configuration(gpt_chat_version)

def generate_hw01(question):
    try:
        llm = AzureChatOpenAI(
                model=gpt_config['model_name'],
                deployment_name=gpt_config['deployment_name'],
                openai_api_key=gpt_config['api_key'],
                openai_api_version=gpt_config['api_version'],
                azure_endpoint=gpt_config['api_base'],
                temperature=gpt_config['temperature']
        )
        # 定义模板字符串
        template = f"""
        你是一个节假日查询助手,请按照json的格式回答: {question}
        json内数据包括：Result:[date,name]
        """

        message_content = template.format(question=question)

        message = HumanMessage(
            content=[
                {"type": "text", "text": message_content},
            ]
        )

        response = llm.invoke([message])

        return response

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()

def generate_hw02(question):
    pass

def generate_hw03(question2, question3):
    pass

def generate_hw04(question):
    pass

def demo(question):
        llm = AzureChatOpenAI(
                model=gpt_config['model_name'],
                deployment_name=gpt_config['deployment_name'],
                openai_api_key=gpt_config['api_key'],
                openai_api_version=gpt_config['api_version'],
                azure_endpoint=gpt_config['api_base'],
                temperature=gpt_config['temperature']
        )
        message = HumanMessage(
                content=[
                    {"type": "text", "text": question},
                ]
        )
        response = llm.invoke([message])

        return response


if __name__ == "__main__":
    result = generate_hw01("2024年台灣10月紀念日有哪些?")
    print(result.content)
