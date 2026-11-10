import os
import requests
from datetime import datetime, timedelta

# ==========================================
# SUA LISTA DE ITENS PARA MONITORAR
# ==========================================
TERMOS_BUSCA = [
    "lâmpada", 
    "toner", 
]

def buscar_compras():
    url = "https://pncp.gov.br/api/search"
    compras_encontradas = []
    
    print("Iniciando varredura no Portal de Compras...")
    
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
                        compras_encontradas.append({
                            "termo": termo,
                            "orgao": item.get("orgaoNome", "Órgão não informado"),
                            "modalidade": item.get("modalidadeNome", "Pregão/Dispensa"),
                            "objeto": item.get("objeto"),
                            "link": item.get("linkSistemaOrigem") or item.get("uri") or "https://compras.gov.br"
                        })
        except Exception as e:
            print(f"Erro ao buscar o termo '{termo}': {e}")
            
    return compras_encontradas

def enviar_alerta_discord(compras):
    
    webhook_url = "https://discord.com/api/webhooks/1569842977470414938/MzlRqaOxTaR_gZiIjq2buGTQW95kycdzPP4kaxrV66Ib5H1Yp5eU94vH3gzfeTLe7BmT"
    
    if not compras:
        print("Nenhuma nova compra encontrada nesta execução.")
        return

    for compra in compras:
        mensagem = {
            "content": (
                f"🚨 **Oportunidade Encontrada!** `[{compra['termo'].upper()}]`\n"
                f"🏢 **Órgão:** {compra['orgao']}\n"
                f"📋 **Modalidade:** {compra['modalidade']}\n"
                f"📦 **Objeto:** {compra['objeto']}\n"
                f"🔗 **Link:** {compra['link']}"
            )
        }
        
        resposta = requests.post(webhook_url, json=mensagem)
        if resposta.status_code == 204:
            print(f"Alerta enviado com sucesso para o termo: {compra['termo']}")

if __name__ == "__main__":
    resultados = buscar_compras()
    enviar_alerta_discord(resultados)
