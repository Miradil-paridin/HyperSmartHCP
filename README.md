# HyperLink Home v0.1

HyperLink Home 是一个运行在局域网内的智能家居可视化中控台。v0.1 默认支持 mock 数据演示，也支持通过 Home Assistant REST API 做只读实体接入。项目不会直接连接米家云，不包含米家账号密码登录逻辑，也不会在第一阶段开放真实设备控制按钮。

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

## Home Assistant 只读接入

当前阶段只读取 Home Assistant 实体列表和状态，并将实体转换成 HyperLink Home 的 `Device` 模型。前端在 Home Assistant 模式下会显示实体列表和状态，快捷操作处于只读禁用状态，不会发起真实控制。

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

后续如果要开放真实控制，请继续通过后端 API 做白名单、二次确认和高风险设备保护，不要让前端直接访问 Home Assistant。
