import sys
import re
import time
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import parse_qs, urlencode
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

def prepare_request(url: str, body: Optional[str], word: str, method: str) -> Tuple[str, Optional[Dict[str, str]]]:
    """Prepare the request URL and data by replacing FCK with the word."""
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

def make_request(url: str, method: str, data: Optional[Dict[str, str]], timeout: float, debug: bool) -> dict:
    """Make an HTTP request and return response details."""
    try:
        start_time = time.time()
        headers = {'Content-Type': 'application/x-www-form-urlencoded'} if method.upper() == 'POST' else {}
        if method.upper() == 'POST':
            if debug:
                console.print(f"[yellow]Debug: Sending POST to {url} with body: {data or 'no body'}[/yellow]")
            response = requests.post(url, data=data, timeout=timeout, headers=headers)
        else:
            if debug:
                console.print(f"[yellow]Debug: Sending GET to {url}[/yellow]")
            response = requests.get(url, timeout=timeout)
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
FCKR – The Ultimate Brute Forcer - A tool for brute-forcing HTTP requests with customizable filters.

Usage: fckr <options>

Options:
  -h, --help              Show this help message and exit
  -u, --url <url>         Target URL with FCK placeholder (e.g., https://example.com/?q=FCK) (required)
  -b, --body <body>       POST body with FCK placeholder (e.g., searchFor=FCK&goButton=go)
  -w, --wordlist <file>   Path to wordlist file (required)
  -m, --method <GET|POST> HTTP method (default: GET)
  -t, --timeout <seconds> Request timeout in seconds (default: 5.0)
  -F, --filter <filter>   Filter responses before processing. Only responses matching ALL -F filters proceed.
                          Format: <s|l|c>:<e|c|nc>:<value>
                          Fields: s (status code), l (content length), c (response body)
                          Types: e (exact match), c (contains, case-insensitive), nc (not contains, case-insensitive)
                          Examples: s:e:200, c:c:success, c:nc:something, l:e:1000
  -o, --output-filter <filter> Filter which responses are displayed. Responses must match AT LEAST ONE -o filter to be shown.
                               Unlike -F filters, which must ALL match for a response to be processed further, -o filters
                               control which processed responses are displayed in the output. If no -o filters are provided,
                               all responses that pass -F filters are displayed. Use -o filters to narrow down the output
                               to specific results of interest, such as successful responses, responses with specific content,
                               or responses meeting certain criteria. Multiple -o filters can be specified, and a response
                               is displayed if it matches any one of them. This is useful for focusing on relevant results
                               without modifying the processing logic defined by -F filters.
                               Format: <s|l|c>:<e|c|nc>:<value>
                               Fields:
                                 - s: Status code (e.g., 200, 404)
                                 - l: Content length (e.g., 1234)
                                 - c: Response body content (e.g., success, <title>Login</title>)
                               Types:
                                 - e: Exact match (e.g., status code or length must match exactly)
                                 - c: Contains match (case-insensitive, HTML attributes normalized)
                                 - nc: Not contains match (case-insensitive, HTML attributes normalized)
                               Examples:
                                 - s:e:200 (display responses with status code exactly 200)
                                 - c:c:success (display responses containing 'success' in the body)
                                 - c:nc:error (display responses not containing 'error' in the body)
                                 - l:e:1000 (display responses with content length exactly 1000)
                                 - c:c:'<h2 class=lead>results</h2>' (display responses with specific HTML)
                                 - s:c:20 (display responses with status codes starting with '20', e.g., 200, 201)
                                 - l:c:100 (display responses with content length containing '100', e.g., 100, 1000)
  -r, --fetch-response <word> Fetch full HTML response for a specific word
  -d, --debug                 Enable debug mode to log requests and filter mismatches
  -T, --threads <number>      Number of concurrent threads (default: 10)

Notes:
  - Use -u to specify the target URL.
  - Use -b to specify the POST body for POST requests.
  - Either -u alone (for GET) or -u with -b (for POST) must be provided.
  - URL must contain 'FCK' for GET requests; body must contain 'FCK' for POST requests.
    """
    console.print(help_text)
    sys.exit(0)

def parse_arguments() -> dict:
    """Parse command-line arguments manually."""
    args = {
        'url': None,
        'body': None,
        'wordlist': None,
        'method': 'GET',
        'timeout': 5.0,
        'filter': [],
        'output_filter': [],
        'fetch_response': None,
        'debug': False,
        'threads': 10
    }
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ('-h', '--help'):
            print_help()
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
        elif arg in ('-F', '--filter'):
            i += 1
            if i < len(sys.argv):
                args['filter'].append(sys.argv[i])
        elif arg in ('-o', '--output-filter'):
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
        else:
            console.print(f"[red]Unknown argument: {arg}[/red]")
            sys.exit(1)
        i += 1
    
    # Validate required arguments
    if not args['url']:
        console.print("[red]Error: -u/--url is required.[/red]")
        sys.exit(1)
    if not args['wordlist']:
        console.print("[red]Error: -w/--wordlist is required.[/red]")
        sys.exit(1)
    if args['method'].upper() == 'POST' and not args['body']:
        console.print("[red]Error: -b/--body is required for POST requests.[/red]")
        sys.exit(1)
    if args['method'].upper() == 'GET' and args['body']:
        console.print("[red]Error: -b/--body is not allowed for GET requests.[/red]")
        sys.exit(1)
    
    # Check for FCK in URL (GET) or body (POST)
    if args['method'].upper() == 'GET' and 'FCK' not in args['url']:
        console.print("[red]Error: URL must contain 'FCK' placeholder for GET requests.[/red]")
        sys.exit(1)
    if args['method'].upper() == 'POST' and args['body'] and 'FCK' not in args['body']:
        console.print("[red]Error: Body must contain 'FCK' placeholder for POST requests.[/red]")
        sys.exit(1)
    
    return args

def process_word(word: str, args: dict, filters: List[dict], output_filters: List[dict]) -> Tuple[str, Optional[dict]]:
    """Process a single word: make request, apply filters, and return result."""
    url, data = prepare_request(args['url'], args['body'], word, args['method'])
    response = make_request(url, args['method'], data, args['timeout'], args['debug'])

    should_skip = False
    for f in filters:
        if not matches_filter(response, f['type'], f['value'], f['field']):
            should_skip = True
            break
    if should_skip:
        if args['debug']:
            console.print(f"[yellow]Debug: Word '{word}' skipped by filter {f}[/yellow]")
        return word, None

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

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    args = parse_arguments()
    
    display_animated_logo()
    console.print("-" * 80)

    words = load_wordlist(args['wordlist'])
    filters = parse_filters(args['filter'])
    output_filters = parse_filters(args['output_filter'])

    console.print(f"[bold]Starting brute force with {len(words)} words...[/bold]")
    console.print(f"[bold]Method:[/bold] {args['method']}")
    console.print(f"[bold]Target:[/bold] {args['url'].replace('FCK', '<word>')}")
    if args['body']:
        console.print(f"[bold]Body:[/bold] {args['body'].replace('FCK', '<word>')}")
    console.print(f"[bold]Filters:[/bold] {filters}")
    console.print(f"[bold]Output Filters:[/bold] {output_filters}")
    console.print(f"[bold]Threads:[/bold] {args['threads']}")
    if args['fetch_response']:
        console.print(f"[bold]Fetching response for word:[/bold] {args['fetch_response']}")
    console.print("-" * 80)

    if args['fetch_response']:
        if args['fetch_response'] not in words:
            console.print(f"[red]Error: Word '{args['fetch_response']}' not in wordlist.[/red]")
            sys.exit(1)
        url, data = prepare_request(args['url'], args['body'], args['fetch_response'], args['method'])
        response = make_request(url, args['method'], data, args['timeout'], args['debug'])
        console.print(f"[bold cyan]HTML Response for '{args['fetch_response']}':[/bold cyan]")
        console.print(response['c'])
        console.print("-" * 80)
        console.print(f"[bold]Status:[/bold] {response['s']} | [bold]Length:[/bold] {response['l']} | [bold]Time:[/bold] {response['t']:.2f}s")
        if response.get('error'):
            console.print(f"[red]Error: {response['error']}[/red]")
        return

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
                future_to_word = {
                    executor.submit(process_word, word, args, filters, output_filters): word
                    for word in words
                }
                for future in as_completed(future_to_word):
                    word, response = future.result()
                    progress.advance(task)  # Update progress in the main thread
                    if response:
                        matches_found = True
                        error = f" [red]Error: {response['error']}[/red]" if response.get('error') else ""
                        console.print(f"[bold]Word:[/bold] {word} | [bold]Status:[/bold] {response['s']} | [bold]Length:[/bold] {response['l']} | [bold]Time:[/bold] {response['t']:.2f}s{error}")
                    time.sleep(0.01)  # Small delay to prevent server overload
        
        if matches_found:
            console.print("[bold magenta]💀 Brute Force Complete! All words processed successfully! 💀[/bold magenta]")
        else:
            console.print("[bold yellow]⚠ Brute Force Complete! No matches found. Check filters or use -r to inspect HTML. ⚠[/bold yellow]")
        
        if args['debug'] and not matches_found:
            console.print("[yellow]Debug: No responses matched the output filters. Try inspecting HTML with -r or adjusting the filter.[/yellow]")
    
    except KeyboardInterrupt:
        console.print("\n[red bold]Process stopped by user.[/red bold]")
        sys.exit(1)

if __name__ == "__main__":
    main()
