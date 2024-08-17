import pandas as pd

# Nome do arquivo Excel
arquivo_excel = 'inventario_prateleira.xlsx'

# Carrega a planilha existente
df = pd.read_excel(arquivo_excel)

# Verifica se a coluna 'Código' existe, caso contrário, cria-a
if 'Código' not in df.columns:
    df['Código'] = None

# Atribui códigos sequenciais aos itens que ainda não têm código
codigo_atual = 1 if df['Código'].isnull().all() else df['Código'].max() + 1

for i in df.index:
    if pd.isnull(df.at[i, 'Código']):
        df.at[i, 'Código'] = codigo_atual
        codigo_atual += 1

# Salva as mudanças de volta na planilha
df.to_excel(arquivo_excel, index=False)

print("Códigos atribuídos com sucesso aos itens existentes.")
