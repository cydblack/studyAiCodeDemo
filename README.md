# studyAiCodeDemo

Dylan 自用 AI / Agent / Demo 代码库，按照我自己的笔记顺序，按主题分目录。

## 一、代码目录

与我的笔记顺序一致：


| #   | 目录              | 文件                    | 说明                           |
| --- | --------------- | --------------------- | ---------------------------- |
| 1   | Agent           | `baseQwenAgent`       | 最基础的 `Qwen Agent`            |
|     |                 | `ACP`                 | Agent Client Protocol        |
| 2   | FunctionCalling | `门票助手1`               | 使用查 SQLite 库的 tool           |
|     |                 | `门票助手2`               | 在 `门票助手1` 上，增加了图表信息展示        |
| 3   | MCP             | `MCP使用-使用Tavily`      | MCP 的使用，远程 Tavily MCP        |
|     |                 | `门票助手2`               | 本地自建 MCP 服务（txt 计数）          |
| 4   | OpenManus       | `OpenManus_cyd`       | OpenManus 本地改版               |
| 5   | Harness         | `Memory`              | 会话压缩、升格、召回、心跳                |
| 6   | LangChain       | `LLMChain-参数传递`       | Prompt 填变量，直接调模型             |
|     |                 | `LLMChain-tool使用`     | Agent + SerpAPI 网页搜索         |
|     |                 | `LLMChain-调用Fuction`  | 搜索工具 + 自定义计算器                |
|     |                 | `带短期记忆的LLMChain`      | 多轮对话记住上文                     |
|     |                 | `本地知识客服`              | Agent 查本地产品/公司信息             |
|     |                 | `ReAct私募基金问答助手`       | 带 system prompt 的规则库问答       |
|     |                 | `工具链组合形式-由LLM自己选工具`   | 多个本地工具，模型自己选                 |
|     |                 | `网络故障诊断Agent`         | 模拟 ping / DNS / 网卡 / 日志诊断    |
|     |                 | `LCEL_demo`           | LCEL 翻译 → 分析 → 回译，流式输出       |
|     |                 | `LCEL_工具链组合形式-不使用大模型` | 工具顺序由代码写死，对照上一则              |
| 7   | prompt          | `意图识别+Query改写`        | 识别问句类型，改写成可单独检索的问题           |
|     |                 | `带联网搜索的Query改写`       | 判断是否需要联网，并改写成搜索查询            |
| 8   | BM25            | `酒店推荐-BM25-TF-IDF`    | 西雅图酒店描述，TF-IDF 余弦相似度推荐 Top10 |
| 9   | Embedding       | `向量数据库`               | 百炼 `text-embedding-v4` 建 FAISS 索引，用自定义 ID 回查元数据 |
|     |                 | `BGE-m3`              | 本地下载 BGE-M3，计算句向量余弦相似度        |
|     |                 | `文本Embedding`         | `text-embedding-v4` 对一句话做向量     |
|     |                 | `图片Embedding`         | `tongyi-embedding-vision-plus` 对海报做向量 |
|     |                 | `视频Embedding`         | 同一模型对同目录 `car.mp4` 做向量        |
| 10  | RAG_Agent       | `基础RAG_Agent(pdf-Faiss)` | 读考核办法 PDF，切分后用 FAISS 做问答     |
| 12  | 多模态             | `Gemini-文字输出`          | Gemini 纯文字问答                  |
|     |                 | `Gemini-图像理解`          | 读同目录 `car.jpg`，解释照片           |
|     |                 | `Gemini-视频理解`          | 上传 `car.mp4`，等转码后描述视频          |
|     |                 | `DeepSeek-图像理解`        | 本地图片转 data URL，DeepSeek 解释照片  |
|     |                 | `DeepSeek-视频理解`        | OpenCV 抽帧后按图片送给 DeepSeek      |
| 88  | Tools           | `Jieba分词`             | 对字符串列表做中文分词                  |
|     |                 | `特征词获取`               | 酒店描述 n-gram 词频 TopK          |
|     |                 | `gui-plus`            | 截图转 GUI 操作（从仓库根目录迁入）         |
|     |                 | `西游记_word2vec`        | jieba 分词后训练 Word2Vec；`BOOK` 在西游记 / 三国演义间切换 |




