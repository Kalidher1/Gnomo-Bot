import discord
from discord.ext import commands,tasks
import os
from random import randint
from discord.voice_client import VoiceClient
from dotenv import load_dotenv
import youtube_dl
import asyncio
from time import sleep
load_dotenv()

indexLista = 0

queue = []
loop = False

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("O bot não esta conectado em nenhum chat de voz.")

@bot.command(name='fila')
async def fila(ctx, url):

    queue.append(url)
    await ctx.send(f'`{url}` adicionado a fila')

@bot.command(name='loop')
async def loop_(ctx):
    global queue
    queue = [queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0],queue[0]]
    await ctx.send("LOOPEI")
        
@bot.command(name='play', help='This command plays music')
async def play(ctx,url = ""):
    try:
        await fila(ctx, url)
    except Exception as e:
        await ctx.send(str(e))
    global queue

    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    
    else:
        channel = ctx.message.author.voice.channel

    try: await channel.connect()
    except: pass

    server = ctx.message.guild
    voice_channel = server.voice_client
    
    try:
        async with ctx.typing():
            player = await YTDLSource.from_url(queue[0])
            voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else play(ctx))
    
        await ctx.send('**Now playing:** {}'.format(player.title))

    except Exception as e:
        await ctx.send(str(e))

@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    global queue
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("Não to tocando nada não seu maluco do caralho")
    queue = []

@bot.command(name='skip', help='Bestooooooooooooooooooooooooooooooga')
async def skip(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("TA TOCANDO GURIZADA")
    else:
        await ctx.send("Não to tocando nada não seu maluco do caralho")
    del queue[0] 
    await play(ctx)

@bot.command(name='view', help='This command shows the queue')
async def view(ctx):
    await ctx.send(f'Your queue is now `{queue}!`')
    
@bot.command(name='clear', help='Stops the song')
async def clear(ctx):
    global queue
    queue = [] 
    await ctx.send("Fila limpa bando de bocó")
    
@bot.command(name='morra', help='Stops the song')
async def morra(ctx):
    await ctx.send("MORRE PRAGA IMUNDA VERME MISERAVEL ESPERO QUE VOCÊ BATA O DEDINHO NA CAMA SEU SACO DE MERDA QUE CHAMAM DE AMIGO")
       
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('!ajuda'))

@bot.command()
async def precos(ctx):
    await ctx.send("O preço de item em maioria se baseia na seguinte tabela: \n \nComum: 100-150 PO \nIncomum: 250-500 PO \nRaro: 1000-2500 PO \nMuito Raro: 5000-10000 PO \nLendários: Vendo apenas informações \nMíticos: Não tenho \n \n ● Devido ao incidente em Magi, todos os itens tem 25% a mais em seu valor"
                   + "\n ● Os preços não são fechados nesse alcance ou fixos, eles podem variar na mesa e podem fugir dessa lista, pois são calculados com a UTILIDADE do item, e não por raridade, mas a lista pode dar uma boa ideia do que esperar de preço.")

@bot.command()
async def ajuda(ctx):
    embed=discord.Embed(title="Comandos do Gnomo", description="Temos os seguintes comandos do GNOMO BOT", color=0x6c25be)
    embed.add_field(name = "Geral", value ="⠀\n● !ajuda = Mostra os comandos do Gnomo\n" 
                    + "● !oqueévocê = Digo quem eu sou!\n"
                    + "● !sugestão = Manda uma sugestão para o Gnomo Bot!\n", inline = True) 
    embed.add_field(name = "Entretenimento", value ="⠀\n● !vigarista = Minha defesa pessoal contra acusações\n ● !morra = morro\n", inline = True)          
    embed.add_field(name = "Música (Atualmente não funciona)", value = "● !play = toco uma musica a sua escolha\n"          
                    + "● !stop = paro a musica caso esteja uma merda\n"
                    + "● !skip = pulo a musica caso ela seja ruim\n", inline = True)
    embed.add_field(name = "Rpg", value ="⠀\n● !base = Informa a base para novos jogadores\n"
                    + "● !precos = Informa a tabela que uso (as vezes) para os itens mágicos por raridades"
                    + "● !comprar [Personagem] [Item] = Adiciona um item a lista de compras de um personagem\n"
                    + "● !atributo = Rola atributos iniciais\n"
                    + "● !npcs = lista os npcs\n"
                    + "● !orgs = lista os organizações do mundo\n"
                    + "● !tesouro = mostra o tesouro do grupo", inline = False)  
    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
    embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
    await ctx.send(embed=embed)
    
