# bio-extract  文献爬取器
本工具原理是本地安装谷歌浏览器后使用selenium控制浏览器访问谷歌学术，获取文献下载链接后自动下载
推荐环境 windows10 + 子系统（WSL Ubuntu 18.04）
子系统在win10的应用商店可以直接安装
#### 使用步骤

git clone https://github.com/yangguang8112/bio-extract.git

###### 安装所需要的环境
```shell
cd bio-extract
pip install -r requirements.txt
```
下载谷歌浏览器驱动chromedriver.exe http://npm.taobao.org/mirrors/chromedriver/ 根据自己系统中的谷歌浏览器版本选择驱动
并修改config.ini中Chrome的配置参数
```shell
[Chrome]
webdriver_path = /mnt/c/Users/yangguang/Downloads/chromedriver_win32/chromedriver.exe
web_user_data = C:\Users\yangguang\Desktop\temp\Chrome\User Data
```
如果你的机器已经可以访问谷歌，不用设置User Data；否则，推荐使用ghelper浏览器插件，百度下载安装，自己的谷歌浏览器能成功访问谷歌后，将谷歌浏览器里的User Data目录复制出来（为了不影响本身浏览器的运行），然后将复制的目录路径改到上述配置文件中即可。

###### 运行爬虫
退出脚本目录，另外新建一个工作目录（workdir）
```shell
cd <workdir>
# 初始化数据库，在新的工作目录一定要做，且只做一次
python <script_dir>/db.py init
# 开始运行爬虫脚本
python <script_dir>/webdriver_scholar/handle.py --keys <keywords_file> --maxpage 20
```
其中<script_dir>为第一步中的脚本目录
可以从 http://60.205.203.207:8081/instance/ 下载已有paper.sqlit 放到workdir这样可以排除数据库中已有文献

###### 注意事项
1.弹出谷歌浏览器如果不是最大化需要手动点选最大化；
2.开始运行后会弹出谷歌浏览器，只有当谷歌学术搜索出现人机验证的时候需要去完成验证以外其他时候都不需要手动操作；
3.我的开发环境是Windows10+WSL(Ubuntu 18.04)，没有测试过完全在Windows10环境下，欢迎debug；
4.