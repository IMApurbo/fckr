# FCKR – The Ultimate Brute Forcer

**FCKR** is a command-line tool designed for **security researchers** and **penetration testers** to perform HTTP brute-forcing or test XSS payload reflection. It supports two modes: `brute` for replacing placeholders in URLs, POST bodies, or raw request parameters with wordlist entries, and `xss` for checking exact payload reflection in response HTML. Traditional mode uses `FCK` placeholders in URLs (for GET) or bodies (for POST). Advanced mode loads full raw HTTP requests from files and fuzzes specific parameters, supporting JSON, form-urlencoded, and other formats.

> ✨ Developed by **[@IMApurbo](https://github.com/imapurbo)**  
> 🛡️ Use responsibly. Authorized testing only.

---

## 🚀 Features

- **Dual Modes**
  - `brute`: Replace placeholders in URLs, POST bodies, or request parameters with wordlist entries for brute-forcing.
  - `xss`: Test XSS payloads for exact reflection in response HTML, replacing placeholders or parameters.
- **HTTP Method Support**
  - Supports `GET`, `POST`, and other methods via raw request files.
  - Traditional: `FCK` required in URLs (GET) or bodies (POST).
  - Raw files: Auto-detects method from file.
- **Raw Request File Support (-R)**
  - Load full HTTP requests from raw files (method, URL, headers, body).
  - Fuzz specific parameters (-p) in query strings, form data, or JSON bodies.
  - Handles JSON (replaces key values), form-urlencoded, and fallbacks to string replacement for other formats.
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
  - Detects exact payload reflection in response HTML, with optional URL encoding (`--encode`).
- **Response Inspection (-r)**
  - Fetch full HTML responses for any specific word or payload in both modes.
- **Output Saving (-o)**
  - Save results to a file (e.g., `result.txt`).
- **Custom Headers (-H)**
  - Add/override HTTP headers as a semicolon-separated string (e.g., `Cookie:JSESSIONID=abc123;Content-Type:application/json`).
- **Debug Mode (-d)**
  - Logs all requests and mismatched filters (brute mode) or non-reflected payloads (xss mode).
- **Threading (-T)**
  - Speed up operations with concurrent threads (default: 10).
- **Progress Bar**
  - Stylish visual feedback during operations.
- **User-Friendly Output**
  - Concise results like:  
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

| Short | Long          | Description                                                                 | Required | Default | Modes     |
|-------|---------------|-----------------------------------------------------------------------------|----------|---------|-----------|
| `-u`  | `--url`       | Target URL with `FCK` placeholder (e.g., `https://example.com/?q=FCK`)      | 🟡       | -       | brute, xss |
| `-b`  | `--body`      | POST body with `FCK` (required for POST)                                    | 🟡       | -       | brute, xss |
| `-w`  | `--wordlist`  | Path to wordlist file                                                       | 🟡       | -       | brute, xss |
| `-m`  | `--method`    | HTTP method (`GET` or `POST`) (ignored with `-R`)                           | ❌       | GET     | brute, xss |
| `-t`  | `--timeout`   | Timeout in seconds                                                          | ❌       | 5.0     | brute, xss |
| `-f`  | `--filter`    | Filter response (e.g., `s:e:200`, `c:c:success`)                            | ❌       | -       | brute     |
| `-o`  | `--output`    | Save results to a file (e.g., `result.txt`)                                 | ❌       | -       | brute, xss |
| `-r`  | `--fetch-response` | Fetch full HTML for a specific word/payload (any string)              | ❌       | -       | brute, xss |
| `-d`  | `--debug`     | Show request and filter/payload logs                                        | ❌       | False   | brute, xss |
| `-H`  | `--header`    | HTTP headers (semicolon-separated)                                          | ❌       | -       | brute, xss |
| `-T`  | `--threads`   | Number of concurrent threads                                                | ❌       | 10      | brute, xss |
|       | `--encode`    | URL-encode payloads before sending                                          | ❌       | False   | xss       |
| `-R`  | `--request`   | Load raw HTTP request file (method, URL, headers, body)                     | ❌       | -       | brute, xss |
| `-p`  | `--param`     | Parameter name to fuzz (required with `-R`)                                 | 🟡       | -       | brute, xss |
| `-h`  | `--help`      | Show this help message and exit                                             | ❌       | -       | brute, xss |

> **Notes**:
> - `-w/--wordlist` is required unless `-r/--fetch-response` is used.
> - Traditional mode: `FCK` required in URL (GET) or body (POST).
> - Raw mode (`-R`): Ignores `-u`, `-b`, `-m`; `-p` required. Supports JSON/form/other formats.
> - `-b/--body` required for POST (traditional) and not allowed for GET.
> - Multiple `-f` flags allowed for combined filters.

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
- `c`: Contains (case-insensitive, HTML attributes normalized)
- `nc`: Not contains (case-insensitive, HTML attributes normalized)

### Examples
```bash
-f s:e:200                # Show only 200 OK
-f c:nc:error             # Show results without "error"
-f 'c:c:signup here'      # Show responses containing "signup here" (quote multi-word values)
-f l:e:1000               # Show only 1000-byte responses
```

---

## 🔧 Examples

### Brute Mode

**Brute-force with GET (traditional):**
```bash
fckr brute -u "https://test.com/search?q=FCK" -w list.txt -m GET
```

**POST request with body (traditional):**
```bash
fckr brute -u "http://test.com/search" -b "query=FCK&submit=1" -w list.txt -m POST
```

**Filter by content (traditional):**
```bash
fckr brute -u "https://test.com/?q=FCK" -w list.txt -f c:nc:'"<h2>Not found</h2>"'
```

**Brute-force using raw request file (JSON POST):**
```bash
# req.txt example:
# POST /api/login HTTP/1.1
# Host: test.com
# Content-Type: application/json
#
# {"username":"admin","password":"FCK"}

fckr brute -R req.txt -p password -w list.txt
```

**Filter with raw request (form-urlencoded):**
```bash
fckr brute -R req.txt -p pass -w list.txt -f c:nc:'signup here'
```

**Inspect full response for a word:**
```bash
fckr brute -u "https://test.com/?q=FCK" -w list.txt -r "admin"
# Or with raw: fckr brute -R req.txt -p pass -r "secret"
```

### XSS Mode

**Test XSS payloads with GET (traditional):**
```bash
fckr xss -u "https://test.com/search?q=FCK" -w payloads.txt -m GET --encode
```

**Test XSS payloads with POST (traditional):**
```bash
fckr xss -u "http://test.com/search" -b "query=FCK&submit=1" -w payloads.txt -m POST
```

**Test XSS with raw request file (JSON):**
```bash
fckr xss -R req.txt -p input -w payloads.txt --encode
```

**Inspect full response for a payload:**
```bash
fckr xss -u "https://test.com/?q=FCK" -w payloads.txt -r "<script>alert('xss')</script>" --encode
# Or with raw: fckr xss -R req.txt -p input -r "<img src=x onerror=alert(1)>"
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

## 🛠️ Installation

```bash
pip install fckr
fckr brute -u "https://example.com/?q=FCK" -w list.txt
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
