import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from .tree_parser import AdvancedCodeParser
from .embedder import CodeEmbedder
from .vector_store import VectorStore
from .local_generator import LocalCodeQAGenerator
from .config import CodeRAGConfig
from .file_scanner import FileScanner

console = Console()

@click.group()
def cli():
    """Code RAG - Index and query your codebase"""
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True, path_type=Path), default='.')
@click.option('--clear', is_flag=True, help='Clear existing index')
@click.option('--config', type=click.Path(path_type=Path), help='Config file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def index(directory: Path, clear: bool, config: Path, verbose: bool):
    """Index code files in directory"""
    
    config_obj = CodeRAGConfig(config)
    scanner = FileScanner(config_obj)
    parser = AdvancedCodeParser()
    embedder = CodeEmbedder()
    vector_store = VectorStore(config_obj.get("index_directory"))
    
    if clear:
        console.print("Clearing existing index...", style="yellow")
        vector_store.clear()
    
    console.print(f"Scanning directory: {directory}", style="blue")
    files = scanner.scan_directory(directory)
    
    if not files:
        console.print("No supported files found", style="red")
        return
    
    stats = scanner.get_file_stats(files)
    
    table = Table(title="File Statistics")
    table.add_column("Extension", style="cyan")
    table.add_column("Count", justify="right")
    
    for ext, count in stats["by_extension"].items():
        table.add_row(ext, str(count))
    
    console.print(table)
    console.print(f"Total size: {stats['total_size'] / 1024:.1f} KB")
    
    all_chunks = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Parsing files...", total=len(files))
        
        for file_path in files:
            if verbose:
                console.print(f"Parsing {file_path}")
            
            try:
                chunks = parser.parse_file(file_path)
                all_chunks.extend(chunks)
                
                if verbose:
                    console.print(f"  Found {len(chunks)} chunks")
                    
            except Exception as e:
                console.print(f"Error parsing {file_path}: {e}", style="red")
            
            progress.update(task, advance=1)
    
    if not all_chunks:
        console.print("No code chunks found", style="red")
        return
    
    console.print(f"Generating embeddings for {len(all_chunks)} chunks...")
    embeddings = embedder.embed_chunks(all_chunks)
    
    console.print("Storing in vector database...")
    vector_store.add_chunks(all_chunks, embeddings)
    
    console.print(f"Successfully indexed {len(all_chunks)} code chunks!", style="green")

@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=5, help='Number of results')
@click.option('--config', type=click.Path(path_type=Path), help='Config file path')
def search(query: str, limit: int, config: Path):
    """Search indexed code"""
    
    config_obj = CodeRAGConfig(config)
    embedder = CodeEmbedder()
    vector_store = VectorStore(config_obj.get("index_directory"))
    
    console.print(f"Searching for: [bold]{query}[/bold]")
    
    query_embedding = embedder.embed_query(query)
    results = vector_store.search(query_embedding, n_results=limit)
    
    if not results:
        console.print("No results found", style="red")
        return
    
    for i, result in enumerate(results, 1):
        console.print(f"\n[bold blue]Result {i}[/bold blue] (score: {result.score:.3f})")
        console.print(f"[dim]{result.chunk.file_path}:{result.chunk.start_line}-{result.chunk.end_line}[/dim]")
        console.print(f"[yellow]{result.chunk.chunk_type}[/yellow]")
        console.print(f"```\n{result.chunk.content}\n```")

@cli.command()
@click.argument('question')
@click.option('--limit', '-l', default=3, help='Context chunks to use')
@click.option('--config', type=click.Path(path_type=Path), help='Config file path')
def ask(question: str, limit: int, config: Path):
    """Ask a question about the codebase"""
    
    config_obj = CodeRAGConfig(config)
    embedder = CodeEmbedder()
    vector_store = VectorStore(config_obj.get("index_directory"))
    generator = LocalCodeQAGenerator()
    
    console.print(f"Question: [bold]{question}[/bold]")
    
    query_embedding = embedder.embed_query(question)
    search_results = vector_store.search(query_embedding, n_results=limit)
    
    if not search_results:
        console.print("No relevant code found", style="red")
        return
    
    console.print("Analyzing relevant code...")
    answer = generator.answer_question(question, search_results)
    
    console.print(f"\n[bold green]Answer:[/bold green]")
    console.print(answer)
    
    console.print(f"\n[dim]Based on {len(search_results)} code chunks[/dim]")

@cli.command()
def init():
    """Initialize code-rag in current directory"""
    config = CodeRAGConfig()
    config.save_config()
    console.print("Created .coderag.json config file", style="green")
    console.print("Edit this file to customize file patterns and ignore rules")

@cli.command()
@click.option('--config', type=click.Path(path_type=Path), help='Config file path')
def status(config: Path):
    """Show indexing status"""
    config_obj = CodeRAGConfig(config)
    vector_store = VectorStore(config_obj.get("index_directory"))
    
    try:
        count = len(vector_store.collection.get()['ids'])
        console.print(f"Indexed chunks: {count}")
    except:
        console.print("No index found - run 'code-rag index' first")

if __name__ == '__main__':
    cli()