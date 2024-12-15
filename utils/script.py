from datetime import datetime
import re
from PyPDF2 import PdfReader
from utils.prompts import (
    get_plan_prompt,
    get_initial_dialogue_prompt,
    get_discussion_prompt,
    get_enhance_prompt
)
from tqdm import tqdm
import os

def parse_pdf(pdf_path: str) -> str:
    """解析PDF文件内容"""
    pdf_reader = PdfReader(pdf_path)
    extracted_text = []
    collecting = True

    for page in tqdm(pdf_reader.pages):
        text = page.extract_text()
        if text and collecting:
            extracted_text.append(text)
            if "Conclusion" in text:
                conclusion_start = text.index("Conclusion")
                extracted_text.append(text[conclusion_start:])
                collecting = False

    return "\n".join(extracted_text)

def get_head(pdf_path: str) -> str:
    """获取PDF文件的头部内容"""
    pdf_reader = PdfReader(pdf_path)
    extracted_text = []
    collecting = True

    for page in tqdm(pdf_reader.pages):
        text = page.extract_text()
        if text and collecting:
            if "Introduction" in text:
                introduction_index = text.index("Introduction")
                extracted_text.append(text[:introduction_index])
                break
            else:
                extracted_text.append(text)

    return "\n".join(extracted_text)

def parse_script_plan(content: str) -> list:
    """解析脚本计划"""
    sections = []
    current_section = []
    lines = content.strip().splitlines()
    lines = lines[1:]

    # header_pattern = re.compile(r"^\d+\.\s+\*\*.+\*\*")
    # bullet_pattern = re.compile(r"^   - ")

    header_pattern = re.compile(r"^#+\s")  # Match headers with any number of #
    bullet_pattern = re.compile(r"^- ")  # Match lines starting with a bullet point "- "

    for line in tqdm(lines):
        if header_pattern.match(line):
            if current_section:
                sections.append(" ".join(current_section))
                current_section = []
            current_section.append(line.strip())
        elif bullet_pattern.match(line):
            current_section.append(line.strip())

    if current_section:
        sections.append(" ".join(current_section))

    return sections

def generate_script(pdf_path: str, llm) -> str:
    """生成播客脚本"""
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S") 
    
    # 解析PDF内容
    paper_content = parse_pdf(pdf_path)
    
    # 生成脚本计划
    plan_prompt = get_plan_prompt(paper_content)
    plan_response = llm.generate(plan_prompt)
    plan = parse_script_plan(plan_response)
    print("计划已生成")
    with open(f"./temp/{start_time}_plan.txt", "w", encoding="utf-8") as f:
        f.write(plan_response)
    # 生成初始对话
    initial_dialogue_prompt = get_initial_dialogue_prompt(get_head(pdf_path))
    script = llm.generate(initial_dialogue_prompt)
    
    # 生成每个部分的对话
    print("plan:", plan)
    for section in tqdm(plan):
        discussion_prompt = get_discussion_prompt(section, script)
        section_script = llm.generate(discussion_prompt)
        print("section_script:"+section_script)
        script += section_script

    with open(f"./temp/{start_time}_script.txt", "w", encoding="utf-8") as f:
        f.write(script)
    # 优化脚本
    enhance_prompt = get_enhance_prompt(script)
    enhanced_script = llm.generate(enhance_prompt)
    # end_time = datetime.now()
    # print(f"耗时: {end_time - start_time}")
    if not os.path.exists("./temp"):
        os.makedirs("./temp")
    with open(f"./temp/{start_time}_enhanced_script.txt", "w", encoding="utf-8") as f:
        f.write(enhanced_script)
    print("最终脚本已生成")
    
    return enhanced_script

# if __name__ == "__main__":
#     with open("./temp/20241215_181016_plan.txt", "r", encoding="utf-8") as f:
#         plan_response = f.read()
#     plan = parse_script_plan(plan_response)
#     print(plan)
