#!/usr/bin/env python3
"""
Marker PDF to Markdown API Server

A FastAPI server that wraps the Marker PDF converter for GPU-accelerated
PDF to Markdown conversion.

Usage:
    python marker_server.py --port 5203 --gpu 7

Requirements:
    pip install marker-pdf fastapi uvicorn
"""

import argparse
import os
import tempfile
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse arguments
parser = argparse.ArgumentParser(description="Marker PDF to Markdown API Server")
parser.add_argument("--port", type=int, default=5203, help="Port to listen on")
parser.add_argument("--gpu", type=str, default="7", help="GPU device ID")
parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
args = parser.parse_args()

# Set environment variables
os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
os.environ.setdefault("HF_HOME", str(Path.home() / ".cache" / "huggingface"))
os.environ.setdefault("DATALAB_CACHE", str(Path.home() / ".cache" / "datalab"))

logger.info(f"Starting Marker server on {args.host}:{args.port} with GPU {args.gpu}")

app = FastAPI(
    title="Marker PDF to Markdown API",
    description="GPU-accelerated PDF to Markdown conversion using Marker",
    version="1.0.0"
)

# Lazy load converter to avoid slow imports on startup
_converter = None

def get_converter():
    global _converter
    if _converter is None:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict

        logger.info("Loading Marker models...")
        model_dict = create_model_dict()
        _converter = PdfConverter(artifact_dict=model_dict)
        logger.info("Marker models loaded successfully")
    return _converter


@app.get("/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "marker-pdf"}


@app.post("/v1/parse/file")
async def parse_pdf_file(file: UploadFile = File(...)):
    """
    Parse a PDF file and return Markdown content.

    Returns:
        JSON with:
        - markdown: The converted Markdown content
        - metadata: Document metadata (pages, etc.)
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        logger.info(f"Processing PDF: {file.filename}")

        # Convert
        converter = get_converter()
        result = converter(tmp_path)

        # Extract markdown
        markdown = result.markdown if hasattr(result, 'markdown') else str(result)

        # Extract metadata
        metadata = {}
        if hasattr(result, 'meta'):
            metadata = {
                'title': getattr(result.meta, 'title', None),
                'author': getattr(result.meta, 'author', None),
                'page_count': getattr(result, 'page_count', None),
            }

        # Cleanup
        os.unlink(tmp_path)

        return JSONResponse(content={
            "markdown": markdown,
            "metadata": metadata,
            "filename": file.filename
        })

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/parse/url")
async def parse_pdf_url(url: str):
    """
    Download and parse a PDF from URL.

    Note: This is a placeholder - implement if needed.
    """
    raise HTTPException(status_code=501, detail="URL parsing not implemented yet")


if __name__ == "__main__":
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
