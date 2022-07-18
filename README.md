# app_performance
perfdog替代品
app性能测试
appcpu测试
appmemory测试
内存cpu测试可能不如perfdog准确但是有参考价值，perfdog是直接通过厂商的api接口约定的获取到这些数据

开发目的：简单，方便，实时，可视化的获取app性能。
优势：
1.支持服务与设备在同一局域网内使用，同一局域网内可直接输入设备adb host port即可使用 
2.支持服务与设备在不同网域内使用，不同局域网下载客户端工具并运行后，输入adb在局域网中的host port即可使用

