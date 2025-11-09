"""Script para eliminar todos los directorios __pycache__ del proyecto"""
import shutil
from pathlib import Path

def clean_pycache():
    """Elimina todos los directorios __pycache__ recursivamente"""
    project_root = Path(__file__).parent
    removed_count = 0
    
    for pycache_dir in project_root.rglob('__pycache__'):
        if pycache_dir.is_dir():
            print(f"Eliminando: {pycache_dir}")
            shutil.rmtree(pycache_dir)
            removed_count += 1
    
    print(f"\n✅ Se eliminaron {removed_count} directorio(s) __pycache__")
    if removed_count == 0:
        print("No se encontraron directorios __pycache__ para eliminar")

if __name__ == "__main__":
    clean_pycache()
