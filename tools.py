import subprocess
from datetime import datetime

try:
    from duckduckgo_search import DDGS
    _DDGS_OK = True
except ImportError:
    _DDGS_OK = False

try:
    from googlesearch import search as gsearch
    _GOOGLE_OK = True
except ImportError:
    _GOOGLE_OK = False

try:
    import requests
    from bs4 import BeautifulSoup
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False


def web_search(query: str) -> str:
    if not _DDGS_OK:
        return "Errore: libreria duckduckgo-search non installata."
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        if not results:
            return "Nessun risultato trovato."
        return "\n\n".join(
            f"**{r['title']}**\n{r['body']}\n{r['href']}" for r in results
        )
    except Exception as e:
        return f"Errore ricerca: {e}"


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content if content else "(file vuoto)"
    except FileNotFoundError:
        return f"File non trovato: {path}"
    except Exception as e:
        return f"Errore: {e}"


def write_file(path: str, content: str) -> str:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File scritto: {path}"
    except Exception as e:
        return f"Errore: {e}"


def run_python(code: str) -> str:
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout or result.stderr or "(nessun output)"
        return output[:2000]
    except subprocess.TimeoutExpired:
        return "Timeout: codice troppo lento (limite 10s)."
    except Exception as e:
        return f"Errore: {e}"


def google_search(query: str) -> str:
    if not _GOOGLE_OK:
        return "Errore: libreria googlesearch-python non installata."
    try:
        results = list(gsearch(query, num_results=5, advanced=True, lang="it"))
        if not results:
            return "Nessun risultato trovato."
        return "\n\n".join(
            f"**{r.title}**\n{r.description}\n{r.url}" for r in results
        )
    except Exception as e:
        return f"Errore ricerca Google: {e}"


def fetch_url(url: str) -> str:
    if not _REQUESTS_OK:
        return "Errore: librerie requests/beautifulsoup4 non installate."
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text[:3000]
    except Exception as e:
        return f"Errore nel fetch della pagina: {e}"


def get_datetime() -> str:
    return datetime.now().strftime("%A %d %B %Y, %H:%M:%S")


TOOLS = {
    "google_search": google_search,
    "web_search": web_search,
    "fetch_url": fetch_url,
    "read_file": read_file,
    "write_file": write_file,
    "run_python": run_python,
    "get_datetime": get_datetime,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "google_search",
            "description": "Cerca su Google. È il motore di ricerca principale — usalo sempre come prima scelta quando hai bisogno di cercare informazioni su internet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "La query di ricerca"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Legge il contenuto testuale di una pagina web dato il suo URL. Usalo dopo google_search per leggere il contenuto delle pagine trovate e ottenere informazioni aggiornate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL della pagina da leggere"}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Cerca informazioni su internet tramite DuckDuckGo. Usalo solo se google_search fallisce o non dà risultati.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "La query di ricerca"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Legge il contenuto di un file dal filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Percorso del file"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Scrive o sovrascrive un file sul filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Percorso del file"},
                    "content": {"type": "string", "description": "Contenuto da scrivere"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Esegue codice Python e restituisce l'output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Codice Python da eseguire"}
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Restituisce la data e l'ora corrente.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    if name not in TOOLS:
        return f"Tool '{name}' non trovato."
    try:
        return str(TOOLS[name](**args))
    except Exception as e:
        return f"Errore nell'esecuzione di '{name}': {e}"
