"""Main entry point for the Academic Research Assistant."""
import os
import sys
import asyncio

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


def main():
    """Run the application."""
    import uvicorn
    from src.api.main import app

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "true").lower() == "true",
    )


if __name__ == "__main__":
    main()
