import json
import subprocess
import tempfile

# Wczytanie danych z pliku
with open("dane.json", "r", encoding="utf-8") as f:
    data = json.load(f)

url = "http://127.0.0.1:5001/register"
headers = [
    "-H", "Host: 127.0.0.1:5001",
    "-H", "accept: application/json",
    "-H", "X-Service-UUID: 8ede9428-68d1-4985-86d8-cf9825d4216d",
    "-H", "Content-Type: application/json"
]

for i, record in enumerate(data, 1):
    # Zapisz JSON do pliku tymczasowego
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmpfile:
        json.dump(record, tmpfile, ensure_ascii=False, indent=4)
        tmpfile.flush()

        # Wyświetlenie danych
        print(f"\n📤 Zapytanie {i}")
        print(f"➡️  Adres e-mail: {record.get('email', '[brak]')}")
        print("➡️  Ciało zapytania JSON:")
        print(json.dumps(record, ensure_ascii=False, indent=4))

        # Budowanie komendy curl
        cmd = ["curl", "-i", "-s", "-k", "-X", "POST"] + headers + ["--data-binary", f"@{tmpfile.name}", url]

        # Wysyłka
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("\n✅ Odpowiedź serwera:")
        print(result.stdout)
        print("=" * 100)
