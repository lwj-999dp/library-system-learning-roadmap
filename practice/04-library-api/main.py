# -*- coding: utf-8 -*-
"""main.py · 应用装配（★ 完整，不需要你改）

对应文档
--------
docs/04-FastAPI与SQLAlchemy.md 「练习 1」的 app/main.py + docs/05 的 CORS 白名单

这个文件做什么
--------------
只做「装配」，不写业务：
  1. 建 FastAPI 实例（标题 / 版本 / lifespan）
  2. lifespan：启动时建表（失败只警告，不让进程起不来）+ 关闭时释放连接池
  3. CORS：只开白名单（Vite 的 5173），绝不用 ["*"] + allow_credentials=True
  4. 中间件：给每个响应加 X-Process-Time
  5. 把 routers 里的三个路由挂上去
  6. `/health` 健康检查

关于「TODO 未填也能启动」
------------------------
脚手架里的 models / schemas / crud / security / routers 都留了 TODO。
这些 TODO 全部在**函数体内部**（import 阶段不会执行），所以 uvicorn 一定能起来。
调用到没实现的接口时抛 NotImplementedError，被下面注册的异常处理器翻译成
**501 Not Implemented**，而不是一坨 500 堆栈 —— 你能一眼看出「这个接口还没写」。

验收标准
--------
- [ ] `uvicorn main:app --reload` 启动无报错，`/docs` 能看到 系统 / 图书 / 借阅 / 鉴权 4 个分组
- [ ] `GET /health` 返回 `{"ok": true, "service": "library-api"}`
- [ ] 没配 .env 时启动只打警告，仍然能起来（接口会 500/501，但进程活着）
- [ ] 没用 `@app.on_event`（已废弃），启动/关闭逻辑都在 lifespan 里
- [ ] CORS 是白名单，不是 ["*"]
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import Base, engine
from routers import auth, books, borrows

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("library")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动 / 关闭钩子（替代已废弃的 @app.on_event）。

    启动时：
      * 提醒你 .env 还没配好（占位密码 / 示例密钥）
      * `create_all` 建**缺失**的表
        ⚠️ 权威建表脚本是 practice/03-sql/schema.sql（含生成列、外键、中文注释），
           create_all 只补缺、不改已存在的表，正式项目请用 Alembic 迁移。
        ⚠️ MySQL 没起来 / 密码不对时**只警告不抛异常** —— 保证脚手架一定能启动。
    关闭时：
      * `engine.dispose()` 释放连接池
    """
    if settings.database_url_is_placeholder:
        logger.warning("DATABASE_URL 还是占位密码，请复制 .env.example 为 .env 并填上真实密码")
    if settings.jwt_secret_is_default:
        logger.warning("JWT_SECRET 还是示例值，阶段 5 上线前必须换成随机密钥")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库连接正常，缺失的表已补齐")
    except Exception as exc:  # noqa: BLE001 —— 启动阶段要吞掉所有数据库异常
        logger.warning("建表失败（不影响启动）：%s", exc)
        logger.warning("请检查 MySQL 是否已启动、.env 的 DATABASE_URL 是否正确，"
                       "并先执行 practice/03-sql/schema.sql")

    logger.info("API 启动完成，文档地址 http://127.0.0.1:8000/docs")
    yield
    engine.dispose()
    logger.info("API 已关闭，连接池释放")


app = FastAPI(
    title="图书管理系统 API",
    version="1.0.0",
    description="阶段 4 + 阶段 5 练习骨架。填掉 TODO 就能跑通完整借还闭环 + 鉴权。",
    lifespan=lifespan,
)

# -----------------------------------------------------------------------------
# CORS：只开白名单
# -----------------------------------------------------------------------------
# ❌ allow_origins=["*"] + allow_credentials=True 会被浏览器直接拒绝
#    （即使生效，也等于把 API 开放给任何网站）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """给每个响应加一个 X-Process-Time 头，方便肉眼发现慢接口。"""
    start = perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{perf_counter() - start:.4f}"
    return response


# -----------------------------------------------------------------------------
# 把 TODO 未实现的接口翻译成 501
# -----------------------------------------------------------------------------
# 脚手架里的算法留白处都写的是 `raise NotImplementedError("TODO: ...")`。
# 不加这个处理器的话你会看到一坨 500 堆栈；加上之后响应是清爽的：
#     HTTP 501  {"detail": "该接口还没实现（TODO）: sync_book() —— 见 crud.py 顶部说明"}
async def _not_implemented_handler(request: Request, exc: NotImplementedError) -> JSONResponse:
    logger.warning("接口未实现：%s %s → %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=501,
        content={"detail": f"该接口还没实现（TODO）：{exc}"},
    )


app.add_exception_handler(NotImplementedError, _not_implemented_handler)


# -----------------------------------------------------------------------------
# 健康检查 + 路由挂载
# -----------------------------------------------------------------------------
@app.get("/health", tags=["系统"], summary="健康检查")
def health() -> dict[str, object]:
    """探活接口：不查库，只证明进程活着。"""
    return {"ok": True, "service": "library-api"}


for _router in (auth.router, books.router, borrows.router):
    app.include_router(_router)


if __name__ == "__main__":
    # 方便直接 `python main.py` 启动（等价于 uvicorn main:app --reload）
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
