#ASEMG: 
#- Com base no relatório AnalíticoTransito:
  
Leitura do arquivo:
df0 = pd.read_csv("{}/AnaliticoTransito(8).csv".format(my_address_bd), sep="\t", encoding="latin1",  on_bad_lines = "skip")

# Filtro das colunas:
df_sui = df[['DATA EMISSÃO','FINALIDADE DE TRÂNSITO', 'ESPÉCIE', 'CÓDIGO DO MUNICÍPIO ORIGEM',
             'MUNICÍPIO ORIGEM','UF DESTINO', 'CÓDIGO MUNICÍPIO DESTINO', 'MUNICÍPIO DESTINO',
             'Macho Leitão (Indefinido)', 'Fêmea Leitão (Indefinido)', 'Macho Reprodutor (Cachaço) (Indefinido)',
             'Fêmea Matriz (Indefinido)', 'Sexo e idade não relevantes (Indefinido)',
             'TOTAL DE MACHOS', 'TOTAL DE FÊMEAS', 'TOTAL DE ANIMAIS']]

# Agrupamento:
df_asemg = df_sui.groupby(['DATA EMISSÃO','FINALIDADE DE TRÂNSITO', 'ESPÉCIE', 'CÓDIGO DO MUNICÍPIO ORIGEM',
             'MUNICÍPIO ORIGEM','UF DESTINO', 'CÓDIGO MUNICÍPIO DESTINO', 'MUNICÍPIO DESTINO'])[['Macho Leitão (Indefinido)', 'Fêmea Leitão (Indefinido)', 'Macho Reprodutor (Cachaço) (Indefinido)',
             'Fêmea Matriz (Indefinido)', 'Sexo e idade não relevantes (Indefinido)',
             'TOTAL DE MACHOS', 'TOTAL DE FÊMEAS', 'TOTAL DE ANIMAIS']].sum().reset_index()

# Salva arquivo csv:
df_asemg.to_csv("{}/TRANSITO_SUINOS_AGOSTO2026.csv".format(my_address), index=False, encoding="utf-8-sig")