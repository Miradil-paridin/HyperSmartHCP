# HyperLink Home v0.1

## 项目定位

这是一个运行在局域网内的智能家居可视化控制平台，第一阶段面向小米智能家居设备，但不要直接逆向米家协议。第一阶段通过 Home Assistant 作为设备接入层，后端连接 Home Assistant API，前端做成类似 HyperLink Pro 图片里的科技感中控台。

项目最终目标：

- 本地电脑开发
- Docker Compose 一键运行
- 后期部署到群晖 NAS
- 局域网长期运行
- 页面视觉效果要高级、科技感、适合大屏展示
- 支持真实 Home Assistant 数据，也支持 mock 数据演示

## 技术栈要求

后端：

- Python 3.11+
- FastAPI
- WebSocket
- httpx
- pydantic-settings
- SQLite，第一版可选
- 后端目录：backend/

前端：

- Vue 3
- Vite
- TypeScript
- TailwindCSS
- ECharts
- AntV G6 或者 Cytoscape.js 用于拓扑图
- 前端目录：frontend/

部署：

- Docker
- docker-compose.yml
- .env.example
- README.md
- 支持本地开发和 NAS 部署

## Home Assistant 接入方式

不要直接控制小米云，不要写小米账号密码登录逻辑。

第一版通过 Home Assistant 接入设备：

- 支持配置 HOME_ASSISTANT_URL
- 支持配置 HOME_ASSISTANT_TOKEN
- 没有配置时使用 mock 数据
- 后端封装 HomeAssistantClient
- 前端不要直接访问 Home Assistant，统一访问本项目后端

需要预留：

- 读取设备/实体状态
- 读取事件日志
- 调用服务控制设备
- WebSocket 推送实时状态变化

## 第一版功能范围

只做 v0.1，不要贪多。

必须实现：

1. 设备总览 Dashboard

- 总设备数
- 在线设备数
- 离线设备数
- 今日事件数
- 家庭健康度

2. 左侧连接中心

- 全部设备
- 灯光
- 传感器
- 空调
- 插座
- 门锁
- 窗帘
- 扫地机器人
- 安防设备

3. 中央拓扑图

- 中心节点：HyperLink Home
- 房间节点：客厅、卧室、厨房、卫生间、阳台
- 设备节点：灯、温湿度传感器、人体传感器、空调、插座、门锁等
- 节点颜色区分在线、离线、告警、未知
- 第一版可以用 mock 数据

4. 数据监控

- 温度曲线
- 湿度曲线
- 光照曲线
- 插座功率曲线
- 使用 ECharts
- 第一版用 mock 实时数据，每 2 秒刷新一次

5. 右侧快捷操作

- 回家模式
- 离家模式
- 睡眠模式
- 观影模式
- 全屋关灯
- 扫地机器人启动
- 第一版点击后调用后端 mock API，不要真正控制设备

6. 消息日志

- 显示最近设备状态变化
- 支持不同类型标签：INFO、WARN、ERROR、DEVICE、AUTO

7. 自动化规则展示

- 温度过高开空调
- 有人经过开灯
- 离家关闭全屋灯
- 夜间小夜灯
- 第一版只展示，不实现复杂规则编辑器

## 后端 API 设计

请至少实现：

GET /api/health
GET /api/overview
GET /api/devices
GET /api/topology
GET /api/metrics
GET /api/events/recent
GET /api/automations
POST /api/actions/execute
WebSocket /ws/realtime

要求：

- 所有接口都有 mock 数据
- 代码结构清晰
- Home Assistant 真实接入逻辑单独放到 backend/app/services/home_assistant.py
- mock 数据单独放到 backend/app/services/mock_data.py
- 不要把 token 写死
- 不要提交 .env
- 提供 .env.example

## 前端页面要求

整体视觉参考我给的 HyperLink Pro 图片：

- 深色背景
- 蓝紫色科技感
- 发光边框
- 卡片式布局
- 顶部导航
- 左侧设备分类
- 中间拓扑图
- 下方数据曲线
- 右侧快捷操作、消息日志、自动化规则
- 页面要能自适应 1920x1080 大屏
- 代码要组件化

前端组件建议：

- AppShell.vue
- TopNav.vue
- Sidebar.vue
- OverviewCards.vue
- TopologyGraph.vue
- MetricCharts.vue
- QuickActions.vue
- EventLog.vue
- AutomationPanel.vue

## Docker 要求

提供：

- backend/Dockerfile
- frontend/Dockerfile
- docker-compose.yml
- README.md

本地运行：

- backend: 8000
- frontend: 5173 或 nginx 8080
- docker compose up -d 后可以访问前端

## 开发纪律

请先生成项目骨架和可运行的 v0.1。
不要一次性加入权限系统、真实米家登录、固件升级、复杂规则引擎。
不要直接操作门锁、摄像头、安防报警等高风险设备。
所有真实控制动作必须走后端 API，并且第一版默认 mock。
完成后请告诉我：

1. 项目目录结构
2. 如何本地启动
3. 如何 Docker 启动
4. 后续如何接入 Home Assistant