## 二、环境准备

```powershell
# 在仓库根目录
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

各章依赖各自维护在子目录 `requirements.txt`，学到哪装到哪即可。

### 环境变量一览

仓库脚本通过 `os.getenv` / `os.environ` 读取的变量如下（密钥放环境变量或本地 `.env`，已在 `.gitignore`，不要提交进仓库）。


| 变量                     | 必需程度                     | 用途                                                                    |
| ---------------------- | ------------------------ | --------------------------------------------------------------------- |
| `DASHSCOPE_API_KEY`    | 几乎所有章节必需                 | 通义千问 / 百炼（模型调用）                                                       |
| `DASHSCOPE_BASE_URL`   | 可选                       | 百炼 OpenAI 兼容地址，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `SERPAPI_API_KEY`      | 跑 LangChain 搜索 Agent 时必需 | `serpapi-search-tools` 网页搜索                                           |
| `DEEPSEEK_API_KEY`     | 跑 ACP 主 Agent 拆任务板时必需    | `ACP/scripts/01`、`04` 的 DeepSeek 主 Agent                              |
| `LANGSMITH_API_KEY`    | 跑 LangSmith 时必需          | LangSmith 鉴权（[smith.langchain.com](https://smith.langchain.com)）      |
| `LANGCHAIN_TRACING_V2` | 跑 LangSmith 时必需          | 设为 `true` 开启追踪；代码里读此开关                                                |
| `LANGCHAIN_PROJECT`    | 可选                       | LangSmith 项目名，默认多为 `wealth-advisor-hybrid-agent`                      |
| `LANGCHAIN_ENDPOINT`   | 可选                       | LangSmith API 端点，不设则用官方默认                                             |
| `LANGFUSE_PUBLIC_KEY`  | 跑 Langfuse 时必需           | Langfuse 公钥                                                           |
| `LANGFUSE_SECRET_KEY`  | 跑 Langfuse 时必需           | Langfuse 私钥                                                           |
| `LANGFUSE_BASE_URL`    | 可选                       | 默认 `https://cloud.langfuse.com`                                       |
| `OPENAI_API_KEY`       | 跑 DeepEval 时必需           | DeepEval 评审模型（如 gpt-4o-mini）                                          |
| `TAVILY_API_KEY`       | 跑 Tavily MCP 时必需         | `MCP` 远程搜索 Agent                                                      |
| `DAYTONA_API_KEY`      | 跑 OpenManus 沙箱时可选        | `OpenManus_cyd` Daytona 云沙箱；`config.toml` 中可留空由环境变量注入                 |
| `GEMINI_API_KEY`       | 跑 Gemini 多模态时必需          | `12-多模态` 的 Gemini 文字、图像、视频理解                                        |




### 按目录对照


