import os
import time
from dotenv import load_dotenv
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActLibraryAgent
from src.telemetry.metrics import ComparisonDashboard

load_dotenv()

def benchmark():
    print("\n" + "="*70)
    print("🚀 BẮT ĐẦU CHẠY BENCHMARK: BASELINE vs REACT AGENT")
    print("="*70 + "\n")

    try:
        provider = OpenAIProvider(model_name=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"))
        agent = ReActLibraryAgent(provider=provider, max_iter=5)
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {str(e)}")
        return

    # Đường dẫn lưu file kết quả
    dashboard = ComparisonDashboard(save_path="logs/benchmark_results.json")

    # Danh sách các Test Case của bạn
    test_cases = [
        {"id": "TC1", "desc": "Sách mượn nhiều nhất", "query": "Sách nào được mượn nhiều nhất ở thư viện?"},
        
        {"id": "TC2_1", "desc": "Trạng thái sách (Còn)", "query": "Tôi muốn mượn 'Computer Vision in Action', có còn không?"},
        {"id": "TC2_2", "desc": "Trạng thái sách (Hết)", "query": "Tôi muốn mượn 'The Secure Coding Handbook', có còn không?"},
        {"id": "TC2_3", "desc": "Trạng thái sách (Không tồn tại)", "query": "Có sách 'Harry Potter' không?"},
        
        {"id": "TC3_1", "desc": "User (Có mượn sách)", "query": "Tôi là STU00061, tôi đang mượn bao nhiêu cuốn?"},
        {"id": "TC3_2", "desc": "User (Không mượn)", "query": "Tôi là STU00001, tôi đang mượn gì?"},
        
        {"id": "TC4_1", "desc": "Tóm tắt (Có sách)", "query": "Hãy giới thiệu sơ qua nội dung sách 'MLOps'"},
        {"id": "TC4_2", "desc": "Tóm tắt (Không sách)", "query": "Sách 'Sử Thi Kiếm Khách' viết về cái gì?"},
        
        {"id": "TC5_1", "desc": "Tác giả (Có sách)", "query": "Tác giả 'Nam Clark' có bao nhiêu cuốn sách?"},
        {"id": "TC5_2", "desc": "Tác giả (Không sách)", "query": "Tác giả 'Nguyễn Nhật Ánh' có sách không?"},
        
        {"id": "TC6_1", "desc": "Out-ofbenchmark (Thời tiết)", "query": "Thời tiết hôm nay ở Hà Nội sao?"},
        {"id": "TC6_2", "desc": "Out-of-Domain (Toán)", "query": "2 + 2 bằng mấy?"}
    ]

    total_tests = len(test_cases)
    
    for idx, tc in enumerate(test_cases, 1):
        print(f"🔄 Đang chạy [{idx}/{total_tests}] {tc['id']}: {tc['desc']}")
        print(f"   Query: \"{tc['query']}\"")
        
        print("   -> Running Baseline...")
        agent.chat_history = [{"role": "system", "content": agent.chat_history[0]["content"]}]
        base_ans, base_metric = agent.run_baseline(tc['query'])
        dashboard.add_metric(base_metric)
        
        print("   -> Running ReAct Agent...")
        agent.chat_history = [{"role": "system", "content": agent.chat_history[0]["content"]}]
        react_ans, react_metric = agent.run_agent(tc['query'])
        dashboard.add_metric(react_metric)
        
        print(f"   ✅ Xong! (ReAct mất {react_metric.latency}s, {react_metric.total_steps} bước)")
        print("-" * 50)
        
        # Chờ 1 chút để tránh rate limit của OpenAI (đặc biệt là tier free)
        time.sleep(1)

    # Lưu toàn bộ dữ liệu vào file JSON
    dashboard.save_to_file()
    
    print("\n🎉 HOÀN THÀNH BENCHMARK!")
    print(f"Đã lưu kết quả chi tiết tại: {dashboard.save_path}")
    
    # In ra một bảng tóm tắt nhỏ
    print("\n" + "="*80)
    print(f"{'Test Case':<10} | {'Method':<12} | {'Latency(s)':<10} | {'Steps':<6} | {'Tool Used'}")
    print("-" * 80)
    
    # Gom nhóm kết quả để in
    for i in range(0, len(dashboard.results), 2):
        base_m = dashboard.results[i]
        react_m = dashboard.results[i+1]
        
        tc_id = test_cases[i//2]['id']
        
        print(f"{tc_id:<10} | {'Baseline':<12} | {base_m.latency:<10} | {base_m.total_steps:<6} | N/A")
        tool_str = ", ".join(set(react_m.tool_calls)) if react_m.tool_calls else "None"
        print(f"{'':<10} | {'ReAct Agent':<12} | {react_m.latency:<10} | {react_m.total_steps:<6} | {tool_str}")
        print("-" * 80)

if __name__ == "__main__":
    benchmark()