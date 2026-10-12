"""Lightweight execution engine for Python and Java code challenges."""
import os
import subprocess
import tempfile
import time
from typing import Dict, Any, List

def run_code(language: str, code: str, custom_input: str = "") -> Dict[str, Any]:
    """Execute code safely and capture stdout, stderr, execution time."""
    lang = language.lower().strip()
    
    if lang == "python":
        return _run_python(code, custom_input)
    elif lang == "java":
        return _run_java(code, custom_input)
    elif lang in ["javascript", "js"]:
        return _run_node(code, custom_input)
    else:
        return {
            "success": False,
            "output": "",
            "error": f"Language '{language}' execution is not supported locally.",
            "execution_time_ms": 0
        }


def _run_python(code: str, custom_input: str) -> Dict[str, Any]:
    start_time = time.time()
    try:
        process = subprocess.run(
            ["python", "-c", code],
            input=custom_input,
            capture_output=True,
            text=True,
            timeout=5
        )
        duration = int((time.time() - start_time) * 1000)
        return {
            "success": process.returncode == 0,
            "output": process.stdout,
            "error": process.stderr,
            "execution_time_ms": duration
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Execution timed out (Time Limit: 5 seconds). Check for infinite loops.",
            "execution_time_ms": 5000
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "execution_time_ms": 0
        }


def _run_java(code: str, custom_input: str) -> Dict[str, Any]:
    start_time = time.time()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Determine class name or use Main
        class_name = "Solution"
        if "public class " in code:
            parts = code.split("public class ")[1].split("{")[0].strip().split()
            if parts:
                class_name = parts[0]

        file_path = os.path.join(tmpdir, f"{class_name}.java")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            # Compile
            compile_proc = subprocess.run(
                ["javac", file_path],
                capture_output=True,
                text=True,
                timeout=8
            )
            if compile_proc.returncode != 0:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Compilation Error:\n{compile_proc.stderr}",
                    "execution_time_ms": int((time.time() - start_time) * 1000)
                }

            # Run
            run_proc = subprocess.run(
                ["java", "-cp", tmpdir, class_name],
                input=custom_input,
                capture_output=True,
                text=True,
                timeout=5
            )
            duration = int((time.time() - start_time) * 1000)
            return {
                "success": run_proc.returncode == 0,
                "output": run_proc.stdout,
                "error": run_proc.stderr,
                "execution_time_ms": duration
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Execution timed out (Time Limit: 5 seconds).",
                "execution_time_ms": 5000
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time_ms": 0
            }


def _run_node(code: str, custom_input: str) -> Dict[str, Any]:
    start_time = time.time()
    try:
        process = subprocess.run(
            ["node", "-e", code],
            input=custom_input,
            capture_output=True,
            text=True,
            timeout=5
        )
        duration = int((time.time() - start_time) * 1000)
        return {
            "success": process.returncode == 0,
            "output": process.stdout,
            "error": process.stderr,
            "execution_time_ms": duration
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "execution_time_ms": 0
        }