| 目录                  | 需要的环境变量                                                                                         |
| ------------------- | ----------------------------------------------------------------------------------------------- |
| `BaseQwenAgent`     | `DASHSCOPE_API_KEY`                                                                             |
| `FunctionCalling`   | `DASHSCOPE_API_KEY`                                                                             |
| `MCP`（本地 MCP）       | `DASHSCOPE_API_KEY`                                                                             |
| `MCP`（Tavily MCP）   | `DASHSCOPE_API_KEY` + `TAVILY_API_KEY`                                                          |
| `LangChain`         | `DASHSCOPE_API_KEY`；搜索 Agent 再加 `SERPAPI_API_KEY`                                               |
| `7.prompt`          | `DASHSCOPE_API_KEY`                                                                             |
| `12-多模态`            | Gemini 脚本需要 `GEMINI_API_KEY`；DeepSeek 脚本需要 `DASHSCOPE_API_KEY`                                |
| `ACP`               | `DEEPSEEK_API_KEY`（拆任务板 / 主循环）；Codex ACP worker 需要本机 Node                                       |
| `LangGraph`         | `DASHSCOPE_API_KEY`                                                                             |
| `LangSmith`         | `DASHSCOPE_API_KEY` + `LANGSMITH_API_KEY` + `LANGCHAIN_TRACING_V2=true`（可选 `LANGCHAIN_PROJECT`） |
| `OpenEvals`         | `DASHSCOPE_API_KEY`；对接 LangSmith 时再加 `LANGSMITH_API_KEY`（及 tracing 相关）                          |
| `DeepEval`          | `DASHSCOPE_API_KEY`（被测 Agent）+ `OPENAI_API_KEY`（评审）                                             |
| `langFuse`          | `DASHSCOPE_API_KEY` + `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`（可选 `LANGFUSE_BASE_URL`）     |
| `OpenManus_cyd`     | `DASHSCOPE_API_KEY`；用 Daytona 沙箱时再加 `DAYTONA_API_KEY`                                           |
| `88-Tools/gui-plus` | `DASHSCOPE_API_KEY`                                                                             |
| `Memory`            | `DASHSCOPE_API_KEY`                                                                             |
| `8-BM25`            | 不需要 API Key                                                                                     |
| `9-Embedding`       | `向量数据库`、`文本Embedding`、`图片Embedding`、`视频Embedding` 需要 `DASHSCOPE_API_KEY`；`BGE-m3` 使用本地模型，不需要百炼 Key |
| `10-RAG_Agent`      | `DASHSCOPE_API_KEY`                                                                             |
| `88-Tools`          | `gui-plus` 需要 `DASHSCOPE_API_KEY`；分词、特征词获取和 Word2Vec 不需要                                         |




### PowerShell 设置示例（当前会话）

```powershell
# 通义 / 百炼（多数脚本）
$env:DASHSCOPE_API_KEY="你的key"
$env:DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# SerpAPI（LangChain 搜索 Agent）
$env:SERPAPI_API_KEY="你的key"

# DeepSeek（ACP 主 Agent）
$env:DEEPSEEK_API_KEY="你的key"

# LangSmith（LangSmith / 部分 OpenEvals）
$env:LANGSMITH_API_KEY="你的key"
$env:LANGCHAIN_TRACING_V2="true"
$env:LANGCHAIN_PROJECT="wealth-advisor-hybrid-agent"

# Langfuse（langFuse）
$env:LANGFUSE_PUBLIC_KEY="你的公钥"
$env:LANGFUSE_SECRET_KEY="你的私钥"
# $env:LANGFUSE_BASE_URL="https://cloud.langfuse.com"

# DeepEval（DeepEval）
$env:OPENAI_API_KEY="你的key"

# Tavily MCP（MCP）
$env:TAVILY_API_KEY="你的key"

# OpenManus Daytona 沙箱（OpenManus_cyd，可选）
$env:DAYTONA_API_KEY="你的key"

# Gemini（12-多模态）
$env:GEMINI_API_KEY="你的key"
```



## 三、模型选择

模型基本上都选的如 `deepseek-v`、`qwen-flash` 之类的便宜模型，主要是省金币

## 四、代码说明



### 1. Agent

1. `baseQwenAgent`
  - 最基础的 `Qwen Agent`
  - 使用 `DashScope` 直接调模型
2. `ACP`
  - 最简连接：`ACP最简连接 _Win.py` / `ACP最简连接_Mac.py`，拉起官方 `@agentclientprotocol/codex-acp`。
  - `scripts/` 可单独跑：`01` 拆任务板 → `02` ACP smoke → `03` 上下文隔离 → `04` TriggerFlow 主循环 → `05` 复盘结果。
  - 业务材料：`ACP/materials/product_goal.txt`；产物：`ACP/.demo_runs/`。
  - 另有 `ACP/Demo/demo1.py`（Agently TriggerFlow，不走 ACP）。
  - 说明见 `ACP/scripts/README.md`。Windows 上用 `node.exe` + `npx-cli.js` 启动 adapter，不要直接跑 `npx.cmd`。



### 2. FunctionCalling

