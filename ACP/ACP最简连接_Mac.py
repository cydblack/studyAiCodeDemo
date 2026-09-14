# ===== ACP 最简连接：启动官方 Codex adapter，发送一轮 prompt =====
import json
import os
import shutil
from pathlib import Path
from typing import Any, cast

# Client：负责与Agent通信，发送请求，接收响应
# spawn_agent_process ：负责连接Agent，创建进程
from acp import PROTOCOL_VERSION, Client, spawn_agent_process, text_block
from acp.schema import (
    ClientCapabilities,
    DeniedOutcome,
    Implementation,
    PermissionOption,
    ReadTextFileResponse,
    RequestPermissionResponse,
    ToolCallUpdate,
)

# Notebook kernel 的 PATH 不一定包含 Codex.app 内置命令。
# 这里把 Codex.app 的资源目录补进子进程环境，npx 启动 adapter 时也能找到本地 Codex。
INTRO_LESSON_DIR = Path.cwd()
if not (INTRO_LESSON_DIR / "materials" / "product_goal.txt").is_file():
    INTRO_LESSON_DIR = Path("harness_class/lessons/Multi_Agent_Orchestration").resolve()

INTRO_ACP_ENV = os.environ.copy()
INTRO_CODEX_BIN_DIR = Path("/Applications/Codex.app/Contents/Resources")
if INTRO_CODEX_BIN_DIR.is_dir():
    INTRO_ACP_ENV["PATH"] = f"{INTRO_CODEX_BIN_DIR}:{INTRO_ACP_ENV.get('PATH', '')}"

INTRO_NPX_COMMAND = os.getenv("ACP_NPX_COMMAND", "npx")

if shutil.which(INTRO_NPX_COMMAND, path=INTRO_ACP_ENV.get("PATH")) is None:
    raise RuntimeError(
        "当前 Notebook kernel 找不到 npx，请从已配置 Node 的 shell 启动 Jupyter kernel。"
    )

INTRO_AGENT_SPECS: dict[str, dict[str, object]] = {
    "codex": {
        "name": "codex",
        "command": INTRO_NPX_COMMAND,
        "args": ("-y", "@agentclientprotocol/codex-acp@1.1.0"),
    },
    # "cc": {
    #     "name": "claude code",
    #     "command": INTRO_NPX_COMMAND,
    #     "args": ("-y", "@agentclientprotocol/claude-agent-acp@0.55.0"),
    # },
}

print(json.dumps(INTRO_AGENT_SPECS, ensure_ascii=False, indent=2))


# ===== ACP 最简 Client：session + prompt + stream =====


class IntroAcpClient:
    def __init__(self, agent_name: str) -> None:
        # 1. 选择本地 Agent，拿到它的启动命令。
        self.agent_name = agent_name
        self.spec = INTRO_AGENT_SPECS[agent_name]
        self.agent_info = "(未初始化)"
        self._process_cm: Any | None = None
        self._connection: Any | None = None
        self._text_chunks: list[str] = []
        self._update_kinds: list[str] = []
        self._on_text_delta: Callable[[str], None] | None = None

    async def session_update(self, session_id: str, update: Any, **kwargs: Any) -> None:
        # 2. ACP adapter 推送流式 update；这里先只收文本 chunk。
        update_kind = str(getattr(update, "session_update", ""))
        self._update_kinds.append(update_kind)

        content = getattr(update, "content", None)
        text = getattr(content, "text", None)
        is_text_chunk = (
            update_kind == "agent_message_chunk"
            and getattr(content, "type", None) == "text"
        )
        if is_text_chunk and isinstance(text, str):
            self._text_chunks.append(text)
            if self._on_text_delta is not None:
                self._on_text_delta(text)

    async def request_permission(
        self,
        options: list[PermissionOption],
        session_id: str,
        tool_call: ToolCallUpdate,
        **kwargs: Any,
    ) -> RequestPermissionResponse:
        # 最简示例不做审批 UI，优先选择 adapter 给出的第一个 allow 选项。
        if not options:
            raise RuntimeError("ACP permission request 没有提供可选项")
        option = next(
            (item for item in options if item.kind.startswith("allow")), options[0]
        )
        return RequestPermissionResponse(
            outcome=AllowedOutcome(outcome="selected", option_id=option.option_id)
        )

    async def __aenter__(self) -> "IntroAcpClient":
        # 3. 启动 adapter 进程，建立 ACP 连接。
        command = str(self.spec["command"])
        args = cast(tuple[str, ...], self.spec["args"])
        self._process_cm = spawn_agent_process(
            cast(Client, self),
            command,
            *args,
            cwd=INTRO_LESSON_DIR,
            env=INTRO_ACP_ENV,
        )
        connection, _process = await self._process_cm.__aenter__()
        self._connection = connection

        # 4. 初始化协议，交换版本和客户端信息。
        init = await connection.initialize(
            protocol_version=PROTOCOL_VERSION,
            client_capabilities=ClientCapabilities(),
            client_info=Implementation(
                name="course-acp-intro", title="ACP 简介最小 Client", version="0.1.0"
            ),
        )
        self.agent_info = (
            init.agent_info.name
            if init.agent_info is not None
            else "(未提供 agentInfo)"
        )
        return self

    async def prompt(
        self,
        prompt_text: str,
        *,
        session_id: str = "",
        on_text_delta: Callable[[str], None] | None = None,
    ) -> dict[str, object]:
        if self._connection is None:
            raise RuntimeError("ACP client 尚未连接")

        self._text_chunks = []
        self._update_kinds = []
        self._on_text_delta = on_text_delta
        requested_session_id = session_id.strip()

        # 5. 选定会话：session_id 留空就创建新会话，有值就加载已有会话。
        if requested_session_id:
            await self._connection.load_session(
                cwd=str(INTRO_LESSON_DIR),
                session_id=requested_session_id,
                mcp_servers=[],
            )
            active_session_id = requested_session_id
            session_state = "loaded"
        else:
            session = await self._connection.new_session(
                cwd=str(INTRO_LESSON_DIR), mcp_servers=[]
            )
            active_session_id = session.session_id
            session_state = "new"

        # 6. 向选定 session 发送这一轮 prompt；文本 chunk 会从 session_update 流式回来。
        response = await self._connection.prompt(
            prompt=[text_block(prompt_text)],
            session_id=active_session_id,
        )
        self._on_text_delta = None

        # 7. 返回给主流程可继续保存和复用的结构体。
        return {
            "agent_name": self.agent_name,
            "agent_info": self.agent_info,
            "session_id": active_session_id,
            "session_state": session_state,
            "result": {
                "stop_reason": str(response.stop_reason),
                "update_kinds": sorted(set(self._update_kinds)),
                "text": "".join(self._text_chunks).strip(),
            },
        }

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._process_cm is not None:
            await self._process_cm.__aexit__(exc_type, exc, tb)


def print_delta(text: str) -> None:
    print(text, end="", flush=True)
