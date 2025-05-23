# FCK – The Ultimate Brute Forcer

**FCK** is a command-line tool designed for **security researchers** and **penetration testers** to brute-force HTTP requests with powerful and customizable filtering capabilities. It replaces the `FCK` placeholder in URLs or POST bodies with values from a wordlist, allowing you to test web endpoints and inspect/filter responses.

> ✨ Developed by **[@IMApurbo](https://github.com/imapurbo)**  
> 🛡️ Use responsibly. Authorized testing only.

---

## 🚀 Features

- **Flexible Brute-Forcing**  
  Replace `FCK` placeholders in URLs or POST bodies with wordlist entries.

- **HTTP Method Support**  
  Supports both `GET` and `POST` methods.

- **Advanced Filtering**  
  - **Response Filters (-F)**: Filter based on:
    - `s`: status code
    - `l`: content length
    - `c`: response body
  - Filter types:
    - `e`: exact
    - `c`: contains
    - `nc`: not contains

- **Output Filters (-o)**  
  Show only filtered results using the same logic as response filters.

- **Response Inspection (-r)**  
  Fetch full HTML responses for specific inputs.

- **Debug Mode (-d)**  
  Logs all requests and mismatched filters.

- **Typewriter-Style ASCII Logo**  
  Animated with gradient colors using `rich`.

- **Progress Bar**  
  Stylish visual feedback during brute-forcing.

- **User-Friendly Output**  
  Concise results like:  
  `Word: <word> | Status: <status> | Length: <length> | Time: <time>s`

---

## 🧪 Installation

Install directly from PyPI:

```bash
pip install fck
````

### Requirements

* Python 3.6+
* Terminal with ANSI support (Linux, macOS, or Windows Terminal)

---

## ⚙️ Usage

```bash
kck -u "<url_with_FCK>" -w <wordlist> [options]
```

### Common Flags

| Short | Long               | Description                                      | Required | Default |
| ----- | ------------------ | ------------------------------------------------ | -------- | ------- |
| `-u`  | `--url`            | Target URL with `FCK` placeholder                | ✅        | -       |
| `-b`  | `--body`           | POST body with `FCK` (use with POST only)        | 🟡       | -       |
| `-w`  | `--wordlist`       | Path to wordlist                                 | ✅        | -       |
| `-m`  | `--method`         | HTTP method (`GET` or `POST`)                    | ❌        | GET     |
| `-t`  | `--timeout`        | Timeout in seconds                               | ❌        | 5.0     |
| `-F`  | `--filter`         | Filter response (e.g., `s:e:200`, `c:c:success`) | ❌        | -       |
| `-o`  | `--output-filter`  | Control output display with same format          | ❌        | -       |
| `-r`  | `--fetch-response` | Fetch full HTML for a specific word              | ❌        | -       |
| `-d`  | `--debug`          | Show request and filter logs                     | ❌        | False   |

---

## 🔍 Filtering Syntax

Format:

```
<field>:<type>:<value>
```

### Fields

* `s`: HTTP status code
* `l`: Content length
* `c`: Response body content

### Types

* `e`: Exact match
* `c`: Contains
* `nc`: Not contains

### Examples

```bash
-F s:e:200              # Process only 200 OK
-o c:nc:error          # Show results that do not contain "error"
-o c:c:login           # Show responses containing "login"
-o l:e:1000            # Show only 1000-byte responses
```

---

## 🔧 Examples

**Brute-force with GET:**

```bash
fck -u "https://test.com/search?q=FCK" -w list.txt -m GET
```

**POST request with body:**

```bash
fck -u "http://test.com/search" -b "query=FCK&submit=1" -w list.txt -m POST
```

**Filter by content:**

```bash
-o c:nc:"<h2>Not found</h2>"
```

**Inspect full response for a word:**

```bash
-r "admin"
```

**Verbose debugging:**

```bash
-d
```

---

## 📂 Wordlist Format

Plain text file, one word per line:

```
admin
test
search
```

---

## 🧪 Example Output

```text
█████▒▄████▄   ██ ▄█▀
▓██   ▒▒██▀ ▀█   ██▄█▒ 
▒████ ░▒▓█    ▄ ▓███▄░ 
░▓█▒  ░▒▓▓▄ ▄██▒▓██ █▄ 
░▒█░   ▒ ▓███▀ ░▒██▒ █▄
The Ultimate Brute Forcer by IMApurbo
----------------------------------------------------
Starting brute force with 88 words...
Method: POST
Target: http://testphp.vulnweb.com/search
Word: hello | Status: 200 | Length: 5142 | Time: 0.25s
Word: bye   | Status: 200 | Length: 5142 | Time: 0.30s
🎉 Brute Force Complete!
```

---

## 🛠️ Development

```bash
git clone https://github.com/imapurbo/fck.git
cd fck
pip install -r requirements.txt
python -m fck -u "https://example.com/?q=FCK" -w list.txt
```

---

## ⚠️ Legal Notice

> 🛑 Use **only on systems you have explicit permission** to test.
> Misuse may violate laws and ethical guidelines.

---

## ⭐ Credits

* Developed by **IMApurbo**

---

## 📃 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

```

