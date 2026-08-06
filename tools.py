import os
import subprocess
import pyautogui
import pytesseract
from PIL import Image
from pdf2docx import Converter
from docx2pdf import convert
import pandas as pd
import tempfile

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
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        out = result.stdout
        err = result.stderr
        if result.returncode != 0:
            return f"Command failed with code {result.returncode}.\nSTDOUT: {out}\nSTDERR: {err}"
        return out if out else "Command executed successfully with no output."
    except Exception as e:
        return f"Error executing command: {e}"

def capture_screen(save_path: str = "screenshot.png") -> str:
    """Takes a screenshot of the current screen."""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        return f"Screenshot saved to {save_path}"
    except Exception as e:
        return f"Error capturing screen: {e}"

def recognize_text_from_screen() -> str:
    """Takes a screenshot and runs OCR to extract text from the screen."""
    try:
        temp_img = tempfile.mktemp(suffix=".png")
        pyautogui.screenshot(temp_img)
        text = pytesseract.image_to_string(Image.open(temp_img), lang='eng+rus')
        os.remove(temp_img)
        return f"Extracted text from screen:\n{text}"
    except Exception as e:
        return f"Error recognizing text: {e}. Note: Make sure Tesseract is installed."

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
            "name": "capture_screen",
            "description": "Takes a screenshot of the user's current screen and saves it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "save_path": {"type": "string"}
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
                "properties": {}
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
    elif name == "capture_screen":
        return capture_screen(arguments.get("save_path", "screenshot.png"))
    elif name == "recognize_text_from_screen":
        return recognize_text_from_screen()
    elif name == "convert_pdf_to_word":
        return convert_pdf_to_word(arguments.get("pdf_path"), arguments.get("docx_path"))
    elif name == "convert_word_to_pdf":
        return convert_word_to_pdf(arguments.get("docx_path"), arguments.get("pdf_path"))
    elif name == "read_excel":
        return read_excel(arguments.get("excel_path"))
    else:
        return f"Error: Unknown tool '{name}'"
