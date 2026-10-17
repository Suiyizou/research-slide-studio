# 历史生图原稿：优先设计参考

本库收录此前实际调用 `image_gen.imagegen` 生成的 **4 张总览原图和 7 张独立内容页原图**。原始 PNG 按原始字节保存，附当时使用的完整提示词；可追溯文件、尺寸、SHA-256 及后续采用关系记录在 [catalog.json](../assets/generated-reference-library/catalog.json)。

制作前先查看 [7 张内容页原图索引](../assets/generated-reference-library/content-contact-sheet.png)，按本页主题打开 1—3 张完整原图。这里的原图决定需要学习的图形细度、科学对象与阅读路径；[13 页可编辑样张](layout-library.md) 用于重建、文字锚点和组件复用。用户认可的目录与白底蓝横幅章节截图另见 [章节规范](research-navigation.md)。

## 独立内容页原图

| 编号 | 原始生图 | 重点参考 | 历史采用关系 | 完整提示词 |
|---|---|---|---|---|
| R01 | [研究意义：过程方案](../assets/generated-reference-library/originals/R01-significance-process.png) | 档案、验证反馈汇入估计器，再到执行与更新 | 探索过程式意义表达；最终意义页 L04 采用 O02 的三角构图。 | [R01.txt](../assets/generated-reference-library/prompts/R01.txt) |
| R02 | [研究不足：四问题汇合](../assets/generated-reference-library/originals/R02-research-gaps.png) | 四组具体机制对照与中心研究问题 | 历史设计方案；现行文献进展页参考 R06/R07。 | [R02.txt](../assets/generated-reference-library/prompts/R02.txt) |
| R03 | [残差结构与 A/B/C 消融](../assets/generated-reference-library/originals/R03-residual-ablation.png) | 预测与残差、ACF、频谱、信息增量对照 | 拆分并核对科学语义后形成 L08/L09，分别承担反馈解释与消融。 | [R03.txt](../assets/generated-reference-library/prompts/R03.txt) |
| R04 | [总体研究框架](../assets/generated-reference-library/originals/R04-overall-workflow.png) | 离线档案、当前任务、选择器、候选池、验证与反馈回环 | 对应 L12；重点参考完整信息流和不同模块的内部细节。 | [R04.txt](../assets/generated-reference-library/prompts/R04.txt) |
| R05 | [总结：过程方案](../assets/generated-reference-library/originals/R05-synthesis-process.png) | 信息证据汇合、实验决策、贡献与下一步 | 总结的过程式备选；最终 L13 的证据汇合构图来自 O03 第 6 格。 | [R05.txt](../assets/generated-reference-library/prompts/R05.txt) |
| R06 | [文献进展：五篇机制](../assets/generated-reference-library/originals/R06-literature-progress.png) | 五篇工作的输入、具体方法、输出、验证与研究空间 | 对应 L05，采用原图构图后精修为可编辑对象。 | [R06.txt](../assets/generated-reference-library/prompts/R06.txt) |
| R07 | [搜索闭环与推进空间](../assets/generated-reference-library/originals/R07-search-and-opportunities.png) | 已有搜索与自动化闭环、拟验证增量、总成本与收益 | 对应 L06，采用原图构图后精修为可编辑对象。 | [R07.txt](../assets/generated-reference-library/prompts/R07.txt) |

R06/R07 优先用于文献综述和研究定位：逐篇画清输入、方法、输出与已有验证，再指明可推进的具体环节。R04 用于多源输入和研究闭环；R03 用于反馈结构与受控消融；R01/R05 提供过程式意义与总结的不同设计路径。

## 四套总览原图

查看 [四套总览索引](../assets/generated-reference-library/overview-contact-sheet.png)。每张总览含六格代表页，小格的采用关系与单页精修分别记录，不能把六格总览当作一张内容页。

| 编号 | 原始生图 | 历史采用关系 | 完整提示词 |
|---|---|---|---|
| O01 | [总览方案 A](../assets/generated-reference-library/originals/O01-overview-A.png) | 第 1 格的研究背景构图演化为 L03。 | [O01.txt](../assets/generated-reference-library/prompts/O01.txt) |
| O02 | [总览方案 B](../assets/generated-reference-library/originals/O02-overview-B.png) | 第 2 格的三角关系构图演化为 L04。 | [O02.txt](../assets/generated-reference-library/prompts/O02.txt) |
| O03 | [总览方案 C](../assets/generated-reference-library/originals/O03-overview-C.png) | 第 6 格的证据汇合构图演化为 L13。 | [O03.txt](../assets/generated-reference-library/prompts/O03.txt) |
| O04 | [总览方案 D](../assets/generated-reference-library/originals/O04-overview-D.png) | 第 5 格结合 R04 的独立总流程参考，形成 L12。 | [O04.txt](../assets/generated-reference-library/prompts/O04.txt) |

四套保留真实历史样貌，配色较接近；学习其中构图与图元细节。新任务的四套总览仍在配色、关系形式和细节上明显区分。

## 接手时直接执行

1. 先选与当前页论证任务相符的原图，实际查看全尺寸，写出要继承的对象清单、层级、连接方向和强调方式。跨页组合构图，同章统一字体、线宽、语义配色与完成度。
2. 将对应提示词改写为当前课题的内容卡，明确具体输入、方法对象、输出与本页问题。提示词提到的附图需作为实际输入提供，并按当前语言核对标签。
3. 新稿继续生成四套总览，并为 `ceil(最终总页数 × 0.5)` 个不同页面生成独立参考。历史图库帮助设计新参考；不计作新任务已经调用的生图数量。同一课题的局部修订按已确认参考继续制作。
4. 选定当次参考后逐对象测量并一比一重建 SVG，配置独立文字层，再与 PPT 实际渲染对照。原稿中的具体模型、公式、示意曲线和文献结论按当前来源核对；设计方案与实验结果在成稿中准确标注。
5. 密集散点合并为矢量组、符号实例或复合路径，保留分布与颜色。原始生成 PNG 保留为对照，不粘入成稿充当科研图。可编辑样张与本次参考几何冲突时，以本次选定参考为准调整图元。

总体流程讲模块关系和反馈回路；总结用证据汇合、贡献及下一步收束。同一套精细图元服务不同的论证任务，避免连续复用一张完整构图。
