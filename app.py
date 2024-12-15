from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import logging
from paper_to_podcast import process_paper
from utils.logger import logger
import threading
from queue import Queue
from collections import deque
import time
import json

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# 确保输出目录存在
output_dir = "./outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
# 存储任务状态
task_status = {}
progress_queue = Queue()

# 日志缓冲区
log_buffer = deque(maxlen=100)  # 保存最近100条日志

# 修改日志处理器的实现
class WebLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        log_entry = {
            'timestamp': self.formatter.formatTime(record),
            'logger': record.name,
            'level': record.levelname,
            'message': record.getMessage()
        }
        log_buffer.append(log_entry)

# 在app初始化后添加
web_handler = WebLogHandler()
logger.addHandler(web_handler)

# 确保根logger也能捕获所有日志
root_logger = logging.getLogger()
root_logger.addHandler(web_handler)
root_logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': '只支持PDF文件'}), 400

    # 保存文件
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)
    
    # 生成任务ID
    task_id = str(hash(filename))
    task_status[task_id] = {
        'status': 'processing',
        'progress': 0,
        'message': '开始处理...'
    }
    
    # 启动处理线程
    def progress_callback(progress, message):
        task_status[task_id]['progress'] = progress
        task_status[task_id]['message'] = message
    
    thread = threading.Thread(
        target=process_paper,
        args=(filename, progress_callback)
    )
    thread.start()
    
    return jsonify({'task_id': task_id})


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    return send_file(file_path, as_attachment=True)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9630, debug=True) 