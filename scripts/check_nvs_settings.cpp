#include <iostream>
#include <string>
#include <vector>
#include <nvs_flash.h>
#include <esp_log.h>

// 简单的NVS读取工具
class NvsReader {
public:
    NvsReader() {
        // 初始化NVS
        esp_err_t ret = nvs_flash_init();
        if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
            ESP_ERROR_CHECK(nvs_flash_erase());
            ret = nvs_flash_init();
        }
        ESP_ERROR_CHECK(ret);
    }

    ~NvsReader() {
        nvs_flash_deinit();
    }

    void ReadNamespace(const std::string& ns_name) {
        nvs_handle_t handle;
        esp_err_t err = nvs_open(ns_name.c_str(), NVS_READONLY, &handle);
        if (err != ESP_OK) {
            std::cout << "无法打开命名空间: " << ns_name << " (错误: " << esp_err_to_name(err) << ")" << std::endl;
            return;
        }

        std::cout << "\n=== 命名空间: " << ns_name << " ===" << std::endl;

        // 读取字符串类型的键值对
        ReadStringKeys(handle, ns_name);
        
        // 读取整数类型的键值对
        ReadIntKeys(handle, ns_name);
        
        // 读取布尔类型的键值对
        ReadBoolKeys(handle, ns_name);

        nvs_close(handle);
    }

private:
    void ReadStringKeys(nvs_handle_t handle, const std::string& ns_name) {
        nvs_iterator_t it = nvs_entry_find("nvs", ns_name.c_str(), NVS_TYPE_STR);
        while (it != nullptr) {
            nvs_entry_info_t info;
            nvs_entry_info(it, &info);
            
            size_t length = 0;
            if (nvs_get_str(handle, info.key, nullptr, &length) == ESP_OK) {
                std::string value;
                value.resize(length);
                nvs_get_str(handle, info.key, value.data(), &length);
                while (!value.empty() && value.back() == '\0') {
                    value.pop_back();
                }
                std::cout << "  " << info.key << " (字符串): " << value << std::endl;
            }
            
            it = nvs_entry_next(it);
        }
    }

    void ReadIntKeys(nvs_handle_t handle, const std::string& ns_name) {
        nvs_iterator_t it = nvs_entry_find("nvs", ns_name.c_str(), NVS_TYPE_I32);
        while (it != nullptr) {
            nvs_entry_info_t info;
            nvs_entry_info(it, &info);
            
            int32_t value;
            if (nvs_get_i32(handle, info.key, &value) == ESP_OK) {
                std::cout << "  " << info.key << " (整数): " << value << std::endl;
            }
            
            it = nvs_entry_next(it);
        }
    }

    void ReadBoolKeys(nvs_handle_t handle, const std::string& ns_name) {
        nvs_iterator_t it = nvs_entry_find("nvs", ns_name.c_str(), NVS_TYPE_U8);
        while (it != nullptr) {
            nvs_entry_info_t info;
            nvs_entry_info(it, &info);
            
            uint8_t value;
            if (nvs_get_u8(handle, info.key, &value) == ESP_OK) {
                // 检查是否是布尔值（0或1）
                if (value == 0 || value == 1) {
                    std::cout << "  " << info.key << " (布尔): " << (value ? "true" : "false") << std::endl;
                } else {
                    std::cout << "  " << info.key << " (U8): " << (int)value << std::endl;
                }
            }
            
            it = nvs_entry_next(it);
        }
    }
};

int main() {
    std::cout << "NVS设置检查工具" << std::endl;
    std::cout << "==================" << std::endl;

    NvsReader reader;

    // 检查常见的命名空间
    std::vector<std::string> namespaces = {
        "websocket",
        "mcp", 
        "assets",
        "settings",
        "system",
        "wifi"
    };

    for (const auto& ns : namespaces) {
        reader.ReadNamespace(ns);
    }

    std::cout << "\n检查完成!" << std::endl;
    return 0;
}
