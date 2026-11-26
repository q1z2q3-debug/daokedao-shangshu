# 道可道之尚书 · Android 壳

- 入口：`app/src/main/assets/index.html`（由站点 `docs/book-full.html` 全站阅读版复制，1.3 MB 自包含：58 篇正文、58 幅义理图内联 SVG，无需联网）。
- 包名 `com.runze.daokedaoshangshu`，应用名「道可道之尚书」，minSdk 21，compileSdk 35。
- 图标 `assets/icon/shangshu-icon-master.png`（1024×1024，暖纸底、墨色简尺、三枚刻度、赭红方印）；`dist/icon-shangshu.png` 为 512 版。
- 已生成五档 `mipmap-*/ic_launcher.png` 与 `ic_launcher_foreground.png`，并有 `mipmap-anydpi-v26/ic_launcher.xml`、`ic_launcher_round.xml`（自适应 / 圆形图标，背景 `#F5E5C8`）。

## 构建

本机需 JDK17 与 Android SDK：

```bash
sanjiu-apk build --dir dist/apk-shangshu --jdk <JDK17> --sdk <ANDROID_SDK>
```

或 debug 直出（自动签名，可直接安装）：

```bash
cd dist/apk-shangshu && ./gradlew assembleDebug
# app/build/outputs/apk/debug/app-debug.apk
```

## CI

`.github/workflows/apk.yml`：push 触发，装 JDK17＋SDK 35，出 debug APK 供下载（Actions → build-apk → Artifacts）。
