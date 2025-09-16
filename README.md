这是一个Alfred workflow，用于美化剪贴板中的截图和图像。

## 功能特性

### 支持的图片处理

1. **背景美化** - 为截图添加圆角和渐变背景
2. **撕裂边缘效果** - 为图像添加撕裂边缘特效
3. **白色背景** - 将透明背景图像转换为白色背景


#### 预览

> 建议浏览器使用黑暗模式！！！！

依次为：原始图片 $\rightarrow$  1️⃣ $\rightarrow$ 1️⃣+2️⃣ $\rightarrow$3️⃣$\rightarrow$3️⃣+1️⃣

<div align="center">
  <img src="https://ayyyyy.sbs/2025/09/581f7630e493b66f93e0845fcf740874.GIF" width="120" style="border:1px solid #ccc;"/>
  <img src="https://ayyyyy.sbs/2025/09/1e45b06731f829a1be58aa76e653854b.gif" width="120" style="border:1px solid #ccc;"/>
  <img src="https://ayyyyy.sbs/2025/09/a8b42d80d98bd36a944101875cd401d1.gif" width="120" style="border:1px solid #ccc;"/>
  <img src="https://ayyyyy.sbs/2025/09/07da54c0505f557e711e9dc622a80dc9.gif" width="120" style="border:1px solid #ccc;"/>
  <img src="https://ayyyyy.sbs/2025/09/766b0de4d89f5f58995cb491c331c34e.gif" width="120" style="border:1px solid #ccc;"/>
</div>


依次为：原始图片$\rightarrow$ 1️⃣ $\rightarrow$ 2️⃣ $\rightarrow$ 1️⃣+2️⃣

<div>
      <img src="https://ayyyyy.sbs/2025/09/8f21efd710b5bf5ae23e29a300eed042.png" width="200" style="border:1px solid #ccc;"/>
      <img src="https://ayyyyy.sbs/2025/09/d0f23138e20bec822d361287c5a9b19a.png" width="200" style="border:1px solid #ccc;"/>
      <img src="https://ayyyyy.sbs/2025/09/6d8e6bff369c79948affcdf598e9e6ca.png" width="200" style="border:1px solid #ccc;"/>
      <img src="https://ayyyyy.sbs/2025/09/5dbfe5df6dcf8a3165db87cb670e1443.png" width="200" style="border:1px solid #ccc;"/>
</div>

### 输入方式

支持从剪贴板获取图像：
- 使用截图工具截图后自动复制到剪贴板
- 直接在`Finder`中复制图像文件到剪贴板

支持通过Alfred universal actions处理文件：
- 在`Finder`中选取一个或多个图像文件，使用Alfred universal action快捷键唤起窗口，搜索本workflow命令，进行处理



## 使用方法

### Step 1: 设置环境变量

在Alfred的`Environment Variables`中添加以下变量：

- `PYTHON_PATHS`：Python可执行文件路径，多个路径用冒号分隔（例如：`/usr/local/bin/python3:/opt/homebrew/bin/python3`）

![环境变量设置](https://ayyyyy.sbs/2025/09/63b81e1dce7a0fe862d92f7644e12ed0.png)


### Step 2: 运行Workflow


在Alfred打开Workflow，可以看到每个图片处理选项有各自的关键字，例如：`图片处理：添加圆角和背景色`，那么就可以在Alfred中输入该关键字来运行对应的图片处理功能：
1. 使用keyword搜索功能，输入关键字即可快速找到对应的处理选项，只能处理剪贴板中的图片
2. 使用universal actions功能，可以处理选中的文件


![](https://ayyyyy.sbs/2025/09/9912a18c61c9fade61f5fad54fa65ff4.gif)