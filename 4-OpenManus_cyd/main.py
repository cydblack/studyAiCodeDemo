import argparse
import asyncio

from app.agent.manus import Manus
from app.logger import logger


async def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="运行 Manus agent")
    parser.add_argument(
        "--prompt", type=str, required=False, help="输入给 agent 的提示"
    )
    args = parser.parse_args()

    # 创建并初始化 Manus agent
    agent = await Manus.create()
    try:
        # 如果提供了命令行提示，则只执行一次；否则进入交互循环
        if args.prompt:
            logger.warning("正在处理你的请求...")
            result = await agent.run(args.prompt)
            logger.info("请求处理完成。")
            logger.info(f"执行结果：\n{result}")
            return

        # 交互循环：持续接收输入，直到用户输入 exit 才退出
        while True:
            prompt = input("请输入你的提示（输入 exit 退出）: ")
            if prompt.strip().lower() == "exit":
                logger.info("已退出 agent。")
                break
            if not prompt.strip():
                logger.warning("提供的提示为空。")
                continue

            logger.warning("正在处理你的请求...")
            result = await agent.run(prompt)
            logger.info("请求处理完成。")
            logger.info(f"执行结果：\n{result}")
    except KeyboardInterrupt:
        logger.warning("操作被中断。")
    finally:
        # 确保在退出前清理 agent 资源
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
