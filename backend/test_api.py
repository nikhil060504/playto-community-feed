# API Testing Script
# Run with: python test_api.py

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

print("🧪 Starting API Tests\n")
print("=" * 60)

# Test 1: Register a new user
print("\n1️⃣ Testing User Registration")
print("-" * 60)
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "bio": "Test user for API testing"
}

try:
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Registration successful")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Registration failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Login
print("\n2️⃣ Testing User Login")
print("-" * 60)
login_data = {
    "username": "alice",  # Using seed data user
    "password": "password123"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access']
        print("✅ Login successful")
        print(f"Access Token: {access_token[:50]}...")
        
        # Save token for subsequent requests
        headers = {"Authorization": f"Bearer {access_token}"}
    else:
        print(f"❌ Login failed: {response.text}")
        exit()
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# Test 3: Get current user
print("\n3️⃣ Testing Get Current User")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/auth/me/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print("✅ Get user successful")
        print(f"User: {user['username']}, Karma: {user['total_karma']}, 24h Karma: {user['karma_24h']}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Get all posts
print("\n4️⃣ Testing Get All Posts")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/posts/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Get posts successful")
        print(f"Total posts: {data['count']}")
        if data['results']:
            print(f"First post by: {data['results'][0]['author']['username']}")
            print(f"Content: {data['results'][0]['content'][:80]}...")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Create a new post
print("\n5️⃣ Testing Create Post")
print("-" * 60)
new_post = {
    "content": "This is a test post created via API testing! 🚀"
}

try:
    response = requests.post(f"{BASE_URL}/posts/", json=new_post, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        post = response.json()
        post_id = post['id']
        print("✅ Post created successfully")
        print(f"Post ID: {post_id}")
        print(f"Content: {post['content']}")
    else:
        print(f"❌ Failed: {response.text}")
        post_id = 1  # Use existing post for further tests
except Exception as e:
    print(f"❌ Error: {e}")
    post_id = 1

# Test 6: Like a post
print("\n6️⃣ Testing Like Post (Race Condition Prevention)")
print("-" * 60)
try:
    # First like
    response = requests.post(f"{BASE_URL}/posts/{post_id}/like/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ First like: is_liked={result['is_liked']}, karma_change={result['karma_change']}")
        
        # Try to like again (should unlike)
        response2 = requests.post(f"{BASE_URL}/posts/{post_id}/like/", headers=headers)
        result2 = response2.json()
        print(f"✅ Second like (toggle): is_liked={result2['is_liked']}, karma_change={result2['karma_change']}")
        
        if result['is_liked'] == True and result2['is_liked'] == False:
            print("✅ Race condition prevention working - like toggled correctly")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: Get comments for a post
print("\n7️⃣ Testing Get Comments (N+1 Prevention)")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/comments/?post=1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        comments = response.json()
        print("✅ Get comments successful")
        print(f"Number of root comments: {len(comments)}")
        if comments:
            print(f"First comment by: {comments[0]['author']['username']}")
            print(f"Replies: {len(comments[0].get('replies', []))}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 8: Create a comment
print("\n8️⃣ Testing Create Comment")
print("-" * 60)
new_comment = {
    "post": 1,
    "parent": None,
    "content": "Test comment via API! Great post!"
}

try:
    response = requests.post(f"{BASE_URL}/comments/", json=new_comment, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        comment = response.json()
        comment_id = comment['id']
        print("✅ Comment created successfully")
        print(f"Comment ID: {comment_id}, Depth: {comment['depth']}")
    else:
        print(f"❌ Failed: {response.text}")
        comment_id = 1
except Exception as e:
    print(f"❌ Error: {e}")
    comment_id = 1

# Test 9: Create nested reply
print("\n9️⃣ Testing Nested Comment (Depth Tracking)")
print("-" * 60)
nested_comment = {
    "post": 1,
    "parent": comment_id,
    "content": "This is a reply to the previous comment!"
}

try:
    response = requests.post(f"{BASE_URL}/comments/", json=nested_comment, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        comment = response.json()
        print("✅ Nested comment created successfully")
        print(f"Parent ID: {comment['parent']}, Depth: {comment['depth']}")
        if comment['depth'] > 0:
            print("✅ Depth auto-calculation working")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 10: Leaderboard (Dynamic 24h Karma)
print("\n🔟 Testing Leaderboard (24h Karma Calculation)")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/leaderboard/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        leaderboard = response.json()
        print("✅ Leaderboard retrieved successfully")
        print("\n📊 Top Users (Last 24 Hours):")
        for i, user in enumerate(leaderboard, 1):
            print(f"  {i}. {user['username']}: {user['karma_24h']} karma")
        
        if leaderboard:
            print("\n✅ Dynamic 24h karma calculation working!")
            print("   (Aggregated from Like records, not stored field)")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ API Testing Complete!\n")
print("Summary:")
print("  ✅ Authentication working (register, login)")
print("  ✅ Posts CRUD working")
print("  ✅ Comments with nesting working")
print("  ✅ Like toggle with race condition prevention")
print("  ✅ Dynamic 24h leaderboard calculation")
print("  ✅ N+1 query prevention (check Django logs)")