1. `门票助手1`
  - 使用 `Qwen-Agent` 封装
  - 原本使用链接数据库，后来改为本地 `SQLite` 文件
  - 使用的是 `qwen` 的 `tools` 注册方式
2. `门票助手2`
  - 在 `门票助手1` 的基础上，增加了图表信息的展示



### 4. OpenManus_cyd（Manus）

1. `OpenManus_cyd`
  - OpenManus 本地改版
  - `config.toml` + 环境变量
  - 可选 Daytona 沙箱
  - 从 `config/config.example.toml` 复制出本地 `config/config.toml`（该文件已被 gitignore，勿提交密钥）。
  - LLM：`config.toml` 里 `api_key` 可留空，启动时读 `DASHSCOPE_API_KEY`。
  - Daytona：`daytona_api_key` 可留空，启动时读 `DAYTONA_API_KEY`。
  - 入口：`python main.py`；沙箱相关见 `app/daytona/README.md`、`sandbox_main.py`。
  - 依赖见该目录 `requirements.txt`；完整安装可能较慢，可按需分批安装。



### 5. Harness

1. `Memory`（Agent 长期记忆）
  - 会话压缩、升格、召回、心跳
  - 综合实例把文件记忆接入 Workspace 再对照出行程
  - 主线看 `Memory/MemoryV2/README.md`：Step1–Step5 压缩与召回，Step6 心跳（有新 `event_id` 才跑前五步）。
  - `MemoryV1` 是文件分层管线存档，日常不用看。
  - 综合实例：`python Memory/综合实例/run.py`，整理后导入本目录 `FileMemoryWorkspace`，对照有/无记忆两份行程。
  - 材料在 `Memory/materials/`，产物在 `Memory/.demo_runs/`。



### 6. LangChain

> 写法以 2026.09 的 LangChain 1.x 为准。
> 不再用已停更的 `langchain_community.ChatTongyi` / `load_tools(["serpapi"])`（`6` 仍用 `ChatTongyi` + `qwen-plus`）。其余走 `ChatOpenAI` + 百炼 `compatible-mode/v1`；`1–7` 多为 `deepseek-v4-flash`，`8`、`9` 为 `qwen-turbo`。搜索用 `serpapi-search-tools` 的 `web_search(provider="langchain")`。



### 7. prompt

两个脚本都用 `deepseek-v4.1-flash`，通过 `dashscope.MultiModalConversation.call` 调用。请求地址写在脚本里，是阿里云 MaaS `https://ws-q8b7jquakv6ldzfd.cn-beijing.maas.aliyuncs.com/api/v1`。

1. `意图识别+Query改写`
  - 先判断问句类型，再按类型改写
  - 五种类型：上下文依赖（补上对话里没写进当前问句的信息）、对比（写明比较对象）、模糊指代（把「它」「都」换成具体对象）、多意图（拆成 JSON 数组）、反问（改成中立、可检索的问句）
  - 同时命中多意图和模糊指代时，按多意图处理
  - `main` 用同一段工作经历对话跑五个例子：还在别的公司就职过吗、哪家公司待得更久、薪资都是多少、带人和绩效、是不是只是参与而非主 R
  - 入口：`python 7.prompt/1-意图识别+Query改写.py`
  - 需要 `DASHSCOPE_API_KEY`。依赖见该目录 `requirements.txt`（`dashscope`）
2. `带联网搜索的Query改写`
  - 判断问句要不要联网。需要时再改写成搜索查询，并给出搜索策略。脚本本身不发起搜索
  - 需要联网的情况包括时效、价格、营业、活动、天气、交通、预订、实时状态
  - 改写结果包含搜索词、关键词、搜索意图和建议来源。策略包含主要词、扩展词、平台和时间范围，时间按运行当天计算
  - `main` 跑三个例子：上海迪士尼今天是否开放、下周六门票价格和预订、我叫什么名字（不需要联网）
  - 入口：`python 7.prompt/2-带联网搜索的Query改写.py`
  - 需要 `DASHSCOPE_API_KEY`。依赖与上一则相同


### 8. BM25

1. `酒店推荐-BM25-TF-IDF`
  - 读 `Seattle_Hotels.csv`（152 家西雅图酒店）
  - 先统计描述里的 Top20 三字词并画条形图，再清洗文本
  - 用 `TfidfVectorizer`（1–3 gram）提取特征，`linear_kernel` 算余弦相似度
  - 按酒店名推荐 Top10，示例是机场希尔顿和 Bacon Mansion
  - 入口：`python 8-BM25/1-酒店推荐-BM25-TF-IDF/酒店推荐.py`。路径按脚本所在目录解析，从仓库根目录启动即可
  - 依赖见该目录 `requirements.txt`（pandas、scikit-learn、matplotlib）


### 9. Embedding

1. `向量数据库`
  - 从 `8-RAG_Agent/2-向量数据库` 迁到 `9-Embedding/1-向量数据库`
  - `生成faiss索引.py`：用百炼 `text-embedding-v4`（1024 维）把四条迪士尼说明写成最简 FAISS 索引
  - `embedding-faiss-元数据.py`：`IndexIDMap` 写入自定义 ID，把索引、元数据和配置保存到 `D:\faiss\vector_db`。Windows 上 `faiss.write_index` 使用纯英文路径
  - 查询「迪士尼门票的退款流程」，按 ID 回查正文和 metadata
  - 需要 `DASHSCOPE_API_KEY`
2. `BGE-m3`
  - `modelscope` 把 `BAAI/bge-m3` 下载到 `D:/models`
  - `BGEM3FlagModel(..., use_fp16=True)` 在本地编码，取 `dense_vecs`
  - `embeddings_1 @ embeddings_2.T` 得到余弦相似度
  - 入口：`python 9-Embedding/2-BGE-m3/本地部署bge-m3模型并使用.py`
  - 使用本地模型，不调用百炼
3. `文本Embedding`
  - `dashscope.TextEmbedding.call`，模型 `text-embedding-v4`，`input` 直接传字符串「我叫陈永达」
  - 入口：`python 9-Embedding/3-文本Embedding/text_embedding.py`
  - 需要 `DASHSCOPE_API_KEY`。依赖见该目录 `requirements.txt`（`dashscope`）
4. `图片Embedding`
  - `dashscope.MultiModalEmbedding.call`，模型 `tongyi-embedding-vision-plus`
  - 读同目录 `海报.jpg`，转成 data URL 后放进 `input`
  - 路径按脚本所在目录解析，从仓库根目录启动即可
  - 入口：`python 9-Embedding/4-图片Embedding/image_embedding.py`
  - 需要 `DASHSCOPE_API_KEY`
5. `视频Embedding`
  - 同一模型 `tongyi-embedding-vision-plus`，把同目录 `car.mp4` 的路径放进 `input`
  - 入口：`python 9-Embedding/5-视频Embedding/video_embedding.py`
  - 需要 `DASHSCOPE_API_KEY`。依赖见该目录 `requirements.txt`（`dashscope`）


### 10. RAG_Agent

1. `基础RAG_Agent(pdf-Faiss)`
  - 读同目录《浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf》。路径按脚本所在目录解析，从仓库根目录启动即可
  - `RecursiveCharacterTextSplitter` 切分，`DashScopeEmbeddings`（`text-embedding-v1`）写入 FAISS，索引在 `D:\faiss\pdf_agent_vector_db`
  - 查询时 `similarity_search_with_score` 取最相近的 10 块，用 `Tongyi`（`deepseek-v4-flash`）回答，并打印页码和 L2 距离，距离越小越近
  - 入口：`python "10-RAG_Agent/1-基础RAG_Agent(pdf-Faiss)/chatpdf-faiss.py"`。建库那一行默认注释掉，已有索引时直接查询
  - 需要 `DASHSCOPE_API_KEY`。依赖见该目录 `requirements.txt`（`langchain_community`、`langchain_text_splitters`、`PyPDF2`）

### 12. 多模态

