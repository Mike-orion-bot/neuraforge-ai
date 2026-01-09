#!/bin/bash
cd "$(dirname "$0")"
echo "🔄 Sincronización rápida..."
git add . 2>/dev/null || true
git commit -m "Auto-sync $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
git pull origin main 2>/dev/null || true
git push origin main 2>/dev/null || true
echo "✅ Sincronización completada"
