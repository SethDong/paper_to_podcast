import os
from fish_audio_gen import FishTTSGenerator

def test_fish_tts_generator():
    api_key = "sk-EBENxiHupW2p4GIyrzyGor8cdPzZWbmwcayy4zdLl3FPWoEM"  # 替换为你的API密钥
    output_dir = "test_output"
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    tts_generator = FishTTSGenerator(api_key, output_dir)
    
    # 测试生成主持人音频
    host_output = tts_generator.generate_host("欢迎来到我们的播客节目。")
    print(f"主持人音频生成成功: {host_output}")
    
    # 测试生成专家音频
    expert_output = tts_generator.generate_expert("我是专家，我非常喜欢这个话题。")
    print(f"专家音频生成成功: {expert_output}")
    
    # 测试生成学习者音频
    learner_output = tts_generator.generate_learner("我是学习者，我对这个话题很感兴趣。")
    print(f"学习者音频生成成功: {learner_output}")

# 运行测试
test_fish_tts_generator()