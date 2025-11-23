# -*- coding: utf-8 -*-
"""
原神/绝区零剧情跳过脚本

功能描述：
    自动化游戏剧情跳过工具，支持自动点击和按键模拟

使用方法：
    1. 建议以管理员身份运行以确保键盘监听功能正常
    2. 启动后切换到游戏窗口，确保游戏处于前台活动状态
    3. 使用热键控制脚本行为

热键说明：
    F12 - 退出程序
    F11 - 暂停/继续运行
    F10 - 开启/关闭剧情跳过功能
    F9  - 开启/关闭自动行走功能

依赖要求：
    pip install keyboard pyautogui

作者: wxm
版本: 1.0
适用游戏: 原神(Genshin Impact) / 绝区零(Zenless Zone Zero)
"""

"""
    程序结构设计：
    1. 主类 GameSkipScript：封装脚本的主要功能和状态。
    2. 多线程设计：使用独立线程处理键盘监听和点击循环。
    3. 热键注册线程：使用 keyboard 库注册热键并绑定回调。手动创建监听线程确实会让监听逻辑和回调函数都在新线程中执行 —— DeepSeek。
    4. 点击线程：根据状态变量决定是否发送点击或按键事件。手动创建点击线程处理点击循环。
    5. 状态管理：使用锁保护共享状态变量，确保线程安全。修改共享变量时需持有锁；只读时不持有锁以避免死锁。
"""

import keyboard
import pyautogui
import threading
import time


