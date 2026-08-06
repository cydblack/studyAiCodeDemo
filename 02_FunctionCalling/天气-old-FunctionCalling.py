#!/usr/bin/env python
# coding: utf-8

# 最基础的Function Calling
# 旧版 Function Calling 写法
# 调用天气Function
# 使用模型：百炼中的 qwen-flash

import json
import os

import dashscope

# 从环境变量中，获取 DASHSCOPE_API_KEY
dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY")


# Function
def get_current_weather(location, unit="摄氏度"):
    """
    获取指定地点的天气情况，当问到天气时，调用此函数
    """
    weather_info = {
        "location": location,
        "temperature": 25,
        "unit": unit,
        "forecast": ["晴天", "微风"],
    }
    return json.dumps(weather_info)


weather_func_message = {
    "name": "get_current_weather",
    "description": "获取指定地点的天气情况，当问到天气时，调用此函数",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "城市，如：大连、上海",
            },
            "unit": {
                "type": "string",
                "enum": ["摄氏度", "华氏度"],
            },
        },
        "required": ["location"],
    },
}


# 封装模型响应函数
def get_response(messages):
    try:
        response = dashscope.Generation.call(
            model="qwen-flash",
            messages=messages,
            functions=[weather_func_message],
            result_format="message",
        )
        return response
    except Exception as e:
        print(f"API调用出错: {str(e)}")
        return None


# 使用function call进行QA
def run_conversation(query):
    print("-" * 120)
    print("用户问题", query)
    print("-" * 120)
    messages = [{"role": "user", "content": query}]

    # 得到第一次响应
    response = get_response(messages)
    if not response or not response.output:
        print("获取响应失败")
        return None

    print("-" * 120)
    print("第一次响应：", response)
    print("-" * 120)

    message = response.output.choices[0].message
    messages.append(message)
    print("messages=", messages)

    # Step 2, 判断用户是否要call function
    if hasattr(message, "function_call") and message.function_call:
        print("需要 Function Calling:")
        function_call = message.function_call
        tool_name = function_call["name"]
        # Step 3, 执行function call
        arguments = json.loads(function_call["arguments"])
        print("arguments=", arguments)
        tool_response = get_current_weather(
            location=arguments.get("location"),
            unit=arguments.get("unit"),
        )
        tool_info = {"role": "function", "name": tool_name, "content": tool_response}
        print("tool_info=", tool_info)
        messages.append(tool_info)
        print("messages=", messages)

        # Step 4, 得到第二次响应
        response = get_response(messages)
        if not response or not response.output:
            print("获取第二次响应失败")
            return None

        print("response=", response)
        message = response.output.choices[0].message
        return message
    else:
        print("不需要 Function Calling")
        return message


if __name__ == "__main__":
    # result = run_conversation("西瓜好吃吗")
    result = run_conversation("常州的天气怎样")
    if result:
        print()
        print("最终结果：", result)
    else:
        print("对话执行失败")
