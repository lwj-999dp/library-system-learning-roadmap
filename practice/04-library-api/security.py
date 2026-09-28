# -*- coding: utf-8 -*-
"""security.py · 密码哈希 + JWT 签发校验 + 权限依赖（TODO，阶段 5）

对应文档
--------
docs/05-鉴权与安全.md 「A. 密码存储」「B. JWT」「C. 签发与校验流程」「D. FastAPI 安全依赖」
（文档里也把依赖写在 app/deps.py，本项目为了文件更少，统一放在 security.py）

这个文件要做什么
----------------
四件事，从上到下依次是：
  1. `hash_password` / `verify_password` —— bcrypt 加盐哈希与恒定时间校验
  2. `create_access_token` / `decode_token` —— 签发和验证 JWT
  3. `get_current_user` —— 把 `Authorization: Bearer xxx` 变成一个真实的 User 对象
  4. `require_admin` / `require_reader` —— 角色闸门（403）

必须记住的三条
--------------
1. **哈希不是加密。** 密码只能哈希（不可逆），绝不能「加密」后存起来。
2. **JWT 的 payload 是明文可读的**（base64url，粘到 jwt.io 就能看），
   所以里面只放 `sub` / `role` / 时间字段，绝不放密码、手机号、身份证。
3. **`algorithms=["HS256"]` 必须硬编码在服务端。**
   如果从 Token 的 header 里读 `alg`，攻击者把它改成 `none` 就能伪造任意身份。

401 与 403 的分工（混用会让前端登录逻辑死循环）
----------------------------------------------
    401 Unauthorized = 「你是谁？我不知道」→ 没带 Token / 签名错 / 过期 / 用户不存在
                       响应要带 `WWW-Authenticate: Bearer` 头（HTTP 规范要求）
    403 Forbidden    = 「我知道你是谁，但你不能干这个」→ 读者调管理员接口、还别人的书

验收标准（逐条跑 docs/05 的「安全验证清单」）
--------------------------------------------
- [ ] `SELECT id, password_hash FROM users;` 全是 `$2b$12$...`，没有一个明文
- [ ] 同一个密码哈希两次结果不同，但两个哈希都能校验通过（盐生效）
- [ ] 改 Token 最后一位字符 → 请求接口返回 **401**
- [ ] 不带 Token / 带 `Bearer abc` → **401**
- [ ] 读者 Token 调 `DELETE /api/books/B001` → **403**（不是 401）
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=-1` 重启后重新登录拿到的 Token → **401**（过期）
- [ ] 角色判断读的是**数据库**（`db.get(User, ...)`），不是 Token 里的 `role` 字段
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import User

# -----------------------------------------------------------------------------
# 常量与依赖（已给出，不用改）
# -----------------------------------------------------------------------------

# bcrypt 只认前 72 字节，超长密码会被**静默截断**（a*100 和 a*72 等价）。
# 这里显式截断，让行为可预期；同时 schemas.UserCreate 用 max_length=64 在入口卡住。
MAX_PASSWORD_BYTES: int = 72

# tokenUrl 必须和真实登录接口路径完全一致，否则 /docs 右上角的 Authorize 按钮用不了
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _unauthorized(detail: str) -> HTTPException:
    """401 的 Factory。⚠️ 401 一定要带 WWW-Authenticate 响应头，这是 HTTP 规范要求。"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


