# PPT MCP 能力地图

本机 2026-10-14 通过 MCP `initialize` 和 `list_tools` 查询到 156 个工具。以下是接口能力，不表示每个工具都已在所有 Office 版本逐一测试。源项目：[ykuwai/ppt-mcp](https://github.com/ykuwai/ppt-mcp)。运行时重新查询工具及参数。

| 类别 | 可做什么 | 代表工具 |
|---|---|---|
| 文件与页面 | 新建、打开、另存、复制移动页面、分节、备注、指定目标文稿 | `ppt_open_presentation`, `ppt_copy_slide`, `ppt_set_slide_notes` |
| 文本与字体 | 文本与富文本格式、段落项目符号、查找替换、字体替换、排版检查 | `ppt_set_text`, `ppt_format_text_range`, `ppt_check_typography` |
| 对象与布局 | 形状、线条、连接器、坐标尺寸、层级、分组、对齐分布、合并形状 | `ppt_group_shapes`, `ppt_align_shapes`, `ppt_add_connector` |
| 原生曲线 | 自由路径、直线与曲线段、控制点、节点位置及编辑类型 | `ppt_build_freeform`, `ppt_set_node_position`, `ppt_set_segment_type` |
| 图像与 SVG | 插图、裁切、亮度对比、色键透明、SVG 图标、比例锁定、导出对象 | `ppt_add_picture`, `ppt_crop_picture`, `ppt_set_picture_format`, `ppt_add_svg_icon` |
| 数据与结构图 | 原生表格、合并拆分单元格、图表数据及坐标轴、SmartArt | `ppt_add_table`, `ppt_set_chart_data`, `ppt_modify_smartart` |
| 动画与转场 | 添加、列出、更新、删除动画；点击／同时／之后／对象点击触发；时长方向、强调、路径、退出、文本分段 | `ppt_add_animation`, `ppt_update_animation`, `ppt_set_slide_transition` |
| 主题与效果 | 主题色、默认字体、背景、阴影、柔化、反射、发光 | `ppt_set_theme_colors`, `ppt_set_shadow`, `ppt_set_soft_edge` |
| 媒体与放映 | 音视频插入、媒体设置、开始停止放映、翻页和状态 | `ppt_add_video`, `ppt_set_media_settings`, `ppt_slideshow_start` |
| 检查与导出 | 获取对象／页面信息、页面预览、图片、PDF、备注、属性 | `ppt_get_slide_preview`, `ppt_export_images`, `ppt_export_pdf` |

## 能力边界

- 能摆放图片、裁切和对对象加动画，不自带 GPT 生图，也不能自动把复杂位图精确拆成可编辑图元。
- 色键透明按颜色处理，不等于智能语义抠图。复杂透明边缘用适当图像编辑生成素材，再由 MCP 插入。
- 可以控制动画参数，但讲解顺序、对象分组与科学内容需作者设计并观察验证。
- 自由曲线是原生能力：`corner` 曲线可指定两控制点和终点；`BuildFreeform` 初始编辑类型有限，其他节点类型通过后续节点工具设置。不要声称 MCP 只能画直线。
- 当前清单没有专门的 CreateVideo 导出工具。若另用 PowerPoint 文档 API 导出动画视频，明确记录为原生 API 步骤，不冒称 MCP 工具。

本次直接验证过的常用路径包括连接、打开、主题设置、原生对象分组、动画、转场、另存和逐页图片导出。其他功能按需求做小范围验证。

SVG 导出补充：本机 `ppt_export_shape` 列出的格式为 PNG、JPG、GIF、BMP、WMF、EMF；不要把它说成直接支持 SVG 导出。本次另用 PowerPoint 原生文档 API Shape.Export(Filter=6) 导出 SVG，已检查不含 image 图元。该接口支持 Windows 2302 及以后版本，参考 Microsoft Learn 的 Shape.Export 文档。
