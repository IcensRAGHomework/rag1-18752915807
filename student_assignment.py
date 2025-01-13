import base64
import json
import re
import traceback
from mimetypes import guess_type

import requests as standard_requests
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import AzureChatOpenAI

from model_configurations import get_model_configuration

gpt_chat_version = 'gpt-4o'
gpt_config = get_model_configuration(gpt_chat_version)
calendarific_api_key="s2CdTTbwrTw52sv45dywDsGuCVG8cSK2"

llm = AzureChatOpenAI(
    model=gpt_config['model_name'],
    deployment_name=gpt_config['deployment_name'],
    openai_api_key=gpt_config['api_key'],
    openai_api_version=gpt_config['api_version'],
    azure_endpoint=gpt_config['api_base'],
    temperature=gpt_config['temperature']
)
store = {}


def clean_response_content(response):
    content = response.content.strip()
    if content.startswith("```") and content.endswith("```"):
        content = content[3:-3].strip()
    if content.startswith("json"):
        content = content[4:].strip()
    return content

def extract_year_and_month(question):
    try:
        template = f"""
        请从以下问题中提取年份和月份，并以json的格式返回year和month
        问题：{question}
        """

        message = HumanMessage(content=template)
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

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def local_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    return f"data:{mime_type};base64,{base64_encoded_data}"

def generate_hw01(question):
    try:
        template = f"""
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

        message = HumanMessage(content=template)

        response = llm.invoke([message])
        if response:
            return clean_response_content(response)
        else:
            return None

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()

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
        output = []
        for holiday in holidays:
            output.append({
                "date": holiday.get('date', {}).get('iso'),
                "name": holiday.get('name')
            })

        output = {
            "Result": output
        }
        return json.dumps(output, ensure_ascii=False)

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return None

def generate_hw03(question2, question3):
    try:
        answer2 = generate_hw02(question2)
        if not answer2:
            raise ValueError("Failed to get answer from generate_hw02")

        with_message_history = RunnableWithMessageHistory(
            llm,
            get_session_history
        )

        # 配置输入和历史消息
        template = f"""
        你是一个纪念日查询助手,请按照json的格式回答: {question3}
        json格式为:
        {{
           "Result": {{
                "add": true or false,
                "reason": "reason"
            }}
        }}
        add : 這是一個布林值，表示是否需要將節日新增到節日清單中。根據問題判斷該節日是否存在於清單中，如果不存在，則為 true；否則為 false。
        reason : 描述為什麼需要或不需要新增節日，具體說明是否該節日已經存在於清單中，以及當前清單的內容。
        """
        input_messages = [
            HumanMessage(content=question2),
            HumanMessage(content=answer2),
            HumanMessage(content=template)
        ]
        response = with_message_history.invoke(input_messages, config={"configurable": {"session_id": "1"}})

        if response:
            return clean_response_content(response)
        else:
            return None

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return None

def generate_hw04(question):
    try:
        data_url = local_image_to_data_url('baseball.png')

        content = [
            {"role": "user", "content":
                [
                    {"type": "text", "text": f'''你需要根据图片内容回答问题{question}，并将结果按照json格式输出：
                     json格式如下：
                     {{
                        "Result": 
                            {{
                                "value":value
                            }}
                    }}
                    其中value可以是score,team,Alliance,rank,根据问题不同使用不同的value
                    '''
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ]
             }
        ]
        response = llm.invoke(content)
        if response:
            return clean_response_content(response)
        else:
            return None

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return None

# if __name__ == "__main__":
#     result = generate_hw01("What are the October anniversaries in Taiwan in 2024?")
#     print(result)
#
#     result = generate_hw02("2024年台灣地区10月紀念日有哪些?")
#     print(result)
#
#     result = generate_hw03("2024年台灣地区10月紀念日有哪些?",
#                            '根據先前的節日清單，這個節日{"date": "10-31", "name": "蔣公誕辰紀念日"}是否有在該月份清單？')
#     print(result)
#
#     result = generate_hw04("請問第1名是哪个队伍?")
#     print(result)