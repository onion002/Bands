import os
from openai import OpenAI
from dotenv import load_dotenv
import argparse
from typing import Generator, Optional

# 加载环境变量
load_dotenv()

class DeepSeekBandTeacher:
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化DeepSeek乐队音乐老师客户端
        
        :param api_key: DeepSeek API密钥 (可选，优先从环境变量获取)
        """
        # 获取API密钥：环境变量 > 参数传递 > 用户输入
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("API密钥未提供且未在环境变量中找到")
            
        # 使用OpenAI SDK客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        # 系统角色定义 - 全能乐队音乐老师
        self.system_prompt = """
        你是一位全能的乐队音乐老师，拥有以下专业能力：
        1. 精通音乐史，熟悉各个时期、各种流派的音乐发展脉络和代表作品
        2. 精通现代流行音乐，包括但不限于流行、摇滚、民谣、前卫、爵士、蓝调、金属等多种曲风
        3. 了解乐队的组建、发展和运营方式，包括成员协作、排练安排、演出策划、作品推广等
        4. 能够提供乐器演奏技巧指导、和声编排建议、歌曲创作辅导
        5. 熟悉音乐制作流程，包括录音、混音等基本知识
        6. 了解音乐行业现状和发展趋势，能为乐队提供职业发展建议
        
        请以专业、耐心、鼓励的态度回应，根据用户的具体需求提供针对性的指导和建议。
        在回答时请使用音乐专业术语但确保解释清晰，必要时可结合音乐史案例或当代乐队实例说明。
        """

    def get_multiline_input(self, prompt: str) -> str:
        """
        获取用户的多行输入，通过输入空行（仅按Enter）结束
        
        :param prompt: 提示信息
        :return: 用户输入的完整内容
        """
        print(f"\n{prompt} (输入完成后请按两次Enter结束)")
        print("请输入你的音乐问题或乐队运营咨询（使用Shift+Enter换行）：")
        
        lines = []
        empty_line_count = 0
        
        while True:
            line = input().rstrip()  # 保留行首空格，移除行尾空格
            
            # 检测连续两个空行结束输入
            if line == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
                continue
            else:
                empty_line_count = 0
            
            lines.append(line)
        
        return "\n".join(lines)
    def stream_teacher_response(self, user_message: str, 
                               model: str = "deepseek-chat",
                               temperature: float = 0.7, 
                               max_tokens: int = 2000) -> Generator[str, None, None]:
        """
        流式获取乐队音乐老师的回应
        
        :param user_message: 用户的问题或请求
        :param model: 使用的模型名称
        :param temperature: 生成结果的随机性，0-1之间
        :param max_tokens: 最大生成 tokens 数
        :return: 生成器，产生老师的回应片段
        """
        try:
            # 流式调用API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 返回生成器
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"请求失败: {str(e)}"

def main():
    # 优先从环境变量获取API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    # 如果环境变量中没有，尝试命令行参数
    parser = argparse.ArgumentParser(description="DeepSeek乐队音乐老师交互工具")
    parser.add_argument("--api-key", help="你的DeepSeek API密钥")
    args = parser.parse_args()
    
    # 合并密钥来源
    api_key = api_key or args.api_key
    
    try:
        # 初始化乐队音乐老师
        band_teacher = DeepSeekBandTeacher(api_key)
    except ValueError as e:
        print(f"错误: {str(e)}")
        print("请通过以下方式之一提供API密钥：")
        print("1. 设置环境变量 DEEPSEEK_API_KEY")
        print("   PowerShell: $env:DEEPSEEK_API_KEY = '您的_API_密钥'")
        print("   CMD: set DEEPSEEK_API_KEY=您的_API_密钥")
        print("2. 使用命令行参数 --api-key")
        print("   例如: python deepseekapi.py --api-key \"您的_API_密钥\"")
        print("3. 创建 .env 文件，内容为: DEEPSEEK_API_KEY=您的_API_密钥")
        return
        
    print("\n🎵🎸 欢迎使用全能乐队音乐老师助手！")
    print("您可以咨询关于音乐创作、乐队运营、音乐史等内容")
    print("输入 'quit' 退出程序\n")
    
    # 交互循环
    while True:
        # 获取用户输入（支持多行）
        user_input = band_teacher.get_multiline_input("准备输入您的咨询内容")
        
        # 检查退出
        if user_input.lower() == 'quit':
            print("\n🎶 再见！祝你在音乐道路上取得成功！🎶")
            break
            
        # 处理空输入
        if not user_input:
            print("问题不能为空，请重新输入")
            continue
            
        print("\n🤔 音乐老师思考中... (流式回答)\n")
        print("💬 老师回答：", end="", flush=True)
        
        # 流式获取并显示回答
        full_response = ""
        for chunk in band_teacher.stream_teacher_response(user_input):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print("\n" + "="*70)  # 分隔线

if __name__ == "__main__":
    main()