@bot.command()
async def base(ctx):
    embed=discord.Embed(title="Base do mundo", description="É recomendado ler: \n \n ● *Os Jornais Semanais* \n \n     Informam o que esta acontecendo ATUALMENTE no mundo de Higalas, comentando sobre os diversos acontecimentos que ocorrem no mundo ao mesmo tempo que os jogadores"
                   + "\n\n ● *Os Contos de Higalas* \n  \n  Contam a origem do mundo e universo de forma mitólogica, e também explicam boa parte da lore que ocorreu até os dias atuais"
                   + "\n \n Todo conteúdo homebrew é liberado, porém deve ser jugado por mim previamente \n O procedimento padrão é começarmos nv 1 ou 3, dependendo da mesa, com atributos definidos em 4d6dl1, com um minímo de 70. \n Você pode usar o !atributo para que sejam rolados!", color=0x6c25be)
    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
    embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
    await ctx.send(embed=embed)
    
@bot.command()
async def gnomo(ctx):
    embed=discord.Embed(title="O Gnomo", description="Olá, eu sou o Gnomo, um ser baixinho e misterioso de varias formas\n\n"
                   + "Eu vendo praticamente de tudo, desde itens completamente malucos até informações extremamente duvidosas, mas sou um bom ser. Sou mais velho que o próprio tempo"
                   + " e sinceramente ja perdi a conta da idade. Minha loja cicla entre diversas cidades vendendo qualquer coisa para aventureiros bem intencionados (*não que seja um requisito*)"
                   + " e por um otimo preço!", color=0x6c25be)
    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
    embed.set_footer(text="Não pergunte de onde em vim")
    await ctx.send(embed=embed)    

@bot.command()
async def nix(ctx):
    await ctx.send("https://tenor.com/view/anya-spy-x-family-anime-spy-x-family-spy-x-family-anya-spy-family-anya-gif-25998501")
    
@bot.command()
async def goro(ctx):
    await ctx.send("https://tenor.com/view/muscular-anya-gif-26336145")
    
@bot.command()
async def sabriel(ctx):
    await ctx.send("https://tenor.com/view/anya-gif-26148058")
    
@bot.command()
async def vigarista(ctx):
    embed=discord.Embed(title="Minha Defesa Pessoal.", description="Eu gostaria de começar dizendo que eu entendo que as aparências podem ser enganosas e que as pessoas podem ter uma opinião prejudicada sobre mim devido a minha aparência ou história anterior. Eu sei que as minhas ações no passado podem ter sido questionáveis e que eu cometi erros, mas eu garanto a vocês que eu nunca tive a intenção de prejudicar alguém."
                    + "Eu sou uma pessoa honesta e trabalhadora que está apenas tentando ganhar a vida como todos nós. Eu trabalho duro todos os dias para garantir que eu possa prover para minha família e cuidar de minhas responsabilidades. Eu sei que as pessoas podem ter uma opinião negativa sobre minhas escolhas no passado, mas eu garanto a vocês que eu aprendi com meus erros e estou trabalhando duro para ser uma pessoa melhor."
                    + "Eu gostaria de lembrá-los que nenhum de nós é perfeito e que todos nós cometemos erros. Eu entendo que é fácil julgar alguém sem conhecer toda a história, mas eu pediria que vocês me dessem a oportunidade de provar minha inocência e mostrar que eu sou uma pessoa confiável e digna de confiança. Eu garanto a vocês que eu nunca vou voltar a cometer os mesmos erros novamente e que vou fazer o meu melhor para ganhar a confiança e o respeito de todos."
                    + "Eu entendo que pode ser difícil confiar em alguém que já decepcionou no passado, mas eu peço que vocês me deem a oportunidade de mostrar que eu mudei e que estou comprometido em ser uma pessoa melhor. Eu sei que posso ser julgado pelo meu passado, mas eu peço que vocês me julguem pelo meu presente e pelo meu futuro. Eu prometo trabalhar duro todos os dias para ganhar a confiança e o respeito de todos, e espero que vocês possam me dar essa oportunidade.", color=0x6c25be)
    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
    embed.set_footer(text="Juro que não sou vigarista :sob: :sob:")
    await ctx.send(embed=embed)

