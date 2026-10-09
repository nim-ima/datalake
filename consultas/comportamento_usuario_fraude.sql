SELECT *
FROM db_dlsidagro_staging.core_tb_Log AS ctlog
JOIN db_dlsidagro_staging.core_tb_log_detalhe AS ctld
    ON  ctld.id_log = ctlog.id_log
WHERE ctlog.dt_log > '2026-01-01'
AND ctld.ds_valor_atual LIKE  '214483%'
AND ctlog.ds_entidade = 'Usuario'

UNION

SELECT *
FROM db_dlsidagro_staging.core_tb_Log AS ctlog
JOIN db_dlsidagro_staging.core_tb_log_detalhe AS ctld
    ON ctld.id_log = ctlog.id_log
WHERE ctlog.dt_log > '2026-01-01'
AND ctld.ds_valor_anterior LIKE  '214483%'
AND ctlog.ds_entidade = 'Usuario'



SELECT *
FROM db_dlsidagro_staging.core_tb_Log AS ctlog
JOIN db_dlsidagro_staging.core_tb_log_detalhe AS ctld
    ON ctld.id_log = ctlog.id_log
WHERE ctlog.dt_log> '2026-01-01'
AND ctlog.id_usuario = 214483
AND ctld.ds_valor_atual = '214483: ATAIDE DIVINO ROSA FILHO'
AND ctld.nm_atributo = 'usuarioAtualizou'
AND ctld.ds_valor_anterior IS NOT NULL
ORDER BY ctlog.dt_log DESC



SELECT *
FROM db_dlsidagro_staging.core_tb_Log AS ctlog
JOIN db_dlsidagro_staging.core_tb_log_detalhe AS ctld
    ON ctld.id_log = ctlog.id_log
WHERE ctlog.dt_log> '2026-01-01'
AND ctld.ds_valor_anterior = '214483: ATAIDE DIVINO ROSA FILHO'
AND ctld.nm_atributo = 'usuarioAtualizou'
AND ctld.ds_valor_anterior IS NOT NULL 
ORDER BY ctlog.dt_log DESC



SELECT *
FROM db_dlsidagro_staging.core_tb_Log AS ctlog
WHERE ctlog.id_usuario = 214483 
AND ctlog.dt_log > '2026-01-01' 
AND ctlog.ds_entidade ='email'