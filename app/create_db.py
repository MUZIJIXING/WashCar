import sqlite3

# 连接到SQLite数据库（如果数据库不存在，则会自动创建）
conn = sqlite3.connect('washcar.db')
cursor = conn.cursor()

# 创建用户表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# 创建车辆表
cursor.execute('''
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    time TEXT NOT NULL,
    expenses REAL NOT NULL
)
''')

# 插入一些测试数据到用户表
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'password'))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('user1', 'pass1'))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('user2', 'pass2'))

# 插入一些测试数据到车辆表
cursor.execute("INSERT INTO cars (model, start, end, time, expenses) VALUES (?, ?, ?, ?, ?)",
               ('ModelX', '2023-07-01 10:00', '2023-07-01 12:00', '2 hours', 30.0))
cursor.execute("INSERT INTO cars (model, start, end, time, expenses) VALUES (?, ?, ?, ?, ?)",
               ('ModelY', '2023-07-01 13:00', '2023-07-01 14:30', '1.5 hours', 20.0))
cursor.execute("INSERT INTO cars (model, start, end, time, expenses) VALUES (?, ?, ?, ?, ?)",
               ('ModelZ', '2023-07-01 15:00', '2023-07-01 15:45', '45 minutes', 15.0))

# 提交事务
conn.commit()

# 关闭数据库连接
conn.close()

print("数据库和表已创建，并插入了测试数据。")
