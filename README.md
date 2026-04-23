# MBTI World Simulator

一个基于 **FastAPI + React + Gemini/OpenAI 可选大模型** 的轻量社交世界模拟器。  
项目以 4 个 MBTI 风格角色为起点，构建一个会自动推进时间、生成事件、更新关系、输出日报，并带有可视化舞台前端的“小型世界”。

> 当前版本为 **MVP / 原型阶段**：
> - 4 个角色：INTJ、ENFP、ISFJ、ESTP
> - 3 个主要场景：合租公寓、大学、游乐园
> - 后端事件流、关系矩阵、needs / emotion、日报、前端可视化舞台已经打通

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
  - [1. 克隆项目](#1-克隆项目)
  - [2. 启动后端](#2-启动后端)
  - [3. 启动前端](#3-启动前端)
- [环境变量说明](#环境变量说明)
- [前后端接口说明](#前后端接口说明)
- [推荐测试流程](#推荐测试流程)
- [LLM 使用说明](#llm-使用说明)
- [常见问题](#常见问题)
- [后续规划](#后续规划)
- [免责声明](#免责声明)

---

## 项目简介

这个项目希望模拟一个 **“有趣、持续发生事情的世界”**。

世界中每个角色并不是任务驱动，而是会根据：

- 人格风格
- 当前 needs（社交、休息、成就、秩序、归属等）
- 当前 emotion
- 与其他角色的关系
- 当前时间段 / 场景 / 天气

自主选择行为，并与他人或环境发生互动。

当前 MVP 中，角色会在如下空间中活动：

- **Apartment（合租公寓）**：四个卧室、客厅、厨房、健身房、两个卫生间
- **University（大学）**：教室、图书馆、食堂、校园广场
- **Amusement Park（游乐园）**：入口、游乐设施区、街机厅、美食区

前端会以可视化舞台形式展示人物所在位置、事件气泡、关系摘要与状态信息。

---

## 功能特性

### 已完成

- 4 个角色原型
  - Ethan Reed（INTJ）
  - Leo Brooks（ENFP）
  - Grace Miller（ISFJ）
  - Chloe Parker（ESTP）
- 世界时间推进：morning → late_morning → afternoon → evening → late_evening → night
- 天气变化与全局标签
- needs / emotion 系统
- relationship matrix（closeness / trust / tension / respect）
- 模板化事件系统 + fallback 行为系统
- daily report（日结摘要）
- `/frontend/overview` 聚合接口
- React 前端可视化舞台
- 角色详情弹窗
- Auto Step / Stop 自动推进控制

### 可选启用

- 使用 Gemini 等 LLM 参与行动决策或日报生成

---

## 技术栈

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- 可选：Google Gemini API

### Frontend

- React
- TypeScript
- Vite
- 原生 CSS（当前没有引入额外 UI 框架）

---

## 项目结构

大致结构示意：

```text
mbti-world-sim/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ data/
│  │  ├─ engine/
│  │  ├─ llm/
│  │  ├─ models/
│  │  ├─ runtime.py
│  │  └─ main.py
│  ├─ .env
│  └─ ...
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  ├─ api.ts
│  │  ├─ App.tsx
│  │  ├─ main.tsx
│  │  ├─ styles.css
│  │  └─ types.ts
│  ├─ .env
│  ├─ package.json
│  └─ vite.config.ts
└─ README.md
```

## 快速开始

## 1. 克隆项目

```bash
git clone https://github.com/guohuiguo/MBTI-WORLD-SIM
cd mbti-world-sim
```

---

## 2. 启动后端

### 方式 A：使用你已有的虚拟环境

新建一个虚拟环境并激活:

```bash
conda create -n mbti_sim python=3.10 -y
conda activate mbti_sim
```
新建项目文件夹:

```bash
cd D:\
mkdir MBTI-WORLD-SIM
cd MBTI-WORLD-SIM
```

进入后端目录：

```bash
cd backend
```

安装依赖：

```bash
pip install fastapi uvicorn pydantic google-genai
```

启动后端：

```bash
uvicorn app.main:app --reload
```

启动成功后，默认可访问：

- API 文档：`http://127.0.0.1:8000/docs`
- 前端聚合接口：`http://127.0.0.1:8000/frontend/overview`

---

## 3. 启动前端

进入前端目录：

```bash
cd frontend
```

安装依赖：（先确保下载了安装 Node.js）
如果你是Windows X64的话，可以在这个链接处下载：https://nodejs.org/dist/v24.15.0/node-v24.15.0-x64.msi?utm_source=chatgpt.com

```bash
npm install
```

启动开发服务器：

```bash
npm run dev
```

启动成功后，默认访问：

- 前端页面：`http://localhost:5173`

---

## 环境变量说明
你需要自己建两个.env文件

### 项目`/.env`
如果你启用 Gemini，请在项目目录下创建 `.env`：
当然，你也可以使用其他的API去进行适配，这里GPT可以帮你完成对应的代码

```env
GEMINI_API_KEY=your_api_key
```

### 前端 `frontend/.env`

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 前后端接口说明

当前前端主要依赖这些接口：

### 状态 / 聚合

- `GET /state`
  - 返回世界状态、agents、relationships、today_events
- `GET /frontend/overview`
  - 返回前端直接消费的聚合数据：
    - world
    - room_distribution
    - focus_events
    - event_feed
    - character_cards
    - relationship_graph
    - latest_report

### 模拟控制

- `POST /simulation/reset`
  - 重置世界到初始状态
- `POST /simulation/step`
  - 推进一步时间槽
- `POST /simulation/run-day`
  - 直接跑完整一天

### 报告

- `GET /reports/{day}`
  - 获取某一天的日报

### 调试（如果你保留了 debug router）

- `POST /debug/prepare-template/{template_id}`
- `POST /debug/run-days?days=30`

---

## 推荐测试流程

后端最小回归测试建议固定为：

1. `POST /simulation/reset`
2. `GET /state`
3. `POST /simulation/run-day`
4. `GET /state`
5. `GET /frontend/overview`

只要这 5 步满足：

- 时间能推进
- 事件能生成
- 日报能生成
- state 与 run-day 结果一致
- `/frontend/overview` 可直接给前端展示

就说明主链路是正常的。

---

## LLM 使用说明

当前项目支持用 LLM 参与以下部分：

- 行动决策（choose_action）
- 日报生成（daily_report）

### 建议

如果你使用的是免费层 Gemini，不建议让 **每个角色每个 step 都调用一次 LLM**，否则非常容易触发：
因为Gemini免费层的额度就20次请求/天

- `429 RESOURCE_EXHAUSTED`
- `503 UNAVAILABLE`

### 更推荐的策略

- 使用其他便宜模型的API

### Prompt 压缩建议

为了减少 token、提高成功率，当前建议 action prompt 只保留：

- 当前角色简档
- 当前 slot / location
- top 2 needs
- 最近 1~2 条 memory
- candidate_actions

不要把 world 全量、所有 relationships 全量都塞进去。

---

## 常见问题

### 1. 前端显示 `Failed to fetch`

通常是以下原因：

- 后端没启动
- FastAPI 没开启 CORS

建议先直接访问：

```text
http://127.0.0.1:8000/frontend/overview
```

如果这里都打不开，就先修后端。

---

### 2. Gemini API 一直报错

常见原因：

- 免费层配额过低，请求次数太多
- 速率限制（429）
- 服务端高负载（503）
- prompt 太长

建议：

- 降低调用频率
- 加 cooldown
- 缩 prompt
- 或者只让日报使用 LLM

---

## 后续规划

### 前端

- 更真实的移动动画（非瞬移）
- 更像小游戏的对话气泡
- University / Amusement Park 场景细化
- 关系图谱可视化升级
- 日报 / 事件流筛选

### 后端

- 模板覆盖率继续扩充
- 更强的多人互动结算
- 持久化增强（SQLite / JSON）
- 更细粒度的 LLM 调度策略
- 更稳定的 debug forcing 体系

### 世界规模

- 从 4 个角色扩展到完整 16 MBTI 角色
- 多场景并行推进
- 更复杂的长期记忆与关系演化

---

## 免责声明

- 本项目中的 MBTI 设定是 **灵感来源 / 风格参考**，并不等同于真实心理测量学结论。
- 角色行为为模拟生成结果，不应视作对现实人格的科学判断。
- 如果你启用了外部 LLM API，请注意：
  - 不要提交真实 API Key 到公开仓库
  - 注意服务商的计费和速率限制

---

如果你觉得这个项目有趣，欢迎 Star、Fork、提 Issue，或者一起把它做成一个真正有意思的社交世界模拟器。
