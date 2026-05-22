import importlib
import sys

packages = {
    "Core": ["fastapi", "uvicorn", "multipart", "pydantic_settings", "aiofiles"],
    "Database": ["sqlalchemy", "asyncpg", "psycopg2", "alembic", "redis"],
    "Security": ["jose", "passlib", "bcrypt"],
    "AI/ML Core": ["torch", "torchvision", "timm", "sklearn", "numpy", "pandas", "albumentations"],
    "Computer Vision": ["cv2", "PIL", "deepface", "fer"],
    "NLP/RAG": ["transformers", "langchain", "langchain_ollama", "chromadb"],
    "Voice": ["whisper", "edge_tts", "soundfile"],
    "Visualization & PDF": ["matplotlib", "fpdf", "reportlab"],
    "Monitoring": ["prometheus_client", "prometheus_fastapi_instrumentator"],
    "Testing": ["pytest", "httpx"]
}

print("=" * 50)
print("  AI WellnessVision — Dependency Verification  ")
print("=" * 50)

all_passed = True

for category, pkg_list in packages.items():
    print(f"\n{category}:")
    for pkg in pkg_list:
        try:
            importlib.import_module(pkg)
            print(f"  [ OK ] {pkg}")
        except ImportError:
            print(f"  [FAIL] {pkg} (Missing or failed to import)")
            all_passed = False

print("\n" + "=" * 50)
if all_passed:
    print("✅ All critical dependencies are successfully installed.")
else:
    print("❌ Some dependencies failed to import. Check the requirements.txt.")
    sys.exit(1)