同一段汽车剐蹭素材 `car.jpg` / `car.mp4`，对照 Gemini 直接看图、看视频，以及 DeepSeek 看图、抽帧后再看。

1. `Gemini-文字输出`
  - `google.genai` 调 `gemini-3.8-flash`，只发一段中文问题
  - 入口：`python "12-多模态/Gemini-文字输出.py"`
  - 需要 `GEMINI_API_KEY`
2. `Gemini-图像理解`
  - 读同目录 `car.jpg`，`contents` 里同时放图片对象和「帮我解释下这张照片」
  - 路径按脚本所在目录解析，从仓库根目录启动即可
  - 入口：`python "12-多模态/Gemini-图像理解.py"`
  - 需要 `GEMINI_API_KEY`
3. `Gemini-视频理解`
  - `client.files.upload` 上传 `car.mp4`，轮询到转码完成后再放进 `contents`
  - 视频路径按当前工作目录解析，先 `cd` 到 `12-多模态` 再运行
  - 入口：`python Gemini-视频理解.py`
  - 需要 `GEMINI_API_KEY`
4. `DeepSeek-图像理解`
  - 模型 `deepseek-v4.1-flash`，走阿里云 MaaS 的 OpenAI 兼容地址
  - 把本地 `car.jpg` 转成 data URL，和文字一起放进 `content`
  - 路径按脚本所在目录解析，从仓库根目录启动即可
  - 入口：`python "12-多模态/DeepSeek-图像理解.py"`
  - 需要 `DASHSCOPE_API_KEY`
5. `DeepSeek-视频理解`
  - DeepSeek 只收图片。用 OpenCV 从 `car.mp4` 均匀抽 6 帧，再按图片理解送给模型
  - 路径按脚本所在目录解析，从仓库根目录启动即可
  - 入口：`python "12-多模态/DeepSeek-视频理解.py"`
  - 需要 `DASHSCOPE_API_KEY`。该目录 `requirements.txt` 有 `Pillow`、`protobuf`、`opencv-python`。Gemini 脚本另需 `google-genai`，DeepSeek 脚本另需 `openai`

### 88. Tools

1. `Jieba分词`
  - `segment_lines` 接收字符串列表，逐条分词后用空格拼回
  - 入口：`python 88-Tools/Jieba分词/jieba分词.py`
2. `特征词获取`
  - 读酒店描述，用 `CountVectorizer` 统计 n-gram 词频 TopK，并画条形图
  - 入口：`python 88-Tools/特征词获取/get_top_n_words.py`
3. `gui-plus`
  - 从仓库根目录 `gui-plus/` 迁到 `88-Tools/gui-plus/`
  - 读本地截图，让视觉模型返回下一步 GUI 操作
  - 需要 `DASHSCOPE_API_KEY`
4. `西游记_word2vec`
  - 三份脚本顶部用 `BOOK` 选语料，默认 `"西游记"`。改成 `"三国演义"` 后，分词、训练、加载都走对应目录
  - `step1_word_seg.py`：jieba 对 `{BOOK}/source` 分词，空格拼接后写到 `{BOOK}/segment`
  - `step2_word_similarity.py`：用分词结果训练两套 Word2Vec。第一套保存 `{BOOK}/model/word2Vec_1.model`，第二套由 `model2.save` 保存 `{BOOK}/model/word2Vec_2.model`，并打印「孙悟空」和相关人物的相似度
  - `step3_use_model.py`：加载 `{BOOK}/model/word2Vec_2.model`。默认算「孙悟空」和「菩提」的相似度，并做 `唐僧 + 孙悟空 - 猪八戒`。三国演义的查询（曹操、刘备、张飞）写在注释里
  - 模型目录和 `*.md` 已在 `.gitignore` 中，克隆后需要自己跑 step1、step2 生成分词结果和模型
  - 查询用的词必须和分词结果一致。jieba 把「金角大王」切成了「金角」和「大王」
  - 依赖见该目录 `requirements.txt`（jieba、gensim）。本机是 Python 3.13 时安装 `gensim==4.4.0`，`4.3.3` 没有对应的安装包



### 其他

