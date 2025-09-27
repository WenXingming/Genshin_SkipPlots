
/*
    Tips:
    1.目的：本脚本是为了通过自动点击鼠标（或按键盘），跳过原神剧情
    2.使用：以管理员身份运行本程序！
    【cmd 以管理员身份运行，即打开管理员powershell，切换目录（cd）到本目录（因为似乎相对路径是相对于终端的相对路径）】

    https://chatgpt.com/share/fed720d5-a278-4764-99a5-644373ab0098
*/

#include <windows.h>
#include <iostream>
#include <thread>
#include <atomic>

// 定义一个全局变量来控制程序的运行状态
std::atomic<bool> is_program_running(true);


// 计算相对坐标（从我的电脑得到）
const double relative_x = 1394.0 / 1920.0;
const double relative_y = 784.0 / 1080.0;
// 获取屏幕分辨率
int screenWidth = GetSystemMetrics(SM_CXSCREEN);
int screenHeight = GetSystemMetrics(SM_CYSCREEN);
// 计算绝对坐标
int solute_x = static_cast<int>(relative_x * screenWidth);
int solute_y = static_cast<int>(relative_y * screenHeight);

// 模拟按键按下：
//这段代码通过构造和发送一个INPUT结构体来模拟按键按下的操作。它使用了Windows API中的SendInput函数，将输入事件发送到系统，从而模拟了按键操作。
void pressKey(WORD key) {
    INPUT ip;
    ip.type = INPUT_KEYBOARD;
    ip.ki.wScan = 0;
    ip.ki.time = 0;
    ip.ki.dwExtraInfo = 0;
    ip.ki.wVk = key;
    ip.ki.dwFlags = 0; // 0 for key press
    SendInput(1, &ip, sizeof(INPUT));
}

// 模拟按键释放
void releaseKey(WORD key) {
    INPUT ip;
    ip.type = INPUT_KEYBOARD;
    ip.ki.wScan = 0;
    ip.ki.time = 0;
    ip.ki.dwExtraInfo = 0;
    ip.ki.wVk = key;
    ip.ki.dwFlags = KEYEVENTF_KEYUP;
    SendInput(1, &ip, sizeof(INPUT));
}

// 模拟按键点击
void pressAndReleaseKey(WORD key) {
    pressKey(key);
    Sleep(50); // 模拟按键按下的时间
    releaseKey(key);
}

// 点击循环函数
void clickLoop() {
    while (true) {
        if (is_program_running.load()) {
            // pressAndReleaseKey(static_cast<WORD>('F')); // 模拟鼠标左键点击f
            // 模拟鼠标左键点击
            SetCursorPos(solute_x, solute_y);
            mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
            Sleep(10); // 模拟鼠标按下的时间
            mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
        }
        Sleep(1000); // 降低 CPU 占用率
    }
}

// 键盘监听函数
void keyboardListener() {
    while (true) {
        if (GetAsyncKeyState(VK_F12) & 0x8000) {
            is_program_running.store(false);
            std::cout << "程序已停止" << std::endl;
            exit(0); // 立即退出程序
        }
        if (GetAsyncKeyState(VK_F9) & 0x8000) {
            is_program_running.store(!is_program_running.load());
            if (is_program_running.load()) {
                std::cout << "程序继续运行中" << std::endl;
            } else {
                std::cout << "程序已暂停" << std::endl;
            }
            Sleep(500); // 防止按键被多次识别
        }
        Sleep(100); // 降低 CPU 占用率
    }
}

int main() {
    // std::cout << "Wait for 5 seconds, please switch to the game screen..." << std::endl; 
    SetConsoleOutputCP(CP_UTF8); // 设置控制台输出代码页为 UTF-8
    std::cout << "等待 5 秒, 请快速切换到游戏界面..." << std::endl;
    MessageBoxW(NULL, L"5 秒后控制外设, 请快速切换到原神游戏界面...（按下 F12 键退出程序，按下 F9 键暂停/继续程序）", L"提示", MB_OK);
    Sleep(5000);

    // 启动点击循环的线程。为什么使用detach？
    // 1.后台运行：分离线程后，主线程和分离线程可以独立运行，分离线程可以在后台执行长时间运行的任务，而主线程可以继续进行其他工作。
    // 2.资源管理：如果不需要等待线程完成任务（即不需要调用join），分离线程可以避免阻塞主线程。
    std::thread click_thread(clickLoop);
    click_thread.detach();

    // 启动键盘监听的线程
    std::thread listener_thread(keyboardListener);
    listener_thread.join();
    
    getchar();
    return 0;
}
