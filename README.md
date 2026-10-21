# 机械结构工程师面试与知识强化手册

588道机械结构工程面试与复习题，按五大板块组织，提供口头首答、深入复习、公式、教学算例和公开技术资料链接。

GitHub仓库：[MXDfc/mechanical-interview-handbook](https://github.com/MXDfc/mechanical-interview-handbook)。

## 阅读

下载或克隆仓库后，用浏览器打开 [index.html](index.html)。网页支持离线阅读、全文检索、题号定位、折叠答案与打印；外部技术来源链接需要联网。也可以直接阅读 [Markdown总索引](01-手册索引.md)。

| 板块 | 内容 | 题数 |
|---|---|---:|
| [理论知识](02-理论知识.md) | 理论力学、材料力学、机械原理、机械设计 | 202 |
| [生活场景实践分析](03-生活场景实践分析.md) | 现象分析、受力、摩擦、热与运动 | 68 |
| [生产场景实践分析](04-生产场景量产实践分析.md) | 公差、工艺、装配与量产质量 | 142 |
| [仿真测试实践分析](05-仿真测试实践分析.md) | 建模、试验、验收与故障分析 | 124 |
| [常用数据和公式汇总](06-常用数据和公式汇总.md) | 公式、数量级、算例与资料索引 | 52 |

[关节模组电机专题](07-关节模组电机面试专题.md)集中收录60道相关题，串联电机原理、结构集成、驱动基础、散热和量产验证。这些题已计入上述五大板块，不重复计算。

## 维护与重建

[完整主手册](机械结构工程师面试与知识强化手册.md)是内容主源。五分册和电机专题由 `maintenance/organization.json` 组织，HTML、检索数据和导航由脚本生成。请先阅读 [编辑约定](AGENTS.md) 和 [维护交接](00-工作总结与编辑交接.md)。

使用Python 3.10或更新版本。仓库附带Markdown渲染依赖及其原始许可；也可通过 `python -m pip install -r maintenance/requirements.txt` 安装指定版本。

```sh
# 修改主源后同步已有题目
python maintenance/sync_questions.py --write

# 生成分册、HTML、首页和检索数据，并运行结构校验
python maintenance/rebuild.py

# 单独检查题号、分类、共享正文、内容变化范围和本地链接
python maintenance/validate.py
```

浏览器检查使用Node.js及Playwright：配置 `PLAYWRIGHT_MODULE` 为可用的Playwright模块路径；如果使用本机浏览器，可设置 `EDGE_BINARY` 为浏览器可执行文件路径，然后执行：

```sh
node maintenance/check_portal.cjs
node maintenance/check_motor_topic.cjs
```

检查截图及报告写入本地 `maintenance/qa/`，不纳入Git。

## 内容与来源

当前公开版本为 **v2.7.2（2026-10-21）**。资料面向通用机械结构岗位，已去除特定应聘企业及公司背景，保留公开厂商、学术与标准机构的技术引用。原始简历、作品集、历史备份和本地迁移记录不随仓库分发；R/P页码仅为匿名案例材料的引用标记。

教学参数、经验值和实际产品要求在正文中分别注明。题目和示例不代表读者的个人经历，也不能直接作为产品放行依据。引用资料及第三方依赖的权利归其相应权利人；本仓库不重新分发引用网页、原厂手册或个人附件。
