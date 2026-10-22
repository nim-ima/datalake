-- EXTRAÇÃO DADOS PTV ABANORTE - A CADA 3 DIAS -
SELECT 
    cptv.dt_emissao,
    cptv.tp_documento_fundamentacao,
    mno.cd_municipio AS cod_muni_origem,
    mno.ds_municipio AS municipio_origem,
    mnd.cd_municipio AS cod_muni_destino,
    mnd.ds_municipio AS municipio_destino,
    ctc.nm_cultura,
    ctv.nm_variedade,
    cptvp.qt_colheita_producao AS total_carga,
    ctum.ds_unidade_medida
FROM db_dlsidagro_staging.client_tb_ptv AS cptv
JOIN db_dlsidagro_staging.core_tb_municipio AS mno
    ON cptv.id_municipio_origem = mno.id_municipio
JOIN db_dlsidagro_staging.core_tb_municipio AS mnd
    ON cptv.id_municipio_destino = mnd.id_municipio
JOIN db_dlsidagro_staging.client_tb_ptv_produto AS cptvp
    ON cptv.id_ptv = cptvp.id_ptv
JOIN db_dlsidagro_staging.client_tb_unidade_medida AS ctum
    ON cptvp.id_unidade_medida = ctum.id_unidade_medida
JOIN db_dlsidagro_staging.client_tb_variedade AS ctv
    ON cptvp.id_variedade = ctv.id_variedade
JOIN db_dlsidagro_staging.client_tb_cultura	AS ctc
    ON ctv.id_cultura = ctc.id_cultura
WHERE cptv.dt_emissao >= '2026-10-05'
AND ctc.nm_cultura = 'BANANA'