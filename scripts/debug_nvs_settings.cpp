#include "settings.h"
#include <iostream>
#include <vector>

/**
 * NVS设置调试工具
 * 这个工具可以添加到您的应用程序中来查看当前NVS中存储的设置值
 */

void DebugNvsSettings() {
    std::cout << "=== NVS设置调试信息 ===" << std::endl;
    
    // 检查websocket命名空间
    {
        Settings ws_settings("websocket", false);
        std::string url = ws_settings.GetString("url");
        std::string token = ws_settings.GetString("token");
        int version = ws_settings.GetInt("version");
        
        std::cout << "\n[websocket命名空间]" << std::endl;
        std::cout << "  url: " << (url.empty() ? "(未设置)" : url) << std::endl;
        std::cout << "  token: " << (token.empty() ? "(未设置)" : "***" + std::to_string(token.length()) + "字符***") << std::endl;
        std::cout << "  version: " << version << std::endl;
    }
    
    // 检查mcp命名空间
    {
        Settings mcp_settings("mcp", false);
        std::string token = mcp_settings.GetString("token");
        
        std::cout << "\n[mcp命名空间]" << std::endl;
        std::cout << "  token: " << (token.empty() ? "(未设置)" : "***" + std::to_string(token.length()) + "字符***") << std::endl;
    }
    
    // 检查assets命名空间
    {
        Settings assets_settings("assets", false);
        std::string download_url = assets_settings.GetString("download_url");
        
        std::cout << "\n[assets命名空间]" << std::endl;
        std::cout << "  download_url: " << (download_url.empty() ? "(未设置)" : download_url) << std::endl;
    }
    
    // 检查system命名空间
    {
        Settings system_settings("system", false);
        std::string device_name = system_settings.GetString("device_name");
        int volume = system_settings.GetInt("volume", -1);
        
        std::cout << "\n[system命名空间]" << std::endl;
        std::cout << "  device_name: " << (device_name.empty() ? "(未设置)" : device_name) << std::endl;
        std::cout << "  volume: " << (volume == -1 ? "(未设置)" : std::to_string(volume)) << std::endl;
    }
    
    // 检查wifi命名空间
    {
        Settings wifi_settings("wifi", false);
        std::string ssid = wifi_settings.GetString("ssid");
        std::string password = wifi_settings.GetString("password");
        
        std::cout << "\n[wifi命名空间]" << std::endl;
        std::cout << "  ssid: " << (ssid.empty() ? "(未设置)" : ssid) << std::endl;
        std::cout << "  password: " << (password.empty() ? "(未设置)" : "***" + std::to_string(password.length()) + "字符***") << std::endl;
    }
    
    std::cout << "\n=== 调试完成 ===" << std::endl;
}

// 使用示例：
// 在您的main函数或任何需要的地方调用 DebugNvsSettings();

/**
 * 设置NVS值的示例函数
 */
void SetNvsExampleValues() {
    std::cout << "=== 设置示例NVS值 ===" << std::endl;
    
    // 设置websocket配置
    {
        Settings ws_settings("websocket", true);
        ws_settings.SetString("url", "wss://example.com/websocket");
        ws_settings.SetString("token", "your-test-token-here");
        ws_settings.SetInt("version", 2);
        std::cout << "设置websocket配置完成" << std::endl;
    }
    
    // 设置mcp配置
    {
        Settings mcp_settings("mcp", true);
        mcp_settings.SetString("token", "mcp-test-token");
        std::cout << "设置mcp配置完成" << std::endl;
    }
    
    std::cout << "=== 设置完成 ===" << std::endl;
}

/**
 * 清除NVS值的示例函数
 */
void ClearNvsSettings() {
    std::cout << "=== 清除NVS设置 ===" << std::endl;
    
    std::vector<std::string> namespaces = {"websocket", "mcp", "assets"};
    
    for (const auto& ns : namespaces) {
        Settings settings(ns, true);
        settings.EraseAll();
        std::cout << "清除命名空间: " << ns << std::endl;
    }
    
    std::cout << "=== 清除完成 ===" << std::endl;
}

// 主函数示例（用于测试）
#ifdef DEBUG_NVS_TOOL
int main() {
    std::cout << "NVS调试工具" << std::endl;
    std::cout << "============" << std::endl;
    
    // 查看当前设置
    DebugNvsSettings();
    
    // 设置示例值（取消注释以启用）
    // SetNvsExampleValues();
    
    // 清除设置（取消注释以启用）
    // ClearNvsSettings();
    
    return 0;
}
#endif
