import sys
import re
import time
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import parse_qs, urlencode, quote
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.live import Live
from rich.style import Style
import signal

console = Console()

def get_gradient_colors(start_rgb: tuple, end_rgb: tuple, steps: int) -> List[str]:
    """Generate a list of gradient colors between start and end RGB."""
    colors = []
    for i in range(steps):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (steps - 1))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (steps - 1))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (steps - 1))
        colors.append(f"#{r:02x}{g:02x}{b:02x}")
    return colors

def display_animated_logo():
    """Display ASCII logo with a typewriter-like effect and gradient colors."""
    logo = """
  █████▒▄████▄   ██ ▄█▀ ██▀███  
▓██   ▒▒██▀ ▀█   ██▄█▒ ▓██ ▒ ██▒	       ╦╔╦╗╔═╗┌─┐┬ ┬┬─┐┌┐ ┌─┐
▒████ ░▒▓█    ▄ ▓███▄░ ▓██ ░▄█ ▒    AUTHOR:    ║║║║╠═╣├─┘│ │├┬┘├┴┐│ │
░▓█▒  ░▒▓▓▄ ▄██▒▓██ █▄ ▒██▀▀█▄  	       ╩╩ ╩╩ ╩┴  └─┘┴└─└─┘└─┘
░▒█░   ▒ ▓███▀ ░▒██▒ █▄░██▓ ▒██▒
 ▒ ░   ░ ░▒ ▒  ░▒ ▒▒ ▓▒░ ▒▓ ░▒▓░
 ░       ░  ▒   ░ ░▒ ▒░  ░▒ ░ ▒░
 ░ ░   ░        ░ ░░ ░   ░░   ░ 
       ░ ░      ░  ░      ░     
       ░                        
    """
    title = "The Ultimate Brute Forcer"
    developer = "Developed by: IMApurbo"
    
    logo_lines = logo.strip().split('\n')
    max_length = max(len(line) for line in logo_lines)
    gradient_colors = get_gradient_colors((0, 102, 255), (255, 0, 255), max_length)
    
    char_styles = []
    for line_idx, line in enumerate(logo_lines):
        for char_idx, char in enumerate(line):
            style = Style(color=gradient_colors[char_idx % len(gradient_colors)])
            char_styles.append((char, style))
        char_styles.append(('\n', None))
    for char in title:
        char_styles.append((char, Style(color="white", bold=True)))
    char_styles.append(('\n', None))
    for char in developer:
        char_styles.append((char, Style(color="cyan", italic=True)))
    char_styles.append(('\n', None))
    
    console.clear()
    for char, style in char_styles:
        if char == '\n':
            console.print()
        else:
            console.print(Text(char, style=style), end='', soft_wrap=True)
        time.sleep(0.01)
    time.sleep(0.3)

def load_wordlist(wordlist_path: str) -> List[str]:
    """Load words from a wordlist file."""
    try:
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        console.print(f"[red]Error: Wordlist file '{wordlist_path}' not found.[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error reading wordlist: {e}[/red]")
        sys.exit(1)

def prepare_request(url: str, body: Optional[str], word: str, method: str, encode: bool = False) -> Tuple[str, Optional[Dict[str, str]]]:
    """Prepare the request URL and data by replacing FCK with the word."""
    if encode:
        word = quote(word)
    full_url = url.replace('FCK', word)
    data = None
    if method.upper() == 'POST' and body:
        body = body.replace('FCK', word)
        try:
            parsed_body = parse_qs(body, keep_blank_values=True)
            data = {k: v[0] for k, v in parsed_body.items()}
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to parse POST body for word '{word}': {e}. Using raw body.[/yellow]")
            data = body
    return full_url, data

