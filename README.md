# HyperLink Home v0.1

HyperLink Home 是一个运行在局域网内的智能家居可视化中控台。v0.1 默认使用 mock 数据，后端预留 Home Assistant 接入层，不直接连接米家云，也不执行真实高风险设备控制。

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
- WebSocket：ws://localhost:8000/ws/realtime

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

## 后续接入 Home Assistant

1. 在 Home Assistant 创建 Long-Lived Access Token。
2. 基于 `.env.example` 创建本地 `.env`，填入 `HOME_ASSISTANT_URL` 和 `HOME_ASSISTANT_TOKEN`。
3. 将 `MOCK_MODE=false`。
4. 后端统一通过 `backend/app/services/home_assistant.py` 访问 Home Assistant，前端仍只访问本项目后端。
5. 真实控制动作继续走 `POST /api/actions/execute`，在后端增加白名单和确认逻辑后再启用。

不要把 `.env` 或真实 token 提交到仓库。
