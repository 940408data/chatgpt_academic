#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   chat_predict.py
@Time    :   2023/06/07 19:34:16
@Author  :   huangxu3 
@Version :   1.0
@Contact :   huangxu3@newhope.cn
@License :   (C)Copyright 2021-2022, newhope.cn
@Desc    :   None
'''

# here put the import lib



import json
import gradio as gr
import logging
import traceback
import requests
import importlib

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from toolbox import get_conf
proxies, API_URL, API_KEY, TIMEOUT_SECONDS, MAX_RETRY, LLM_MODEL = \
    get_conf('proxies', 'API_URL', 'API_KEY', 'TIMEOUT_SECONDS', 'MAX_RETRY', 'LLM_MODEL')

timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                  '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'

def get_full_error(chunk, stream_response):
    """
        获取完整的从Openai返回的报错
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk

def predict(inputs, history=[],top_p=1, temperature = 0.6, sys_prompt=""):
    """
        发送至chatGPT，等待回复，一次性完成，不显示中间过程。
        predict函数的简化版。
        用于payload比较大的情况，或者用于实现多线、带嵌套的复杂功能。

        inputs 是本次问询的输入
        top_p, temperature是chatGPT的内部调优参数
        history 是之前的对话列表
        （注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误，然后raise ConnectionAbortedError）
    """
    headers, payload = generate_payload(inputs, top_p, temperature, history, system_prompt=sys_prompt, stream=False)

    retry = 0
    while True:
        try:
            # make a POST request to the API endpoint, stream=False
            response = requests.post(API_URL, headers=headers, proxies=proxies,
                                    json=payload, stream=False, timeout=TIMEOUT_SECONDS*2); break
        except requests.exceptions.ReadTimeout as e:
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY: raise TimeoutError
            if MAX_RETRY!=0: print(f'请求超时，正在重试 ({retry}/{MAX_RETRY}) ……')

    try:
        result = json.loads(response.text)["choices"][0]["message"]["content"]
        return result
    except Exception as e:
        if "choices" not in response.text: print(response.text)
        raise ConnectionAbortedError("Json解析不合常规，可能是文本过长" + response.text)




def generate_payload(inputs, top_p, temperature, history, system_prompt, stream):
    """
        整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    conversation_cnt = len(history) // 2

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_cnt:
        for index in range(0, 2*conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index+1]
            if what_i_have_asked["content"] != "":
                if what_gpt_answer["content"] == "": continue
                if what_gpt_answer["content"] == timeout_bot_msg: continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]['content'] = what_gpt_answer['content']

    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = inputs
    messages.append(what_i_ask_now)
    print(messages)
    payload = {
        "model": LLM_MODEL,
        "messages": messages, 
        "temperature": temperature,  # 1.0,
        "top_p": top_p,  # 1.0,
        "n": 1,
        "stream": stream,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }
    
    print(f" {LLM_MODEL} : {conversation_cnt} : {inputs}")
    return headers,payload


