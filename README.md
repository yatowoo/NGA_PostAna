# NGA舰萌投票统计

## 基本功能

* 抓取NGA舰萌投票帖数据，根据收集到的别名对回帖进行匹配，导出初步结果及Excel格式计票辅助（包含求和公式）。

* 引入分词验证功能，比较回帖计票数与分词数，过滤NGA表情、常用标签与字数填充词

* 实现服务端自动监控脚本，并将当前进行中投票结果网页展示

## 依赖

Python 3 ( >= 3.5.2)

PyPI库：requests, bs4, zhconv, pypinyin

Web库：bootstrap 4, ChartJS

## NGA API

Cookie: guestJS={UNIX Timestamp}

数据格式：参考zeg帖子，tid=6406100

分页：第n页楼层数[20(n-1), 20n-1]，删帖直接抽楼

## 使用方法

./run-analysis.py [-h] [-l] [-d] [-a] [-i INFO [INFO ...]]

|参数||说明
|---|---|---|
|-h|--help|show this help message and exit
|-l|--local|Do not update thread data, analysis with existed local files
|-d|--debug|Do not run any commands, only check metadata and output commands for analysis
|-a|--all|Analyse all selected thread, ignore deadline
|-i INFO|--info INFO|Group information, SAIMOE_YEAR SAIMOE_STAGE (if not specified, latest votes will be selected)

## 代码及文件

metadata.json - 数据源，包含投票帖信息、舰娘别名

### 抓取脚本

./get-post.py [tid]

按页抓取帖子内容，组成列表后导出JSON文件到output/NGA-[tid].json

### 格式转换

./export-post.py [json_file] [output_file]

将JSON文件转换为csv文件，分隔符为半角逗号<,>，同时去除回帖中的半角逗号

输出格式为：楼层、用户ID、注册时间、回帖时间、回帖内容，每行一楼、不含主楼

### 投票分析

./ana-group.py [csv_file] [YEAR] [STAGE] [GROUP]

输入csv文件为export-post.py导出格式，分析后生成result.csv和validation.csv。

* 匹配顺序：舰娘名称、别名、名称谐音

* 验证方法：去除舰娘名中的空格、NGA表情、标签、非分词特殊字符、替换分词字符

* 单句处理：分词为1、匹配数大于1，通过逐个去除舰娘名及别名重新分词

|验证列标记|说明|
|---|---|
|●|验证通过，分词数等于投票匹配数|
|×|验证失败，分词数不等于投票匹配数|
|?|超票，投票匹配数超过限制|
|-|新号，用户注册时间晚于投票限制|