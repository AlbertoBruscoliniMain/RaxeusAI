#!/usr/bin/env python3
"""
rag_index.py — Indicizza file di testo nel database vettoriale RAG.

Uso:
    python rag_index.py <file_o_cartella> [<file_o_cartella> ...]

Formati supportati: .txt  .md  .pdf

Esempi:
    python rag_index.py note.txt
    python rag_index.py ~/Documenti/appunti/
    python rag_index.py articolo.pdf promemoria.md

Il database viene salvato in rag_db/ (nella cartella del progetto).
Per resettare tutto: cancella la cartella rag_db/ e riesegui.
"""

import os
import sys

try:
    import chromadb
except ImportError:
    print("Errore: chromadb non installato. Esegui: pip install chromadb")
    sys.exit(1)

try:
    from pypdf import PdfReader
    _PYPDF_OK = True
except ImportError:
    _PYPDF_OK = False

from config import RAG_DB_PATH

CHUNK_SIZE = 600
CHUNK_OVERLAP = 60
SUPPORTED_EXT = {".txt", ".md", ".pdf"}


def chunk_text(text: str) -> list[str]:
    chunks = []
    text = text.strip()
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        if not _PYPDF_OK:
            print(f"  [SKIP] pypdf non installato — impossibile leggere {path}")
            return ""
        try:
            reader = PdfReader(path)
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            print(f"  [ERRORE] {path}: {e}")
            return ""
    else:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"  [ERRORE] {path}: {e}")
            return ""


def collect_files(paths: list[str]) -> list[str]:
    files = []
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.isfile(p):
            if os.path.splitext(p)[1].lower() in SUPPORTED_EXT:
                files.append(p)
            else:
                print(f"  [SKIP] {p} (formato non supportato)")
        elif os.path.isdir(p):
            for root, _, filenames in os.walk(p):
                for fn in sorted(filenames):
                    if os.path.splitext(fn)[1].lower() in SUPPORTED_EXT:
                        files.append(os.path.join(root, fn))
        else:
            print(f"  [SKIP] {p} (non trovato)")
    return files


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    paths = sys.argv[1:]
    files = collect_files(paths)

    if not files:
        print("Nessun file .txt/.md/.pdf trovato nei percorsi indicati.")
        sys.exit(1)

    print(f"File trovati: {len(files)}\n")

    client = chromadb.PersistentClient(path=RAG_DB_PATH)

    try:
        collection = client.get_collection("documents")
        print(f"Database esistente trovato in {RAG_DB_PATH}")
    except Exception:
        collection = client.create_collection("documents")
        print(f"Nuovo database creato in {RAG_DB_PATH}")

    print()
    total_new = 0

    for path in files:
        abs_path = os.path.abspath(path)
        text = read_file(path)
        if not text.strip():
            print(f"  [SKIP] {path} (vuoto o non leggibile)")
            continue

        chunks = chunk_text(text)
        basename = os.path.basename(path)
        ids = [f"{abs_path}::{i}" for i in range(len(chunks))]
        metadatas = [{"source": abs_path, "file": basename} for _ in chunks]

        # Upsert: aggiorna i chunk già esistenti, aggiunge i nuovi
        collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
        print(f"  [OK] {path} → {len(chunks)} chunk")
        total_new += len(chunks)

    count = collection.count()
    print(f"\nFatto. Chunk aggiunti/aggiornati: {total_new}")
    print(f"Totale chunk nel database: {count}")
    print(f"Database: {RAG_DB_PATH}")


if __name__ == "__main__":
    main()
