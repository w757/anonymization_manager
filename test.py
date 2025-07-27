import json
import pandas as pd
from collections import Counter

# 1. Wczytanie danych
with open("dane-test.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# 2. Parametry metryk
k = 2
l = 2

# Statystyki do podsumowania
total_groups = 0
k_valid = 0
l_valid = 0

# Definicje identyfikatorow
QI = ['gender', 'age', 'postal_code']
SA = 'salary'

# Grupowanie
grouped = df.groupby(QI)

# Ocena metryk
for name, group in grouped:
    total_groups += 1
    print(f"Grupa: {name} (rozmiar={len(group)})")

    # K-anonimowość
    if len(group) >= k:
        k_valid += 1
        print(f"K-anonimowość (k >= {k})")
    else:
        print(f"K-anonimowość naruszona (k < {k})")

    # L-diversity
    unique_sensitive = group[SA].nunique()
    if unique_sensitive >= l:
        l_valid += 1
        print(f"L-diversity (l >= {l}), unikalnych: {unique_sensitive}")
    else:
        print(f"L-diversity naruszona,  unikalnych: {unique_sensitive}")

    print("-" * 60)

# 6. Podsumowanie
print(f"Liczba wszystkich grup: {total_groups}")
print(f"Spełniających k-anonimowość (k >= {k}): {k_valid} / {total_groups}")
print(f"Spełniających l-diversity (l >= {l}): {l_valid} / {total_groups}")

