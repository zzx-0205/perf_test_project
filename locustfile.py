import json
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import config


class JSONPlaceholderUser(HttpUser):
    """
    模拟真实用户行为：
    - 大部分时间在浏览（GET 列表）
    - 偶尔查看文章详情
    - 低频创建新文章（POST）
    """
    wait_time = between(1, 3)  # 用户操作间隔 1-3 秒，模拟真实思考时间
    host = config.HOST

    # ----- 任务权重：模拟读写比例 -----
    @task(6)  # 最高频：浏览列表
    def get_all_posts(self):
        with self.client.get("/posts", name="GET /posts", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"GET /posts 状态码异常: {resp.status_code}")

    @task(2)  # 中频：查看单篇文章
    def get_single_post(self):
        post_id = 1  # 可扩展为随机 ID
        with self.client.get(f"/posts/{post_id}", name="GET /posts/{id}", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 404:
                # 如果是 404，也标记为成功（因为接口行为如此）
                resp.success()
            else:
                resp.failure(f"GET /posts/{post_id} 状态码异常: {resp.status_code}")

    @task(1)  # 低频：创建新帖子（写操作）
    def create_post(self):
        headers = {"Content-type": "application/json"}
        data = {
            "title": "foo",
            "body": "bar",
            "userId": 1
        }
        with self.client.post("/posts", name="POST /posts", json=data, headers=headers, catch_response=True) as resp:
            if resp.status_code == 201:
                resp.success()
            else:
                resp.failure(f"POST /posts 状态码异常: {resp.status_code}")


# ----- 全局事件：压测结束后自动断言关键指标 -----
@events.quitting.add_listener
def check_performance_assertions(environment, **kwargs):
    """
    在 Locust 结束运行时自动检查：
    1. 总失败率是否超标
    2. P95 响应时间是否超标
    如果超标，则标记退出码为 1（CI 构建失败）
    """
    if not isinstance(environment.runner, MasterRunner):
        stats = environment.stats.total
        total_requests = stats.num_requests
        total_failures = stats.num_failures

        # 避免除 0
        if total_requests > 0:
            fail_rate = total_failures / total_requests
            p95 = stats.get_response_time_percentile(0.95)

            print("\n" + "=" * 50)
            print("📊 性能测试结果汇总")
            print(f"总请求数: {total_requests}")
            print(f"失败请求: {total_failures}")
            print(f"失败率: {fail_rate:.2%}")
            print(f"平均响应时间: {stats.avg_response_time:.0f} ms")
            print(f"P95 响应时间: {p95:.0f} ms")
            print("=" * 50)

            # 断言失败率
            if fail_rate > config.MAX_FAIL_RATE:
                print(f"❌ 失败率 {fail_rate:.2%} 超过阈值 {config.MAX_FAIL_RATE:.2%}")
                environment.process_exit_code = 1

            # 断言 P95 响应时间
            if p95 > config.MAX_P95_RESPONSE:
                print(f"❌ P95 响应时间 {p95:.0f}ms 超过阈值 {config.MAX_P95_RESPONSE}ms")
                environment.process_exit_code = 1

            if environment.process_exit_code != 1:
                print("✅ 所有性能指标均达标！")