@bot.command()
async def comprar(ctx):
    """
    !comprar
    """
    novalista = str(ctx.message.content).replace("!comprar","",).split(" ")
    del novalista[0]

    if novalista[0].lower() == "nix":
        novalista.remove("nix")
        item =" ".join(novalista)
        file = open('C:\\Users\\Gustavo\\Documents\\Gnomo\\ComprasNix.txt','a')
        for i in novalista:
            file.write(i+" ")
        file.write("\n")
        file.close()
        embed=discord.Embed(title="Tesouro", description="Item " + item + " adicionado com sucesso a lista de compras de Nix", color=0x6c25be)
        embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
        embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
        await ctx.send(embed=embed)    
    elif novalista[0].lower() == "sabriel": 
        novalista.remove("sabriel")
        item =" ".join(novalista)
        file = open('C:\\Users\\Gustavo\\Documents\\Gnomo\\ComprasSabriel.txt','a')
        for i in novalista:
            file.write(i+" ")
        file.write("\n")
        file.close()
        embed=discord.Embed(title="Tesouro", description="Item " + item + " adicionado com sucesso a lista de compras de Sabriel" , color=0x6c25be)
        embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
        embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
        await ctx.send(embed=embed) 
    elif novalista[0].lower() == "goro":
        novalista.remove("goro")
        item =" ".join(novalista)
        file = open('C:\\Users\\Gustavo\\Documents\\Gnomo\\ComprasGoro.txt','a')
        for i in novalista:
            file.write(i+" ")
        file.write("\n")
        file.close()
        embed=discord.Embed(title="Tesouro", description="Item " + item + " adicionado com sucesso a lista de compras de Goro Blackspear" , color=0x6c25be)
        embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
        embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
        await ctx.send(embed=embed)
    elif novalista[0].lower() == "neron":
        novalista.remove("neron") 
        file = open('C:\\Users\\Gustavo\\Documents\\Gnomo\\ComprasNeron.txt','a')
        for i in novalista:
            file.write(i+" ") 
        file.write("\n")
        file.close()
        embed=discord.Embed(title="Tesouro", description="Item " + item + " adicionado com sucesso a lista de compras de Neron" , color=0x6c25be)
        embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
        embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
        await ctx.send(embed=embed)
        
    else :
         await ctx.send("Seu personagem não esta na base de dados, reclama com o mestre")

