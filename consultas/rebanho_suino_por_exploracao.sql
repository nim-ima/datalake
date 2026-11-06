WITH mov AS (
  SELECT
    ctexp.id_exploracao,
    ftm.cd_municipio_ibge,
    ftm.ds_municipio,
    cte.nm_especie,
    ctes.id_faixa_etaria,
    ctl.qt_animal_lancamento * CASE
        WHEN ctl.id_tipo_lancamento = 32 THEN 1
        WHEN ctl.id_tipo_lancamento = 26 THEN -1
        WHEN ctl.in_debito_credito = 'C' THEN 1
        ELSE -1
    END AS mov
  FROM db_dlsidagro_staging.client_tb_exploracao ctexp
  JOIN db_dlsidagro_staging.client_tb_propriedade ctprop ON ctprop.id_propriedade = ctexp.id_propriedade
  JOIN db_dlsidagro_staging.client_tb_pessoa ctps ON ctps.id_pessoa = ctprop.id_pessoa_juridica
  JOIN db_dlsidagro_staging.fiscal_tb_municipio ftm ON ftm.id_municipio = ctps.id_municipio
  JOIN db_dlsidagro_staging.client_tb_especie cte ON cte.id_especie = ctexp.id_especie
  JOIN db_dlsidagro_staging.client_tb_nucleo ctn ON ctn.id_exploracao = ctexp.id_exploracao
  JOIN db_dlsidagro_staging.client_tb_estratificacao_nucleo cten ON cten.id_nucleo = ctn.id_nucleo
  JOIN db_dlsidagro_staging.client_tb_estratificacao ctes ON ctes.id_estratificacao = cten.id_estratificacao
  JOIN db_dlsidagro_staging.client_tb_lancamento ctl ON ctl.id_estratificacao_nucleo = cten.id_estratificacao_nucleo
  WHERE ctl.id_tipo_lancamento IN (25,26,27,28,29,31,32,34,37)
    AND ctexp.id_especie = 14
    AND ctexp.in_ativo = 'S'
    -- AND CAST(ctl.dt_lancamento AS DATE) <= '2026-11-06'  -- opcional: data de corte
)
SELECT
  id_exploracao,
  cd_municipio_ibge,
  ds_municipio,
  nm_especie,
  SUM(CASE WHEN id_faixa_etaria = 67 THEN mov ELSE 0 END) AS macho_leitao,
  SUM(CASE WHEN id_faixa_etaria = 68 THEN mov ELSE 0 END) AS femea_leitao,
  SUM(CASE WHEN id_faixa_etaria = 65 THEN mov ELSE 0 END) AS macho_reprodutor_cachaco,
  SUM(CASE WHEN id_faixa_etaria = 66 THEN mov ELSE 0 END) AS femea_matriz,
  SUM(CASE WHEN id_faixa_etaria = 69 THEN mov ELSE 0 END) AS sexo_idade_nao_relevantes,
  SUM(mov) AS total
FROM mov
GROUP BY id_exploracao, cd_municipio_ibge, ds_municipio, nm_especie
HAVING SUM(mov) > 0
ORDER BY cd_municipio_ibge, id_exploracao;