import requests
import os
import sys

def test_api_endpoints():
    """Test API endpoints after deployment"""
    
    
    base_url = os.getenv('API_BASE_URL', 'http://34.93.29.106')
    
    print(f"Testing API at: {base_url}")
    
    
    print("\n✓ Testing GET /products...")
    response = requests.get(f"{base_url}/products")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"  Response: {response.json()}")
    
    
    print("\n✓ Testing POST /products...")
    new_product = {
        "name": "CI/CD Test Product",
        "price": 99.99,
        "description": "Created by CI/CD pipeline",
        "quantity": 1
    }
    response = requests.post(f"{base_url}/products", json=new_product)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    product_id = response.json().get('id')
    print(f"  Created product ID: {product_id}")
    
    
    print(f"\n✓ Testing GET /products/{product_id}...")
    response = requests.get(f"{base_url}/products/{product_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"  Product: {response.json()}")
    
    
    print(f"\n✓ Testing PUT /products/{product_id}...")
    updated_product = {
        "name": "Updated Test Product",
        "price": 149.99
    }
    response = requests.put(f"{base_url}/products/{product_id}", json=updated_product)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    
    print(f"\n✓ Testing DELETE /products/{product_id}...")
    response = requests.delete(f"{base_url}/products/{product_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    print("\n All tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"\n Tests failed: {e}")
        sys.exit(1)