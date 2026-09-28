-- =============================================================================
-- schema.sql · 图书管理系统建库建表脚本（MySQL 8.0+ / 8.4 实测通过）
-- =============================================================================
-- 这个文件是【基础设施】，不是练习。直接整份执行即可：
--
--     mysql -u root -p < schema.sql
--
-- 设计要点（每一处都在 docs/03-数据库与SQL.md 里讲过，建议逐行看懂）：
--   1. 4 张表：users / books / borrow_records / reservations
--   2. 全部 InnoDB（要事务 + 行锁）、utf8mb4（中文 + emoji）
--   3. 软删除 is_deleted，绝不物理 DELETE（有借阅历史的书删不掉，见文件末尾演示）
--   4. 借阅状态【不落库】：由 return_date / due_date 和今天推导，避免两份真相
--   5. 软删除 + 唯一索引的冲突：用【生成列】解法（isbn_active），删掉的书不再占 ISBN
--   6. 幂等：可重复执行（先按依赖倒序 DROP TABLE，再重建）
-- =============================================================================

CREATE DATABASE IF NOT EXISTS library
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE library;

SET NAMES utf8mb4;

-- 建表前先关外键检查，避免 DROP 顺序问题；脚本结尾会重新打开
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS borrow_records;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;


-- -----------------------------------------------------------------------------
-- 1. users · 用户表（管理员 + 读者）
-- -----------------------------------------------------------------------------
CREATE TABLE users (
  id            VARCHAR(16)  NOT NULL              COMMENT '编号：A001=管理员 / R001=读者',
  name          VARCHAR(50)  NOT NULL              COMMENT '姓名',
  phone         VARCHAR(20)      NULL              COMMENT '手机号，唯一；NULL 可重复',
  role          ENUM('admin','reader') NOT NULL DEFAULT 'reader' COMMENT '角色，只由后端赋值',
  password_hash VARCHAR(100) NOT NULL DEFAULT ''   COMMENT 'bcrypt 哈希（$2b$12$...），绝不存明文',
  is_deleted    TINYINT(1)   NOT NULL DEFAULT 0    COMMENT '软删除：0=正常 1=已删除',
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  -- 手机号唯一：注意 MySQL 里 NULL 不参与唯一性判断，可以有多行 NULL
  UNIQUE KEY uk_users_phone (phone),
  -- 按角色查用户列表时走这条索引（带上 is_deleted 满足最左前缀）
  KEY idx_users_role (role, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';


-- -----------------------------------------------------------------------------
-- 2. books · 图书表
-- -----------------------------------------------------------------------------
CREATE TABLE books (
  id         VARCHAR(16)   NOT NULL              COMMENT '图书编号 B001（业务编号，非自增）',
  isbn       VARCHAR(20)       NULL              COMMENT 'ISBN，允许 NULL',
  title      VARCHAR(200)  NOT NULL              COMMENT '书名',
  author     VARCHAR(100)  NOT NULL DEFAULT ''   COMMENT '作者',
  publisher  VARCHAR(100)  NOT NULL DEFAULT ''   COMMENT '出版社',
  category   VARCHAR(50)   NOT NULL DEFAULT ''   COMMENT '分类',
  price      DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '定价：金额一律用 DECIMAL，不用 FLOAT',
  stock      INT           NOT NULL DEFAULT 0    COMMENT '总库存（管理员设定）',
  available  INT           NOT NULL DEFAULT 0    COMMENT '可借数，只能由 sync_book() 重算，禁止 += / -=',
  cover_url  VARCHAR(255)  NOT NULL DEFAULT ''   COMMENT '封面地址',
  is_deleted TINYINT(1)    NOT NULL DEFAULT 0    COMMENT '软删除：0=在架 1=已下架',
  created_at DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                           ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间，由 MySQL 自动维护',

  -- ★ 软删除 + 唯一索引的推荐解法：生成列
  --   删除时 isbn 还在，但 isbn_active 变成 NULL，而 NULL 不参与唯一性判断，
  --   于是同一个 ISBN 可以被新书重新使用。
  isbn_active VARCHAR(20) GENERATED ALWAYS AS (IF(is_deleted = 0, isbn, NULL)) STORED
                          COMMENT '在架时的 ISBN，用于唯一约束',

  PRIMARY KEY (id),
  UNIQUE KEY uk_books_isbn_active (isbn_active),
  KEY idx_books_title (title),
  KEY idx_books_category (category, is_deleted),
  KEY idx_books_available (is_deleted, available),
  -- CHECK 是最后一道防线：库存永远不可能为负、可借数不可能超过总库存
  CONSTRAINT ck_books_stock CHECK (stock >= 0 AND available >= 0 AND available <= stock)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书表';


-- -----------------------------------------------------------------------------
-- 3. borrow_records · 借阅记录表（事实表：库存由它推导）
-- -----------------------------------------------------------------------------
CREATE TABLE borrow_records (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  user_id     VARCHAR(16) NOT NULL COMMENT '读者编号',
  book_id     VARCHAR(16) NOT NULL COMMENT '图书编号',
  borrow_date DATE        NOT NULL COMMENT '借出日',
  due_date    DATE        NOT NULL COMMENT '应还日',
  return_date DATE            NULL COMMENT '归还日；NULL = 仍在借（借阅状态由此推导，不落库）',
  renew_count TINYINT     NOT NULL DEFAULT 0 COMMENT '续借次数',
  created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  -- 以下三条索引分别服务：查某人的在借、查某本书的在借、查逾期未还
  KEY idx_br_user (user_id, return_date),
  KEY idx_br_book (book_id, return_date),
  KEY idx_br_due  (return_date, due_date),
  CONSTRAINT fk_br_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_br_book FOREIGN KEY (book_id) REFERENCES books(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='借阅记录表';


-- -----------------------------------------------------------------------------
-- 4. reservations · 预约表（ready 状态会占用库存！）
-- -----------------------------------------------------------------------------
CREATE TABLE reservations (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  user_id      VARCHAR(16) NOT NULL COMMENT '预约人',
  book_id      VARCHAR(16) NOT NULL COMMENT '被预约图书',
  status       ENUM('pending','ready','fulfilled','expired','cancelled')
               NOT NULL DEFAULT 'pending'
               COMMENT 'pending=排队中 ready=已到书待取 fulfilled=已借走 expired=已过期 cancelled=已取消',
  reserve_date DATE     NOT NULL COMMENT '预约日',
  expire_date  DATE     NOT NULL COMMENT '到期日；ready 之后即取书截止日',
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_res_book   (book_id, status),
  KEY idx_res_user   (user_id, status),
  KEY idx_res_expire (status, expire_date),
  CONSTRAINT fk_res_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_res_book FOREIGN KEY (book_id) REFERENCES books(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预约表';


-- -----------------------------------------------------------------------------
-- 演示数据（够阶段 3 的 20 道 SQL 练习题用）
-- -----------------------------------------------------------------------------
-- ⚠️ 这里的 password_hash 故意留空，登录会失败。
--    阶段 5 请运行 practice/04-library-api/seed.py 生成带真实 bcrypt 哈希的用户。
INSERT INTO users (id, name, phone, role) VALUES
  ('A001', '管理员', '13800000001', 'admin'),
  ('R001', '张三',  '13800000002', 'reader'),
  ('R002', '李四',  '13800000003', 'reader'),
  ('R003', '王五',  '13800000004', 'reader');

INSERT INTO books (id, isbn, title, author, publisher, category, price, stock, available) VALUES
  ('B001', '9787115428028', 'Python 编程：从入门到实践', 'Eric Matthes',   '人民邮电出版社', '编程',  89.80, 1, 1),
  ('B002', '9787111544937', '深入理解计算机系统',       'Randal Bryant',  '机械工业出版社', '计算机', 139.00, 3, 3),
  ('B003', '9787111213826', '算法导论',                 'Thomas Cormen',  '机械工业出版社', '计算机', 128.00, 2, 2),
  ('B004', '9787020002207', '红楼梦',                   '曹雪芹',         '人民文学出版社', '文学',   59.70, 5, 5),
  ('B005', '9787544270878', '解忧杂货店',               '东野圭吾',       '南海出版公司',   '文学',   39.50, 2, 2);

-- 两条借阅记录：B001 被借走 1 本（所以 available 改成 0），B003 正常在借
INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date, return_date) VALUES
  ('R001', 'B001', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), NULL),
  ('R002', 'B003', DATE_SUB(CURDATE(), INTERVAL 40 DAY), DATE_SUB(CURDATE(), INTERVAL 10 DAY), NULL);

UPDATE books SET available = 0 WHERE id = 'B001';
UPDATE books SET available = 1 WHERE id = 'B003';

-- 一条 ready 预约：B002 的 1 本被占位（available 因此从 3 变 2）
INSERT INTO reservations (user_id, book_id, status, reserve_date, expire_date) VALUES
  ('R003', 'B002', 'ready', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 3 DAY));

UPDATE books SET available = 2 WHERE id = 'B002';


-- =============================================================================
-- 自检（可选，手动执行）
-- =============================================================================
-- ① 4 张表都在？
-- SHOW TABLES;

-- ② 索引命中情况（key 列应该有值，type 不要是 ALL）
-- EXPLAIN SELECT id, title FROM books WHERE category = '计算机' AND is_deleted = 0;

-- ③ 库存守恒校验：结果必须是 0
-- SELECT (SELECT IFNULL(SUM(stock - available), 0) FROM books WHERE is_deleted = 0)
--      - (SELECT COUNT(*) FROM borrow_records WHERE return_date IS NULL)
--      - (SELECT COUNT(*) FROM reservations  WHERE status = 'ready') AS diff;

-- ④ 亲手触发一次外键错误：有借阅记录的书删不掉 → ERROR 1451
-- DELETE FROM books WHERE id = 'B001';
