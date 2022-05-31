# MyHook
本人自用，windows窗口操作用，包括 窗口置顶、隐藏窗口、窗口全屏、锁定鼠标到窗口、修改快捷键、运行控制台指令等

# how to run
1. 下载本仓库
2. 在vbs文件内配置你的python路径
3. 安装所需python包
4. additional - 你可以自定义按键绑定（在MyHook._init_），目前我用的绑定方案是：
```
key Mapping{
  F3         -> 隐藏当前窗口/显示窗口　　　　　　　　　, 不保留按键, 
  F4         -> 隐藏当前窗口/显示窗口　　　　　　　　　, 保留按键, 
  Pause      -> 当前窗口置顶/取消置顶　　　　　　　　　, 不保留按键, 
  F5         -> 当前窗口全屏/取消全屏　　　　　　　　　, 保留按键, 
  F6         -> 锁定鼠标到当前窗口/解锁鼠标　　　　　　, 保留按键, 
  Snapshot   -> 还原窗口，退出程序　　　　　　　　　　　, 保留按键, 
  O          -> 运行command命令　　　　　　　　　, 不保留按键, [cp -rf someFile1 someFile2]
  P          -> 运行command命令　　　　　　　　　, 不保留按键, [cp -rf someFile2 someFile1]
}
```
