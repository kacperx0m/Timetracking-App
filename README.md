# Aplikacja w trakcie tworzenia ...
**Pozostało do zrobienia:**

Backend:
- uwierzytelnianie

Frontend:
- wszystkie widoki
<br>
<br>
<br>
## Zadanie rekrutacyjne – Rejestracja czasu pracy  
**Backend: Django + Django REST Framework**  
**Frontend (mile widziane): Vue 3**

---

## 1. Cel projektu

Celem zadania jest stworzenie prostej aplikacji do rejestrowania czasu pracy pracowników z wykorzystaniem skanów kodów QR na tablecie oraz panelu administracyjnego do układania grafiku pracy. System ma umożliwiać generowanie raportów obecności i rozliczeń czasu pracy.

Projekt nie musi być produkcyjny, ale powinien pokazywać poprawne podejście architektoniczne, logikę biznesową oraz jakość kodu.

---

## 2. Zakres funkcjonalny (MVP)

### 2.1 Rejestracja czasu pracy (tablet / QR)

Pracownik skanuje kod QR na tablecie. Tablet wysyła żądanie do API rejestrujące zdarzenie.

**Obsługiwane typy zdarzeń:**
- `CHECK_IN` – wejście do pracy
- `CHECK_OUT` – wyjście z pracy
- `BREAK_START` – rozpoczęcie przerwy
- `BREAK_END` – zakończenie przerwy

**Wymagania:**
- każde zdarzenie zapisywane jest z:
  - pracownikiem
  - typem zdarzenia
  - znacznikiem czasu (timestamp)
  - identyfikatorem urządzenia (tablet)
- timestamp domyślnie generowany po stronie serwera
- walidacja logiki zdarzeń:
  - brak możliwości `CHECK_OUT` bez wcześniejszego `CHECK_IN`
  - brak możliwości `BREAK_END` bez `BREAK_START`
  - brak możliwości `BREAK_START` bez aktywnego `CHECK_IN`
  - blokada podwójnego `CHECK_IN` w tym samym dniu (lub zapis jako anomalia)

---

### 2.2 Grafik czasu pracy (administrator)

Administrator może definiować grafik pracy dla pracowników.

**Zakres grafiku:**
- pracownik
- data
- godzina rozpoczęcia i zakończenia
- typ dnia:
  - `WORK` – dzień roboczy
  - `OFF` – dzień wolny
  - `LEAVE` – urlop

**Operacje:**
- tworzenie, edycja i usuwanie wpisów grafiku
- pobranie grafiku:
  - dla jednego pracownika
  - dla konkretnej daty
  - dla zakresu dat

---

### 2.3 Raporty czasu pracy

System powinien generować raporty dla wybranego zakresu dat (np. tydzień, miesiąc).

**Raport per pracownik powinien zawierać:**
- planowaną liczbę godzin (z grafiku)
- faktycznie przepracowane godziny  
  (czas między `CHECK_IN` a `CHECK_OUT` pomniejszony o przerwy)
- spóźnienia  
  (wejście po planowanej godzinie rozpoczęcia, próg np. 5 minut)
- absencje  
  (dzień `WORK` w grafiku bez żadnego `CHECK_IN`)
- urlopy
- listę anomalii:
  - brak `CHECK_OUT`
  - przerwa bez zakończenia
  - wyjście bez wejścia
  - wielokrotne wejścia w tym samym dniu

Raport w formacie JSON. Eksport do CSV jako opcja dodatkowa.

---

## 3. Wymagania techniczne

### Backend (obowiązkowe)
- Python 3.11+
- Django
- Django REST Framework
- Baza danych: SQLite (wystarczająca na potrzeby zadania) - dowolna, sqlite, postgres
- Django Admin może pełnić rolę panelu administratora

### Frontend (mile widziane)
- Vue 3
- Prosty interfejs:
  - podgląd grafiku
  - lista zdarzeń
  - podgląd raportów

---

## 4. Proponowane endpointy API

### Rejestracja zdarzeń (tablet)

---

## $. Kryteria oceny

Kryterium oceny to głównie logika biznesowa i to istotniejsze niż techniczna lub wodotryski

- poprawność logiki biznesowej
- jakość i czytelność kodu
- struktura projektu Django
- sensowne użycie DRF (serializery, walidacje)
- obsługa błędów i anomalii
- testy

---

## $. Elementy dodatkowe (opcjonalne, punktowane)

- eksport raportów do CSV
- prosta autoryzacja (admin vs tablet)
- konfiguracja progu spóźnień
- podsumowania tygodniowe i miesięczne
- prosty frontend w Vue