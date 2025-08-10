from flask import Blueprint, request, jsonify, Response
from auth_decorators import optional_auth
import os
from openai import OpenAI
from flask import stream_with_context
import json



music_teacher_bp = Blueprint('music_teacher', __name__)


def _get_client():
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        return None, '服务器未配置 DEEPSEEK_API_KEY'
    try:
        client = OpenAI(api_key=api_key, base_url='https://api.deepseek.com')
        return client, None
    except Exception as e:
        return None, f'客户端初始化失败: {str(e)}'





@music_teacher_bp.route('/chat', methods=['POST'])
@optional_auth
def chat_teacher():
    """调用 DeepSeek 乐队音乐老师，支持 SSE 流式与一次性返回（所有用户可用）"""
    try:
        data = request.get_json(silent=True) or {}
        user_message = (data.get('message') or '').strip()
        model = data.get('model') or 'deepseek-chat'
        temperature = float(data.get('temperature') or 0.7)
        max_tokens = int(data.get('max_tokens') or 1200)
        top_p = float(data.get('top_p') or 0.9)
        is_stream = str(request.args.get('stream') or '').lower() in ['1', 'true', 'yes'] or \
            ('text/event-stream' in (request.headers.get('accept') or ''))

        if not user_message:
            return jsonify({'error': 'message 不能为空'}), 400

        client, err = _get_client()
        if err:
            return jsonify({'error': err}), 500

        # 构建系统提示词
        system_prompt = (
            "你是一位全能的乐队音乐老师，精通音乐史与现代各类曲风，"
            "熟悉乐队组建/排练/演出/推广，擅长器乐技巧、和声编配、作曲建议，"
            "理解基础录音混音流程与行业发展。回答专业但清晰，必要时给出现实案例。"
        )

        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        if not is_stream:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=False
            )
            content = completion.choices[0].message.content if completion and completion.choices else ''
            return jsonify({'answer': content or '', 'model': model})

        # SSE 流
        def generate():
            try:
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    stream=True
                )
                for chunk in stream:
                    try:
                        delta = chunk.choices[0].delta
                        token = getattr(delta, 'content', None)
                        if token:
                            yield f"data: {json.dumps({'token': token})}\n\n"
                    except Exception:
                        continue
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache, no-transform',
            'X-Accel-Buffering': 'no'
        }
        return Response(stream_with_context(generate()), headers=headers)
    except Exception as e:
        return jsonify({'error': f'调用失败: {str(e)}'}), 500


