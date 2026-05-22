# HyperLink Home v0.1

HyperLink Home 是一个运行在局域网内的智能家居可视化中控台。v0.1 默认支持 mock 数据演示，也支持通过 Home Assistant REST API 接入实体状态和低风险设备控制。项目不会直接连接米家云，不包含米家账号密码登录逻辑，高风险设备默认禁止控制。

## 项目结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── core/config.py
│   │   ├── models/schemas.py
│   │   ├── services/home_assistant.py
│   │   ├── services/mock_data.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/api.ts
│   │   ├── types/api.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .env.example
├── docker-compose.yml
└── README.md
```

## 本地开发启动

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

访问：

- 前端：http://localhost:5173
- 后端健康检查：http://localhost:8000/api/health
- WebSocket mock 流：ws://localhost:8000/ws/realtime

## Docker Compose 启动

```bash
docker compose up -d --build
```

访问：

- 前端：http://localhost:8080
- 后端：http://localhost:8000/api/health

停止：

```bash
docker compose down
```

## 已实现 API

- `GET /api/health`
- `GET /api/overview`
- `GET /api/devices`
- `GET /api/topology`
- `GET /api/metrics`
- `GET /api/events/recent`
- `GET /api/automations`
- `POST /api/actions/execute`
- `WebSocket /ws/realtime`

## Home Assistant 接入

当前阶段读取 Home Assistant 实体列表和状态，并将实体转换成 HyperLink Home 的 `Device` 模型。控制能力只开放低风险 domain，且所有前端操作必须经过本项目后端 `/api/actions/execute`，前端不会直接访问 Home Assistant。

### 创建长期访问令牌

1. 登录 Home Assistant。
2. 点击左下角用户头像或用户名，进入个人资料页面。
3. 滚动到 `Long-Lived Access Tokens` 或“长期访问令牌”区域。
4. 点击 `Create Token` 或“创建令牌”。
5. 输入名称，例如 `HyperLink Home`。
6. 复制生成的 token。令牌只会显示一次，请保存到本机 `.env`，不要提交到仓库。

### 配置 `.env`

复制示例文件：

```bash
copy .env.example .env
```

填写 Home Assistant 地址和令牌：

```env
APP_NAME=HyperLink Home
ENVIRONMENT=development
MOCK_MODE=false
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080

HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=replace_with_long_lived_access_token
```

说明：

- 没有配置 `HOME_ASSISTANT_URL` 或 `HOME_ASSISTANT_TOKEN` 时，后端自动使用 mock 数据。
- 设置 `MOCK_MODE=true` 可以强制使用 mock 数据，即使已经配置 Home Assistant。
- 本地开发时 `.env` 可以放在项目根目录，也可以放在 `backend/` 目录。
- Docker Compose 默认使用 mock 数据；部署时可以在 `docker-compose.yml` 里添加 `HOME_ASSISTANT_URL` 和 `HOME_ASSISTANT_TOKEN` 环境变量，或改成读取外部 `.env`。

### 已支持的实体分类

后端会根据 Home Assistant 的 `entity_id` domain 和 `device_class` 做基础分类：

- `light`：灯光
- `sensor`、`binary_sensor`：传感器；门窗、移动、烟雾等会归为安防设备
- `climate`：空调
- `switch` 中带插座特征的实体：插座
- `lock`：门锁
- `cover` 中窗帘、百叶、卷帘等：窗帘
- `vacuum`：扫地机器人
- `alarm_control_panel`、`camera`：安防设备
- 其他实体：其他设备

### 安全控制策略

控制入口只有：

- `POST /api/actions/execute`

请求可以使用快捷动作：

```json
{
  "action_id": "all_lights_off"
}
```

也可以使用实体服务调用：

```json
{
  "entity_id": "light.living_room",
  "service": "turn_off",
  "service_data": {}
}
```

后端安全限制：

- 允许控制：`light`、`switch`、`fan`、`climate`、`cover`
- 禁止控制：`lock`、`camera`、`alarm_control_panel`、`siren`
- 其他未列入允许清单的 domain 默认拒绝
- 高风险或未开放 domain 会返回 `403`
- 所有成功、拒绝和无效控制请求都会写入事件日志
- 真实控制只在配置 Home Assistant 且 `MOCK_MODE=false` 时执行；否则只记录 mock 执行结果

第一版内置的快捷动作只映射到低风险 domain：

- `all_lights_on`：`light.turn_on`
- `all_lights_off`：`light.turn_off`
- `all_fans_off`：`fan.turn_off`
- `climate_off`：`climate.turn_off`
- `curtains_open`：`cover.open_cover`
- `curtains_close`：`cover.close_cover`

后续如果要开放更多真实控制，请继续通过后端 API 做白名单、二次确认和高风险设备保护，不要让前端直接访问 Home Assistant。
