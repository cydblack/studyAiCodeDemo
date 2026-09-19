# 多文件保险问答助手

三份脚本做同一件事：读取 `docs/` 下的保险条款与产品说明，按用户问题检索相关内容并回答。

差异只在框架和检索方式，便于对比 Qwen Agent、LlamaIndex、LangChain 各自怎么落地 RAG。

运行前需要环境变量 `DASHSCOPE_API_KEY`。模型统一为 DashScope 兼容接口上的 `deepseek-v4-flash`。

```bash
pip install -r requirements.txt
```

知识库在 `docs/`：若干 `.txt` 产品说明，以及部分条款 PDF。

---

## 1. Qwen Agent — `1-千问Agent.py`

阿里 Qwen Agent 框架。把 `docs/` 里的文件直接交给 `Assistant`，由框架内置 RAG 处理。

- 召回：Qwen 自带 BM25（关键字召回），不建向量库
- 交互：默认 WebUI；同文件里还有终端模式 `app_tui()`
- 文档：加载 `docs/` 下全部文件（含 txt、pdf）
- 额外：注册了文生图工具 `my_image_gen`（演示用，与保险问答无关）

```bash
python 1-千问Agent.py
```

适合看「框架把文档 RAG + GUI 包好」的写法。Web 界面里有示例问题，例如「介绍下雇主责任险」。

---

## 2. LlamaIndex — `2-llamaindex-agent.py`

LlamaIndex。文档切分后做向量索引，再用 ReAct Agent 调用检索工具回答。

- 召回：DashScope Embedding（`text-embedding-v2`）+ 向量相似度，`top_k=5`
- 索引：首次构建后落到 `storage/`，下次直接加载
- 文档：`SimpleDirectoryReader` 读 `docs/` 全部可读文件
- 交互：命令行；当前查询写死为「介绍下雇主责任险」
- Agent：`ReActAgent` + `retrieve_documents` 工具

```bash
python 2-llamaindex-agent.py
```

适合看「向量索引 + Agent 工具调用」这条链路。

---

## 3. LangChain — `3-langchain-agent.py`

LangChain。FAISS 向量检索 + LCEL 问答链，没有独立 Agent 循环。

- 召回：DashScope Embedding（`text-embedding-v1`）+ FAISS，`k=5`
- 索引：落到 `langchain_storage/`；Windows 下对含中文的绝对路径做了切目录后再读写
- 文档：只加载 `docs/` 下的 `.txt`（不读 PDF）
- 切分：`RecursiveCharacterTextSplitter`，块大小 1000、重叠 200
- 交互：命令行；当前查询同样写死为「介绍下雇主责任险」

```bash
python 3-langchain-agent.py
```

适合看「检索上下文再喂给 LLM」的经典 RAG 写法。

---

## 对照

| | Qwen Agent | LlamaIndex | LangChain |
|---|---|---|---|
| 文件 | `1-千问Agent.py` | `2-llamaindex-agent.py` | `3-langchain-agent.py` |
| 检索 | BM25 | 向量（embedding-v2） | 向量（embedding-v1 + FAISS） |
| 问答形态 | Assistant + 内置 RAG | ReAct Agent + 检索工具 | LCEL 问答链 |
| 界面 | WebUI（可切终端） | 终端单次查询 | 终端单次查询 |
| 文档范围 | `docs/` 全部文件 | `docs/` 全部可读文件 | 仅 `.txt` |
| 索引落盘 | 无 | `storage/` | `langchain_storage/` |

建议先跑 Qwen Agent 看完整问答体验，再对照另外两份看向量检索和 Agent / Chain 的组织方式。
