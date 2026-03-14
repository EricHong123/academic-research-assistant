"""Main entry point for the Academic Research Assistant."""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


def main():
    """Run the application."""
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    reload_enabled = os.getenv("DEBUG", "true").lower() == "true"

    if reload_enabled:
        # Use import string for reload mode
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=True,
        )
    else:
        # Direct app for production
        from src.api.main import app
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
        )


if __name__ == "__main__":
    main()
