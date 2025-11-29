"""
测试客户端：用于测试API接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试健康检查接口...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_chat():
    """测试聊天接口"""
    print("=" * 60)
    print("测试聊天接口...")
    
    data = {
        "user_id": 1,
        "query": "我学Java多线程很吃力，接下来咋办？",
        "context": {}
    }
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"用户ID: {result['user_id']}")
        print(f"AI回复: {result['answer']}")
    else:
        print(f"错误: {response.text}")
    print()


def test_sync():
    """测试数据同步接口"""
    print("=" * 60)
    print("测试数据同步接口...")
    
    data = {
        "force": False
    }
    
    response = requests.post(
        f"{BASE_URL}/sync",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"成功: {result['success']}")
        print(f"消息: {result['message']}")
        print(f"同步数量: {result['synced_count']}")
    else:
        print(f"错误: {response.text}")
    print()


def test_stats():
    """测试统计接口"""
    print("=" * 60)
    print("测试统计接口...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


if __name__ == "__main__":
    print("\n开始测试 API 接口...\n")
    
    try:
        test_health()
        test_stats()
        # test_sync()  # 取消注释以测试同步接口
        # test_chat()  # 取消注释以测试聊天接口（需要配置API密钥）
        
        print("测试完成！")
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务已启动")
    except Exception as e:
        print(f"测试失败: {e}")

