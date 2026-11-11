import os
import discord
from discord.ext import commands
import requests

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def pesquisar_editais_pncp(termo):
    url = "https://pncp.gov.br/api/contratacoes/v1/pesquisar"
    params = {
        "q": termo,
        "modalidades": [3, 6], # 3 = Pregão Eletrônico, 6 = Dispensa Eletrônica
        "pagina": 1,
        "tamanhoPagina": 10
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    
    resultados = []
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            dados = response.json()
            lista = dados.get("resultado", []) if isinstance(dados, dict) else dados
            
            for item in lista:
                numero_compra = item.get("numeroCompra", item.get("numero", "N/A"))
                ano = item.get("ano", "2026")
                
                unidade = item.get("unidadeCompradora", {})
                uasg = unidade.get("codigoUnidade", "N/A")
                orgao = item.get("orgaoNome", "Órgão não informado")
                modalidade = item.get("modalidadeNome", "Pregão / Dispensa")
                objeto = item.get("objetoContratacao") or item.get("objeto") or "Objeto não informado"
                
                cnpj = item.get("orgaoCnpj", "")
                sequencial = item.get("sequencial", item.get("sequencialCompra", ""))
                link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}" if (cnpj and sequencial) else "https://compras.gov.br"
                
                resultados.append({
                    "edital": f"{numero_compra}/{ano}",
                    "uasg": uasg,
                    "orgao": orgao,
                    "modalidade": modalidade,
                    "objeto": objeto,
                    "link": link
                })
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        
    return resultados

@bot.event
async def on_ready():
    print(f"Bot online e pronto como {bot.user}!")

@bot.command(name="licitacoes")
async def consultar_licitacoes(ctx, *, termo: str):
    await ctx.send(f"🔍 Pesquisando licitações para **'{termo}'**...")
    
    compras = pesquisar_editais_pncp(termo)
    
    if not compras:
        await ctx.send(f"❌ Nenhuma licitação encontrada para **'{termo}'** no momento.")
        return
        
    for c in compras[:5]:
        mensagem = (
            f"📦 **{c['modalidade']} | Edital:** `{c['edital']}`\n"
            f"🏛️ **Unidade Compradora (UASG):** `{c['uasg']}`\n"
            f"🏢 **Órgão:** {c['orgao']}\n"
            f"📝 **Objeto:** {c['objeto'][:150]}...\n"
            f"🔗 **Link:** {c['link']}\n"
            f"-----------------------------------"
        )
        await ctx.send(mensagem)

# Pega o token de forma segura direto das variáveis de ambiente do Render
token = os.getenv("DISCORD_TOKEN")
bot.run(token)