def make_request(url: str, method: str, data: Optional[Dict[str, str]], timeout: float, debug: bool, headers: Optional[str] = None) -> dict:
    """Make an HTTP request and return response details."""
    try:
        start_time = time.time()
        request_headers = {'Content-Type': 'application/x-www-form-urlencoded'} if method.upper() == 'POST' else {}
        
        if headers:
            header_list = headers.split(';')
            for header_str in header_list:
                header_str = header_str.strip()
                if header_str:
                    try:
                        key, value = header_str.split(':', 1)
                        request_headers[key.strip()] = value.strip()
                    except ValueError:
                        console.print(f"[yellow]Warning: Invalid header format '{header_str}'. Expected 'Key:Value'. Skipping.[/yellow]")
        
        if debug:
            console.print(f"[yellow]Debug: Sending {method.upper()} to {url} with headers: {request_headers}, body: {data or 'no body'}[/yellow]")
        
        if method.upper() == 'POST':
            response = requests.post(url, data=data, timeout=timeout, headers=request_headers)
        else:
            response = requests.get(url, timeout=timeout, headers=request_headers)
        
        elapsed_time = time.time() - start_time
        return {
            's': response.status_code,
            'l': len(response.content),
            'c': response.text,
            'url': response.url,
            't': elapsed_time
        }
    except requests.RequestException as e:
        console.print(f"[red]Error making request to {url}: {e}[/red]")
        return {
            's': None,
            'l': 0,
            'c': '',
            'url': url,
            't': 0,
            'error': str(e)
        }

def normalize_html_attributes(text: str) -> str:
    """Normalize HTML attributes by removing quotes around values for comparison."""
    return re.sub(r'(\w+)="([^"]*)"', r'\1=\2', text)

def matches_filter(response: dict, filter_type: str, filter_value: str, field: str) -> bool:
    """Check if response matches the filter criteria."""
    value = str(response.get(field, ''))
    if filter_type == 'e':
        return value == filter_value
    elif filter_type == 'c':
        normalized_value = normalize_html_attributes(value)
        normalized_filter = normalize_html_attributes(filter_value)
        return normalized_filter.lower() in normalized_value.lower()
    elif filter_type == 'nc':
        normalized_value = normalize_html_attributes(value)
        normalized_filter = normalize_html_attributes(filter_value)
        return normalized_filter.lower() not in normalized_value.lower()
    return False

def check_xss_reflection(response_text: str, payload: str, encode: bool = False) -> bool:
    """Check if the exact payload is reflected in the response HTML."""
    if encode:
        payload = quote(payload)
    return payload in response_text

def parse_filters(filter_args: List[str]) -> List[dict]:
    """Parse filter arguments into a list of filter dictionaries."""
    filters = []
    for f in filter_args:
        try:
            parts = f.split(':', 2)
            if len(parts) != 3:
                raise ValueError
            field, ftype, value = parts
            if field not in ['s', 'l', 'c'] or ftype not in ['e', 'c', 'nc']:
                console.print(f"[red]Invalid filter format: {f}. Expected <s|l|c>:<e|c|nc>:<value>[/red]")
                sys.exit(1)
            filters.append({'field': field, 'type': ftype, 'value': value})
        except ValueError:
            console.print(f"[red]Invalid filter format: {f}. Expected <s|l|c>:<e|c|nc>:<value>[/red]")
            sys.exit(1)
    return filters

def signal_handler(sig, frame):
    """Handle Ctrl+C with a user-stopped message."""
    console.print("\n[red bold]Process stopped by user.[/red bold]")
    sys.exit(1)

