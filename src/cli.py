import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import tempfile
import shutil
from .tree_parser import AdvancedCodeParser
from .embedder import CodeEmbedder
from .vector_store import VectorStore
from .local_generator import LocalCodeQAGenerator
from .config import CodeRAGConfig
from .file_scanner import FileScanner
from .indexer import IncrementalIndexer
from .github_downloader import GitHubDownloader

console = Console()

@click.group()
@click.version_option(version="0.2.0")
def cli():
    """Code RAG - Index and query any codebase with AI"""
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True, path_type=Path), default='.')
@click.option('--clear', is_flag=True, help='Clear existing index')
@click.option('--config', type=click.Path(path_type=Path), help='Config file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--force', is_flag=True, help='Force reindex all files')
def index(directory: Path, clear: bool, config: Path, verbose: bool, force: bool):
    """Index code files in directory (incremental by default)"""
    
    config_obj = CodeRAGConfig(config)
    scanner = FileScanner(config_obj)
    indexer = IncrementalIndexer(config_obj, console)
    
    if clear:
        console.print("Clearing existing index...", style="yellow")
        indexer.vector_store.clear()
    
    console.print(f"Scanning directory: {directory}", style="blue")
    files = scanner.scan_directory(directory)
    
    if not files:
        console.print("No supported files found", style="red")
        return
    
    stats = scanner.get_file_stats(files)
    
    if verbose:
        table = Table(title="File Statistics")
        table.add_column("Extension", style="cyan")
        table.add_column("Count", justify="right")
        
        for ext, count in stats["by_extension"].items():
            table.add_row(ext, str(count))
        
        console.print(table)
        console.print(f"Total size: {stats['total_size'] / 1024:.1f} KB")
    
    result = indexer.index_files(files, force_reindex=force or clear)
    
    console.print(f"Processed {result['files_processed']} files, "
                 f"added {result['chunks_added']} chunks", style="green")

@cli.command()
@click.argument('github_url')
@click.option('--target', type=click.Path(path_type=Path), help='Target directory')
@click.option('--config', type=click.Path(path_type=Path), help='Config file path')
def index_github(github_url: str, target: Path, config: Path):
    """Index a GitHub repository"""
    
    config_obj = CodeRAGConfig(config)
    downloader = GitHubDownloader(console)
    
    if target is None:
        target = Path(tempfile.mkdtemp(prefix="code_rag_"))
    
    try:
        if downloader.download_repo(github_url, target):
            scanner = FileScanner(config_obj)
            indexer = IncrementalIndexer(config_obj, console)
            
            files = scanner.scan_directory(target)
            if files:
                result = indexer.index_files(files, force_reindex=True)
                console.print(f"Indexed GitHub repo: {result['chunks_added']} chunks", style="green")
            else:
                console.print("No supported files found in repository", style="red")
    finally:
        if target.exists() and target.name.startswith("code_rag_"):
            shutil.rmtree(target)

@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=5, help='Number of results')
@click.option('--config', type=click.Path(path_type=Path), help='Config file path')
@click.option('--file-filter', help='Filter by file pattern (e.g., "*.py")')
@click.option('--type-filter', help='Filter by chunk type (function, class, import)')
def search(query: str, limit: int, config: Path, file_filter: str, type_filter: str):
    """Search indexed code with optional filters"""
    
    config_obj = CodeRAGConfig(config)
    embedder = CodeEmbedder()
    vector_store = VectorStore(config_obj.get("index_directory"))
    
    console.print(f"Searching for: [bold]{query}[/bold]")
    
    query_embedding = embedder.embed_query(query)
    results = vector_store.search(query_embedding, n_results=limit * 2)
    
    if file_filter or type_filter:
        filtered_results = []
        for result in results:
            if file_filter and not Path(result.chunk.file_path).match(file_filter):
                continue
            if type_filter and not result.chunk.chunk_type.startswith(type_filter):
                continue
            filtered_results.append(result)
        results = filtered_results[:limit]
    else:
        results = results[:limit]
    
    if not results:
        console.print("No results found", style="red")
        return
    
    for i, result in enumerate(results, 1):
        console.print(f"\n[bold blue]Result {i}[/bold blue] (score: {result.score:.3f})")
        console.print(f"[dim]{result.chunk.file_path}:{result.chunk.start_line}-{result.chunk.end_line}[/dim]")
        console.print(f"[yellow]{result.chunk.chunk_type}[/yellow]")
        console.print(f"```\n{result.chunk.content}\n```")

@cli.command()
@click.option('--config', type=click.Path(path_type=Path), help='Config file path')
def stats(config: Path):
    """Show detailed indexing statistics"""
    config_obj = CodeRAGConfig(config)
    vector_store = VectorStore(config_obj.get("index_directory"))
    
    try:
        data = vector_store.collection.get()
        total_chunks = len(data['ids'])
        
        if total_chunks == 0:
            console.print("No indexed chunks found", style="red")
            return
        
        file_stats = {}
        type_stats = {}
        
        for metadata in data['metadatas']:
            file_path = metadata.get('file_path', 'unknown')
            chunk_type = metadata.get('chunk_type', 'unknown')
            
            file_stats[file_path] = file_stats.get(file_path, 0) + 1
            type_stats[chunk_type] = type_stats.get(chunk_type, 0) + 1
        
        console.print(f"Total indexed chunks: {total_chunks}")
        console.print(f"Files indexed: {len(file_stats)}")
        
        type_table = Table(title="Chunks by Type")
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", justify="right")
        
        for chunk_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            type_table.add_row(chunk_type, str(count))
        
        console.print(type_table)
        
    except Exception as e:
        console.print(f"Error reading index: {e}", style="red")

if __name__ == '__main__':
    cli()