class GameSkipScript:
    def __init__(self, click_position=(1500, 740), click_interval=1, storyline_key="f", movement_key="w"):
        self.click_position = click_position
        self.click_interval = click_interval
        self.storyline_key = storyline_key
        self.movement_key = movement_key

        # 锁用于多线程共享变量的保护，修改共享变量时需持有锁
        self.state_lock = threading.Lock()

        # 状态标志。脚本的 3 个功能开关
        self.is_running = True
        self.start_storyline_key = False
        self.start_movement_key = False

        # 创建条件变量，用于线程间退出通知
        self.listener_thread_exit_event = threading.Event()
        self.click_thread_exit_event = threading.Event()
        
        # 屏幕尺寸（用于计算绝对坐标）
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"屏幕分辨率: {self.screen_width} x {self.screen_height}")

    # ---------- 热键注册与处理 ----------
    def _register_hotkeys(self):
        """注册热键，回调不带 event 参数"""
        keyboard.add_hotkey('f12', self._handle_exit)
        keyboard.add_hotkey('f11', self._handle_pause_toggle)
        keyboard.add_hotkey('f10', self._handle_storyline_toggle)
        keyboard.add_hotkey('f9',  self._handle_movement_toggle)
        print("热键已注册：F12 退出 / F11 暂停-继续 / F10 剧情键 / F9 行走键")

    def _listener_loop(self):
        """守护线程：注册热键并等待退出事件"""
        self._register_hotkeys()
        self.listener_thread_exit_event.wait()  # 阻塞等待退出事件
        keyboard.unhook_all()
        print("键盘监听线程已结束并卸载热键")

    def _handle_exit(self):
        """处理退出按键 (F12)"""
        with self.state_lock:
            self.listener_thread_exit_event.set()
            self.click_thread_exit_event.set()
        print("收到退出指令，准备退出...")
        pyautogui.alert("程序即将退出", "提示")

    def _handle_pause_toggle(self):
        """处理暂停/继续按键 (F11)"""
        with self.state_lock:
            if(self.is_running):
                self.is_running = False
                self.previous_state = (self.start_storyline_key, self.start_movement_key)
                self.start_storyline_key = False
                self.start_movement_key = False
            else:
                self.is_running = True
                self.start_storyline_key, self.start_movement_key = self.previous_state
        state = "继续" if self.is_running else "暂停"
        print(f"程序已{state}")
        if not self.is_running:
            pyautogui.alert("程序已暂停，按 F11 继续运行")

    def _handle_storyline_toggle(self):
        """处理剧情按键开关 (F10)"""
        with self.state_lock:
            self.start_storyline_key = not self.start_storyline_key
        state = "开启" if self.start_storyline_key else "关闭"
        print(f"剧情按键已{state}")
        if not self.start_storyline_key:
            pyautogui.alert("剧情按键已关闭, 按 F10 开启")

    def _handle_movement_toggle(self):
        """处理行走按键开关 (F9)"""
        with self.state_lock:
            self.start_movement_key = not self.start_movement_key
        state = "开启"  if self.start_movement_key else "关闭"
        print(f"行走按键已{state}") # 不弹窗，避免频繁打扰

    # ---------- 坐标计算 ----------
    def _calculate_relative_position(self):
        x, y = self.click_position
        return x / self.screen_width, y / self.screen_height

    def _calculate_absolute_position(self):
        rx, ry = self._calculate_relative_position()
        return int(rx * self.screen_width), int(ry * self.screen_height)

    # ---------- 点击 / 按键循环 ----------
    def _click_storyline_key(self):
        """发送剧情按键，单次按下并释放"""
        try:
            keyboard.press_and_release(self.storyline_key)
        except Exception as e:
            print(f"发送剧情按键出错: {e}")

    def _click_movement_key(self):
        """发送行走按键，需要保持按下状态。这是一个耗时操作，为了避免阻塞原线程，单独开启一个线程执行（但是后面还得 join，还是同步操作...）。"""
        try:
            click_movement_key_thread = threading.Thread(target=self._click_movement_key_thread)
            click_movement_key_thread.start()
            click_movement_key_thread.join(timeout=1)
        except Exception as e:
            print(f"发送行走按键出错: {e}")

    def _click_movement_key_thread(self):
        try:
            keyboard.press(self.movement_key)
            time.sleep(self.click_interval)
            keyboard.release(self.movement_key)
        except Exception as e:
            print(f"发送行走按键出错: {e}")

    def _click_loop(self):
        """点击循环：扁平化逻辑，使用 exit_event.wait 做超时与退出检测"""
        abs_x, abs_y = self._calculate_absolute_position()
        print(f"点击坐标: ({abs_x}, {abs_y})")
        # 只访问状态标志，不修改，无需持有锁（也避免了一直循环持有锁导致死锁）
        while not self.listener_thread_exit_event.is_set():
            if not self.is_running:
                wait_time = 1 # 避免频繁轮询
                time.sleep(wait_time)
                continue
            if self.start_storyline_key:
                self._click_storyline_key()
            if self.start_movement_key:
                # self._click_movement_key()
                self._click_movement_key_thread()
            time.sleep(self.click_interval)

    # ---------- UI / 启动流程 ----------
    def _show_warning(self):
        warning_msg = (
            "5秒后开始自动点击，请确保：\n"
            "1. 已切换到游戏界面\n"
            "2. 游戏窗口处于活动状态\n"
            "3. 点击位置正确设置\n\n"
            "控制键说明：\n"
            "F12 - 退出程序\n"
            "F11 - 暂停/继续\n"
            "F10 - 开启/关闭剧情按键\n"
            "F9  - 开启/关闭行走按键\n"
        )
        try:
            pyautogui.alert(warning_msg, "原神跳过脚本")
        except Exception:
            print("警告弹窗显示失败，继续运行。")

    def _show_countdown(self, seconds=5):
        print(f"等待 {seconds} 秒，请切换到游戏界面...")
        for i in range(seconds, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        print("开始执行!")

    def start(self, countdown_seconds=3):
        """启动点击线程并等待退出事件"""
        self._show_warning()
        self._show_countdown(countdown_seconds)

        # 启动键盘监听守护线程
        listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        listener_thread.start()
        print("键盘监听线程已启动（热键模式）")

        # 启动点击守护线程
        click_thread = threading.Thread(target=self._click_loop, daemon=True)
        click_thread.start()
        self._click_loop()
        print("脚本已启动，等待键盘事件（按 F12 退出）...")
        
        # 主线程阻塞等待退出事件，由 listener 或其它源触发
        self.exit_event.wait()
        print("收到退出事件，正在清理...")
        listener_thread.join(timeout=1)
        click_thread.join(timeout=2)

def main():
    game_positions = {
        "genshin": (1400, 780),
        "zzz": (1500, 740),
        "default": (1500, 740),
    }

    game_type = "zzz"
    click_interval = 0.2

    script = GameSkipScript(
        click_position=game_positions.get(game_type, game_positions["default"]),
        click_interval=click_interval,
    )
    script.start()


if __name__ == "__main__":
    # Windows 管理员检测（可选）
    try:
        import ctypes

        if ctypes.windll.shell32.IsUserAnAdmin():
            print("以管理员权限运行")
        else:
            print("建议以管理员权限运行以保证 keyboard 功能可用")
    except Exception:
        print("无法检测管理员权限")

    main()
