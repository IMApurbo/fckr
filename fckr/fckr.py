
import requests
import argparse
import sys
import re
import time
from typing import Optional, List, Tuple, Dict
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich import print as rprint
from rich.live import Live
from rich.style import Style
import signal
from urllib.parse import parse_qs, urlencode

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
    """Display ASCII logo and text with a typewriter-like typing effect and gradient colors."""
    logo = """
  █████▒▄████▄   ██ ▄█▀
▓██   ▒▒██▀ ▀█   ██▄█▒ 		   ╦╔╦╗╔═╗┌─┐┬ ┬┬─┐┌┐ ┌─┐
▒████ ░▒▓█    ▄ ▓███▄░ 	AUTHOR:    ║║║║╠═╣├─┘│ │├┬┘├┴┐│ │
░▓█▒  ░▒▓▓▄ ▄██▒▓██ █▄ 	           ╩╩ ╩╩ ╩┴  └─┘┴└─└─┘└─┘
░▒█░   ▒ ▓███▀ ░▒██▒ █▄
 ▒ ░   ░ ░▒ ▒  ░▒ ▒▒ ▓▒
 ░       ░  ▒   ░ ░▒ ▒░
 ░ ░   ░        ░ ░░ ░ 
       ░ ░      ░  ░   
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

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(
        description="CLI Request Brute Forcer - A tool for brute-forcing HTTP requests with customizable filters.\n\n"
                    "Notes:\n"
                    "- Use -u to specify the target URL.\n"
                    "- Use -b to specify the POST body for POST requests.\n"
                    "- Either -u alone (for GET) or -u with -b (for POST) must be provided."
    )
    parser.add_argument('-u', '--url', required=True, help="Target URL with optional FCK placeholder (e.g., https://example.com/?q=FCK)")
    parser.add_argument('-b', '--body', help="POST body with FCK placeholder (e.g., searchFor=FCK&goButton=go)")
    parser.add_argument('-w', '--wordlist', required=True, help="Path to wordlist file")
    parser.add_argument('-m', '--method', choices=['GET', 'POST'], default='GET', help="HTTP method")
    parser.add_argument('-t', '--timeout', type=float, default=5.0, help="Request timeout in seconds")
    parser.add_argument(
        '-F', '--filter',
        action='append',
        help="Filter responses before processing. Only responses matching ALL -F filters proceed.\n\n"
             "Filtering Options:\n"
             "  Fields:\n"
             "    - s: Status code (e.g., 200, 404)\n"
             "    - l: Content length (e.g., 1234)\n"
             "    - c: Response body content (e.g., success, <title>Login</title>)\n\n"
             "  Types:\n"
             "    - e: Exact match\n"
             "    - c: Contains match (case-insensitive, HTML attributes normalized)\n"
             "    - nc: Not contains match (case-insensitive, HTML attributes normalized)\n\n"
             "Examples:\n"
             "  - s:e:200\n"
             "  - c:c:success\n"
             "  - c:nc:something\n"
             "  - l:e:1000\n"
             "  - c:c:'<h2 class=lead>results</h2>'"
    )
    parser.add_argument(
        '-o', '--output-filter',
        action='append',
        help="Filter which responses are displayed. Responses must match AT LEAST ONE -o filter.\n\n"
             "Filtering Options:\n"
             "  Fields:\n"
             "    - s: Status code (e.g., 200, 404)\n"
             "    - l: Content length (e.g., 1234)\n"
             "    - c: Response body content (e.g., success, <title>Login</title>)\n\n"
             "  Types:\n"
             "    - e: Exact match\n"
             "    - c: Contains match (case-insensitive, HTML attributes normalized)\n"
             "    - nc: Not contains match (case-insensitive, HTML attributes normalized)\n\n"
             "Examples:\n"
             "  - s:e:200\n"
             "  - c:c:success\n"
             "  - c:nc:something\n"
             "  - l:e:1000\n"
             "  - c:c:'<h2 class=lead>results</h2>'"
    )
    parser.add_argument('-r', '--fetch-response', help="Fetch full HTML response for a specific word")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode to log requests and filter mismatches")
    
    args = parser.parse_args()

    if args.method.upper() == 'POST' and not args.body:
        console.print("[red]Error: -b/--body is required for POST requests.[/red]")
        sys.exit(1)
    if args.method.upper() == 'GET' and args.body:
        console.print("[red]Error: -b/--body is not allowed for GET requests.[/red]")
        sys.exit(1)

    display_animated_logo()
    console.print("-" * 80)

    words = load_wordlist(args.wordlist)
    filters = parse_filters(args.filter or [])
    output_filters = parse_filters(args.output_filter or [])

    console.print(f"[bold]Starting brute force with {len(words)} words...[/bold]")
    console.print(f"[bold]Method:[/bold] {args.method}")
    console.print(f"[bold]Target:[/bold] {args.url.replace('FCK', '<word>')}")
    if args.body:
        console.print(f"[bold]Body:[/bold] {args.body.replace('FCK', '<word>')}")
    console.print(f"[bold]Filters:[/bold] {filters}")
    console.print(f"[bold]Output Filters:[/bold] {output_filters}")
    if args.fetch_response:
        console.print(f"[bold]Fetching response for word:[/bold] {args.fetch_response}")
    console.print("-" * 80)

    if args.fetch_response:
        if args.fetch_response not in words:
            console.print(f"[red]Error: Word '{args.fetch_response}' not in wordlist.[/red]")
            sys.exit(1)
        url, data = prepare_request(args.url, args.body, args.fetch_response, args.method)
        response = make_request(url, args.method, data, args.timeout, args.debug)
        console.print(f"[bold cyan]HTML Response for '{args.fetch_response}':[/bold cyan]")
        console.print(response['c'])
        console.print("-" * 80)
        console.print(f"[bold]Status:[/bold] {response['s']} | [bold]Length:[/bold] {response['l']} | [bold]Time:[/bold] {response['t']:.2f}s")
        if response.get('error'):
            console.print(f"[red]Error: {response['error']}[/red]")
        return

    matches_found = False
    progress = Progress(
        TextColumn("[cyan]Working..."),
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
            for word in words:
                url, data = prepare_request(args.url, args.body, word, args.method)
                response = make_request(url, args.method, data, args.timeout, args.debug)

                should_skip = False
                for f in filters:
                    if not matches_filter(response, f['type'], f['value'], f['field']):
                        should_skip = True
                        break
                if should_skip:
                    if args.debug:
                        console.print(f"[yellow]Debug: Word '{word}' skipped by filter {f}[/yellow]")
                    progress.advance(task)
                    continue

                should_display = not output_filters
                for f in output_filters:
                    if matches_filter(response, f['type'], f['value'], f['field']):
                        should_display = True
                        break
                if should_display:
                    matches_found = True
                    error = f" [red]Error: {response['error']}[/red]" if response.get('error') else ""
                    console.print(f"[bold]Word:[/bold] {word} | [bold]Status:[/bold] {response['s']} | [bold]Length:[/bold] {response['l']} | [bold]Time:[/bold] {response['t']:.2f}s{error}")
                elif args.debug:
                    console.print(f"[yellow]Debug: Word '{word}' did not match output filter {output_filters}[/yellow]")
                
                progress.advance(task)
                time.sleep(0.5)
        
        if matches_found:
            console.print("[bold magenta]🎉 Brute Force Complete! All words processed successfully! 🎉[/bold magenta]")
        else:
            console.print("[bold yellow]⚠ Brute Force Complete! No matches found. Check filters or use -r to inspect HTML. ⚠[/bold yellow]")
        
        if args.debug and not matches_found:
            console.print("[yellow]Debug: No responses matched the output filters. Try inspecting HTML with -r or adjusting the filter.[/yellow]")
    
    except KeyboardInterrupt:
        console.print("\n[red bold]Process stopped by user.[/red bold]")
        sys.exit(1)

if __name__ == "__main__":
    main()