def print_help():
    """Print help message and exit."""
    help_text = """
FCKR – The Ultimate Brute Forcer - A tool for brute-forcing HTTP requests or testing XSS payload reflection.

Usage: fckr <mode> <options>

Modes:
  brute                  Perform brute-forcing with customizable filters
  xss                    Test for exact XSS payload reflection in response HTML

Options for 'brute' mode:
  -h, --help              Show this help message and exit
  -H, --header <headers>  HTTP headers as a semicolon-separated string (e.g., "Cookie:JSESSIONID=abc123;Content-Type:application/json")
  -u, --url <url>         Target URL with FCK placeholder (e.g., https://example.com/?q=FCK) (required)
  -b, --body <body>       POST body with FCK placeholder (e.g., searchFor=FCK&goButton=go)
  -w, --wordlist <file>   Path to wordlist file (required unless -r is used)
  -m, --method <GET|POST> HTTP method (default: GET)
  -t, --timeout <seconds> Request timeout in seconds (default: 5.0)
  -o, --output <file>     Save results to a file (e.g., result.txt)
  -f, --filter <filter>   Filter which responses are displayed.
                          Format: <s|l|c>:<e|c|nc>:<value>
                          Fields:
                            - s: Status code (e.g., 200, 404)
                            - l: Content length (e.g., 1234)
                            - c: Response body content (e.g., success, <title>Login</title>)
                          Types:
                            - e: Exact match
                            - c: Contains match (case-insensitive, HTML attributes normalized)
                            - nc: Not contains match (case-insensitive, HTML attributes normalized)
                          Examples:
                            - s:e:200
                            - c:c:success
                            - c:nc:error
  -r, --fetch-response <word> Fetch full HTML response for a specific word (can be any string)
  -d, --debug             Enable debug mode to log requests and filter mismatches
  -T, --threads <number>  Number of concurrent threads (default: 10)

Options for 'xss' mode:
  -h, --help              Show this help message and exit
  -H, --header <headers>  HTTP headers as a semicolon-separated string
  -u, --url <url>         Target URL with FCK placeholder for GET requests (e.g., https://example.com/?q=FCK) (required)
  -b, --body <body>       POST body with FCK placeholder for POST requests (e.g., search=FCK)
  -w, --wordlist <file>   Path to wordlist file with XSS payloads (required unless -r is used)
  -m, --method <GET|POST> HTTP method (default: GET)
  -t, --timeout <seconds> Request timeout in seconds (default: 5.0)
  -o, --output <file>     Save results to a file (e.g., result.txt)
  -r, --fetch-response <word> Fetch full HTML response for a specific payload (can be any string)
  -d, --debug             Enable debug mode to log requests
  -T, --threads <number>  Number of concurrent threads (default: 10)
  --encode                URL-encode payloads before sending

Notes:
  - In 'brute' mode, use 'FCK' in the URL for GET requests or in the body for POST requests for word replacement.
  - In 'xss' mode, use 'FCK' in the URL for GET requests or in the body for POST requests to indicate where payloads are inserted; checks for exact payload reflection in the response HTML.
  - Use -o or --output to save results to a file.
  - Use -H or --header to include custom headers like cookies or content-type, separated by semicolons.
  - The -r/--fetch-response option can be used with any string, not limited to the wordlist.
    """
    console.print(help_text)
    sys.exit(0)

def validate_arguments(args: dict, mode: str):
    """Validate required command-line arguments."""
    if not args['url']:
        console.print("[red]Error: -u/--url is required.[/red]")
        sys.exit(1)
    if not args['wordlist'] and not args['fetch_response']:
        console.print("[red]Error: -w/--wordlist is required unless -r/--fetch-response is used.[/red]")
        sys.exit(1)
    if args['method'].upper() == 'POST' and not args['body']:
        console.print("[red]Error: -b/--body is required for POST requests.[/red]")
        sys.exit(1)
    if args['method'].upper() == 'GET' and args['body']:
        console.print("[red]Error: -b/--body is not allowed for GET requests.[/red]")
        sys.exit(1)
    
    if args['method'].upper() == 'GET' and 'FCK' not in args['url']:
        console.print("[red]Error: URL must contain 'FCK' placeholder for GET requests.[/red]")
        sys.exit(1)
    if args['method'].upper() == 'POST' and args['body'] and 'FCK' not in args['body']:
        console.print("[red]Error: Body must contain 'FCK' placeholder for POST requests.[/red]")
        sys.exit(1)

