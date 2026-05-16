from flask import Flask, request, jsonify, render_template, send_file
from flask_httpauth import HTTPBasicAuth
import os
import shutil
import json
import zipfile
from datetime import datetime
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

feishu_app_id = os.getenv('FEISHU_APP_ID')
feishu_app_secret = os.getenv('FEISHU_APP_SECRET')
feishu_spaces = json.loads(os.getenv('FEISHU_SPACES'))
vitepress_docs_path = os.getenv('VITEPRESS_DOCS_PATH')
host = os.getenv('HOST')
flask_port = os.getenv('FLASK_PORT')
preview_port = os.getenv('PREVIEW_PORT')

app = Flask(__name__)
auth = HTTPBasicAuth()

users = json.loads(os.getenv('DOWNLOAD_AUTH'))

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None


def modify_docs_json(obj, feishu_space_name):
    if isinstance(obj, dict):
        # 若有 depth 字段，就加 1
        if 'depth' in obj:
            obj['depth'] += 1
        # 处理 slug 字段
        if 'slug' in obj:
            obj['slug'] = f'{feishu_space_name}/{obj['slug']}'
        # 递归处理所有子项
        for key, value in obj.items():
            modify_docs_json(value, feishu_space_name)
    elif isinstance(obj, list):
        # 如果是列表，递归处理每个元素
        for item in obj:
            modify_docs_json(item, feishu_space_name)
    # 其他类型（str, int, bool 等）无需处理


def download_and_parse():
    logging.info("Start downloading feishu spaces...")
    # Feishu Pages envs
    os.environ['FEISHU_APP_ID'] = feishu_app_id
    os.environ['FEISHU_APP_SECRET'] = feishu_app_secret
    # os.environ['ASSET_BASE_URL'] = "/public" # Seems not implemented in Feishu Pages project

    os.makedirs("Downloads", exist_ok=True)
    shutil.rmtree(f'dist/', ignore_errors=True)
    os.makedirs("dist/assets/", exist_ok=True)
    for i, (feishu_space_name, feishu_space_id) in enumerate(feishu_spaces.items()):
        logging.debug(f"Downloading Feishu space: {feishu_space_name}, id: {feishu_space_id}")
        os.environ['OUTPUT_DIR'] = f'Downloads/{feishu_space_name}'
        os.environ['FEISHU_SPACE_ID'] = feishu_space_id

        # Download feishu space using Feishu Pages
        os.system("yarn feishu-pages")
        logging.info("Download finished, start parsing...")

        # Create space_name.md file
        markdown_content = f"""
        # {feishu_space_name}

        ID: {feishu_space_id}
        """
        with open(f'dist/{feishu_space_name}.md', "w") as file:
            file.write(markdown_content)

        # Move to dist/
        shutil.move(f'Downloads/{feishu_space_name}/docs/', f'dist/{feishu_space_name}/')
        for filename in os.listdir(f'dist/{feishu_space_name}/assets/'):
            shutil.copy(f'dist/{feishu_space_name}/assets/{filename}', 'dist/assets/')

        # Modify docs.json
        docs_json_path = f'Downloads/{feishu_space_name}/docs.json'
        with open(docs_json_path) as f:
            docs = json.load(f)

        modify_docs_json(docs, feishu_space_name)
        outter = [
            {
                "depth": 0,
                "title": feishu_space_name,
                "children": docs,
                "has_child": True,
                "slug": feishu_space_name,
                "position": i,
                "filename": f"{feishu_space_name}.md"
            }
        ]

        with open(docs_json_path, 'w') as file:
            json.dump(outter, file, indent = 2, ensure_ascii=False)

        if os.path.exists('dist/docs.json'):
            # Merge docs.json
            with open('dist/docs.json') as f:
                existed_docs_json = json.load(f)
            with open(docs_json_path) as f:
                new_docs_json = json.load(f)
            existed_docs_json.append(new_docs_json[0])
            with open('dist/docs.json', 'w') as file:
                json.dump(existed_docs_json, file, indent = 2, ensure_ascii=False)
        else:
            shutil.copy(f'Downloads/{feishu_space_name}/docs.json', 'dist/docs.json')

        logging.info("Parse finished.")


sync_time = 0


def apply_to_vitepress():
    logging.info("Applying to VitePress project...")
    shutil.rmtree(vitepress_docs_path)
    shutil.copytree('dist/', vitepress_docs_path)
    os.makedirs(f'{vitepress_docs_path}/.vitepress/', exist_ok=True)

    # Move non-png files to public/assets/
    os.makedirs(f'{vitepress_docs_path}/public/assets/', exist_ok=True)
    for filename in os.listdir(f'{vitepress_docs_path}/assets/'):
        if not filename.lower().endswith('.png'):
            shutil.move(f'{vitepress_docs_path}/assets/{filename}', f'{vitepress_docs_path}/public/assets/{filename}')  # 移动文件

    shutil.copy('Sample/config.mts', f'{vitepress_docs_path}/.vitepress/config.mts')
    shutil.copy('Sample/index.md', f'{vitepress_docs_path}/index.md')
    # 打开文件并追加内容
    with open(f'{vitepress_docs_path}/index.md', "a", encoding="utf-8") as index_md_file:
        index_md_file.write(f"\n同步时间：{sync_time}\n")

    logging.info("Building VitePress static pages...")
    orig_cwd = os.getcwd()
    os.chdir(f'{vitepress_docs_path}/../')
    os.system("npm run docs:build")
    os.chdir(orig_cwd)


def compress_archive():
    logging.info("Compressing archive...")
    os.makedirs("Archives/", exist_ok=True)
    zip_path = f"Archives/RO-Static-Wiki_{sync_time.strftime('%Y%m%d%H%M%S')}.zip"
    folder_path = f"{vitepress_docs_path}/.vitepress/dist/"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_object:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # 1. 获取文件的绝对路径 (用于读取文件)
                file_path = os.path.join(root, file)

                # 2. 计算相对路径 (用于在压缩包中存储)
                # 这会将 "path/to/dist/subdir/file.txt" 转换为 "subdir/file.txt"
                arcname = os.path.relpath(file_path, start=folder_path)

                # 3. 写入文件，并指定压缩包内的名字
                zip_object.write(file_path, arcname=arcname)


is_working = False


@app.route("/")
def handle_index():
    preview_url = f"http://{host}:{preview_port}/"
    download_url = f"http://{request.host}/download"
    return render_template("index.html", preview_url=preview_url, download_url=download_url)


@app.route("/build", methods=["POST"])
def handle_build():
    global is_working, sync_time
    if not is_working:
        is_working = True

        sync_time = datetime.now()
        download_and_parse()
        apply_to_vitepress()
        compress_archive()
        
        is_working = False
        return jsonify({
            "success": True,
            "message": "已同步并构建完毕。"
        })
    else:
        return jsonify({
            "success": False,
            "message": "有未完成的任务，请稍后再试。"
        })


@app.route('/download')
@auth.login_required
def handle_download():
    files = [f for f in os.listdir('Archives') if os.path.isfile(os.path.join('Archives', f))]
    if files:
        # 按文件名排序，取最后一个
        latest_filename = sorted(files)[-1]
        logging.info(f"Sending latest file: {latest_filename}")
        return send_file(f"Archives/{latest_filename}", as_attachment=True)
    return None


if __name__ == "__main__":
    logging.info("RO-Static-Wiki Launched.")
    # app.run(host="0.0.0.0", port=5001, debug=True)
    app.run(host="0.0.0.0", port=flask_port)

