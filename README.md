基于Python实现的以游客身份拉取tiktok直播视频流，并切分成自定义时长的片段保存到本地


# 注意事项
1. 需要在脚本执行的操作系统里提前安装好 `ffmpeg`。
2. 每次拉流之前先随机产生一个匿名cookie。
3. 拉流的 HLS 地址是从直播页面中提取出来的，位于 `script` 标签内。

# donate

如果该项目对您有帮助，欢迎微信打赏

<img src="./img/donate.jpg" width="33.3%" />

如果对上述技术感兴趣，可以加WX `sh-moranliunian` 进行技术交流～