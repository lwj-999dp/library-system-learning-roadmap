# -*- coding: utf-8 -*-
"""routers/auth.py · 注册 / 登录 / 当前用户（TODO，阶段 5 练习 2）

对应文档
--------
docs/05-鉴权与安全.md 练习 2 的 app/routers/auth.py（完整流程 + 用户枚举防护都在那里）

这个文件要做什么
----------------
| 方法 | 路径                 | 作用         | 成功码 | 请求体形式        | 失败              |
|------|----------------------|--------------|:------:|-------------------|-------------------|
| POST | `/api/auth/register` | 注册         | 201    | JSON              | 409 编号已存在 / 422 参数非法 |
| POST | `/api/auth/login`    | 登录发 Token | 200    | **form-data**     | 401 用户名或密码错误 |
| GET  | `/api/auth/me`       | 当前用户     | 200    | 带 Bearer Token   | 401 未登录        |

★ 登录接口的请求体是 **form-data**（`username` + `password`），不是 JSON！
  这是 OAuth2 的规范形式，也是 `/docs` 上 Authorize 按钮能工作的前提：
      curl -X POST .../api/auth/login -d "username=A001&password=Admin@12345"
  用 JSON 调会得到 422 —— 这一条踩过就记住了。

三条安全底线
------------
1. **角色由后端写死**：注册时 `role="reader"`，绝不接受前端传 role（否则自己就能提权成管理员）
2. **用户枚举防护**：用户不存在和密码错误返回**同一句话**「用户名或密码错误」
   —— 回「该用户不存在」等于给攻击者一个撞库探测器
3. **密码只在内存里出现**：`payload.password` 立刻哈希，绝不入库、绝不进日志

验收标准（前几条来自 docs/05 的安全验证清单）
--------------------------------------------
- [ ] 注册两个密码都是 `Reader@12345` 的读者，两条 `password_hash` **不相等**（盐生效）
- [ ] `SELECT id, password_hash FROM users;` 全是 `$2b$12$...`
- [ ] 不存在的用户 / 错误的密码 → 返回的 `detail` 完全一样，都是 401
- [ ] 用 A001 登录能拿到 `access_token`，粘到 https://jwt.io 能看到 sub/role/iat/exp
- [ ] payload 里**没有**手机号、姓名、密码
- [ ] 注册时多传一个 `"role": "admin"` → 数据库里 role 仍然是 `reader`
- [ ] `GET /api/auth/me` 不带 Token → 401
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import TokenOut, UserCreate, UserOut
from security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["鉴权"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             summary="注册（只能注册成读者）")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """注册新读者。成功 201 返回用户信息（**不含**任何密码字段）。

    TODO ①：
        1. `if db.get(User, payload.id) is not None:` → `HTTPException(409, detail="用户编号已存在")`
        2. 建用户：
               user = User(
                   id=payload.id,
                   name=payload.name,
                   phone=payload.phone,
                   role="reader",                              # ★ 写死，不接受前端传
                   password_hash=hash_password(payload.password),  # ★ 立刻哈希
               )
        3. `db.add(user)` → `db.commit()` → `db.refresh(user)` → `return user`

    ⚠️ 出参是 `UserOut`，里面没有 password / password_hash 字段 —— 字段都不存在，
       物理上不可能泄露。永远不要把 ORM 对象直接当响应模型返回。
    ⚠️ 如果用户已存在，也可以顺手提示「如需管理员账号请改数据库或跑 seed.py」。
    """
    raise NotImplementedError("TODO: routers/auth.register() —— 409 查重 + role 写死 + 哈希入库")


@router.post("/login", response_model=TokenOut, summary="登录（form-data: username + password）")
def login(
    form: OAuth2PasswordRequestForm = Depends(),   # ★ 注意：这里吃的是 form-data
    db: Session = Depends(get_db),
):
    """校验密码并签发 JWT。成功 200 返回 `{accessToken, tokenType, user}`。

    TODO ②：
        user = db.get(User, form.username)

        # ⚠️ 两种失败必须返回同一句话，避免用户枚举
        if user is None or user.is_deleted:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        if not verify_password(form.password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

        token = create_access_token(user.id, user.role)
        return TokenOut(access_token=token, token_type="bearer", user=user)

    想清楚这几个问题（面试会追问）：
      * 为什么失败信息要统一？→ 否则「该用户不存在」就成了撞库探测器
      * Token 里为什么还要放 role？→ 只给前端做界面引导（隐藏管理按钮），
        后端鉴权一律以数据库为准，这样降级能立刻生效
      * 为什么不用 `==` 比对密码哈希？→ 时序侧信道，必须用 `bcrypt.checkpw`
      * 暴力破解怎么办？→ 生产上要加失败计数 + 锁定/限流（本项目只做提示）
    """
    raise NotImplementedError("TODO: routers/auth.login() —— 统一 401 文案 + 签发 Token")


@router.get("/me", response_model=UserOut, summary="当前登录用户")
def me(user: User = Depends(get_current_user)):
    """返回 Token 对应的用户。依赖 `get_current_user` 负责解析 Token 与 401。

    TODO ③：一行就够 —— 依赖已经把 User 查好塞进参数了，直接 `return user`。

    这一步能跑通，说明整条链路都对了：
        登录拿 Token → 请求头带 `Authorization: Bearer xxx` → 验签 → 查库 → 拿到 User
    """
    raise NotImplementedError("TODO: routers/auth.me() —— return user")
