# RO-Static-Wiki
将飞书知识库导出成静态网页，供断网环境查阅

## 部署

部署前请确保您已有 Python 和 Node.js 环境。这里是在 Ubuntu 26.04 上操作的。

1. 新建一个工作目录，安装 [VitePress](https://vitepress.dev/zh/)：`npm add -D vitepress@next`
2. 执行 `npx vitepress init`：
```
┌  Welcome to VitePress!
│
◇  Where should VitePress initialize the config?
│  ./docs
│
◇  Where should VitePress look for your markdown files?
│  ./docs
│
◇  Site title:
│  My Awesome Project
│
◇  Site description:
│  A VitePress Site
│
◇  Theme:
│  Default Theme
│
◇  Use TypeScript for config and theme files?
│  Yes
│
◇  Add VitePress npm scripts to package.json?
│  Yes
│
◇  Add a prefix for VitePress npm scripts?
│  Yes
│
◇  Prefix for VitePress npm scripts:
│  docs
│
└  Done! Now run npm run docs:dev and start writing.
```

记住一开始回答的这个 docs 目录

3. 安装搜索插件：`npm i vitepress-plugin-pagefind pagefind`
4. 下载本 GitHub 仓库，并切换到仓库目录
5. 安装 yarn：`npm install -g yarn`
6. 安装 feishu-pages：`yarn add feishu-pages`
7. 安装 pip 和 venv：`sudo apt install python3-pip python3.14-venv`
8. 新建虚拟环境：`python3 -m venv .`
9. 激活虚拟环境：`source ./bin/activate`
10. 安装 Python 依赖：`pip3 install -r requirements.txt`
11. 配置 `.env`，示例：
```env
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_SPACES='{
    "Pentest": "0000000000000000000",
    "Web": "1111111111111111111",
    "Pwn": "2222222222222222222"
}'
VITEPRESS_DOCS_PATH=/home/ro/ro-static-wiki-vitepress/docs
HOST=0.0.0.0
FLASK_PORT=5000
PREVIEW_PORT=4000
DOWNLOAD_AUTH='{
    "ro": "rororo114514"
}'
```
13. 启动 flask 服务：`python3 main.py`
14. 用 [miniserve](https://github.com/svenstaro/miniserve) 启动预览服务：`./miniserve-0.35.0-x86_64-unknown-linux-gnu /home/ro/ro-static-wiki-vitepress/docs/.vitepress/dist/ -p 4000 --index index.html --auth ro:rororo114514`

### 后记

写的很💩，仅供内部使用，能用就行。

感谢用到的这些开源项目：

- Feishu Pages: https://longbridge.github.io/feishu-pages/
- VitePress: https://vitepress.dev/
- vitepress-plugin-pagefind: https://github.com/ATQQ/sugar-blog/tree/master/packages/vitepress-plugin-pagefind
- miniserve: https://github.com/svenstaro/miniserve
