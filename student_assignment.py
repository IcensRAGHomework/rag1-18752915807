import json
import re

import requests as standard_requests
import traceback

from langchain import requests as langchain_requests
from langchain_core.utils import print_text

from model_configurations import get_model_configuration
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

gpt_chat_version = 'gpt-4o'
gpt_config = get_model_configuration(gpt_chat_version)
calendarific_api_key="s2CdTTbwrTw52sv45dywDsGuCVG8cSK2"

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

        template = """
        你是一个纪念日查询助手,请按照json的格式回答: {question}
        json格式为:
        {{
           "Result": [
                {{
                    "date": "YYYY-MM-dd",
                    "name": "name1"
                }},
                {{
                    "date": "YYYY-MM-dd",
                    "name": "name2"
                }},
                ...
            ]
        }}
        请确保根据问题提供相关的所有纪念日信息,并根据输入语言返回相同的语言。
        """

        message_content = template.format(question=question)

        message = HumanMessage(content=message_content)

        response = llm.invoke([message])
        if response:
            content = response.content.strip()
            if content.startswith("```") and content.endswith("```"):
                content = content[3:-3].strip()
            if content.startswith("json"):
                content = content[4:].strip()
            return content
        else:
            return None

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()

def extract_year_and_month(question):
    try:
        llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
        )
        template = f"""
        请从以下问题中提取年份和月份，并以json的格式返回year和month
        问题：{question}
        """

        message_content = template

        message = HumanMessage(content=message_content)
        response = llm.invoke([message])


        if response:
            content = response.content.strip()

            year_match = re.search(r'"year":\s*(\d+)', content, re.IGNORECASE)
            month_match = re.search(r'"month":\s*(\d+)', content, re.IGNORECASE)
            if year_match and month_match:
                year = year_match.group(1)
                month = month_match.group(1)
                return year, month
            else:
                return None, None
        else:
            return None, None

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return None, None

def generate_hw02(question):
    try:
        year, month = extract_year_and_month(question)
        if not year or not month:
            raise ValueError("Failed to extract year and month from the question")

        url = f"https://calendarific.com/api/v2/holidays?api_key={calendarific_api_key}&country=TW&year={year}&month={month}"
        response = standard_requests.get(url)
        if response.status_code != 200:
            raise ValueError("Failed to fetch data from Calendarific API")

        data = response.json()

        holidays = data.get('response', {}).get('holidays', [])
        result = []
        for holiday in holidays:
            result.append({
                "date": holiday.get('date', {}).get('iso'),
                "name": holiday.get('name')
            })

        output = {
            "Result": result
        }
        return json.dumps(output, ensure_ascii=False)

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return None

def generate_hw03(question2, question3):
    try:
        # 获取作业2的回答
        answer2 = generate_hw02(question2)
        if not answer2:
            raise ValueError("Failed to get answer from generate_hw02")

        holidays = json.loads(answer2)["Result"]

        match = re.search(r'\{"date":\s*"(\d{2}-\d{2})",\s*"name":\s*"([^"]+)"\}', question3)
        if not match:
            raise ValueError("Failed to parse holiday from question3")

        date_to_check, name_to_check = match.groups()

        # 检查节日是否存在
        exists = any(h["date"][5:] == date_to_check and h["name"] == name_to_check for h in holidays)

        response = {
            "add": not exists,
            "reason": f"The holiday {name_to_check} on {date_to_check} is {'already' if exists else 'not'} in the list. Current list: {holidays}"
        }

        return json.dumps(response, ensure_ascii=False)

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return None

def generate_hw04(question):
    pass

def demo(question):
    try:
        llm = AzureChatOpenAI(
                model=gpt_config['model_name'],
                deployment_name=gpt_config['deployment_name'],
                openai_api_key=gpt_config['api_key'],
                openai_api_version=gpt_config['api_version'],
                azure_endpoint=gpt_config['api_base'],
                temperature=gpt_config['temperature']
        )
        message = HumanMessage(
                content=question
        )
        response = llm.invoke([message])

        return response

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()

if __name__ == "__main__":
    # # 测试 generate_hw01
    # result = generate_hw01("What are the October anniversarities in Taiwan in 2024?")
    # print(result)
    #
    # # 测试 generate_hw02
    # result = generate_hw02("2024年台灣地区10月紀念日有哪些?")
    # print(result)

    result = generate_hw03("2024年台灣地区10月紀念日有哪些?", '根據先前的節日清單，這個節日{"date": "10-31", "name": "蔣公誕辰紀念日"}是否有在該月份清單？')
    print(result)