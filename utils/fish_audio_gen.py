from pydub import AudioSegment
import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import glob
import re
import requests
from config import get_fish_api_key

from spliter import parse_dialogue
from tqdm import tqdm
from utils.logger import logger
from tqdm.contrib.logging import logging_redirect_tqdm

class FishTTSGenerator:
    def __init__(self, api_key: str, output_dir: str):
        self.api_key = api_key
        self.output_dir = output_dir
        self.base_url = "https://api.302.ai/fish-audio/v1"  # 假设这是API端点
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _generate_audio(self, text: str, speaker: str, output_path: str):
        """
        通用的音频生成方法
        """
        payload = {
            "text": text,
            "reference_id": speaker,
            "format": "mp3"
        }

        response = requests.post(
            f"{self.base_url}/tts",
            headers=self.headers,
            json=payload
        )


        if response.status_code == 200:
            response_data = response.json()
            audio_url = response_data.get('url')
            audio_content = requests.get(audio_url).content
            with open(output_path, 'wb') as f:
                f.write(audio_content)
            return output_path
        else:
            raise Exception(f"API调用失败: {response.status_code}, {response.text}")

    def generate_host(self, text: str):
        now = int(datetime.datetime.now().timestamp())
        output_path = f"./{self.output_dir}/host_{now}.mp3"
        return self._generate_audio(text, "d1de7a7c6ecb48328f033264773c18c9", output_path)  # 假设male_01是主持人音色   https://fish.audio/text-to-speech/?modelId=&taskId=1eb187fc74b6497896b0f9291e1852af

    def generate_expert(self, text: str):
        now = int(datetime.datetime.now().timestamp())
        output_path = f"./{self.output_dir}/expert_{now}.mp3"
        return self._generate_audio(text, "c2df2d5b007940c8bded208261bbfc0c", output_path)  # 假设male_02是专家音色  MY 220d51a6a3b045e7abee83decc7b34c0

    def generate_learner(self, text: str):
        now = int(datetime.datetime.now().timestamp())
        output_path = f"./{self.output_dir}/learner_{now}.mp3"
        return self._generate_audio(text, "faccba1a8ac54016bcfc02761285e67f", output_path)  # ��设female_01是学习者音色 9954afe557a5417bb93de7459cbe913e

def merge_mp3_files(directory_path: str, output_file: str):
    """
    合并指定目录下的所有MP3文件
    """
    mp3_files = [os.path.basename(x) for x in glob.glob(f"./{directory_path}/*.mp3")]
    
    sorted_files = sorted(
        mp3_files,
        key=lambda x: re.search(r"(\d{10})", x).group(0)
    )
    
    merged_audio = AudioSegment.empty()
    
    for file in sorted_files:
        audio = AudioSegment.from_mp3(f"./{directory_path}/{file}")
        if file.startswith("expert"):
            audio = increase_expert_volume(audio)   
        merged_audio += audio
    
    merged_audio.export(output_file, format="mp3")
    print(f"已保存合并文件: {output_file}")

def generate_podcast(script: str, api_key: str):
    """
    生成完整的播客音频
    """
    logger.info("开始生成播客音频")
    time_start = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"./outputs/{time_start}"
    os.mkdir(output_path)
    
    tts_generator = FishTTSGenerator(api_key, output_path)
    
    dialogues = parse_dialogue(script)
    with logging_redirect_tqdm():
        for dialogue_dict in tqdm(dialogues, desc="生成对话音频"):
            for role, content in dialogue_dict.items():
                logger.info(f"正在处理角色: {role}")
                if role == "主持人" or role == "host":
                    tts_generator.generate_host(content)
                elif role == "王同学" or role == "学习者":
                    tts_generator.generate_learner(content)
                elif role == "董老师" or role == "expert" or role == "专家":
                    tts_generator.generate_expert(content)
              

    logger.info("音频生成完成")
    generate_audio(output_path, "./outputs")


def generate_audio(directory_path: str, output_path: str):
    logger.info("开始生成音频文件")
    try:
        merge_mp3_files(directory_path, f"{output_path}/{directory_path.split('/')[-1]}_merged.mp3")
        logger.info("音频生成成功")
    except Exception as e:
        logger.error(f"音频生成失败: {str(e)}")

def increase_expert_volume(audio_segment, db_increase=10):
    """
    提高专家音频的音量
    """
    return audio_segment + db_increase

# 修改generate_podcast函数中的代码
def generate_podcast(script: str, api_key: str):
    """
    生成完整的播客音频
    """
    logger.info("开始生成播客音频")
    time_start = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"./outputs/{time_start}"
    os.mkdir(output_path)
    
    tts_generator = FishTTSGenerator(api_key, output_path)
    
    dialogues = parse_dialogue(script)
    print(dialogues)
    with logging_redirect_tqdm():
        for dialogue_dict in tqdm(dialogues, desc="生成对话音频"):
            for role, content in dialogue_dict.items():
                logger.info(f"正在处理角色: {role}")
                if role == "主持人":
                    tts_generator.generate_host(content)
                elif role == "王同学" or role == "学习者":
                    tts_generator.generate_learner(content)
                elif role == "董老师" or role == "专家":
                    expert_audio = tts_generator.generate_expert(content)
                    # expert_audio = increase_expert_volume(expert_audio)
                    # expert_audio.export(f"{output_path}/{role}_{time_start}.mp3", format="mp3")
                else:
                    tts_generator.generate_generic(role, content)

    logger.info("音频生成完成")
    generate_audio(output_path, "./outputs")


if __name__ == "__main__":
    script = r"H:\0-project\paper_to_podcast\temp\20241215_185306_enhanced_script.txt"
    with open(script, "r", encoding="utf-8") as file:
        script_content = file.read()
    generate_podcast(script_content, get_fish_api_key())
    # merge_mp3_files(r"outputs\20241214_115500", "./20241214_115500.mp3")