def parse_arguments() -> Tuple[str, dict]:
    """Parse command-line arguments manually."""
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print_help()
    
    mode = sys.argv[1].lower()
    if mode not in ('brute', 'xss'):
        console.print(f"[red]Error: Invalid mode '{mode}'. Use 'brute' or 'xss'.[/red]")
        sys.exit(1)
    
    args = {
        'url': None,
        'body': None,
        'wordlist': None,
        'method': 'GET',
        'timeout': 5.0,
        'output_filter': [],
        'fetch_response': None,
        'debug': False,
        'threads': 10,
        'output': None,
        'headers': None,
        'encode': False
    }
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ('-H', '--header'):
            i += 1
            if i < len(sys.argv):
                args['headers'] = sys.argv[i]
        elif arg in ('-u', '--url'):
            i += 1
            if i < len(sys.argv):
                args['url'] = sys.argv[i]
        elif arg in ('-b', '--body'):
            i += 1
            if i < len(sys.argv):
                args['body'] = sys.argv[i]
        elif arg in ('-w', '--wordlist'):
            i += 1
            if i < len(sys.argv):
                args['wordlist'] = sys.argv[i]
        elif arg in ('-m', '--method'):
            i += 1
            if i < len(sys.argv) and sys.argv[i] in ('GET', 'POST'):
                args['method'] = sys.argv[i]
        elif arg in ('-t', '--timeout'):
            i += 1
            if i < len(sys.argv):
                try:
                    args['timeout'] = float(sys.argv[i])
                except ValueError:
                    console.print(f"[red]Error: Invalid timeout value '{sys.argv[i]}'. Must be a number.[/red]")
                    sys.exit(1)
        elif arg in ('-f', '--filter') and mode == 'brute':
            i += 1
            if i < len(sys.argv):
                args['output_filter'].append(sys.argv[i])
        elif arg in ('-r', '--fetch-response'):
            i += 1
            if i < len(sys.argv):
                args['fetch_response'] = sys.argv[i]
        elif arg in ('-d', '--debug'):
            args['debug'] = True
        elif arg in ('-T', '--threads'):
            i += 1
            if i < len(sys.argv):
                try:
                    args['threads'] = int(sys.argv[i])
                except ValueError:
                    console.print(f"[red]Error: Invalid threads value '{sys.argv[i]}'. Must be an integer.[/red]")
                    sys.exit(1)
        elif arg in ('-o', '--output'):
            i += 1
            if i < len(sys.argv):
                args['output'] = sys.argv[i]
        elif arg == '--encode' and mode == 'xss':
            args['encode'] = True
        else:
            console.print(f"[red]Unknown or invalid argument for {mode} mode: {arg}[/red]")
            sys.exit(1)
        i += 1
    
    validate_arguments(args, mode)
    return mode, args

def process_brute_word(word: str, args: dict, output_filters: List[dict]) -> Tuple[str, Optional[dict]]:
    """Process a single word in brute mode: make request, apply filters, and return result."""
    url, data = prepare_request(args['url'], args['body'], word, args['method'])
    response = make_request(url, args['method'], data, args['timeout'], args['debug'], args['headers'])
    
    should_display = not output_filters
    for f in output_filters:
        if matches_filter(response, f['type'], f['value'], f['field']):
            should_display = True
            break
    if should_display:
        return word, response
    elif args['debug']:
        console.print(f"[yellow]Debug: Word '{word}' did not match output filter {output_filters}[/yellow]")
    
    return word, None

