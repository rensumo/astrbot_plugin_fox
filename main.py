from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import At, Image, Plain
import os
import random
import time  

@register(
    "astrbot_plugin_fox",
    "rensumo",
    "随机发送一张狐狸图",
    "1.0.2",
    "https://github.com/rensumo/astrbot_plugin_fox"
)
class DoroTodayPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.user_cooldowns = {}
        self.cooldown_seconds = 1800

    @filter.command("dorotoday", alias={'狐狸图', '🦊图'})
    async def dorotoday(self, event: AstrMessageEvent, *args, **kwargs):
        '''随机抽取一张狐狸图并发送，同时@发送者'''
        sender_id = event.get_sender_id()
        current_time = time.time()
        last_used_time = self.user_cooldowns.get(sender_id, 0)
        remaining_cooldown = last_used_time + self.cooldown_seconds - current_time
        
        if remaining_cooldown > 0:
            minutes = int(remaining_cooldown // 60)
            seconds = int(remaining_cooldown % 60)
            yield event.chain_result([
                At(qq=sender_id),
                Plain(f" 狐狸图冷却中哦～ 还需要等待 {minutes}分{seconds}秒才能再次使用")
            ])
            return
        
        try:
            sender_name = event.get_sender_name()
        except AttributeError:
            sender_name = str(sender_id)
        
        doro_folder = os.path.join(os.path.dirname(__file__), "fox")
        
        if not os.path.exists(doro_folder):
            yield event.plain_result("fox文件夹不存在，请检查插件目录")
            return
        
        image_files = [f for f in os.listdir(doro_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if not image_files:
            yield event.plain_result("fox文件夹中没有图片")
            return
        
        self.user_cooldowns[sender_id] = current_time
        random_image = random.choice(image_files)
        image_path = os.path.join(doro_folder, random_image)
        image_name = os.path.splitext(random_image)[0]

        message_chain = [
            At(qq=sender_id),
            Plain(f" {image_name}"),
            Image.fromFileSystem(image_path)  
        ]
        
        yield event.chain_result(message_chain)