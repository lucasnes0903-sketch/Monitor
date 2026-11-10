import os
import requests
from datetime import datetime

# ==========================================
# SUA LISTA DE ITENS PARA MONITORAR
# ==========================================
TERMOS_BUSCA = [
    "lâmpada", 
    "toner", 
    "luvas de procedimento", 
    "álcool em gel"
]

def buscar_compras():
    url = "https://pncp.gov.br/api/search"
    compras_encontradas = []
    
    print("Iniciando varredura diária no Portal de Compras...")
    
    for termo in TERMOS_BUSCA:
        params = {
            "q": termo,
            "status": "ativa",
            "pagina": 1,
            "tamanhoPagina": 15
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                dados = response.json()
                for item in dados.get("items", []):
                    objeto = item.get("objeto", "").lower()
                    if termo.lower() in objeto:
                        # Extrai informações solicitadas
                        orgao_nome = item.get("orgaoNome", "Órgão não informado")
                        uasg = item.get("unidadeCompradora", {}).get("codigoUnidade", "UASG não informada")
                        numero_compra = item.get("numeroCompra", "N/A")
                        ano_compra = item.get("anoCompra", "")
                        modalidade = item.get("modalidadeNome", "Pregão/Dispensa")
                        
                        # Formata identificador do pregão/dispensa
                        identificador = f"{numero_compra}/{ano_compra}" if ano_compra else numero_compra
                        
                        compras_encontradas.append({
                            "termo": termo,
                            "modalidade": modalidade,
                            "identificador": identificador,
                            "uasg": uasg,
                            "orgao": orgao_nome,
                            "link": item.get("linkSistemaOrigem") or item.get("uri") or "https://compras.gov.br"
                        })
        except Exception as e:
            print(f"Erro ao buscar o termo '{termo}': {e}")
            
    return compras_encontradas

def enviar_alerta_discord(compras):
    # Cole aqui a URL completa do Webhook do seu Discord entre as aspas
    webhook_url = "https://discord.com/api/webhooks/1569842977470414938/MzlRqaOxTaR_gZiIjq2buGTQW95kycdzPP4kaxrV66Ib5H1Yp5eU94vH3gzfeTLe7BmT"
    
    if not compras:
        mensagem = {"content": "📋 **Relatório Diário:** Nenhuma nova compra ativa encontrada hoje para os termos monitorados."}
        requests.post(webhook_url, json=mensagem)
        return

    # Cabeçalho da listagem
    cabecalho = f"🌅 **BOM DIA! Aqui estão as oportunidades ativas encontradas hoje ({datetime.now().strftime('%d/%m/%Y')}):**\n"
    requests.post(webhook_url, json={"content": cabecalho})

    # Envia cada item em formato de lista simples e limpa
    for compra in compras:
        texto_item = (
            f"🔹 **Item:** `{compra['termo'].upper()}`\n"
            f"📋 **{compra['modalidade']} Nº:** `{compra['identificador']}`\n"
            f"🏛️ **UASG (Órgão):** `{compra['uasg']}` — *{compra['orgao']}*\n"
            f"🔗 **Link Direto:** {compra['link']}\n"
            f"-----------------------------------"
        )
        requests.post(webhook_url, json={"content": texto_item})

if __name__ == "__main__":
    resultados = buscar_compras()
    enviar_alerta_discord(resultados)
