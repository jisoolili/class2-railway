import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from typing import Optional

# 创建 FastAPI 应用
app = FastAPI(title="智能客服机器人")

# 添加 CORS 中间件（允许跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 尝试挂载静态文件目录（如果存在）
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# 定义请求模型
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None


# 系统提示词
SYSTEM_PROMPT = """你是智能客服助手，回答要准确、友好、简洁。
你可以帮助用户解答关于产品、服务、技术等问题。
如果遇到不确定的问题，请诚实告知用户。"""


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """返回主页"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>智能客服机器人</h1><p>请确保 static/index.html 文件存在</p>")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理对话请求"""
    try:
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="消息不能为空")

        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9
        )

        answer = completion.choices[0].message.content

        return ChatResponse(
            response=answer,
            success=True
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return ChatResponse(
            response="",
            success=False,
            error=f"处理请求时出错: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


# Railway 会通过 PORT 环境变量指定端口
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)