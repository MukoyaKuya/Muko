import os
import sys
from pathlib import Path

# Use the virtual environment created by cPanel's Python App manager.  The
# explicit re-exec matters on hosts where Passenger otherwise starts with the
# system Python instead of this application's selected Python version.
project_root = Path(__file__).resolve().parent
venv_python = (
    project_root.parent
    / "virtualenv"
    / project_root.name
    / "3.13"
    / "bin"
    / "python"
)
if venv_python.is_file() and Path(sys.executable).resolve() != venv_python.resolve():
    os.execl(str(venv_python), str(venv_python), *sys.argv)

# Add the project root directory to the Python path.
sys.path.insert(0, str(project_root))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import the WSGI application
from config.wsgi import application
