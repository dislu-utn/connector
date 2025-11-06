#!/usr/bin/env python3
"""
Script para generar un DISLU_SECRET seguro.
Ejecutar: python generate_secret.py
"""

import secrets

def generate_secure_secret(length=32):
    """
    Genera un secret seguro usando el módulo secrets de Python.
    
    Args:
        length (int): Longitud del secret en bytes (default 32 = 256 bits)
    
    Returns:
        str: Secret URL-safe
    """
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("=" * 60)
    print("Generador de DISLU_SECRET")
    print("=" * 60)
    print()
    
    secret = generate_secure_secret(32)
    
    print("Tu nuevo DISLU_SECRET seguro es:")
    print()
    print(f"  {secret}")
    print()
    print("Copia este valor y úsalo en:")
    print("  1. El archivo .env del connector: DISLU_SECRET=<valor>")
    print("  2. El archivo .env de dislu: DISLU_SECRET=<valor>")
    print()
    print("⚠️  IMPORTANTE:")
    print("  - Guarda este secret de forma segura")
    print("  - No lo compartas públicamente")
    print("  - No lo commits en git")
    print("  - Úsalo SOLO con HTTPS en producción")
    print()
    print("=" * 60)

