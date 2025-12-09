# FCKR – The Ultimate Brute-Forcer

**FCKR** is a powerful CLI tool for **penetration testers** and **security researchers** that performs:

* **HTTP brute forcing** (placeholder replacement & parameter fuzzing)
* **XSS reflection testing** (exact payload match detection)

Supports both:

* **Traditional mode** using `FCK` placeholder
* **Raw request mode** using full HTTP request files

> Developed by **[@IMApurbo](https://github.com/imapurbo)**
> ⚠️ *Use responsibly. Authorized testing only.*

---

## 🚀 Features

### 🔹 Dual Modes

* **brute** — wordlist-based brute forcing
* **xss** — reflected XSS detection

### 🔹 Traditional Mode

Place `FCK` in:

* URL (GET fuzzing)
* Body (POST fuzzing)

Each wordlist entry replaces `FCK`.

### 🔹 Raw Request Mode (`-R`)

Supports full HTTP request files:

```
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{"user":"admin","pass":"FCK"}
```

Raw mode features include:

* Auto-extract method, URL, headers, and body
* Parameter-specific fuzzing (`-p param`)
* FCK placeholder substitution when `-p` is not used
* JSON, form, query, and fallback raw-body fuzzing

**Real behaviors matched to your code:**

* JSON → parsed/replaced as dict
* Form data → parsed with `parse_qs()`
* Unknown content-type → fallback string replace
* Missing parameter → *warning printed*

### 🔹 Parameter-Specific Fuzzing (`-p`)

Fuzzes:

* Query parameters
* JSON keys
* Form-encoded fields

Missing key → warning.

### 🔹 URL Encoding Support (`--encode`)

Payloads encoded using `quote()`.

### 🔹 Header Merging (`-H`)

Headers added using this format:

```
Header1:Value;Header2:Value
```

Invalid format → warning.

### 🔹 Filtering (`-f`)

Supports:

| Field | Meaning        |
| ----- | -------------- |
| `s`   | status code    |
| `l`   | content length |
| `c`   | body content   |

Types:

* `e` → exact
* `c` → contains
* `nc` → not contains

### 🔹 Debug Mode (`-d`)

Displays:

* Requests sent
* Filter mismatches
* Non-reflected XSS payloads

### 🔹 Threading (`-T`)

Uses ThreadPoolExecutor
Default: **10 threads**

### 🔹 Fetch Raw Response (`-r`)

Fetch raw HTML for a specific word/payload.


---

## 📦 Installation

```bash
pip install fckr
```

---

## ⚙️ Usage

```bash
fckr <mode> <options>
```

### Modes

| Mode  | Description            |
| ----- | ---------------------- |
| brute | Wordlist brute forcing |
| xss   | XSS reflection testing |

---

## 🧰 Options

### Common Options

| Option                   | Description                |
| ------------------------ | -------------------------- |
| `-u`, `--url`            | URL containing `FCK`       |
| `-b`, `--body`           | POST body containing `FCK` |
| `-w`, `--wordlist`       | Wordlist file              |
| `-m`, `--method`         | GET/POST                   |
| `-H`, `--header`         | Extra headers              |
| `-t`, `--timeout`        | Timeout (seconds)          |
| `-T`, `--threads`        | Thread count               |
| `-d`, `--debug`          | Debug mode                 |
| `-o`, `--output`         | Save results to file       |
| `-r`, `--fetch-response` | Fetch full raw HTML        |
| `--encode`               | URL-encode payloads        |

### Raw Request Options

| Option | Description                          |
| ------ | ------------------------------------ |
| `-R`   | HTTP raw request file                |
| `-p`   | Fuzz specific parameter (query/json) |

### Notes (matches your code exactly)

* `-u` **or** `-R` required
* In **raw mode**:

  * `-u`, `-b`, `-m` → **ignored**
  * If no `-p` → FCK replacement used
* JSON/form/query all supported
* Unknown content-type → fallback string replace
* Missing parameter → warning shown

---

## 🔍 Filter Syntax

```
<field>:<type>:<value>
```

Examples:

```bash
-f s:e:200
-f c:nc:error
-f c:c:"success"
-f l:e:1024
```

---

## 🔧 Examples

### 1️⃣ Simple GET Brute

```bash
fckr brute -u "https://test.com/?id=FCK" -w ids.txt
```

### 2️⃣ POST Brute

```bash
fckr brute -u "https://test.com/login" -b "user=admin&pass=FCK" -w pass.txt
```

### 3️⃣ Raw Request Placeholder (FCK)

```bash
fckr brute -R req.txt -w list.txt
```

### 4️⃣ Raw Request + Parameter Fuzzing

```bash
fckr brute -R req.txt -p password -w pass.txt
```

### 5️⃣ Fetch Full Response

```bash
fckr brute -u "https://a.com/?q=FCK" -w list.txt -r admin
```

### 6️⃣ XSS Reflection Test

```bash
fckr xss -u "https://test.com/?q=FCK" -w payloads.txt --encode
```

### 7️⃣ Raw JSON XSS

```bash
fckr xss -R req.txt -p search -w payloads.txt
```

---

## 📂 Wordlist Examples

**Brute-force list:**

```
admin
test123
root
```

**XSS payload list:**

```
<script>alert(1)</script>
<img src=x onerror=alert(1)>
```

---

## 🛠 Development

```bash
git clone https://github.com/IMApurbo/fckr
cd fckr
pip install -r requirements.txt
```

Run:

```bash
python -m fckr brute -u "https://example.com/?q=FCK" -w list.txt
```

---

## ⚠️ Legal Disclaimer

Use only with explicit permission.
Unauthorized testing is illegal.

---

## ⭐ Credits

**Created by:** [IMApurbo](https://github.com/imapurbo)

---
## 📃 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
