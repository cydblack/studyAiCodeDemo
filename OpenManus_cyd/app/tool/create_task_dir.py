import re
from datetime import datetime

from app.config import config
from app.tool.base import BaseTool, ToolResult


_CREATE_TASK_DIR_DESCRIPTION = """在项目的 workspace 目录下创建本次任务专属的文件夹，用于存放本次任务产生的所有内容（文件、下载、截图等）。
文件夹命名格式为 “{项目名}_{时间}”，其中时间戳由本工具自动生成（格式 YYYYMMDDHHMMSS），无需你自己提供时间。
在正式开始任务操作前调用一次即可，之后所有读写文件、保存截图都应使用本工具返回的目录路径。"""


class CreateTaskDir(BaseTool):
    name: str = "create_task_dir"
    description: str = _CREATE_TASK_DIR_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "project_name": {
                "type": "string",
                "description": "根据当前任务概括出的简短名称，长度不超过 20 个字符，不含空格和特殊字符（可用下划线连接），例如 flight_query。",
            }
        },
        "required": ["project_name"],
    }

    async def execute(self, project_name: str) -> ToolResult:
        """生成时间戳并创建任务目录，返回其绝对路径。"""
        # 清洗项目名：仅保留中文、字母、数字和下划线，其余字符替换为下划线
        cleaned = re.sub(r"[^\w\u4e00-\u9fa5]+", "_", project_name.strip()).strip("_")
        if not cleaned:
            cleaned = "task"
        # 限制项目名长度不超过 20 个字符
        cleaned = cleaned[:20]

        # 生成 14 位时间戳，格式 YYYYMMDDHHMMSS
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        dir_name = f"{cleaned}_{timestamp}"
        task_dir = config.workspace_root / dir_name

        try:
            task_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return ToolResult(error=f"创建任务目录失败: {str(e)}")

        return ToolResult(
            output=(
                f"任务目录已创建：{task_dir}\n"
                f"本次任务的所有文件、截图等内容都请保存到该目录下。"
            )
        )
