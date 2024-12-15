import re

def parse_dialogue(text):
    # 定义正则表达式模式，匹配角色和内容
    pattern = r'\*\*(.*?)\*\*：(.*?)(?=\n\n\*\*|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)

    # 创建字典存储角色和对应的内容

    list_dialogue = []

    for role, content in matches:
        dialogue_dict = {}
        # 去除多余的换行符和空格
        content = content.strip()
        dialogue_dict[role] = content
        list_dialogue.append(dialogue_dict)
    return list_dialogue

# # 示例文本
# text = """
# **主持人**：大家好，欢迎来到我们的节目。
# \n\n**学习者**：当然可以！这篇论文的核心理念在于通过一种简单而有效的机制——注意力机制，完全取代传统的递归神经网络和卷积神经网络。
# \n\n**专家**：确实如此。实验结果显示，注意力机制在许多任务中表现优异。
# \n\n**主持人**：那么，我们接下来讨论一下具体的实现细节。
# \n\n**学习者**：好的，我认为实现的关键在于...
# """

# script = r"H:\0-project\paper_to_podcast\temp\20241215_164026.txt"
# with open(script, "r", encoding="gbk") as file:
#     script_content = file.read()
# # # 解析文本
# ls = parse_dialogue(script_content)

# # 打印结果
# for item in ls:
#     for role, content in item.items():
#         print(role, content)
