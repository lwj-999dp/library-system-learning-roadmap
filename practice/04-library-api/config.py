# -*- coding: utf-8 -*-
"""config.py · 配置读取（★ 这个文件是完整的，不需要你改）

对应文档
--------
docs/05-鉴权与安全.md 「F. 密钥与配置管理」+ 练习 2 的 app/config.py

这个文件要做什么
----------------
把「会随环境变化、且不能提交进 Git」的东西全部集中到一处：
数据库地址、JWT 密钥、Token 有效期、SQL 日志开关、CORS 白名单、bcrypt 代价因子。

优先级：**真实环境变量 > .env 文件 > 代码里的默认值**。
这样同一份代码在本地、测试、生产跑，只需要换环境变量，不用改一行代码。

为什么不用 pydantic-settings
----------------------------
文档里用的是 `pydantic_settings.BaseSettings`，也很好。但本项目 requirements.txt
里没有这个包，为了「clone 下来就能跑」，这里用一个 30 行的 .env 解析器，
零额外依赖，行为完全一样，还顺便让你看清「.env 到底是怎么生效的」。

验收标准
--------
- [ ] `python -c "import config; print(config.settings.database_url)"` 能读到 .env 里的值
- [ ] 设了同名环境变量时，环境变量赢过 .env（可以用 `$env:DATABASE_URL="x"` 试）
- [ ] 代码里搜不到任何真实密码 / 密钥，只有占位符
- [ ] `settings.jwt_secret_is_default` 在用了示例密钥时为 True（main.py 会据此打警告）
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# 本项目根目录（config.py 所在目录）
BASE_DIR: Path = Path(__file__).resolve().parent

# 用于识别「密钥还是示例值」的标记，千万不要在 .env 里用这个值
DEFAULT_JWT_SECRET: str = "change-me-generate-with-secrets-token-urlsafe-48"


def load_dotenv(path: Path) -> None:
    """把 .env 文件里的键值对写进 os.environ。

    规则（和主流 dotenv 库一致）：
      * 已经存在的环境变量**不覆盖** —— 真实环境变量优先级更高
      * 空行、以 # 开头的注释行跳过
      * 值两边的引号会被去掉，`KEY=value  # 注释` 里的行内注释不处理（避免误伤密码）
      * 解析失败不抛异常 —— 配置问题不应该让程序起不来
      * 用 `utf-8-sig` 读：Windows 记事本保存的 UTF-8 文件带 BOM，
        不然第一个键名会变成 "\ufeffDATABASE_URL"，静默失效（这个坑很常见）
    """
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _env_str(name: str, default: str) -> str:
    value = os.environ.get(name)
    return default if value is None or value == "" else value


def _env_int(name: str, default: int) -> int:
    """读整数配置：值不合法时退回默认值，并打一行警告（不崩）。"""
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"[config] ⚠️ {name}={raw!r} 不是整数，已退回默认值 {default}")
        return default


def _env_bool(name: str, default: bool) -> bool:
    """读布尔配置：1/true/yes/on 都算真（大小写不敏感）。"""
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_list(name: str, default: list[str]) -> list[str]:
    """读逗号分隔的列表配置（用于 CORS 白名单）。"""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# 先加载 .env，再构造 Settings —— 顺序不能反
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """全项目唯一的配置对象。想加配置项就在这里加一个字段。

    frozen=True：配置是只读的，避免运行时被某处代码悄悄改掉。
    """

    # ---------- 数据库 ----------
    database_url: str = field(
        default_factory=lambda: _env_str(
            "DATABASE_URL",
            # 默认值故意用一个连不上的占位密码：
            # 让你第一眼就发现「.env 忘了配」，而不是连到别人的库上
            "mysql+pymysql://root:your_password_here@127.0.0.1:3306/library?charset=utf8mb4",
        )
    )

    # ---------- JWT（阶段 5）----------
    # 没有默认密钥：这是故意的。密钥必须由 .env 提供，代码里绝不硬编码真密钥。
    jwt_secret: str = field(default_factory=lambda: _env_str("JWT_SECRET", DEFAULT_JWT_SECRET))
    jwt_algorithm: str = field(default_factory=lambda: _env_str("JWT_ALGORITHM", "HS256"))
    access_token_expire_minutes: int = field(
        default_factory=lambda: _env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )
    bcrypt_rounds: int = field(default_factory=lambda: _env_int("BCRYPT_ROUNDS", 12))

    # ---------- 其他 ----------
    sql_echo: bool = field(default_factory=lambda: _env_bool("SQL_ECHO", False))
    cors_origins: list[str] = field(
        default_factory=lambda: _env_list(
            "CORS_ORIGINS", ["http://localhost:5173", "http://127.0.0.1:5173"]
        )
    )

    @property
    def jwt_secret_is_default(self) -> bool:
        """密钥还是示例值？是的话 main.py 会在启动日志里打一条醒目警告。"""
        return self.jwt_secret == DEFAULT_JWT_SECRET

    @property
    def database_url_is_placeholder(self) -> bool:
        """数据库密码还是占位符？是的话 main.py 会提醒你去配 .env。"""
        return "your_password_here" in self.database_url


settings = Settings()
