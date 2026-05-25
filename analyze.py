import csv
import sys
import os

def analyze_perf_results(csv_path: str):
    """读取 Locust 生成的 stats CSV 并输出关键指标"""
    if not os.path.exists(csv_path):
        print(f"❌ 找不到文件: {csv_path}")
        sys.exit(1)

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("CSV 文件为空")
        return

    # 聚合行通常在最后一行为 "Aggregated"
    aggregated = rows[-1]
    total_reqs = aggregated.get("Request Count", "0")
    failures = aggregated.get("Failure Count", "0")
    avg_resp = aggregated.get("Average Response Time", "0")
    p95 = aggregated.get("95%", "0")

    print("\n" + "="*50)
    print("📊 性能测试结果分析")
    print(f"总请求数: {total_reqs}")
    print(f"失败请求: {failures}")
    fail_rate = int(failures)/int(total_reqs) if int(total_reqs) > 0 else 0
    print(f"失败率: {fail_rate:.2%}")
    print(f"平均响应时间: {avg_resp} ms")
    print(f"P95 响应时间: {p95} ms")

    # 可以在这里添加历史数据对比逻辑
    # 比如读取上一次的 CSV 做 diff

    # 简单阈值判断
    p95_threshold = 5700
    if float(p95) > p95_threshold:
        print(f"⚠️ 警告：P95 ({p95}ms) 超过阈值 {p95_threshold}ms")
    else:
        print(f"✅ P95 指标达标 (< {p95_threshold}ms)")

    print("="*50 + "\n")

if __name__ == "__main__":
    # 默认读取最新生成的 stats CSV，也可以传入自定义路径
    target = "report/perf_result_stats.csv"
    if len(sys.argv) > 1:
        target = sys.argv[1]
    analyze_perf_results(target)