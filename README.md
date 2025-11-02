# connector

## Limpieza de __pycache__

Para eliminar todos los directorios `__pycache__`:

**Windows (PowerShell):**
```powershell
.\clean_cache.ps1
```

**Python:**
```bash
python clean_cache.py
```

## Prevenir la creación de __pycache__

Para evitar que Python genere archivos `__pycache__`, puedes usar una de estas opciones:

1. **Variable de entorno** (recomendado):
   ```powershell
   # PowerShell
   $env:PYTHONDONTWRITEBYTECODE = "1"
   
   # CMD
   set PYTHONDONTWRITEBYTECODE=1
   ```

2. **Al ejecutar scripts:**
   ```bash
   python -B script.py
   ```

3. **En el código Python:**
   ```python
   import sys
   sys.dont_write_bytecode = True
   ```
