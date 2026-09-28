# -*- coding: utf-8 -*-
"""routers 包 · 每个模块负责一组接口。

对应文档：docs/04-FastAPI与SQLAlchemy.md「D. 项目结构」

| 文件            | 负责的接口                                        | 阶段   |
|-----------------|---------------------------------------------------|--------|
| routers/auth.py | 注册 / 登录 / 当前用户（/api/auth/*）              | 阶段 5 |
| routers/books.py| 图书增删改查（/api/books/*）                       | 阶段 4 |
| routers/borrows.py | 借书 / 还书（/api/borrows/*）★ 行锁在这里        | 阶段 4 |

约定：**只有路由层可以抛 HTTPException**，crud / security 层不关心 HTTP。
"""

from __future__ import annotations

# 导入顺序无所谓：main.py 会用 `from routers import auth, books, borrows` 显式导入。
# 这里不做 re-export，避免循环导入（routers 依赖 database / crud，main 依赖 routers）。
__all__: list[str] = ["auth", "books", "borrows"]
