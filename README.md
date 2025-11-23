# SkipPlots_Script

## Introduction

本脚本用于自动跳过《原神》游戏中的剧情动画和对话，以及自动行走（移动）以提升游戏体验。理论上来说也支持其他米哈游的游戏，但只在《原神》上进行了测试。

## Prerequisites

- Operating System: Windows 10/11
- Python 3.8 or higher

## Installation

1. **Step 1: Clone the Repository**

   ```bash
   git clone https://github.com/WenXingming/Genshin_SkipPlots.git
   cd Genshin_SkipPlots
   ```

2. **Step 2: Install Required Packages**
   You can use python directly, or create a conda virtual environment with python 3.8+. Then install the required packages using pip:

   ```bash
   # Create conda environment
   # conda create -n genshin_skip_plots python=3.8
   # conda activate genshin_skip_plots
   pip install keyboard
   pip install pyautogui
   ```

## Usage

Run the script using Python (if unused, you may run it with administrator privileges):

```bash
# conda activate genshin_skip_plots
python SkipPlots_Script.py
```

## Reference architecture diagram

函数调用流程图（DeepSeek 生成）：

```mermaid
flowchart TD
    A[main] --> B[GameSkipScript.__init__]
    A --> C[script.start]
    
    B --> B1[初始化状态标志]
    B --> B2[创建线程锁和退出事件]
    B --> B3[获取屏幕尺寸]
    
    C --> C1[_show_warning]
    C --> C2[_show_countdown]
    C --> C3[启动监听线程]
    C --> C4[_click_loop]
    
    C3 --> D1[_listener_loop]
    D1 --> D2[_register_hotkeys]
    D2 --> D3[注册所有热键回调]
    
    D3 --> E1[_handle_exit]
    D3 --> E2[_handle_pause_toggle]
    D3 --> E3[_handle_storyline_toggle]
    D3 --> E4[_handle_movement_toggle]
    
    C4 --> F1[_calculate_absolute_position]
    F1 --> F2[_calculate_relative_position]
    
    C4 --> F3[状态检查循环]
    F3 --> F4[_click_storyline_key]
    F3 --> F5[_click_movement_key_thread]
    
    F4 --> F6[keyboard.press_and_release]
    F5 --> F7[keyboard.press]
    F5 --> F8[keyboard.release]
    
    E1 --> G1[设置退出事件]
    E1 --> G2[显示退出提示]
    
    E2 --> H1[切换运行状态]
    E3 --> H2[切换剧情按键状态]
    E4 --> H3[切换行走按键状态]
    
    style A fill:#4CAF50,color:white
    style B fill:#2196F3,color:white
    style C fill:#2196F3,color:white
    style D2 fill:#FF9800,color:white
    style E1 fill:#F44336,color:white
    style E2 fill:#F44336,color:white
    style E3 fill:#F44336,color:white
    style E4 fill:#F44336,color:white
    style C4 fill:#9C27B0,color:white
```

程序设计架构图（Google Gemini 生成）：

```mermaid
classDiagram
    class GameSkipScript {
        -click_position : tuple
        -click_interval : float
        -storyline_key : str
        -movement_key : str
        -state_lock : threading.Lock
        -is_running : bool
        -start_storyline_key : bool
        -start_movement_key : bool
        -listener_thread_exit_event : threading.Event
        -click_thread_exit_event : threading.Event
        +__init__(...)
        +_register_hotkeys()
        +_listener_loop()
        +_handle_exit()
        +_handle_pause_toggle()
        +_handle_storyline_toggle()
        +_handle_movement_toggle()
        +_click_loop()
        +_click_storyline_key()
        +_click_movement_key_thread()
        +start()
    }

    class MainThread {
        +main()
        +start()
        +Wait for Exit Event
    }

    class ListenerThread {
        +_listener_loop()
        +keyboard.add_hotkey()
        +Wait for Exit Event
    }

    class ClickThread {
        +_click_loop()
        +Check is_running
        +Check start_storyline_key
        +Check start_movement_key
    }

    MainThread --> GameSkipScript : Instantiates
    MainThread --> ListenerThread : Spawns (Daemon)
    MainThread --> ClickThread : Spawns (Daemon)

    ListenerThread ..> GameSkipScript : Modifies State (via Hotkeys)
    ClickThread ..> GameSkipScript : Reads State

    note for ListenerThread "Listens for F9, F10, F11, F12\nUpdates flags safely using state_lock"
    note for ClickThread "Loop while not exit_event\nExecutes actions based on flags"
```

## License
