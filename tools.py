import os
import subprocess
import pyautogui
import pytesseract
from PIL import Image
from pdf2docx import Converter
from docx2pdf import convert
import pandas as pd
import tempfile
import pygetwindow as gw
import pandas as pd
import tempfile
from duckduckgo_search import DDGS

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def list_directory(path: str = ".") -> str:
    """Lists the contents of a directory."""
    try:
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        items = os.listdir(path)
        if not items:
            return f"Directory '{path}' is empty."
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {e}"

def read_file(path: str) -> str:
    """Reads the contents of a text file."""
    try:
        if not os.path.exists(path):
            return f"Error: File '{path}' does not exist."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path: str, content: str) -> str:
    """Writes content to a text file. Overwrites if it exists."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{path}'."
    except Exception as e:
        return f"Error writing file: {e}"

def run_command(command: str) -> str:
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True)
        try:
            out = result.stdout.decode('utf-8')
            err = result.stderr.decode('utf-8')
        except UnicodeDecodeError:
            try:
                out = result.stdout.decode('cp1251')
                err = result.stderr.decode('cp1251')
            except UnicodeDecodeError:
                out = result.stdout.decode('cp866', errors='replace')
                err = result.stderr.decode('cp866', errors='replace')
                
        if result.returncode != 0:
            return f"Command failed with code {result.returncode}.\nSTDOUT: {out}\nSTDERR: {err}"
        return out if out else "Command executed successfully with no output."
    except Exception as e:
        return f"Error executing command: {e}"

def open_file(path: str) -> str:
    """Opens a file or URL with the default Windows application."""
    try:
        os.startfile(path)
        return f"Successfully opened {path}"
    except Exception as e:
        return f"Error opening file: {e}"

def get_window_bbox(window_title=None):
    if not window_title:
        return None
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return None
        win = windows[0]
        return (win.left, win.top, win.width, win.height)
    except Exception:
        return None

def capture_screen(save_path: str = "screenshot.png", window_title: str = None) -> str:
    """Takes a screenshot of the current screen or a specific window."""
    try:
        bbox = get_window_bbox(window_title)
        if bbox:
            screenshot = pyautogui.screenshot(region=bbox)
        else:
            screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        return f"Screenshot saved to {save_path}"
    except Exception as e:
        return f"Error capturing screen: {e}"

def recognize_text_from_screen(window_title: str = None) -> str:
    """Takes a screenshot and runs OCR to extract text from the screen or specific window."""
    try:
        bbox = get_window_bbox(window_title)
        if bbox:
            img = pyautogui.screenshot(region=bbox)
        else:
            img = pyautogui.screenshot()
            
        text = pytesseract.image_to_string(img, lang='eng+rus')
        return f"Extracted text from screen:\n{text}"
    except pytesseract.TesseractNotFoundError:
        return (
            "ОШИБКА OCR: Программа Tesseract не установлена! "
            "Пожалуйста, скажите пользователю следующее: "
            "«Чтобы я мог читать текст с экрана, вам нужно установить программу Tesseract. "
            "Скачайте её по ссылке: https://github.com/UB-Mannheim/tesseract/wiki и установите. "
            "После этого я смогу читать всё, что вы мне покажете!»"
        )
    except Exception as e:
        return f"Error recognizing text: {e}"

def convert_pdf_to_word(pdf_path: str, docx_path: str) -> str:
    """Converts a PDF file to a Word (docx) file."""
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return f"Successfully converted {pdf_path} to {docx_path}"
    except Exception as e:
        return f"Error converting PDF to Word: {e}"

def convert_word_to_pdf(docx_path: str, pdf_path: str) -> str:
    """Converts a Word (docx) file to a PDF file."""
    try:
        convert(docx_path, pdf_path)
        return f"Successfully converted {docx_path} to {pdf_path}"
    except Exception as e:
        return f"Error converting Word to PDF: {e}"

def read_excel(excel_path: str) -> str:
    """Reads an Excel file and returns its summary."""
    try:
        df = pd.read_excel(excel_path)
        return f"Excel file {excel_path} has {len(df)} rows and {len(df.columns)} columns.\nColumns: {', '.join(df.columns.astype(str))}\nHead:\n{df.head(3).to_string()}"
    except Exception as e:
        return f"Error reading Excel: {e}"

def search_web(query: str) -> str:
    """Searches the web using DuckDuckGo and returns the top 3 results."""
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return f"No results found for '{query}'."
        
        output = f"Top 3 Web Search Results for '{query}':\n\n"
        for i, res in enumerate(results, 1):
            output += f"{i}. {res.get('title')}\n{res.get('body')}\nURL: {res.get('href')}\n\n"
        return output.strip()
    except Exception as e:
        return f"Error searching the web: {e}"

# Tool definitions for the LLM
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Lists all files and folders in a specified directory path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads and returns the contents of a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Creates or overwrites a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Executes a shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Opens a file (image, text, etc) using the default Windows application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to open."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "capture_screen",
            "description": "Takes a screenshot of the user's current screen or a specific window and saves it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "save_path": {"type": "string"},
                    "window_title": {"type": "string", "description": "Optional title of the window to capture."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recognize_text_from_screen",
            "description": "Takes a screenshot and extracts text from it using OCR. Useful for answering 'what is on my screen'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "window_title": {"type": "string", "description": "Optional title of the window to extract text from."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_pdf_to_word",
            "description": "Converts a PDF file to a DOCX (Word) file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string"},
                    "docx_path": {"type": "string"}
                },
                "required": ["pdf_path", "docx_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_word_to_pdf",
            "description": "Converts a DOCX (Word) file to a PDF file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "docx_path": {"type": "string"},
                    "pdf_path": {"type": "string"}
                },
                "required": ["docx_path", "pdf_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_excel",
            "description": "Reads an Excel file and returns a summary and the first few rows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "excel_path": {"type": "string"}
                },
                "required": ["excel_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the internet for current events, news, or factual information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query (e.g., 'news in Krasnoyarsk today')"}
                },
                "required": ["query"]
            }
        }
    }
]

def execute_tool(name: str, arguments: dict) -> str:
    if name == "list_directory":
        return list_directory(arguments.get("path", "."))
    elif name == "read_file":
        return read_file(arguments.get("path"))
    elif name == "write_file":
        return write_file(arguments.get("path"), arguments.get("content"))
    elif name == "run_command":
        return run_command(arguments.get("command"))
    elif name == "open_file":
        return open_file(arguments.get("path"))
    elif name == "capture_screen":
        return capture_screen(arguments.get("save_path", "screenshot.png"), arguments.get("window_title"))
    elif name == "recognize_text_from_screen":
        return recognize_text_from_screen(arguments.get("window_title"))
    elif name == "convert_pdf_to_word":
        return convert_pdf_to_word(arguments.get("pdf_path"), arguments.get("docx_path"))
    elif name == "convert_word_to_pdf":
        return convert_word_to_pdf(arguments.get("docx_path"), arguments.get("pdf_path"))
    elif name == "read_excel":
        return read_excel(arguments.get("excel_path"))
    elif name == "search_web":
        return search_web(arguments.get("query"))
    else:
        return f"Error: Unknown tool '{name}'"
