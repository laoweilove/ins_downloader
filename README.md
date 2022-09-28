# ins_downloader
 download instagram pics and videos by username  
通过用户名下载该用户全部图片和视频

## packages
requests  
pyaria2

## 用法
- 需配合aria2使用，默认是6800端口，无密钥，如果aria2配置不同可以在代码中进行配置
- `pip install -r requirements.txt` 来安装所需包
- `python3 newins.py` 来运行程序
- 输入你心仪的女神的用户名
- 开始使用aria2下载

## 2022.9.28 更新
使用httpx 替换requests  
使用loger替换print输出  
使用yaml进行配置  
增加tqdm进度条  

