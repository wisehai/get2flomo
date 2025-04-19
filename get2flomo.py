import requests  
from bs4 import BeautifulSoup  
from pathlib import Path  
import time  

def extract_and_send_to_flomo(html_file_path, flomo_webhook):  
    # 读取HTML文件  
    with open(html_file_path, 'r', encoding='utf-8') as f:  
        html_content = f.read()  
    
    # 解析HTML  
    soup = BeautifulSoup(html_content, 'html.parser')  
    
    # 提取笔记内容  
    note_div = soup.select_one('.note')  
    if not note_div:  
        print(f"  ❌ 未找到笔记内容: {html_file_path}")  
        return False  
    
    # 获取创建时间  
    created_time = note_div.find('p', string=lambda t: t and t.startswith('创建于')).text.strip()  
    
    # 获取标签 (如果有)  
    tags_p = note_div.find('p', string=lambda t: t and t.startswith('标签'))  
    tags = tags_p.text.replace('标签：', '').strip() if tags_p else ""  
    
    # 获取正文内容  
    content_p = note_div.find_all('p')[-1]  
    note_content = content_p.text.strip()  
    
    # 组合完整内容  
    full_content = f"{note_content}\n\n{created_time}"  
    if tags:  
        full_content += f"\n{tags}"  
    
    # 发送到flomo  
    payload = {"content": full_content}  
    response = requests.post(flomo_webhook, json=payload)  
    if response.status_code == 200:  
        print(f"  ✅ 发送成功: {html_file_path.name}")  
        return True  
    else:  
        print(f"  ❌ 发送失败({response.status_code}): {html_file_path.name}")  
        print(f"  错误信息: {response.text}")  
        return False  

def process_folder(folder_path, flomo_webhook, delay=1):  
    """处理文件夹中的所有HTML文件"""  
    folder = Path(folder_path)  
    
    # 获取所有html文件  
    html_files = list(folder.glob("*.html"))  
    total = len(html_files)  
    
    if total == 0:  
        print(f"⚠️ 文件夹 '{folder}' 中未找到HTML文件")  
        return  
    
    print(f"📂 找到 {total} 个HTML文件，开始处理...")  
    
    successful = 0  
    failed = 0  
    
    for i, html_file in enumerate(html_files, 1):  
        print(f"[{i}/{total}] 处理: {html_file.name}")  
        try:  
            if extract_and_send_to_flomo(html_file, flomo_webhook):  
                successful += 1  
            else:  
                failed += 1  
                
            # 添加延迟避免API限制  
            if i < total and delay > 0:  # 不是最后一个文件  
                print(f"  ⏱️ 等待 {delay} 秒...")  
                time.sleep(delay)  
        except Exception as e:  
            failed += 1  
            print(f"  ❌ 处理错误: {str(e)}")  
    
    print(f"\n📊 处理完成! ✅ 成功: {successful}, ❌ 失败: {failed}")  

# 使用示例  
if __name__ == "__main__":  
    folder_path = "your_folder_path"  # 替换为你的HTML文件夹路径  
    flomo_webhook = "your_flomo_api"  # 替换为你的api地址  
    
    # 处理整个文件夹，每次发送后等待0.1秒  
    process_folder(folder_path, flomo_webhook, delay=0.1)
