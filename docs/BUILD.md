# 构建与无手机验证

递归克隆本仓库以取得固定子模块：`git clone --recurse-submodules <本仓库地址>`。已克隆时运行 `git submodule update --init --recursive`。

需要 Python 3.10+、JDK 17、Android SDK。当前外壳要求 compileSdk 37（SDK 包名 `platforms;android-37.0`；命令行工具 22.0）、CMake 3.22.1，Gradle Wrapper 使用 9.4.1；不要使用旧版点到的 Gradle 8.11.1 脚本。

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
python3 scripts/fetch_dependencies.py
.venv/bin/python -m unittest discover -s tests -v
# 设置 JAVA_HOME 和 ANDROID_HOME 后：
sh scripts/build.sh
```

产物为 `artifacts/diandao-experimental-debug.apk`，仅用于开发测试。脚本覆盖子模块被忽略的 local.properties，指定 arm64-v8a；正式发布需单独配置稳定签名，不能把私钥提交。

无手机可以做资源协议校验、真实 OCR 样本识别、状态分支模拟以及 APK 构建。这些都不能证明淘宝实际到账，也不能证明虚拟屏幕/锁屏兼容性。手机截图应放在 `.cache/` 或本地外部目录，禁止推送含账号信息的截图和日志。

用已有图片检查某个节点（只识别，不发送任何手机操作）：

```sh
.venv/bin/python scripts/check_image.py /absolute/path/to/image.png CoinPage
```

构建使用的外壳子模块、引擎版本和 OCR 下载校验值均已固定。更新它们必须重新验证。
