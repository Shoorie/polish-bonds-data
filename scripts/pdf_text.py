import subprocess
import tempfile


def text_of(pdf: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as file:
        file.write(pdf)
        file.flush()
        return subprocess.run(
            ["pdftotext", "-layout", file.name, "-"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout
