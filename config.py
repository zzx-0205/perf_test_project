# 被测系统基地址
HOST = "https://jsonplaceholder.typicode.com"

# 并发用户数
USERS = 100

# 用户启动速率（每秒增加的用户数）
SPAWN_RATE = 10

# 压测持续时间（秒）
RUN_TIME = 60

# 性能断言阈值
MAX_FAIL_RATE = 0.01      # 失败率不得超过 1%
MAX_P95_RESPONSE = 1500    # P95 响应时间不得超过 500ms