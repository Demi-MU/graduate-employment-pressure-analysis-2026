# Liepin University Job Demand Structure Dictionary

## 文件位置

- 原始转录表：`data/raw/recruitment_reports/liepin_university_job_demand_image_transcription.csv`
- 处理后数据：`data/processed/liepin_university_job_demand_structure.csv`
- 清洗脚本：`src/data_cleaning/clean_liepin_university_job_demand.py`
- 制图脚本：`src/visualization/plot_liepin_university_job_demand.py`

## 数据来源

数据来自用户提供的三张猎聘大数据截图，当前以人工转录方式整理。由于尚未获得原始报告 PDF、Excel 或可下载数据表，所有记录均标记为 `source_type=image_transcription` 和 `confidence_flag=needs_review`。

## 指标组

| indicator_group | 含义 | 图表 |
| --- | --- | --- |
| education_requirement | 大学生岗位学历要求分布 | `liepin_job_education_requirement_distribution.png` |
| registered_capital | 按企业注册资本划分的大学生需求分布 | `liepin_job_registered_capital_distribution.png` |
| company_type | 按企业性质划分的大学生需求分布 | `liepin_job_company_type_distribution.png` |

## 字段说明

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| indicator_group | 指标组英文代码 | `education_requirement` |
| indicator_group_name | 指标组中文名称 | `岗位学历要求` |
| category_order | 分类在原图中的展示顺序 | `1` |
| category | 分类名称 | `硕士` |
| period | 标准化时期 | `2025H1` |
| period_label | 原图时期标签 | `2025前半年` |
| percentage | 占比，单位为百分点 | `17.4` |
| unit | 数值单位 | `percent` |
| source | 数据来源名称 | `猎聘大数据` |
| source_type | 来源类型 | `image_transcription` |
| confidence_flag | 质量标记 | `needs_review` |
| note | 原图标题或口径备注 | `截图标题：大学生岗位学历要求` |

## 使用边界

该数据适合用于招聘报告摘录和需求侧结构背景分析，尤其是说明岗位学历要求、需求企业规模和企业性质结构的变化。它不应被直接解释为全国完整招聘市场结构，也不能替代后续岗位样本中的硕士岗位吸纳比计算。
