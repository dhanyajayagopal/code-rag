# Code RAG — AI-Powered Code Documentation System

**Code RAG** is a Retrieval-Augmented Generation (RAG) system I built for code documentation and semantic exploration of codebases. I designed it to support intelligent search and question-answering over code, using modern NLP and vector search techniques. The system supports local inference, making it suitable for offline or privacy-sensitive development environments.

---

## What I Built

### Project Purpose
I developed Code RAG to enable developers to ask natural-language questions about their codebases and receive contextually accurate answers. The system combines static code parsing with deep semantic understanding through embeddings.

### Architecture Overview

I implemented a complete RAG pipeline tailored for code. The major components include:

- **Code Parsing**: AST-based parsers for Python, JavaScript, and TypeScript.
- **Embedding Generation**: Sentence transformer models to represent code semantics.
- **Vector Storage**: Integrated ChromaDB for fast and scalable similarity search.
- **Query Interface**: CLI tool with rich terminal output.
- **Incremental Indexing**: Hash-based change detection to avoid unnecessary reprocessing.

---

## What I Learned

### Vector Embeddings & Semantic Search

- Used sentence-transformer models to embed code into 384-dimensional vectors.
- Learned how cosine similarity improves search relevance over keyword matching.
- Explored trade-offs between model size, inference speed, and accuracy.

### End-to-End RAG Design

- Built a full retrieval system: parsing, chunking, embedding, answer generation.
- Designed chunking strategies that preserve contextual meaning in code.
- Implemented fallback mechanisms for when AI models are unavailable.

### Performance Engineering

- Created a hash-based incremental indexer to avoid full reprocessing.
- Optimized memory usage and latency in the embedding/retrieval loop.
- Supported large codebases via configurable ignore patterns.

### Developer Tooling

- Developed a production-ready CLI using `click` and `rich` with error handling and progress bars.
- Built a flexible configuration system for different project types.
- Packaged the tool for pip-based installation with proper entry points.
  
---

## Usage

### Basic Operations

**Index a codebase:**  
Index your project directory to prepare it for semantic search and question answering.

**Search for code:**  
Perform a natural-language search across your indexed codebase.

**Ask questions about the code:**  
Query the system with high-level or implementation-specific questions to get intelligent answers.

---

### Advanced Features

**Index a GitHub repo:**  
Fetch and index code directly from public GitHub repositories.

**Filter search results:**  
Narrow down search results using type or file pattern filters.

**View indexing statistics:**  
See detailed stats about the indexed project, including file count, function count, and chunking metrics.

---

## Configuration

**Initialize a configuration file:**  
Set up a project-specific config file to customize indexing behavior.

**Example Configuration Includes:**

- File patterns to include (e.g., Python, JS, TS)
- Folders to ignore (e.g., node_modules, venv)
- Max file size limits
- Embedding model selection

---

## Implementation Highlights

### Code Parsing

Used regex and AST-based methods to extract functions, classes, imports, and docstrings, preserving the structure and semantics of the code.

### Embedding Strategy

Built semantic vector representations of code chunks using transformer-based models for accurate similarity comparisons.

### Vector Search

Employed cosine similarity in a vector database for fast, relevant code retrieval with support for metadata filtering.

### Incremental Indexing

Implemented change detection using hash functions to skip unchanged files and reduce indexing time.

---

## Example Query Types

- How is user authentication implemented?  
- What are the main API endpoints?  
- Where is input validation performed?  
- How are exceptions handled in this codebase?  

---

## Performance Benchmarks

- Indexing throughput: approximately 1000 lines per second  
- Search latency: under 100 milliseconds  
- Memory footprint: around 2GB for medium-large codebases  
- Storage overhead: about 10MB per 100k lines of code  

---

## Challenges I Solved

### Preserving Context

Ensured code chunks included imports, docstrings, and surrounding class/function context for semantic completeness.

### Multi-language Support

Built modular parsing logic to support Python, JavaScript, and TypeScript with consistent structure extraction.

### Scalability

Enabled parallel and streaming indexing, along with customizable chunk sizes and ignore rules for handling large repositories.

---

## Validation

Tested Code RAG on well-known open-source projects and evaluated query accuracy on over 100 natural-language questions to ensure high relevance and reliability.

---

## Future Improvements

### Technical Enhancements

- Multi-modal embeddings (combining code and documentation)
- Call graph modeling using graph neural networks
- Real-time streaming for continuous embedding updates

### User Experience

- Browser-based UI for easier access
- IDE plugin for in-context querying
- Collaborative features like annotation and feedback sharing

---

## Dependencies

- Sentence embedding models for semantic understanding  
- Vector database for efficient retrieval  
- CLI libraries for user interaction and output formatting  
- Transformer-based language models for local inference  
