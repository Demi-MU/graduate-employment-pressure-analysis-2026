# 法人单位数分行业与分地区数据字典

本数据由截图《1-5 分地区按主要行业分法人单位数》人工转录得到。由于来源不是原始 Excel 或官方数据库下载文件，所有记录均标记为 `confidence_flag=needs_review`，后续如果获得原始表，应优先用原始表替换截图转录数据。

## 原始转录表

```text
data/raw/official_statistics/legal_person_units_industry_year_image_transcription.csv
data/raw/official_statistics/legal_person_units_province_industry_2024_image_transcription.csv
```

## 处理后表

```text
data/processed/legal_person_units_by_industry_year_panel.csv
data/processed/legal_person_units_by_province_industry_2024.csv
```

## 字段说明

| 字段 | 含义 | 说明 |
| --- | --- | --- |
| year | 年份 | 全国年度表为2005-2024，省级地区表为2024 |
| province | 地区 | 全国年度表固定为“全国”；省级表为省、自治区、直辖市 |
| industry_code | 行业代码 | 项目内部使用的英文标准字段 |
| industry_name | 行业名称 | 原表主要行业名称 |
| legal_person_units | 法人单位数 | 单位为“个”；缺失值保留为空 |
| total_units | 合计法人单位数 | 对应同一年或同一地区的合计 |
| industry_share | 行业占比 | `legal_person_units / total_units` |
| unit | 单位 | 固定为“个” |
| data_scope | 数据口径 | 全国年度分行业 / 2024年省级地区分行业 |
| source | 来源说明 | 截图表名 |
| source_file | 转录 CSV 路径 | 指向 raw transcription 文件 |
| source_type | 来源类型 | 固定为 `image_transcription` |
| confidence_flag | 置信度标记 | 固定为 `needs_review` |
| note | 备注 | 记录截图转录、缺失或口径说明 |

## 质量检查

```text
reports/tables/legal_person_units_transcription_quality_check.csv
```

该表用于检查“合计”与各行业分项求和之间是否存在差异。截图转录数据出现极小差异时，不直接在 raw 层改数，而是通过 QA 表标记，等待后续用原始 Excel 或官方数据库复核。

## 使用边界

法人单位数反映市场主体或机构主体数量，适合描述产业结构和地区主体结构变化。它不能直接等同于招聘岗位数、应届岗位数或硕士岗位数。用于本项目时，它应作为需求侧背景变量，与岗位样本数据、学历要求分布和硕士岗位吸纳比结合分析。
