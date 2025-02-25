from telethon import TelegramClient, events
import re
from datetime import datetime
import utils

config = utils.load_conf()

api_id = config['account']['api_id']
api_hash = config['account']['api_hash']
session = config['account']['session']
rule = config['rule']
target = config['target_chat']['group']

# 替换为你的会话名称
client = TelegramClient(session, api_id, api_hash)

# 定义正则表达式规则
# 匹配以下关键词：搭建网站、开发软件、IM 软件、客服系统、爬虫、Telegram 机器人开发
pattern = re.compile(
    rule,
    re.IGNORECASE  # 忽略大小写
)


# 监听新消息
@client.on(events.NewMessage)
async def handler(event):
    # 只处理群组消息
    if not event.is_group:  # 判断消息是否来自群组
        return

    # 检查消息是否符合正则规则
    if not pattern.search(event.message.message or ""):
        return

    # 检查消息类型
    is_text_only = not event.message.media  # 是否是纯文字消息
    is_media_with_text = event.message.media and event.message.message  # 是否是有图片和文字的消息

    # 规则 1：纯文字消息不能超过 15 个字
    if is_text_only and len(event.message.message) > 15:
        return

    # 规则 2：放行既有图片又有文字的消息
    if is_media_with_text and len(event.message.message) > 15:
        return

    # 获取原始消息的发送者和群组信息
    sender = await event.get_sender()
    chat = await event.get_chat()
    message_id = event.message.id  # 消息 ID，用于跳转到消息位置
    message_date = event.message.date  # 消息发送日期

    # 提取发送者信息
    sender_name = "未知用户"  # 默认值
    sender_link = "tg://user?id=0"  # 默认链接

    if sender:
        # 如果 sender 存在，尝试获取 username 或 first_name
        sender_name = (
            f"@{sender.username}"  # 如果有 username，显示为 @username
            if sender.username
            else sender.first_name
            if sender.first_name
            else "未知用户"
        )
        # 如果 sender.id 存在，生成用户链接
        if sender.id:
            sender_link = f"tg://user?id={sender.id}"

    # 提取群组信息
    chat_name = chat.title if hasattr(chat, 'title') else "群组"
    chat_link = f"https://t.me/c/{chat.id}/{message_id}"  # 群组消息链接

    # 格式化消息日期
    formatted_date = message_date.strftime("%Y-%m-%d %H:%M:%S")

    # 构造转发消息的附加信息
    additional_info = (
        f"📨 **转发消息**\n"
        f"👤 **发送者**: {sender_name}\n"
        f"👥 **群组**: {chat_name}\n"
        f"🚪 **传送门**: [点击这里跳转]({chat_link})\n"
        f"📅 **发送时间**: `{formatted_date}`\n"
        f"---\n"
    )

    # 获取原始消息内容
    original_message = event.message.message or ""

    # 构造完整的转发消息
    forwarded_message = additional_info + original_message

    # 替换为目标群组的 ID 或用户名
    target_chat = target

    # 发送转发消息
    if event.message.media:
        # 如果消息包含媒体（如图片），转发媒体和文字
        await client.send_file(target_chat, event.message.media, caption=forwarded_message)
    else:
        # 如果消息是纯文字，仅转发文字
        await client.send_message(target_chat, forwarded_message, link_preview=True)


if __name__ == '__main__':
    # 启动客户端
    print("监听消息中...")
    client.start()
    client.run_until_disconnected()
