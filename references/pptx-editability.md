# PPT 内对象与文字可编辑：最终交付契约

验收对象是用户打开的最终 PPTX。SVG 源文件中的 `<text>`、`<g>`、`path` 可编辑，不代表把 SVG 插入 PowerPoint 后内部文字和图形已成为原生对象。`addImage({path: 'whole-slide.svg'})` 只插入一张图片；附上 labels.json 也不会自动生成文本框。

## 从图源到真实对象

1. 由同一份几何来源输出 SVG 和 PowerPoint 原生形状、自由曲线、连接线及语义组。每个主体模块、局部小图、图例与箭头可单独选择和移动；组内对象可继续编辑。
2. 所有标题、段落、图内短标签、坐标标签和图例文字落为 PowerPoint 原生文本框或原生表格/图表文字。标签层逐项实际生成，不能只保存 JSON；也不把文字转轮廓、截图或藏在 SVG 中。
3. 重复散点、细密纹理按语义或颜色合并为原生组/复合自由曲线。确需独立 SVG 的局部密集图元仅限无字的局部细节，单独可选；在清单登记 `vector_detail`，轴、图例和标签仍在原生层。整页、主体流程或完整带字面板不能登记为密集细节。
4. 保留图源中的结构与视觉层次：细线、浅填色、渐变、曲线、子模块、图例和局部放大可以由矢量实现。遇到转换问题，修复图元转换或重绘该局部；不把全页压成图片，也不为便于转换删掉关键对象。

## 先做一页，再批量

选一页对象较丰富的正文完成端到端样页：参考图 → 按语义重绘无字图形与独立文字 → PPTX → PowerPoint 实际渲染。打开工作副本，修改一个图内短标签、移动一个机制节点、修改一条线的颜色，再移开一处文字确认底层没有旧字、白块或颜色补丁，保存并重新打开确认。通过后再复用转换方式批量制作。测试在副本上完成，交付文件保留正式内容。

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

用户封面、真实照片、来源图按形状名称登记在该页 `allowed_pictures`，写 `role`（`user_cover`、`photo`、`source_image`）和具体 `reason`；局部无字矢量细节用 `vector_detail`。这份名单说明素材的真实用途，不能给生成的整页科研图改名放行。

最终运行：

```text
python scripts/audit_design.py design-plan.json --pptx final.pptx
python scripts/audit_pptx.py final.pptx --plan design-plan.json --require-object-map --output checks/pptx-audit.json
```

检查会读取最终 PPT 的真实对象、SVG 媒体、文字与标签映射，拒绝整页 SVG、藏在 SVG 中的文字、缺失原生标签及把图片冒充主体对象。只统计形状数量、只检查 SVG 无位图、只验证有 labels.json，都不足以完成验收。`--inventory` 仅供盘点，不能作为通过凭据。

最后实际查看三方对照和编辑测试。脚本负责发现结构性失败，视觉检查负责构图、缺项、对齐与完成度；纯矢量碎片、文字补丁、模糊轮廓不会因为结构检查通过而合格。按 [重绘规范](faithful-vector-reconstruction.md) 检查语义对象与文字锚点，两项都完成后再称“对象级可编辑”。

最终交付还需完成 [画面与版式终检](visual-system.md#最终画面与版式验收) 以及 [目录与章节终检](research-navigation.md#整稿目录与章节终检)，记录全部问题页的整改与重新渲染结果。可编辑性通过不替代清晰度、表格式布局和科研主线检查。
