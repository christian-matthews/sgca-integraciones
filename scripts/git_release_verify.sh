#!/bin/bash
#
# git_release_verify.sh
# =====================
# Verifica y prepara el repo para deploy en Render.
# Asegura que el código local esté sincronizado con el remoto.
#
# Uso:
#   ./scripts/git_release_verify.sh
#   bash scripts/git_release_verify.sh
#

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}   GIT RELEASE VERIFY - SGCA Integraciones${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Verificar que estamos en un repo git válido
# ═══════════════════════════════════════════════════════════════════════════════

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: No estás dentro de un repositorio git válido.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Repositorio git válido${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Información del repo
# ═══════════════════════════════════════════════════════════════════════════════

REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
LAST_COMMIT=$(git log -1 --oneline)

echo ""
echo -e "${YELLOW}📁 Repo:${NC}   ${REPO_NAME}"
echo -e "${YELLOW}🌿 Branch:${NC} ${CURRENT_BRANCH}"
echo -e "${YELLOW}📝 Commit:${NC} ${LAST_COMMIT}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Verificar si el working tree está limpio
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}----------------------------------------------------------------------${NC}"
echo -e "${BLUE}Verificando estado del working tree...${NC}"
echo -e "${BLUE}----------------------------------------------------------------------${NC}"

STATUS=$(git status --porcelain)

if [ -z "$STATUS" ]; then
    echo -e "${GREEN}✓ Working tree limpio - nada que commitear${NC}"
else
    echo -e "${YELLOW}⚠️  Working tree tiene cambios sin commitear:${NC}"
    echo ""
    git status --porcelain
    echo ""
    
    # Pedir confirmación
    read -p "¿Deseas commitear todos los cambios? (y/n): " CONFIRM
    
    if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
        echo ""
        echo -e "${BLUE}Commiteando cambios...${NC}"
        git add -A
        git commit -m "chore(release): sync bridge for render cron"
        echo -e "${GREEN}✓ Cambios commiteados${NC}"
    else
        echo -e "${YELLOW}⚠️  Cambios NO commiteados. El deploy puede no reflejar tu código local.${NC}"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Push al remoto
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}----------------------------------------------------------------------${NC}"
echo -e "${BLUE}Sincronizando con remoto...${NC}"
echo -e "${BLUE}----------------------------------------------------------------------${NC}"

# Push con -u para setear upstream si no existe
if git push -u origin "${CURRENT_BRANCH}" 2>&1; then
    echo -e "${GREEN}✓ Push exitoso a origin/${CURRENT_BRANCH}${NC}"
else
    echo -e "${YELLOW}⚠️  Push falló o ya está actualizado${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Resumen final
# ═══════════════════════════════════════════════════════════════════════════════

LOCAL_HEAD=$(git rev-parse HEAD)
SHORT_HEAD=$(git rev-parse --short HEAD)

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}   RESUMEN - LISTO PARA RENDER${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo -e "${GREEN}✅ Hash local:${NC} ${LOCAL_HEAD}"
echo -e "${GREEN}✅ Short hash:${NC} ${SHORT_HEAD}"
echo -e "${GREEN}✅ Branch:${NC}     ${CURRENT_BRANCH}"
echo ""
echo -e "${YELLOW}👉 Para verificar en Render ejecutar:${NC}"
echo "   git rev-parse HEAD"
echo ""
echo -e "${YELLOW}👉 Branch esperada en Render:${NC}"
echo "   ${CURRENT_BRANCH}"
echo ""
echo -e "${YELLOW}👉 Si el hash no coincide:${NC}"
echo "   1. Verifica que Render esté configurado con branch: ${CURRENT_BRANCH}"
echo "   2. Haz Manual Deploy desde el dashboard de Render"
echo "   3. O espera al próximo deploy automático"
echo ""
echo -e "${BLUE}======================================================================${NC}"
echo ""

