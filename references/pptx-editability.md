# PPT 内对象与文字可编辑：最终交付契约

验收对象是用户打开的最终 PPTX。SVG 源文件中的 `<text>`、`<g>`、`path` 可编辑，不代表把 SVG 插入 PowerPoint 后内部文字和图形已成为原生对象。`addImage({path: 'whole-slide.svg'})` 只插入一张图片；附上 labels.json 也不会自动生成文本框。

## 从图源到真实对象

1. 由同一份几何来源输出 SVG 和 PowerPoint 原生形状、自由曲线、连接线及语义组。每个主体模块、局部小图、图例与箭头可单独选择和移动；组内对象可继续编辑。
2. 所有标题、段落、图内短标签、坐标标签和图例文字落为 PowerPoint 原生文本框或原生表格/图表文字。标签层逐项实际生成，不能只保存 JSON；也不把文字转轮廓、截图或藏在 SVG 中。
3. 重复散点、细密纹理按语义或颜色合并为原生组/复合自由曲线。确需独立 SVG 的局部密集图元仅限无字的局部细节，单独可选；在清单登记 `vector_detail`，轴、图例和标签仍在原生层。整页、主体流程或完整带字面板不能登记为密集细节。
4. 保留图源中的结构与视觉层次：细线、浅填色、渐变、曲线、子模块、图例和局部放大可以由矢量实现。遇到转换问题，修复图元转换或重绘该局部；不把全页压成图片，也不为便于转换删掉关键对象。

## 组件必须能改内容与布局

视觉保真、原生文字、组件可调同时验收，不让用户在“视觉优先”和“可编辑优先”之间替制作方法作取舍。用户主动强调其中一项时，保留其他已明确要求；只有用户明确指定某部分保留图片时才按其范围处理，并如实标识该部分的编辑能力。单个 SVG 文件可以保留为图源，插入后的单张 SVG 图片不等于原生组件。

组件是一次合理编辑所涉及的对象集合，按两级组织：父组用于整体移动，组内的容器、分隔线、子图和文字可分别修改。以 UML 类卡为例：

```text
person_card（PPT 原生组）
  body / header_fill / compartment_lines（原生形状与线）
  class_name / attributes / operations（原生文字）
stereotype_tag（独立组：底框 + 原生标签）
constraint_note（独立组：折角外形 + 原生文字）
relation_edges（独立连接：source / target / 两端锚点）
```

- 每个可见边框、标签和箭头只有一个归属。页面背景不进入组件裁片，跨组件箭头不烘焙进任一节点；组内局部线与跨组关系线分开管理。不能出现“旧箭头在 SVG 里，新箭头在上面”的双重表示。
- 组件的宽高、文本区内边距、分隔线和连接锚点由同一几何来源维护。记录父组及子对象 ID，用局部坐标定位文字；整组只施加一次页面变换。文字变长时调整文本区、容器及邻近空间，不把布局锁在一张去字图里。
- 标准 PPT 不自动理解任意自定义图的排版关系。能绑定的连接器绑定到节点；自由曲线记录端点依赖，调整组件后重算或重接。承诺的是可以实际修改和重新排版，不虚称所有修改都会自动重排。

## 先做一页，再批量

选一页对象较丰富、含跨组件连线的正文完成端到端样页：参考图 → 按语义重绘图形与独立文字 → PPTX → PowerPoint 实际渲染。在工作副本完成以下变更，交付文件保留正式内容：

1. 将一个图内标签改为约两倍长度或增加一行属性；实际编辑文字，不能只改标题。
2. 拉宽或增高所属容器，调整分隔线与文字区，检查边框、字号和其他标签仍清楚。
3. 整体移动该组件；组内文字与图形一起移动，再单独移动一处文字。修改线色并更新外部连接端点，确认没有截断的旧线或重复箭头。
4. 在副本删除该组件，检查原位置是否残留文字、边框、底色补丁或半条连线；关系线按端点依赖更新或删除。恢复组件后保存、重新打开、渲染检查。

在 `checks/editability-pilot.md` 记录实际文件、页码、对象名称、操作前后截图与结果。通过后再批量制作；短标签可替换、对象数量很多、截图看似相同，均不能替代以上变更测试。更新制作方式后须重新验证样页。

## 清单与检查

`design-plan.json` 每个生图页保留 `labels`，增加 `objects`、`pptx_comparison`、`pptx_overlay`；后两项必须包含最终 PPT 的实际渲染，与已有“参考/SVG”对照区分。

```json
{
  "slide": 8,
  "labels": "labels/08.json",
  "objects": "objects/08.json",
  "pptx_comparison": "checks/08-reference-svg-ppt.png",
  "pptx_overlay": "checks/08-svg-ppt-overlay.png"
}
```

文字层为 `{"labels": [{"text": "任务特征", "x": 80, "y": 130}]}`。对象映射记录语义 ID、类型、SVG ID 与实际 PPT 形状名称；不要求密集散点逐点映射。

```json
{"objects": [
  {"id": "feature_label", "kind": "text", "svg_ids": ["feature_label"], "pptx_names": ["feature_label"]},
  {"id": "model_forest", "kind": "group", "svg_ids": ["model_forest"], "pptx_names": ["model_forest"]},
  {"id": "feedback", "kind": "connector", "svg_ids": ["feedback"], "pptx_names": ["feedback"]}
]}
```

用户封面、真实照片、来源图按形状名称登记在该页 `allowed_pictures`，写 `role`（`user_cover`、`photo`、`source_image`）和具体 `reason`；局部无字矢量细节用 `vector_detail`，还须填写 `detail_kind`：`dense_scatter`、`heatmap_cells`、`repeated_ticks` 或 `texture`，写明所属子图及合并原因。主体卡片、注释框、类图、节点、完整子图或流程不属于这些类型，即使面积小、无字、路径很多也要重建原生组件。此名单记录素材真实用途，不根据“凡是 SVG 就登记为细节”的逻辑自动生成。

预期标签与组件清单先从核对过的内容卡和参考图建立，再与最终 PPT 实际对象对照。不能只从已经生成的 PPT 导出文字和图片名单，然后用这份名单证明内容完整或编辑性达标；漏掉的内容也会被这样的自检一同漏掉。结构通过后仍检查实际图形是否符合所报角色。

最终运行：

```text
python scripts/audit_design.py design-plan.json --pptx final.pptx
python scripts/audit_pptx.py final.pptx --plan design-plan.json --require-object-map --output checks/pptx-audit.json
```

检查会读取最终 PPT 的真实对象、SVG 媒体、文字与标签映射，拒绝整页 SVG、藏在 SVG 中的文字、缺失原生标签及把图片冒充主体对象。只统计形状数量、只检查 SVG 无位图、只验证有 labels.json，都不足以完成验收。`--inventory` 仅供盘点，不能作为通过凭据。

最后实际查看三方对照和编辑测试。脚本负责发现结构性失败，视觉检查负责构图、缺项、对齐与完成度；纯矢量碎片、文字补丁、模糊轮廓不会因为结构检查通过而合格。按 [重绘规范](faithful-vector-reconstruction.md) 检查语义对象与文字锚点，两项都完成后再称“对象级可编辑”。

最终交付还需完成 [画面与版式终检](visual-system.md#最终画面与版式验收) 以及 [目录与章节终检](research-navigation.md#整稿目录与章节终检)，记录全部问题页的整改与重新渲染结果。可编辑性通过不替代清晰度、表格式布局和科研主线检查。
