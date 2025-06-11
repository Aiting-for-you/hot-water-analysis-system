import os
from flask import Blueprint, request, jsonify
from openai import OpenAI, AuthenticationError
from ..utils.decorators import login_required
from ..config import Config

ai_assistant_bp = Blueprint('ai_assistant', __name__)

@ai_assistant_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    # if not Config.BAILIAN_API_KEY:
    #     error_msg = "AI assistant API key is not configured. Please set the BAILIAN_API_KEY environment variable."
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON in request body.", "reply": "请求格式错误，请确保发送的是有效的JSON。"}), 400
        
    user_message = data.get('message')
    api_key = data.get('apiKey')

    if not user_message or not api_key:
        error_msg = "Message and API Key are required."
        return jsonify({"error": error_msg, "reply": error_msg}), 400

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    messages = [
        {'role': 'system', 'content': '你是一个乐于助人、知识渊博的智能助手，专门帮助用户分析和理解与热水系统相关的数据。'},
        {'role': 'user', 'content': user_message}
    ]

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            stream=False
        )
        
        response_message = completion.choices[0].message.content
        return jsonify({"reply": response_message})
    except AuthenticationError as e:
        print(f"Bailian API Authentication Error: {e}")
        error_msg = "您提供的API密钥无效或已过期，请检查后重试。"
        return jsonify({"error": error_msg, "reply": error_msg}), 401
    except Exception as e:
        # Catching other potential errors, e.g., network issues, invalid requests to the API
        print(f"Error calling Bailian API: {e}")
        error_msg = "调用AI服务时发生内部错误，请稍后再试。"
        return jsonify({"error": error_msg, "reply": error_msg}), 500 