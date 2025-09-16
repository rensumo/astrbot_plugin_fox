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
    "1.0.2",  # 版本号更新
    "https://github.com/rensumo/astrbot_plugin_fox"
)
class DoroTodayPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 存储用户最后一次使用命令的时间，格式: {user_id: timestamp}
        self.user_cooldowns = {}
        # 默认冷却时间30分钟（1800秒）
        self.cooldown_seconds = 1800

    @filter.command("dorotoday", alias={'狐狸图', '🦊图'})
    async def dorotoday(self, *args, **kwargs):
        '''随机抽取一张狐狸图并发送，同时@发送者'''
        # 从参数中提取event对象（通常是第一个参数）
        event = args[0] if args else None
        if not isinstance(event, AstrMessageEvent):
            yield event.plain_result("获取事件对象失败")
            return
        
        # 获取发送者的ID
        sender_id = event.get_sender_id()
        
        # 检查冷却时间
        current_time = time.time()
        last_used_time = self.user_cooldowns.get(sender_id, 0)
        
        # 计算剩余冷却时间（秒）
        remaining_cooldown = last_used_time + self.cooldown_seconds - current_time
        
        if remaining_cooldown > 0:
            # 转换剩余时间为分钟和秒，方便用户理解
            minutes = int(remaining_cooldown // 60)
            seconds = int(remaining_cooldown % 60)
            yield event.chain_result([
                At(qq=sender_id),
                Plain(f" 狐狸图冷却中哦～ 还需要等待 {minutes}分{seconds}秒才能再次使用")
            ])
            return
        
        # 获取发送者昵称
        try:
            sender_name = event.get_sender_name()
        except AttributeError:
            sender_name = str(sender_id)
        
        # 获取fox文件夹的路径
        doro_folder = os.path.join(os.path.dirname(__file__), "fox")
        
        # 检查fox文件夹是否存在
        if not os.path.exists(doro_folder):
            yield event.plain_result("fox文件夹不存在，请检查插件目录")
            return
        
        # 获取fox文件夹中的所有图片文件
        image_files = [f for f in os.listdir(doro_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if not image_files:
            yield event.plain_result("fox文件夹中没有图片")
            return
        
        # 更新用户最后使用时间
        self.user_cooldowns[sender_id] = current_time
        
        random_image = random.choice(image_files)
        image_path = os.path.join(doro_folder, random_image)
        image_name = os.path.splitext(random_image)[0]  # 去除文件扩展名
        
        message_chain = [
            At(qq=sender_id),
            Plain(f" {image_name}"),
            Image.fromFileSystem(image_path)  
        ]
        
        # 发送消息
        yield event.chain_result(message_chain)
    