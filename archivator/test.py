import requests

headers = {
    "Authorization" : "Bearer hxosCipxZrOhnzZfnAG82Xj0KZrSj8Z0UKR51lXI",
}
resp = requests.get("http://0.0.0.0:8081/archivator/files-list/", headers=headers)
print(resp.text)
