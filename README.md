# FCKR – The Ultimate Brute Forcer

**FCKR** is a command-line tool designed for **security researchers** and **penetration testers** to perform HTTP brute-forcing or test XSS payload reflection. It supports two modes: `brute` for replacing `FCK` placeholders in URLs or POST bodies with wordlist entries, and `xss` for checking exact payload reflection in response HTML. Both modes require the `FCK` placeholder in the URL (for GET) or body (for POST).

> ✨ Developed by **[@IMApurbo](https://github.com/imapurbo)**  
> 🛡️ Use responsibly. Authorized testing only.

---

## 🚀 Features

- **Dual Modes**  
  - `brute`: Replace `FCK` placeholders in URLs or POST bodies with wordlist entries for brute-forcing.  
  - `xss`: Test XSS payloads for exact reflection in response HTML, replacing `FCK` placeholders.

- **HTTP Method Support**  
  Supports both `GET` and `POST` methods, with `FCK` required in URLs (GET) or bodies (POST).

- **Advanced Filtering (brute mode)**  
  - **Response Filters (-f)**: Filter based on:  
    - `s`: status code  
    - `l`: content length  
    - `c`: response body  
  - Filter types:  
    - `e`: exact match  
    - `c`: contains  
    - `nc`: not contains  

- **XSS Reflection Checking (xss mode)**  
  Detects exact payload reflection in response HTML, with optional URL encoding (`--encode`).

- **Response Inspection (-r)**  
  Fetch full HTML responses for any specific word or payload in both modes.

- **Output Saving (-o)**  
  Save results to a file (e.g., `result.txt`).

- **Custom Headers (-H)**  
  Add HTTP headers as a semicolon-separated string (e.g., `Cookie:JSESSIONID=abc123;Content-Type:application/json`).

- **Debug Mode (-d)**  
  Logs all requests and mismatched filters (brute mode) or non-reflected payloads (xss mode).

- **Threading (-T)**  
  Speed up operations with concurrent threads (default: 10).

- **Progress Bar**  
  Stylish visual feedback during operations.

- **User-Friendly Output**  
  Concise results like:  
  `Word: <word> | Status: <status> | Length: <length> | Time: <time>s` (brute mode)  
  `Payload: <payload> | Status: <status> | Length: <length> | Time: <time>s` (xss mode)

---

## 🧪 Installation

Install directly from PyPI:

```bash
pip install fckr
```

### Requirements

- Python 3.6+
- Terminal with ANSI support (Linux, macOS, or Windows Terminal)

---

## ⚙️ Usage

```bash
fckr <mode> <options>
```

### Modes

- `brute`: Perform traditional brute-forcing with wordlist and filters.
- `xss`: Test XSS payloads for exact reflection in response HTML.

### Common Flags

| Short | Long               | Description                                      | Required  | Default | Modes       |
| ----- | ------------------ | ------------------------------------------------ | --------- | ------- | ----------- |
| `-u`  | `--url`            | Target URL with `FCK` placeholder (e.g., `https://example.com/?q=FCK`) | ✅        | -       | brute, xss  |
| `-b`  | `--body`           | POST body with `FCK` (required for POST)         | 🟡        | -       | brute, xss  |
| `-w`  | `--wordlist`       | Path to wordlist file                            | 🟡        | -       | brute, xss  |
| `-m`  | `--method`         | HTTP method (`GET` or `POST`)                    | ❌        | GET     | brute, xss  |
| `-t`  | `--timeout`        | Timeout in seconds                               | ❌        | 5.0     | brute, xss  |
| `-f`  | `--filter`         | Filter response (e.g., `s:e:200`, `c:c:success`) | ❌        | -       | brute       |
| `-o`  | `--output`         | Save results to a file (e.g., `result.txt`)      | ❌        | -       | brute, xss  |
| `-r`  | `--fetch-response` | Fetch full HTML for a specific word/payload (any string) | ❌ | -       | brute, xss  |
| `-d`  | `--debug`          | Show request and filter/payload logs             | ❌        | False   | brute, xss  |
| `-H`  | `--header`         | HTTP headers (semicolon-separated)               | ❌        | -       | brute, xss  |
| `-T`  | `--threads`        | Number of concurrent threads                     | ❌        | 10      | brute, xss  |
|       | `--encode`         | URL-encode payloads before sending               | ❌        | False   | xss         |
| `-h`  | `--help`           | Show this help message and exit                  | ❌        | -       | brute, xss  |

> **Note**:  
> - `-w/--wordlist` is required unless `-r/--fetch-response` is used.  
> - `FCK` is required in the URL for GET requests or in the body for POST requests in both modes.  
> - `-b/--body` is required for POST requests and not allowed for GET requests.

---

## 🔍 Filtering Syntax (brute mode only)

Format:

```
<field>:<type>:<value>
```

### Fields

- `s`: HTTP status code
- `l`: Content length
- `c`: Response body content

### Types

- `e`: Exact match
- `c`: Contains
- `nc`: Not contains

### Examples

```bash
-f s:e:200             # Show only 200 OK
-f c:nc:error          # Show results that do not contain "error"
-f c:c:login           # Show responses containing "login"
-f l:e:1000            # Show only 1000-byte responses
```

---

## 🔧 Examples

### Brute Mode

**Brute-force with GET:**

```bash
fckr brute -u "https://test.com/search?q=FCK" -w list.txt -m GET
```

**POST request with body:**

```bash
fckr brute -u "http://test.com/search" -b "query=FCK&submit=1" -w list.txt -m POST
```

**Filter by content:**

```bash
fckr brute -u "https://test.com/?q=FCK" -w list.txt -f c:nc:"<h2>Not found</h2>"
```

**Inspect full response for a word:**

```bash
fckr brute -u "https://test.com/?q=FCK" -w list.txt -r "admin"
```

### XSS Mode

**Test XSS payloads with GET:**

```bash
fckr xss -u "https://test.com/search?q=FCK" -w payloads.txt -m GET --encode
```

**Test XSS payloads with POST:**

```bash
fckr xss -u "http://test.com/search" -b "query=FCK&submit=1" -w payloads.txt -m POST
```

**Inspect full response for a payload:**

```bash
fckr xss -u "https://test.com/?q=FCK" -w payloads.txt -r "<script>alert('xss')</script>" --encode
```

**Verbose debugging:**

```bash
fckr xss -u "https://test.com/?q=FCK" -w payloads.txt -d
```

---

## 📂 Wordlist Format

Plain text file, one word or payload per line:

**For brute mode:**

```
admin
test
search
```

**For xss mode:**

```
<script>alert('xss')</script>
<img src=x onerror=alert(1)>
test' onload='alert(1)'
```

---

## 🛠️ Development

```bash
git clone https://github.com/IMApurbo/fckr.git
cd fckr
pip install -r requirements.txt
python -m fckr brute -u "https://example.com/?q=FCK" -w list.txt
```

---

## ⚠️ Legal Notice

> 🛑 Use **only on systems you have explicit permission** to test.  
> Misuse may violate laws and ethical guidelines.

---

## ⭐ Credits

- Developed by **IMApurbo**

---

## 📃 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
