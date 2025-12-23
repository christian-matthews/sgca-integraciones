-- ═══════════════════════════════════════════════════════════════════════════════
-- MIGRACIÓN: erp_backlog_snapshots
-- ═══════════════════════════════════════════════════════════════════════════════
-- Tabla para almacenar snapshots continuos del backlog de ERP (Odoo)
-- Permite tracking histórico de pendientes por empresa y período
--
-- Ejecutar en Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════════════

-- Crear tabla
CREATE TABLE IF NOT EXISTS erp_backlog_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Referencia a empresa
    company_id UUID NOT NULL REFERENCES companies(company_id),
    
    -- Período (YYYY-MM)
    period VARCHAR(7) NOT NULL,
    
    -- Timestamp de captura (America/Santiago)
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Contadores de backlog
    sii_count INTEGER NOT NULL DEFAULT 0,
    contabilizar_count INTEGER NOT NULL DEFAULT 0,
    conciliar_count INTEGER NOT NULL DEFAULT 0,
    
    -- Metadata
    source VARCHAR(50) NOT NULL DEFAULT 'odoo',
    db_alias VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para queries eficientes
CREATE INDEX IF NOT EXISTS idx_backlog_snapshots_company_period 
    ON erp_backlog_snapshots(company_id, period);

CREATE INDEX IF NOT EXISTS idx_backlog_snapshots_captured_at 
    ON erp_backlog_snapshots(captured_at DESC);

CREATE INDEX IF NOT EXISTS idx_backlog_snapshots_period 
    ON erp_backlog_snapshots(period);

-- Comentarios
COMMENT ON TABLE erp_backlog_snapshots IS 'Snapshots históricos del backlog de ERP para tracking de tendencias';
COMMENT ON COLUMN erp_backlog_snapshots.period IS 'Período en formato YYYY-MM';
COMMENT ON COLUMN erp_backlog_snapshots.sii_count IS 'Documentos pendientes en SII';
COMMENT ON COLUMN erp_backlog_snapshots.contabilizar_count IS 'Asientos por contabilizar';
COMMENT ON COLUMN erp_backlog_snapshots.conciliar_count IS 'Movimientos bancarios por conciliar';
COMMENT ON COLUMN erp_backlog_snapshots.source IS 'Fuente de datos (odoo, skualo, etc)';
COMMENT ON COLUMN erp_backlog_snapshots.db_alias IS 'Alias de la base de datos origen (FactorIT, FactorIT2)';

-- RLS (Row Level Security)
ALTER TABLE erp_backlog_snapshots ENABLE ROW LEVEL SECURITY;

-- Política para service role (backend)
CREATE POLICY "Service role full access on erp_backlog_snapshots"
    ON erp_backlog_snapshots
    FOR ALL
    USING (auth.role() = 'service_role');

-- Política para usuarios autenticados (solo lectura de sus empresas via company_memberships)
CREATE POLICY "Users can view their company snapshots"
    ON erp_backlog_snapshots
    FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_memberships 
            WHERE user_id = auth.uid()
        )
    );

-- ═══════════════════════════════════════════════════════════════════════════════
-- Vista útil: último snapshot por empresa
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE VIEW v_latest_backlog_snapshot AS
SELECT DISTINCT ON (company_id)
    snapshot_id,
    company_id,
    period,
    captured_at,
    sii_count,
    contabilizar_count,
    conciliar_count,
    (sii_count + contabilizar_count + conciliar_count) as total_backlog,
    source,
    db_alias
FROM erp_backlog_snapshots
ORDER BY company_id, captured_at DESC;

COMMENT ON VIEW v_latest_backlog_snapshot IS 'Último snapshot de backlog por empresa';

