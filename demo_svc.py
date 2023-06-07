import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict,List, Any,Optional
from logger import console, log
from enum import Enum
from chat_predict import predict
from fastapi import applications
from fastapi.openapi.docs import get_swagger_ui_html

def swagger_monkey_patch(*args, **kwargs):
    """
    Wrap the function which is generating the HTML for the /docs endpoint and
    overwrite the default values for the swagger js and css.
    """
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.org/swagger-ui/4.15.5/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.org/swagger-ui/4.15.5/swagger-ui.min.css")


# Actual monkey patch
applications.get_swagger_ui_html = swagger_monkey_patch


app = FastAPI()




class MsgType(int, Enum):  # 枚举类
    user_msg = 1
    ai_msg = 2

class Msg(BaseModel):
    msgType: MsgType  # 1为用户提问，2为用户回答
    msg: str
    num: int

class Msgs(BaseModel):
    modelType: int
    newFlag: int
    msgs: List[Msg]


@app.post('/nhchat/api/v1/askai')
def get_answer(mesgs:Msgs):
    try:
        msgs = mesgs.msgs
        print(msgs)
        history_msgs = []
        question = None
        if len(msgs) == 0:
            return {'code':200, 'msg': '请输入有用的信息'}

        for msg in msgs[:-1]:
            history_msgs.append(msg.msg)
        if msgs[-1].msgType == 1:
            question = msgs[-1].msg
        log.info(f'历史消息为：{history_msgs}, 最新问题为：{question}')
        if not question:
            return {'code':200, 'msg': '请输入有用的信息'}

        answer = predict(question,history_msgs)

        return {'code':200, 'msg': answer}
    except:
        log.exception('chat服务出错!')
        return {'code':400, 'msg': ''}

if __name__ == "__main__":
    # uvicorn.run(app='main_svc:app', host='0.0.0.0', port=8200, workers=1,  reload=True)
    uvicorn.run(app='demo_svc:app', host='0.0.0.0', port=8500, reload=True)