# -----------------------------------------------------------------------------
# 1. 密码哈希（bcrypt）
# -----------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """把明文密码变成 bcrypt 哈希串（存进 users.password_hash）。

    TODO ①：
        raw = plain.encode("utf-8")[:MAX_PASSWORD_BYTES]        # 显式截断到 72 字节
        return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=settings.bcrypt_rounds)).decode("utf-8")

    为什么用 bcrypt 而不是 MD5 / SHA256（面试必答三点）：
      1. **自带随机盐**：每次调用盐都不同 → 同一个密码两次哈希结果不同 → 彩虹表直接失效
      2. **故意慢**：代价因子每 +1，计算量翻倍；rounds=12 一次约 200~300 ms，
         登录能接受，而暴力破解的成本高到不可行
      3. **盐存在哈希串里**：`$2b$12$<22位盐><31位摘要>`，验证时自动从串里读盐，
         不需要额外存字段
    返回示例：`$2b$12$Xk9...`（bcrypt 返回 bytes，记得 .decode()）
    """
    raise NotImplementedError("TODO: security.hash_password() —— bcrypt 加盐哈希（见函数内注释）")


def verify_password(plain: str, hashed: str) -> bool:
    """校验密码是否匹配哈希串。

    TODO ②：
        try:
            return bcrypt.checkpw(plain.encode("utf-8")[:MAX_PASSWORD_BYTES], hashed.encode("utf-8"))
        except ValueError:
            return False        # 哈希串格式不对（比如空串），当校验失败处理，别抛 500

    ⚠️ 必须用 `bcrypt.checkpw`（内部是**恒定时间比较**）。
       自己写 `hash == stored` 会有时序侧信道，能被逐字节猜出哈希。
    ⚠️ 数据库里 password_hash 默认是空串 ''，checkpw 遇到它会抛 ValueError —— 所以要 try。
    """
    raise NotImplementedError("TODO: security.verify_password() —— bcrypt.checkpw（见函数内注释）")


# -----------------------------------------------------------------------------
# 2. JWT 签发与校验
# -----------------------------------------------------------------------------


def create_access_token(user_id: str, role: str) -> str:
    """签发 Token。

    TODO ③：payload 里放这些，然后用 settings.jwt_algorithm（HS256）签名：
        {
            "sub": user_id,                                    # 主体：用户 ID
            "role": role,                                      # ⚠️ 仅供前端做界面引导
            "iat": datetime.now(timezone.utc),                 # 签发时间
            "exp": now + timedelta(minutes=settings.access_token_expire_minutes),  # 过期时间
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    ⚠️ exp 必须设（一般 30 分钟 ~ 2 小时）。设成一年等于 Token 泄露后无法挽回。
    ⚠️ payload 是**明文可读**的 —— 粘到 https://jwt.io 谁都能看到内容，
       所以只放 sub / role / 时间字段，绝不放手机号、真实姓名、密码。
    ⚠️ role 放进去只是给前端用（比如隐藏管理按钮），**后端鉴权一律以数据库为准**。
    """
    raise NotImplementedError("TODO: security.create_access_token() —— jwt.encode（见函数内注释）")


def decode_token(token: str) -> dict:
    """验签 + 校验 exp（过期会抛 ExpiredSignatureError）。

    TODO ④：
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],   # ⚠️ 硬编码！绝不从 Token header 读 alg
            # 少了上面这行，攻击者把 alg 改成 none 就能伪造任意身份的 Token
        )

    可能抛出的异常（调用方 get_current_user 负责翻译成 401）：
        jwt.ExpiredSignatureError  过期
        jwt.InvalidTokenError      签名不对 / 格式不对（它的父类能一网打尽）
    """
    raise NotImplementedError("TODO: security.decode_token() —— jwt.decode，algorithms 必须硬编码")


# -----------------------------------------------------------------------------
# 3. 当前用户依赖
# -----------------------------------------------------------------------------


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """把 `Authorization: Bearer xxx` 变成一个真实的 User 对象。

    TODO ⑤：按这个顺序做，顺序不能乱（先验签名和 exp，再查用户，最后才谈角色）：
        1. `payload = decode_token(token)`
           - 抛 jwt.ExpiredSignatureError → `raise _unauthorized("登录已过期，请重新登录")`
           - 抛 jwt.InvalidTokenError     → `raise _unauthorized("登录状态无效")`
        2. `user_id = payload.get("sub")`；为空 → `_unauthorized("登录状态无效")`
        3. `user = db.get(User, user_id)`
           - `user is None or user.is_deleted` → `_unauthorized("账号不存在或已停用")`
             ★ 一定要查库，不要只信 Token 里的 role：
               管理员被降级、账号被停用后立刻生效，不用等 Token 过期
        4. `return user`

    全部失败路径都是 **401**（「我不知道你是谁」），一个 403 都没有 —— 角色的事归下一个函数。
    """
    raise NotImplementedError("TODO: security.get_current_user() —— 解析 Token → 查库 → 返回 User（见注释）")


def require_admin(user: User = Depends(get_current_user)) -> User:
    """垂直越权拦截：只有管理员能过（写图书、删图书、改库存）。

    TODO ⑥：`user.role != "admin"` 时
        `raise HTTPException(status.HTTP_403_FORBIDDEN, detail="需要管理员权限")`
    注意是 **403 不是 401**：他身份是有效的，只是没权限。
    用法：`admin: User = Depends(require_admin)`
    """
    raise NotImplementedError("TODO: security.require_admin() —— 非 admin 抛 403（见注释）")


def require_reader(user: User = Depends(get_current_user)) -> User:
    """借书 / 还书 / 预约 / 列表：读者和管理员都可以。

    TODO ⑦：`user.role not in ("reader", "admin")` → 403「需要读者权限」。
    用法：`user: User = Depends(require_reader)`
    """
    raise NotImplementedError("TODO: security.require_reader() —— 非 reader/admin 抛 403（见注释）")


def _unused_example_of_expiry() -> None:
    """（仅作提示，不用实现）本地验证 Token 过期的最快办法：

        ACCESS_TOKEN_EXPIRE_MINUTES=-1  →  重启后端  →  重新登录拿 Token  →  请求任何接口
        预期：401 + detail「登录已过期，请重新登录」（异常类型 ExpiredSignatureError）
    """