1. `LLMChain-参数传递`
  - **功能**：给公司起名字
  - **说明**：通过 `prompt | llm` 方式，`PromptTemplate` 把 `{product}` 填进「给某方向公司起名」
2. `LLMChain-tool使用`
  - Agent 挂上 SerpAPI 的 `web_search`，问「十月一日是什么节日」
  - 看 `create_agent` + 现成搜索工具的最小写法
3. `LLMChain-调用Fuction`
  - 搜索工具再加自定义 `calculator`，问北京气温（华氏）再算其 1/4
  - 看现成工具和 `@tool` 函数怎么拼进同一个 Agent
4. `带短期记忆的LLMChain`
  - `RunnableWithMessageHistory` 同一 `session_id` 连问三轮
  - 第三轮问「我叫什么名字」，看短期记忆怎么挂到 chain 上（不经过 Agent）
5. `本地知识客服`
  - 两个 `@tool`：按车型查描述、按问题查公司介绍；命令行循环提问
  - 看 Agent 在本地字典/固定文案上当客服，不联网
6. `ReAct私募基金问答助手`
  - 内存规则库 + 关键词/类别/直接问答三个工具
  - `system_prompt` 约束只答私募；循环对话
  - 仍用 `ChatTongyi`（`qwen-plus`），和其余走 `ChatOpenAI` 的文件不是同一套模型入口
7. `工具链组合形式-由LLM自己选工具`
  - 五个本地工具（情感分析、JSON/CSV 转换、行数、查找、替换）
  - 三个任务分别测组合调用和「没有对应工具」
  - 看工具链组合：模型按题自己选工具，而不是代码写死调用顺序
8. `网络故障诊断Agent`
  - 四个模拟工具：`ping`、DNS、网卡状态、日志分析
  - 跑「访问超时」和「eth1 连不上网」两个诊断任务
  - 看同一套 `create_agent` 用在故障排查场景，工具返回的是模拟结果
9. `LCEL_demo`
  - **功能**：LCEL 基本写法 Demo，`ChatPromptTemplate | llm | StrOutputParser` 组成翻译 → 分析 → 回译
  - `workflow.stream` 流式输出打印
10. `LCEL_工具链组合形式-不使用大模型`
  - 使用 `LCEL` 方式，对 7 的代码进行修改
    - 这里没有大模型，选哪个工具、什么顺序全是代码决定的



## 五、最终说明

- 纯学习用途，代码以可跑通、好对照为主，不可用于生成环境。
- 同一业务场景（投顾助手）会在 LangGraph / LangSmith / Langfuse / DeepEval 中反复出现，方便横向对比「编排 → 追踪 → 评测」。
- `ACP` 用杭州三日游团建目标，对照「主 Agent 拆板 → Codex worker 执行 → 上下文隔离 → TriggerFlow 汇总」。
- `Memory` 用同一套亲子行程对话，对照「压缩 → 升格 → 召回 → 有/无记忆出行程」。
- `7.prompt` 用同一段工作经历对话，对照五种问句「识别类型 → 改写成可单独检索的问题」；再用迪士尼问句对照「是否需要联网 → 改写成搜索查询」。
- `8-BM25` 用西雅图酒店对照「词频 → TF-IDF 推荐」。
- `9-Embedding` 用百炼 `text-embedding-v4` 建带元数据的 FAISS 索引，并用本地 BGE-M3 算句向量余弦相似度。文本、图片、视频三条 Demo 分别走 `TextEmbedding` 和 `tongyi-embedding-vision-plus`。
- `10-RAG_Agent` 用考核办法 PDF 对照「切分 → DashScope 嵌入 → FAISS 问答」。
- `12-多模态` 用同一段汽车剐蹭素材对照「Gemini 直接看图 / 看视频」和「DeepSeek 看图 / 抽帧后再看」。
- `88-Tools/西游记_word2vec` 用《西游记》/《三国演义》对照「分词 → Word2Vec → 加载模型算相似度」。
- Windows 环境；运行前确认已激活虚拟环境并设置好对应 API Key。