@bot.command()
async def tesouro(ctx):
    """
    !tesouro
    """
    listaT = str(ctx.message.content).replace("!tesouro","",).split(" ")
    del listaT[0]
    print(listaT)
    
    if len(listaT)>0:
        if listaT[0] == "adicionar":
            file = open('C:\\Users\\Gustavo\\Documents\\Gnomo\\TesouroPiratas.txt','a')
            listaT.remove("adicionar")
            for i in listaT:
                file.write(i+" ")
            file.write("\n")
            file.close()
            await ctx.send("Item " + " ".join(listaT) + " adicionado com sucesso ao tesouro da party!")
        elif listaT[0] == "add":
                file = open('C:\\Users\\Gustavo\\Documents\\Gnomo\\TesouroPiratastxt','a')
                listaT.remove("add")
                for i in listaT:
                    file.write(i+" ")
                    file.write("\n")
                    file.close()
                await ctx.send("Item " + " ".join(listaT) + " adicionado com sucesso ao tesouro da party!")      
        elif listaT[0] == "ver": 
            file = open('C:\\Users\\Gustavo\\Documents\\Gnomo\\TesouroPiratas.txt','r')
            lista = []
            for x in file:
                lista.append(x.replace("\n", "")) 
            bufferstring = ""
            for i in lista:
                bufferstring += ("● " + i + "\n")
            embed=discord.Embed(title="Tesouro", description=bufferstring, color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
            await ctx.send(embed=embed)    
        file.close()
    else: await ctx.send("Use '!tesouro ver' pra ver os itens atuais no tesouro, e 'tesouro adicionar [item]' para adicioanr coisas a tesouro")
  
@bot.command()
async def oqueévocê(ctx):
    await ctx.send("Eu sou um ser além do tempo e realidade. Alguem extremamente forte que não liga muito pras coisas, ja vi o universo sumir e ser recriado tantas vezes que perdi a conta"
                   + " e sinceramente ja perdi a conta dos meu anos. Em geral, apenas um vendedor que vende quase qualquer coisa por dinheiro e ja que vivi tantas vidas e tanto tempo, "
                   + "tenho dos mais simples aos mais incriveis itens que o simples cerebro humanoide pode compreender.")

"""
@bot.command()
async def embed(ctx):
    embed=discord.Embed(title="Teste", url="https://youtu.be/erCxCAh8Wcw", description="Teste porra", color=0x6c25be)
    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
    embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
    await ctx.send(embed=embed)
"""
@bot.command()
async def sugestão(ctx):
    """
    !sugestão
    """
    novalista = str(ctx.message.content).replace("!sugestão","")
    await ctx.send("Sugestão adicionada com sucesso!")
    nome = ctx.author.name
    file = open('C:\\Users\\Gustavo\\Documents\\Gnomo\\Sugestões.txt','a')
    file.write(f"\nIdeia do usuario {nome}:"+novalista)
    file.close()
    
@bot.command()
async def atributo(ctx): 
    resultados = []
    for i in range(0, 6):
        status = []
        status.append(randint(1,6))
        status.append(randint(1,6))
        status.append(randint(1,6))
        status.append(randint(1,6))
        status.sort(reverse=True)
        resultados.append(status[0] + status[1] + status[2])
    resultados.sort(reverse = True)
    total = sum(resultados)
    embed=discord.Embed(title="Atributos gerados", description=f"Seus status serão:\nAtributo 1: **{resultados[0]}**\nAtributo 2: **{resultados[1]}**\nAtributo 3: **{resultados[2]}**\nAtributo 4: **{resultados[3]}**\nAtributo 5: **{resultados[4]}**\nAtributo 6: **{resultados[5]}**\nSeus atributos somaram: **{total}**", color=0x6c25be)
    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
    embed.set_footer(text="Pedido por: {}".format(ctx.author.display_name))
    await ctx.send(embed=embed)
    if (total >= 71 and total <= 80):
        await ctx.send("Ta na média, dale")
    elif (total <= 70):
        await ctx.send("Se fudeu gostoso, rola denovo")
    elif (total >= 81 and total <= 90):
        await ctx.send("CARALHO MLK TA FORTE")
    elif (total >= 91):
        await ctx.send("O QUE É VOCÊ??????????")
    
@bot.command()
async def npcs(ctx):
    """
    !npcs   
    """
    novalista = str(ctx.message.content).replace("!npcs","",).split(" ")
    del novalista[0]
    if len(novalista)>0:
        if novalista[0].lower() == "azeron":
            embed=discord.Embed(title="Azeron de Camila", description="Azeron é um poderoso morto vivo, rei do Castelo de Luisiana, que entrou em ruinas em 27 mil A.G.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/300423545/i6CxQxpvnCGYyw0heaeIzw/max.jpg?1660946704")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "faust":
            embed=discord.Embed(title="Faust", description="Velho alquimista que se involveu com as forças naturais de tal forma que foi amaldiçoado. Portador do homunculo Washington, um robo alcoolotra que o segue em sua jornada.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/257011054/llxlNw58QjjGjbMv1bE4MA/med.png?1637637959")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "goro":
            embed=discord.Embed(title="Goro Blackspear", description="goro, o melhor, mago, aventureiro, cozineiro, explorador, inteligente, forte, dominador de caos, duelista, assasino de demonios, mata palhaço maluco, stompador de khadas, terrorista, blackspear", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1029501658532683799/1087814427597885601/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "gabriel":
            embed=discord.Embed(title="Gabriel D. Saint", description="Um dos maiores piratas de todos os tempos, nascido no ano 0 e servindo como contagem de tempo, havendo A.G (Antes de Gabriel) e D.G (Depois de Gabriel)", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://static.vecteezy.com/ti/vetor-gratis/p3/7126739-icone-de-ponto-de-interrogacao-gratis-vetor.jpg")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "joana":
            embed=discord.Embed(title="Joana", description="Uma tripulante de Sarah, muito bem humorada e curiosa, vive de maneira modesta e sempre ajudado todos no barco.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/252805546/Boxrd2x8Gk961kozsfiS_w/max.jpg?1635483337")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "jouni":
            embed=discord.Embed(title="Jouni", description="Tripulante de Sarah, sempre curioso e buscando manter ordem no navio, não trabalha muito e apronta bastante, mas é muito sabio. Recentemente perdeu sua perna em um acidente, mas vive com uma de metal no lugar. Portador da Marca da Pluma", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/252805636/q-6HfXlIoHmNHU6cP1rDYw/max.jpg?1635483402")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "kapen":
            embed=discord.Embed(title="Kapen", description="Kapen, um ex-aventureiro renomado, que ja lutou com centenas de criaturas e inimigos poderosos, até onde se sabe, ele não deixou discipulos de sua tecnica. Ele ainda é caçado por varios mercenarios, mas vive uma vida tranquila na fazenda. Seus maiores feitos foram, derrotar um dragão, derrubar o imperador Donkai e conseguir lutar de igual para igual com Khada Golp"
                   + " Morreu recentemente na Guerra de Vilentus, morto por um golpe inesperado de Khada Golp em combate", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/251747392/As3N-6BXkArgC7SE6zvRWw/max.jpg?1634949361")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "karma":
            embed=discord.Embed(title="Karma", description="Encontrado na base secreta de Kapen, pouco se sabe sobre ele além de que foi o unico sobrevivente", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1029501658532683799/1051587999055491114/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "kayen":
            embed=discord.Embed(title="Kayen", description="Espadachim muito habilidoso que vive no Dragão Despedaçado. \n \n Link para seu dossiê:https://drive.google.com/drive/folders/1Da31GdqRgBCG4A7jW-DerBRIUmehVNPM", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/284944756/MI-qgoOoDhvpys7cqg1VUw/max.jpg?1652476794")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "khada":
            if len(novalista)>1:
                if novalista[1].lower() == "golp":
                    embed=discord.Embed(title="Khada Golp", description="Um assassino renomado. É um assassino classe S, capaz de se infiltrar sem dificuldade nos maiores castelos do mundo. Recentemente escapou de sua prisão. Traços dizem que ele foi ajudado. Ele foi visto recentemente na destruição da cidade de Magi, na Guerra de Vilentus assassinando Kapen, e em outros locais.", color=0x6c25be)
                    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
                    embed.set_footer(text="Habita em: Higalas Atual")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1070866345035567114/image.png")
                    await ctx.send(embed=embed)
                elif novalista[1].lower() == "nord":
                    embed=discord.Embed(title="Khada Nord", description="Não se sabe quase nada sobre Khada Nord.", color=0x6c25be)
                    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
                    embed.set_footer(text="Habita em: Higalas Atual")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1070866345782153338/image.png")
                    await ctx.send(embed=embed)
                elif novalista[1].lower() == "jack":
                    embed=discord.Embed(title="Khada Jack", description="Não se sabe quase nada sobre Khada Jack.", color=0x6c25be)
                    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
                    embed.set_footer(text="Habita em: Higalas Atual")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1070866345304006827/image.png")
                    await ctx.send(embed=embed)
                elif novalista[1].lower() == "niva":
                    embed=discord.Embed(title="Khada Niva", description="Não se sabe quase nada sobre Khada Niva.", color=0x6c25be)
                    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
                    embed.set_footer(text="Habita em: Higalas Atual")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1070866345543090276/image.png")
                    await ctx.send(embed=embed)
            else:
                embed=discord.Embed(title="Khadas", description="Os 4 Khadas são os maiores terroristas do mundo, extremamente controversos e misteriosos", color=0x6c25be)
                embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
                embed.set_footer(text="Arte feita por @JackLayson")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1065332906773458975/1065333387662999602/os_khadas.jpg")
                await ctx.send(embed=embed)
        elif novalista[0].lower() == "koupen":
            embed=discord.Embed(title="Koupen", description="Koupen, o blibliotecario da Grande Biblioteca de Nendasta, muito conhecido por ter seus olhos em toda a biblioteca, sua habilidade de achar livros e perceber furtos são inigualaveis.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/251744244/lIrFblI_2UpyJzh3bJr98w/max.jpg?1634948220")
            await ctx.send(embed=embed)    
        elif novalista[0].lower() == "normand":
            embed=discord.Embed(title="Normand", description="Normand era um aventureiro lendário lider dos Guerreiros do Desconhecido. Ele desapareu a pouco menos de 20 anos durante uma missão.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            await ctx.send(embed=embed) 
        elif novalista[0].lower() == "oazen":
            embed=discord.Embed(title="Oazen", description="Um dos maiores genios de Lorian, e o Warforged mais avançado do mundo. Admirado por muitos por criar as armas mais potentes do mundo.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/263112622/kK3a0jTdwhyX0h4bXoH0ww/max.jpg?1641329760")
            await ctx.send(embed=embed) 
        elif novalista[0].lower() == "sarah":
            embed=discord.Embed(title="Sarah", description="Capitã dos Piratas de Sarah, bem conhecida internacionalmente, mesmo oficialmente não tendo nenhuma recompensa sobre sua cabeça. Não se sabe muito sobre o passado dela, mas se sabe que ela é uma pistoleira incrivel", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1029501658532683799/1037168008516345927/unknown.png")
            await ctx.send(embed=embed) 
        elif novalista[0].lower() == "yaru":
            embed=discord.Embed(title="Yaru", description="Irmão de Goro Blackspear, muito mais talentoso e poderoso, porém introvertido e anti-social", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/258673355/azF-Y-2uq7rk0j6jgfNaHw/med.jpg?1638645084")
            await ctx.send(embed=embed) 
        elif novalista[0].lower() == "esparda":
            embed=discord.Embed(title="Jack Esparda", description="Um dos 6 generais do Governo Mundial. De longe o mais honrado e experiente dos 6, conhecido pelo seu estilo de 2 Lâminas aperfeiçoado com o tempo", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091452220903538729/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "nick":
            embed=discord.Embed(title="Nick Punhos de Aço", description="Um dos 6 generais do Governo Mundial. O mais velho de todos, e o que toma a posição de lider quando as coisas apertam. Sempre é lembrado por sua força estrondosa capaz de derrubar predios com simples socos", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091452221436219574/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "karna":
            embed=discord.Embed(title="Karna Stradavarius", description="Um dos 6 generais do Governo Mundial. O mais estrategista dos 6, e raramente aparece pessoalmente para lutas, porém, nas poucas que apareceu dizem ter destrúido kilometros de terra por onde passava", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091452221696249886/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "baki":
            embed=discord.Embed(title="Baki Pugnala", description="Um dos 6 generais do Governo Mundial. Conhecido como o mais sanguinário dos 6, sempre dilacerando pessoas com suas lâminas por onde passa e conhecido pelo seu estilo de luta extremamente selvagem, sem deixar o oponente nem sequer atacar", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091452222010839171/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "mike":
            embed=discord.Embed(title="Mike Bardete", description="Um dos 6 generais do Governo Mundial. Provavelmente o mais impulsivo, gosta de se divertir durante lutar e fazer um verdadeiro show enquanto executa seus oponentes.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091452222363156640/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "zeke":
            embed=discord.Embed(title="Zeke", description="Um dos 6 generais do Governo Mundial. Um dos mais misteriosos, vindo diretamente do norte do mundo. Chama-se atenção a falta de sobrenome ou titulo, ele é apenas conhecido como Zeke. É o responsavel pela Marinha.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091452222723854536/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "hizaki":
            embed=discord.Embed(title="Hizaki", description="Um dos 3 Almirantes da Marinha do Governo Mundial. Reconhecivel pelo sua postura calma e debochada na maior parte do tempo", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091453865087488070/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "kazaski":
            embed=discord.Embed(title="Kazaski", description="Um dos 3 Almirantes da Marinha do Governo Mundial. Muito característico por seu senso de justiça quase imutavel, aonde acredita que não existe perdão para aqueles que se rebelaram contra a lei além de uma postura sempre acima dos outros.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091453865381077154/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "aka":
            embed=discord.Embed(title="Aka Menske", description="Um dos 3 Almirantes da Marinha do Governo Mundial. Reconhecido facilmente pelo seu método de luta, que envolve misturar sua marca com seus sopros", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Atual")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/838535464439906314/1091453866152825064/image.png")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "leandro":
            embed=discord.Embed(title="Leandro", description="Um péssimo mentiroso conhecido muito bem por sua ótima lábia.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Bélica")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/329520692/hR7nj5GeqoWbpfv34yQJuA/med.jpg?1677214566")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "allstrom":
            embed=discord.Embed(title="Allstrom", description="Sudda Allstrom é conhecido como lider da familia Allstrom, familia conhecida por gerenciar guildas e fiscalizar mercadorias. Um bom reino se constrói sob um olhar vigilante.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Bélica")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/334755439/oLUSp8terYbZrtwDpeFSww/med.png?1680022477")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "arcthur":
            embed=discord.Embed(title="Arcthur", description="N/A", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Bélica")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/334712146/rA7-oLniTl_L_PGHDJ2aaA/med.png?1679982201")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "north":
            embed=discord.Embed(title="North", description="Herdeira da mascara do guardião da espada - protetora da corte camersim e lider da casa Grumdelll. ", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Bélica")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/329523405/XaXiiriYd_NE2as8daYerQ/med.jpg?1677216239")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "kael":
            embed=discord.Embed(title="Kael", description="Rei da corte camersim. Um homem alto que, mesmo pelo pesar da idade, ainda parece capaz de mover montanhas.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Habita em: Higalas Bélica")
            embed.set_thumbnail(url="https://s3.amazonaws.com/files.d20.io/images/331497279/PRYO2ho2jE1S6SGZrN-mjA/med.png?1678230649")
            await ctx.send(embed=embed)
    else:
        embed=discord.Embed(title="Npcs", description="Aqui esta a lista de Npcs apresentados até agora, você pode dar ![nome do npc] para obter mais informações sobre o mesmo (use letras maiúsculas)\n \n", color=0x6c25be)
        embed.add_field(name="➤ **Higalas**", value="⠀\n **Higalas** \n\n ● Azeron de Camila - use apenas Azeron \n"
                    + "● Faust \n"
                    + "● Gabriel D. Saint - use apenas Gabriel \n"
                    + "● Oazen \n"
                    + "● Koupen \n"
                    + "● Karma \n\n"
                    + "**Heróis**\n\n"
                    + "● Goro \n"
                    + "● Normand \n"
                    + "● Kapen \n"
                    + "● Kayen \n"
                    + "● Yaru Blackspear \n\n"
                    + "**Khadas**\n\n"
                    + "● Khada Golp \n"
                    + "● Khada Nord \n"
                    + "● Khada Jack \n"
                    + "● Khada Niva \n\n"
                    + "**Piratas**\n\n"
                    + "● Joana \n"
                    + "● Jouni \n"
                    + "● Sarah \n\n"
                    + "**Governo Mundial\n\n**"
                    + "● Jack Esparda - Use apenas Esparda\n"
                    + "● Nick Punhos de Aço - Use apenas Nick\n"
                    + "● Karna Stradavarius - Use apenas Karna\n"
                    + "● Baki Pugnala - Use apenas Baki\n"
                    + "● Mike Bardete - Use apenas Mike\n"
                    + "● Zeke - Use apenas Zeke\n\n"
                    + "**Marinha\n\n**"
                    + "● Hizaki\n"
                    + "● Kazaski\n"
                    + "● Aka Mesnke - Use apenas Aka\n"
                    , inline = True)
        embed.add_field(name="➤ **Cataclisma**", value="⠀\n ● Ozymandias\n", inline = False)
        embed.add_field(name="➤ **Higalas Bélica - 27.000 A.G**", value="⠀\n ● Allstrom\n"
                    + "● Arcthur\n"
                    + "● Kael\n"
                    + "● Leandro\n"
                    + "● North\n", inline = True)

        embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
        embed.set_footer(text="Para saber mais sobre um deles, use !npcs [npc]")
        await ctx.send(embed=embed)

@bot.command()
async def orgs(ctx):
    """
    !orgs   
    """
    novalista = str(ctx.message.content).replace("!orgs","",).split(" ")
    del novalista[0]
    if len(novalista)>0:
        if novalista[0].lower() == "governo":
            embed=discord.Embed(title="Governo Mundial", description="Uma organização que compõe representantes de todo o mundo, buscando manter a paz mundial. Composta por 6 Generais que lideram o governo em diversas sub-areas.", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Opera em: Higalas Bélica")
            embed.set_thumbnail(url="")
            await ctx.send(embed=embed)
        elif novalista[0].lower() == "marinha":
            embed=discord.Embed(title="Marinha", description="A marinha é uma força naval que controla a pirataria ao redor do mundo.\n\n"
                + "Existem 3 **Almirantes**:\n\n"
                + "● Hizaki\n"
                + "● Kazaski\n"
                + "● Aka Mesnke\n\n", color=0x6c25be)
            embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
            embed.set_footer(text="Opera em: Higalas Bélica")
            embed.set_thumbnail(url="")
            await ctx.send(embed=embed)
    else:
        embed=discord.Embed(title="Organizações", description="Aqui esta a lista de Organizações apresentados até agora\n \n"
                    + "**Higalas\n\n**"
                    + "● Governo Mundial - use apenas Governo\n"
                    + "⠀⠀● Marinha\n"
                    
                    , color=0x6c25be)
        embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
        embed.set_footer(text="Para saber mais sobre um deles, use !organizações [organização]")
        await ctx.send(embed=embed)
    
@bot.command()
async def inv(ctx):
    """
    !inv   
    """
    novalista = str(ctx.message.content).replace("!inv","",).split(" ")
    if len(novalista) == 1:
        with open("data.txt", "r") as f:
            data = f.read()
            coisas = data.split("\n")
        del coisas[-1]
        mensagem = ""
        for item in coisas:
            mensagem += f"● {item}\n"
        embed=discord.Embed(title="Inventário do Navio", description=("Aqui estão os itens que atualmente estão dentro do navio:\n\n" + mensagem + "\n \n __**Use add ou sub para adicionar ou subtrair materiais do navio, respectivamente**__"), color=0x6c25be)
        embed.set_author(name="Navio", icon_url="https://i.imgur.com/xR3qHfp.png")
        embed.set_footer(text="carai mó pobre")
        embed.set_thumbnail(url="https://img6.arthub.ai/63e1834e-ba8d.webp")
        await ctx.send(embed=embed)
    else:
        del novalista[0] 
        with open("C:\\Users\\Gustavo\\Documents\\Gnomo\\data.txt", "r") as f:
                data = f.read()
                coisas = data.split("\n")
                del coisas[-1]
                dados = []
                for coisa in coisas:
                    coisa = coisa.split(" ")
                    del coisa[1]
                    dados.append(coisa)
                material = novalista[1]
                operacao = novalista[0]
                quantidade = int(novalista[2])
                resultado = -1
                for i in range(len(coisas)):
                    if dados[i][0] == material:
                        resultado = i
                if operacao.lower() == "add":
                    if resultado == -1:
                        novoMaterial = [material, str(quantidade)]
                        dados.append(novoMaterial)
                    else:
                        dados[resultado][1] = str(int(dados[resultado][1]) + quantidade)
                        embed=discord.Embed(title="Inventário do Navio", description= ("*" + str(quantidade) + " " + dados[resultado][0] + "*" + "s foram adicionados/as a Carga do Navio, totalizando " + "*" + dados[resultado][1] + " " + dados[resultado][0] + "*"), color=0x6c25be)
                        embed.set_author(name="", icon_url="https://i.imgur.com/xR3qHfp.png")
                        embed.set_footer(text="Carga do Barco")
                        embed.set_thumbnail(url="https://img6.arthub.ai/63e1834e-ba8d.webp")
                        await ctx.send(embed=embed)

                elif operacao.lower() == "sub":
                    if resultado == -1:
                        embed=discord.Embed(title="Inventário do Navio", description="Este recurso não existe no banco de dados", color=0x6c25be)
                        embed.set_author(name="", icon_url="https://i.imgur.com/xR3qHfp.png")
                        embed.set_footer(text="otario porco")
                        embed.set_thumbnail(url="https://img6.arthub.ai/63e1834e-ba8d.webp")
                        await ctx.send(embed=embed)
                    else:
                        
                        if int(dados[resultado][1]) < 0:
                            embed=discord.Embed(title="Inventário do Navio", description="COMO CARALHOS TU QUER DEVER MATERIAL???????", color=0x6c25be)
                            embed.set_author(name="", icon_url="https://i.imgur.com/xR3qHfp.png")
                            embed.set_footer(text="otario porco")
                            embed.set_thumbnail(url="https://img6.arthub.ai/63e1834e-ba8d.webp")
                            await ctx.send(embed=embed)
                        else:
                            dados[resultado][1] = str(int(dados[resultado][1]) - quantidade)
                            embed=discord.Embed(title="Inventário do Navio", description= ("*" + str(quantidade) + " " + dados[resultado][0] + "*" + "s foram retirados/as a Carga do Navio, totalizando " + "*" + dados[resultado][1] + " " + dados[resultado][0] + "*"), color=0x6c25be)
                            embed.set_author(name="", icon_url="https://i.imgur.com/xR3qHfp.png")
                            embed.set_footer(text="Carga do Barco")
                            embed.set_thumbnail(url="https://img6.arthub.ai/63e1834e-ba8d.webp")
                            await ctx.send(embed=embed)
                else:
                    embed=discord.Embed(title="Inventário do Navio", description="Use add ou sub para adicionar ou subtrair materiais do navio, respectivamente", color=0x6c25be)
                    embed.set_author(name="", icon_url="https://i.imgur.com/xR3qHfp.png")
                    embed.set_footer(text="otario porco")
                    embed.set_thumbnail(url="https://img6.arthub.ai/63e1834e-ba8d.webp")
                    await ctx.send(embed=embed)
                with open("data.txt", "w") as f:
                    for item in dados:
                        if int(item[1]) > 0:
                            f.write(item[0] + " = ")
                            f.write(item[1] + "\n")
                        
@bot.command()
async def lore(ctx):
    """
    !lore   
    """
    embed=discord.Embed(title = "Link para a lore", description="https://1drv.ms/w/s!AocpWuY1u4QWg9AlNZIq2YTeenzZQA?e=uJLMYg")
    embed.set_author(name="O Gnomo", icon_url="https://i.imgur.com/xR3qHfp.png")
    embed.set_footer(text="Aqui está :>")
    await ctx.send(embed=embed)

@bot.command()
async def jack(ctx):
    await ctx.send("Ta apaixonado cara???")
 
bot.run("TOKEN")