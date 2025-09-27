"""
    原神/绝区零剧情跳过脚本
    功能：通过自动点击鼠标跳过游戏剧情
    使用方法：（如出现失效请）以管理员身份运行本程序
    注意事项：请确保游戏窗口处于活动状态，且点击位置正确设置
    控制键：F12 - 退出程序，F9 - 暂停/继续

    依赖库：keyboard, pyautogui
    安装依赖：pip install keyboard pyautogui
"""

import keyboard
import pyautogui
import threading
import time


class GameSkipScript:
    def __init__(self, click_position=(1500, 740), click_interval=1):
        """
        初始化脚本

        Args:
            click_position: 点击坐标 (x, y)
            click_interval: 点击间隔时间(秒)
        """
        self.is_running = True
        self.click_position = click_position
        self.click_interval = click_interval

        # 获取屏幕分辨率
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"屏幕分辨率: {self.screen_width} x {self.screen_height}")

        # 注册键盘事件监听
        self._setup_keyboard_listener()

    def _setup_keyboard_listener(self):
        """设置键盘事件监听器"""
        keyboard.on_press(self._keyboard_callback)
        print("键盘监听器已设置 - F12:退出, F9:暂停/继续")

    def _keyboard_callback(self, event):
        """键盘事件回调函数"""
        if event.name == "f12":  # 退出程序
            print("收到退出指令，程序即将退出...")
            keyboard.unhook_all()

            # 设置退出标志，让主线程结束
            self.should_exit = True
            # 按下 f12 程序无法退出：问题在于 keyboard.wait() 会阻塞主线程，导致 exit() 无法立即生效。 需要修改退出机制。
            # exit()

            # 弹出提示框，放在设置退出标志后面
            pyautogui.alert("程序即将退出", "提示")
        elif event.name == "f9":  # 暂停/继续
            self.is_running = not self.is_running
            status = "继续运行" if self.is_running else "暂停"
            print(f"程序已{status}")

            # 弹出提示框，放在状态改变后面
            if(not self.is_running):
                pyautogui.alert("程序已暂停，请先关闭此弹窗。按 F9 可继续", "提示") # 暂停时弹出提示框，继续时不弹出
            

    def _calculate_relative_position(self):
        """计算相对坐标位置"""
        x, y = self.click_position
        relative_x = x / self.screen_width
        relative_y = y / self.screen_height
        return relative_x, relative_y

    def _calculate_absolute_position(self):
        """计算绝对坐标位置"""
        relative_x, relative_y = self._calculate_relative_position()
        absolute_x = relative_x * self.screen_width
        absolute_y = relative_y * self.screen_height
        return absolute_x, absolute_y

    def _click_loop(self):
        """点击循环线程函数"""
        absolute_x, absolute_y = self._calculate_absolute_position()
        print(f"点击坐标: ({absolute_x:.0f}, {absolute_y:.0f})")

        while True:
            if self.is_running:
                # pyautogui.click(x=absolute_x, y=absolute_y, button="left")
                # 改为按 下 'f' 键
                pyautogui.press("f")
            time.sleep(self.click_interval)

    def _show_warning(self):
        """显示警告信息"""
        warning_msg = (
            "5秒后开始自动点击，请确保：\n"
            "1. 已切换到游戏界面\n"
            "2. 游戏窗口处于活动状态\n"
            "3. 点击位置正确设置\n\n"
            "控制键说明：\n"
            "F12 - 退出程序\n"
            "F9 - 暂停/继续"
        )
        pyautogui.alert(warning_msg, "原神跳过脚本")

    def _countdown(self, seconds=5):
        """倒计时函数"""
        print(f"等待 {seconds} 秒，请切换到游戏界面...")
        for i in range(seconds, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        print("开始执行!")

    def start(self, countdown_seconds=5):
        """
        启动脚本

        Args:
            countdown_seconds: 倒计时秒数
        """
        self.should_exit = False  # 退出标志
        try:
            # 显示警告和倒计时
            self._show_warning()
            self._countdown(countdown_seconds)

            # 启动点击线程
            click_thread = threading.Thread(target=self._click_loop)
            click_thread.daemon = True
            click_thread.start()

            print("脚本已启动，等待键盘事件...")

            # 保持主线程运行。按下 f12 程序无法退出：问题在于 keyboard.wait() 会阻塞主线程，导致 exit() 无法立即生效。需要修改退出机制。
            # keyboard.wait()
            while not self.should_exit:
                time.sleep(10)  # 主线程每 10 秒检查一次退出标志
            print("程序退出完成")

        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"程序运行出错: {e}")
        finally:
            keyboard.unhook_all()
            print("程序已退出")


def main():
    """主函数"""
    # 根据不同游戏设置点击位置
    game_positions = {
        "genshin": (1400, 780),  # 原神
        "zzz": (1500, 740),  # 绝区零
        "default": (1500, 740),  # 默认
    }

    # 选择游戏类型
    game_type = "zzz"  # 修改这里切换游戏

    # 创建并启动脚本
    script = GameSkipScript(
        click_position=game_positions.get(game_type, game_positions["default"]),
        click_interval=1,  # 点击间隔1秒
    )

    script.start(countdown_seconds=5)


if __name__ == "__main__":
    # 检查是否以管理员权限运行（在Windows上）
    try:
        import ctypes

        if ctypes.windll.shell32.IsUserAnAdmin():
            print("以管理员权限运行")
        else:
            print("警告：建议以管理员身份运行本程序")
    except:
        print("无法检测管理员权限（非Windows系统）")

    main()
