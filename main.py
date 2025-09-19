from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import At, Image
from astrbot.api import AstrBotConfig  # 用于加载配置
import os
import random
import time  


@register(
    "astrbot_plugin_fox",
    "rensumo",
    "随机发送一张狐狸图（冷却时间可配置）",
    "1.0.5",  # 版本更新：删除昵称获取+简化配置
    "https://github.com/rensumo/astrbot_plugin_fox"
)
class DoroTodayPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        # 存储用户最后一次使用时间
        self.user_cooldowns = {}
        # 加载配置（无配置时用默认值）
        self.config = config or AstrBotConfig()
        self._load_cooldown_config()

    def _load_cooldown_config(self):
        """仅加载冷却时间配置，简化逻辑"""
        # 读取配置中的冷却时间，无配置则用默认1800秒
        fox_config = self.config.get("fox_config", {})
        self.cooldown_seconds = fox_config.get("cooldown_seconds", 1800)
        # 容错：确保冷却时间为正整数
        if not isinstance(self.cooldown_seconds, int) or self.cooldown_seconds <= 0:
            self.cooldown_seconds = 1800

    @filter.command("dorotoday", alias={'狐狸图', '🦊图'})
    async def dorotoday(self, event: AstrMessageEvent):
        '''随机发狐狸图+@发送者（无昵称获取，冷却可配置）'''
        # 1. 获取发送者ID
        sender_id = event.get_sender_id()

        # 2. 检查冷却时间
        current_time = time.time()
        last_used = self.user_cooldowns.get(sender_id, 0)
        remaining = last_used + self.cooldown_seconds - current_time

        if remaining > 0:
            # 格式化剩余时间（分+秒）
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            yield event.chain_result([
                At(qq=sender_id),
                Plain(f" 狐狸图冷却中～还需等待 {mins}分{secs}秒")
            ])
            return

        # 3. 检查狐狸图文件夹
        fox_folder = os.path.join(os.path.dirname(__file__), "fox")
        if not os.path.exists(fox_folder):
            yield event.plain_result("fox文件夹不存在，请检查插件目录")
            return

        # 4. 筛选图片文件
        image_files = [f for f in os.listdir(fox_folder) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not image_files:
            yield event.plain_result("fox文件夹中没有图片")
            return

        # 5. 更新冷却时间+发送图片
        self.user_cooldowns[sender_id] = current_time
        random_img = random.choice(image_files)
        img_path = os.path.join(fox_folder, random_img)

        yield event.chain_result([
            At(qq=sender_id),
            Image.fromFileSystem(img_path)
        ])
