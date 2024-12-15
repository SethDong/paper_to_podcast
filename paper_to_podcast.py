import os
from utils.script import generate_script
from utils.fish_audio_gen import generate_podcast
from utils.custom_chat import CustomChatModel
import config
from utils.logger import logger

def process_paper(pdf_path, progress_callback=None):
    """
    处理PDF文件并生成播客
    progress_callback: 回调函数，用于更新进度
    """
    try:
        logger.info(f"开始处理文件: {os.path.basename(pdf_path)}")
        
        if progress_callback:
            progress_callback(0, "正在初始化...")
        
        # 从配置文件获取API密钥
        api_key = config.get_api_key()
        if not api_key:
            logger.error("未找到API密钥")
            raise ValueError("未找到API密钥")
        
        # 初始化模型
        if progress_callback:
            progress_callback(10, "正在初始化LLM模型...")
        logger.info("初始化LLM模型")
        
        # 初始化聊天模型
        llm = CustomChatModel(api_key=api_key, model="gpt-4o-mini")
        
        logger.info("开始生成脚本")
        script = generate_script(pdf_path, llm)
        
        # 生成音频
        logger.info("开始生成音频")
        generate_podcast(script, api_key)
        
        if progress_callback:
            progress_callback(100, "处理完成！")
        logger.info("任务完成")
        
        return True
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        if progress_callback:
            progress_callback(0, f"处理失败: {str(e)}")
        raise

def main():
    try:
        logger.info("开始处理文档")
        import argparse
        parser = argparse.ArgumentParser(description="从研究论文生成播客。")
        parser.add_argument("pdf_path", type=str, help="研究论文PDF文件的路径。")
        args = parser.parse_args()
        process_paper(args.pdf_path)
        
        logger.info("开始生成音频")
        # 音频生成代码...
        
        logger.info("处理完成")
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)

if __name__ == "__main__":
    logger.info("开始运行 Paper to Podcast 转换程序")
    main()