def process_xss_word(word: str, args: dict) -> Tuple[str, Optional[dict]]:
    """Process a single word in XSS mode: check for exact payload reflection."""
    url, data = prepare_request(args['url'], args['body'], word, args['method'], args['encode'])
    response = make_request(url, args['method'], data, args['timeout'], args['debug'], args['headers'])
    
    if check_xss_reflection(response['c'], word, args['encode']):
        return word, response
    elif args['debug']:
        console.print(f"[yellow]Debug: Payload '{word}' not reflected in response.[/yellow]")
    
    return word, None

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    mode, args = parse_arguments()
    
    display_animated_logo()
    console.print("-" * 80)

    words = []
    if args['wordlist']:
        words = load_wordlist(args['wordlist'])
    
    console.print(f"[bold]Starting {mode} mode{' with ' + str(len(words)) + ' payloads' if words else ''}...[/bold]")
    console.print(f"[bold]Method:[/bold] {args['method']}")
    console.print(f"[bold]Target:[/bold] {args['url'].replace('FCK', '<word>')}")
    if args['body']:
        console.print(f"[bold]Body:[/bold] {args['body'].replace('FCK', '<word>')}")
    if args['headers']:
        console.print(f"[bold]Headers:[/bold] {args['headers']}")
    if mode == 'brute':
        output_filters = parse_filters(args['output_filter'])
        console.print(f"[bold]Output Filters:[/bold] {output_filters}")
    if args['encode']:
        console.print(f"[bold]Encoding:[/bold] URL-encode payloads")
    console.print(f"[bold]Threads:[/bold] {args['threads']}")
    if args['fetch_response']:
        console.print(f"[bold]Fetching response for:[/bold] {args['fetch_response']}")
    if args['output']:
        console.print(f"[bold]Output File:[/bold] {args['output']}")
    console.print("-" * 80)

    output_file = None
    if args['output']:
        try:
            output_file = open(args['output'], 'w', encoding='utf-8')
        except Exception as e:
            console.print(f"[red]Error: Could not open output file '{args['output']}': {e}[/red]")
            sys.exit(1)

    if args['fetch_response']:
        url, data = prepare_request(args['url'], args['body'], args['fetch_response'], args['method'], args['encode'] if mode == 'xss' else False)
        response = make_request(url, args['method'], data, args['timeout'], args['debug'], args['headers'])
        console.print(f"[bold cyan]HTML Response for '{args['fetch_response']}':[/bold cyan]")
        console.print(response['c'])
        console.print("-" * 80)
        console.print(f"[bold]Status:[/bold] {response['s']} | [bold]Length:[/bold] {response['l']} | [bold]Time:[/bold] {response['t']:.2f}s")
        if response.get('error'):
            console.print(f"[red]Error: {response['error']}[/red]")
        if output_file:
            output_file.write(f"{'Word' if mode == 'brute' else 'Payload'}: {args['fetch_response']} | Status: {response['s']} | Length: {response['l']} | Time: {response['t']:.2f}s")
            if response.get('error'):
                output_file.write(f" | Error: {response['error']}")
            output_file.write("\n")
            output_file.write(f"Response:\n{response['c']}\n{'-' * 80}\n")
            output_file.close()
        return

    if not words:
        console.print("[red]Error: No wordlist provided and -r/--fetch-response not used.[/red]")
        if output_file:
            output_file.close()
        sys.exit(1)

    matches_found = False
    progress = Progress(
        TextColumn("[cyan]Running..."),
        BarColumn(
            bar_width=40,
            complete_style=Style(color="#0066ff"),
            finished_style=Style(color="#00ffcc"),
            style=Style(color="#00cc00")
        ),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    )
    
    try:
        with Live(progress, console=console, transient=True):
            task = progress.add_task("Working...", total=len(words))
            with ThreadPoolExecutor(max_workers=args['threads']) as executor:
                if mode == 'brute':
                    future_to_word = {
                        executor.submit(process_brute_word, word, args, output_filters): word
                        for word in words
                    }
                else:  # xss mode
                    future_to_word = {
                        executor.submit(process_xss_word, word, args): word
                        for word in words
                    }
                for future in as_completed(future_to_word):
                    word, response = future.result()
                    progress.advance(task)
                    if response:
                        matches_found = True
                        error = f" | Error: {response['error']}" if response.get('error') else ""
                        result_line = f"{'Word' if mode == 'brute' else 'Payload'}: {word} | Status: {response['s']} | Length: {response['l']} | Time: {response['t']:.2f}s{error}"
                        console.print(f"[bold]{result_line}[/bold]")
                        if output_file:
                            output_file.write(result_line + "\n")
                    time.sleep(0.01)
        
        if matches_found:
            console.print(f"[bold magenta]💀 {mode.capitalize()} Mode Complete! All payloads processed successfully! 💀[/bold magenta]")
        else:
            console.print(f"[bold yellow]⚠ {mode.capitalize()} Mode Complete! No matches found. Check {'filters' if mode == 'brute' else 'payload reflection'} or use -r to inspect HTML. ⚠[/bold yellow]")
        
        if args['debug'] and not matches_found:
            console.print(f"[yellow]Debug: No responses matched the {'output filters' if mode == 'brute' else 'payload reflection criteria'}. Try inspecting HTML with -r or adjusting the {'filter' if mode == 'brute' else 'payloads'}.[/yellow]")
    
    except KeyboardInterrupt:
        console.print("\n[red bold]Process stopped by user.[/red bold]")
        if output_file:
            output_file.close()
        sys.exit(1)
    finally:
        if output_file:
            output_file.close()

if __name__ == "__main__":
    main()
