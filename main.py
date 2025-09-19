from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import At, Image, Plain
from astrbot.api import AstrBotConfig
import os
import random
import time  


@register(
    "astrbot_plugin_fox",
    "rensumo",
    "随机发送一张狐狸图（冷却时间可配置）",
    "1.0.6",  # 版本更新：修复发送者ID获取异常
    "https://github.com/rensumo/astrbot_plugin_fox"
)
class DoroTodayPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.user_cooldowns = {}  # {user_id: 最后使用时间戳}
        self.config = config or AstrBotConfig()
        self._load_cooldown_config()

    def _load_cooldown_config(self):
        """加载冷却时间配置"""
        fox_config = self.config.get("fox_config", {})
        # 确保冷却时间为正整数，默认30分钟（1800秒）
        self.cooldown_seconds = max(
            60,  # 最小冷却时间限制为60秒，避免配置过小
            int(fox_config.get("cooldown_seconds", 1800))
        )

    @filter.command("dorotoday", alias={'狐狸图', '🦊图'})
    async def dorotoday(self, event: AstrMessageEvent):
        """随机发送狐狸图，修复发送者ID获取逻辑"""
        # 关键修复：确保从事件对象event中获取发送者ID
        # 避免误将context当作事件对象使用
        try:
            # 优先使用event的get_sender_id方法
            sender_id = event.get_sender_id()
        except AttributeError:
            # 兼容部分版本可能的方法名差异
            try:
                sender_id = event.get_user_id()  # 备选方法名
            except AttributeError:
                # 若所有方法都失败，返回错误提示
                yield event.plain_result("获取发送者信息失败，请重试")
                return

        # 检查冷却时间
        current_time = time.time()
        last_used_time = self.user_cooldowns.get(sender_id, 0)
        remaining_cooldown = last_used_time + self.cooldown_seconds - current_time

        if remaining_cooldown > 0:
            mins = int(remaining_cooldown // 60)
            secs = int(remaining_cooldown % 60)
            yield event.chain_result([
                At(qq=sender_id),
                Plain(f" 狐狸图冷却中～还需等待 {mins}分{secs}秒")
            ])
            return

        # 检查图片文件夹
        fox_folder = os.path.join(os.path.dirname(__file__), "fox")
        if not os.path.exists(fox_folder):
            yield event.plain_result("fox文件夹不存在，请检查插件目录")
            return

        # 获取图片列表
        image_files = [
            f for f in os.listdir(fox_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]
        if not image_files:
            yield event.plain_result("fox文件夹中没有图片")
            return

        # 发送随机图片
        self.user_cooldowns[sender_id] = current_time
        random_image = random.choice(image_files)
        image_path = os.path.join(fox_folder, random_image)

        yield event.chain_result([
            At(qq=sender_id),
            Image.fromFileSystem(image_path)
        ])
