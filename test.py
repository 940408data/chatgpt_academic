#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test.py
@Time    :   2023/06/07 15:23:28
@Author  :   huangxu3 
@Version :   1.0
@Contact :   huangxu3@newhope.cn
@License :   (C)Copyright 2021-2022, newhope.cn
@Desc    :   None
'''
# import gradio as gr
from chat_predict import predict

inputs = "请详细介绍上一个问题"
top_p = 1
temperature = 0.6
history = ["机器学习的主要思想","什么是二分查找","什么是冒泡排序"]

res = predict(inputs,history)
print(res)



