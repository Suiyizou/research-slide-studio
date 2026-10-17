# 科研版式库：按内容选择样张

设计先查看 [历史生图原稿与提示词](generated-reference-library.md)，本库提供原生对象和文字锚点，辅助完成矢量重建。以下预览均为 PPT 导出画面，原始生图单独保存在原稿库。

再查看 [13 页缩略图索引](../assets/research-layout-library/contact-sheet.png)，再按下表打开对应大图和 [可编辑 PPTX](../assets/research-layout-library/library.pptx)。[catalog.json](../assets/research-layout-library/catalog.json) 记录版式编号、PPT 页码、适用内容与保留图元。

| 编号 | 页面类型 | 构图形式 | 适用内容 | 大图 |
|---|---|---|---|---|
| L01 | 主线目录 | 编号节点与章节递进 | 交代全稿逻辑、各章问题和本次重点 | [预览](../assets/research-layout-library/previews/01.png) |
| L02 | 章节过渡 | 白底蓝横幅与导航 | 进入主要章节或新的研究问题 | [预览](../assets/research-layout-library/previews/02.png) |
| L03 | 研究背景 | 任务—方法—应用约束 | 解释研究需求从何而来 | [预览](../assets/research-layout-library/previews/03.png) |
| L04 | 研究意义 | 三角关系与中心汇合 | 呈现多个目标的联系和权衡 | [预览](../assets/research-layout-library/previews/04.png) |
| L05 | 多文献机制 | 不等宽多面板与方法小图 | 讲清多篇工作各自的输入、方法、输出和验证 | [预览](../assets/research-layout-library/previews/05.png) |
| L06 | 研究定位 | 已有闭环与拟验证增量 | 从已有系统能力收敛到具体研究空间 | [预览](../assets/research-layout-library/previews/06.png) |
| L07 | 研究问题与基线 | 历史训练—估计器—候选输出 | 区分离线训练、新任务输入与输出 | [预览](../assets/research-layout-library/previews/07.png) |
| L08 | 反馈结构对照 | 预测产物与成组诊断图 | 解释同一整体指标下的结构差异 | [预览](../assets/research-layout-library/previews/08.png) |
| L09 | 消融对照 | A/B/C 递进与新增信息强调 | 隔离某个新增模块或信息的作用 | [预览](../assets/research-layout-library/previews/09.png) |
| L10 | 预算搜索 | 条件分支与反馈回环 | 解释迭代策略、预算和停止条件 | [预览](../assets/research-layout-library/previews/10.png) |
| L11 | 智能体工具流程 | 调度层—工具层—产物 | 说明智能体和确定性工具的分工 | [预览](../assets/research-layout-library/previews/11.png) |
| L12 | 总体研究框架 | 多源输入与完整方法闭环 | 把各研究问题放回整体模块位置 | [预览](../assets/research-layout-library/previews/12.png) |
| L13 | 总结与下一步 | 证据汇合与贡献收束 | 收束预期或已验证贡献并说明实施顺序 | [预览](../assets/research-layout-library/previews/13.png) |

## 接手时怎样用

1. 按本页承担的论证任务选型。目录与章节页参考 L01/L02；说明意义时参考 L04；文献机制参考 L05/L06；研究问题与对照参考 L07—L09；搜索和工具流程参考 L10/L11；总框架与总结分别参考 L12/L13。
2. 先看缩略图，再看选中样张的大图，检查必需对象和信息容量。一个章节选相近的图形细度，不把同一布局连续复制到不同主题。
3. 从 library.pptx 复制整页或语义对象，保留字体、锚点、线宽、配色与可编辑文字；根据当前内容替换、增减和重新连接。样张中的模型、数据、论文和研究问题按当前课题更新。
4. 新稿仍执行四套总览和约 50% 逐页生图。样张帮助写清提示词、选择关系形式和复用矢量图元；选定的新参考图决定本页最终构图。库内预览图用于浏览，最终页面使用可编辑图形与文字。
5. 章节页复制 L02 后更新章标题、引导问题和导航状态。文献页保留每篇工作的输入—方法—输出—验证信息密度。L12 负责整体模块位置，L13 负责证据、意义与下一步，讲述任务分别安排。

## 库内页码

L01—L13 对应 library.pptx 的第 1—13 页。样张保留原稿的页面文字和原页码，catalog 中另存 source_slide，方便回查。用于新稿时按新页序重编号。13 页是版式样本数量，成稿页数随研究内容安排。

## 结构与渲染

13 页均由已认可原稿直接保留原生对象，已导出逐页 PowerPoint 画面并与源页比较。复制后的图形和文字保持可编辑。各页 native_shapes、native_connectors 与图片数量见 catalog，图片数均为 0。

样张副本已定向解除生成器写入的 noGrp 分组锁，便于后续选取对象后分组复用；保留其余属性与源稿几何。
