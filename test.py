from requests import get, post, delete

print(get('http://localhost:5000/api/ads').json())
print(get('http://localhost:5000/api/ads').json())
print(get('http://localhost:5000/api/ads/1').json())
print(get('http://localhost:5000/api/ads/111111111111').json())  # нет пользователя
print(get('http://localhost:5000/api/ads/qeqweqwe').json())  # не число

