#-----------------------
# BIBLIOTECAS
#-----------------------
import os
import csv
import CRUD as bd
from dados import Banco as dzn
#-----------------------
# CONSTANTES
#-----------------------
TAMANHO_MINIMO=200;
CODIFICADOR='HEVC'; # OPÇÕES ['HEVC','H265','H264']; Eu escolhi o hevc, pois ele faz o processo todo na minha placa de video.
PASTAS_DE_FILMES=['/nfs/Streaming-HDD0/Filmes','/nfs/Streaming-HDD1/Filmes-HDD1','/nfs/Streaming-SSD/Filmes'];
PASTAS_DE_SERIES=['/nfs/Streaming-HDD1/Séries','/nfs/Streaming-HDD2/Séries','/nfs/Streaming-SSD/Séries'];
ARQUIVO='logCodificacao.csv';
ARQUIVO_RESERVA='logReserva.csv'
#-----------------------
# FUNÇÕES
#-----------------------
def buscaFilmes(pasta) -> list:
    arqMkv = [];
    arqMp4 = [];
    arqAvi = [];
    i = 0;
    for diretorio, subpastas, arquivos in os.walk(pasta):
        if i >= 1:
            for dir, sub, arq in os.walk(diretorio):
                for a in arq:
                    if '.mkv' in a:
                        arqMkv.append(dir+'/'+a);
                    elif '.mp4' in a:
                        arqMp4.append(dir+'/'+a);
                    elif '.avi' in a:
                        arqAvi.append(dir+'/'+a);
        i+=1;
    return [arqMkv,arqMp4,arqAvi];

def correcaoFilmes(filme:str = '') -> list:
    pasta   = filme[:filme.index(')/')+2];
    nome    = filme[filme.index(')/')+2:len(filme)-4];
    arquivo = filme[filme.index(')/')+2:];
    imdb    = filme[filme.index('(tt')+1:filme.index(')/')];
    tmp     = f'{pasta}tmp/';
    tmpArq  = f'{tmp}{nome}';
    return[pasta,nome,arquivo,imdb,tmp,tmpArq,filme];

def codificacaoDeFilmes_Locais() -> None:
    with open(ARQUIVO,'w',newline='') as file:
        escrever = csv.writer(file);
        escrever.writerow(['Nome','Arquivo','imdb','Pasta','Tamanho']);
        for pasta in PASTAS_DE_FILMES:
            [arqMkv,arqMp4,arqAvi] = buscaFilmes(pasta);
            for tipo in [arqMkv,arqMp4,arqAvi]:
                for arq in tipo:
                    [pasta_filme,nome,arquivo,imdb,tmpPasta,tmpArq,localDoArquivo] = correcaoFilmes(arq);
                    if(os.path.getsize(f'{localDoArquivo}') >= TAMANHO_MINIMO):
                        os.system(f'mkdir {tmpPasta}');
                        if(CODIFICADOR == 'HEVC'):
                            linhaDeComando = f'ffmpeg -i "{localDoArquivo}" -c:v hevc_nvenc -c:a copy "{tmpArq}"';
                        elif(CODIFICADOR == 'H265'):
                            linhaDeComando = f'ffmpeg -i "{localDoArquivo}" -c:v libx265 -c:a copy "{tmpArq}"';
                        else:
                            linhaDeComando = f'ffmpeg -i "{localDoArquivo}" -vcodec h264 -acodec mp3 "{tmpArq}"';
                        print(linhaDeComando);
                        os.system(linhaDeComando);
                    if(os.path.isfile(tmpArq)):
                        if((os.path.getsize(tmpArq) <= os.path.getsize(localDoArquivo)) and (os.path.getsize(tmpArq) > TAMANHO_MINIMO)):
                            os.system(f'mv {tmpArq} "{pasta_filme}"');
                    if(os.path.exists(f'"{tmpPasta}"')):
                        os.system(f'rm -r "{tmpPasta}"');
                    escrever.writerow(['Nome','Arquivo','imdb','Pasta','Tamanho']);
                    linha = [nome,arquivo,imdb,pasta_filme,str(os.path.getsize(localDoArquivo))];
                    escrever.writerow(linha);

def codificacaoDeFilmes_Banco(cursor,cnxn) -> None:
    comando = f"SELECT pasta, arquivo,imdb FROM filmes WHERE  codificado = 0 and tamanho != 0 ORDER BY pasta LIMIT 1;";
    retorno = bd.read(comando=comando,cursor=cursor);
    while retorno != []:
        retorno                 = retorno[0];
        [pasta,arquivo,imdb]    = [retorno[0],retorno[1],retorno[2]];
        tmpPasta                = f'{pasta}tmp/';
        localDoArquivo          = f'{pasta}{arquivo}';
        tmpArq                  = f'{tmpPasta}{arquivo}';
        print(pasta,arquivo,imdb)
        print(f'tmp pasta = {pasta}tmp/')
        print(f'local do arquivo = "{pasta}{arquivo}"')
        print(f'tmp arquivo = "{tmpPasta}{arquivo}"')

        if(os.path.isfile(localDoArquivo)):
            comando = f'UPDATE filmes SET codificado=2 WHERE imdb="{imdb}";';
            bd.update(comando=comando,cnxn=cnxn,cursor=cursor);
            linhaDeComando = '';
            if(os.path.getsize(f'{localDoArquivo}') >= TAMANHO_MINIMO):
                os.system(f'mkdir "{tmpPasta}"');
                if(CODIFICADOR == 'HEVC'):
                    linhaDeComando = f'ffmpeg -i "{localDoArquivo}" -c:v hevc_nvenc -c:a copy "{tmpArq}"';
                elif(CODIFICADOR == 'H265'):
                    linhaDeComando = f'ffmpeg -i "{localDoArquivo}" -c:v libx265 -c:a copy "{tmpArq}"';
                else:
                    linhaDeComando = f'ffmpeg -i "{localDoArquivo}" -vcodec h264 -acodec mp3 "{tmpArq}"';
                os.system("clear");
                print(linhaDeComando);
                os.system(linhaDeComando);
            if(os.path.isfile(tmpArq)):
                if((os.path.getsize(tmpArq) <= os.path.getsize(localDoArquivo)) and (os.path.getsize(tmpArq) > TAMANHO_MINIMO)):
                    os.system(f'mv {tmpArq} "{pasta}"');
            if(os.path.exists(f'"{tmpPasta}"')):
                os.system(f'rm -r "{tmpPasta}"');
            comando = f'UPDATE filmes.filmes SET tamanho="{os.path.getsize(localDoArquivo)}", codificado=1 WHERE imdb="{imdb}";';
            bd.update(comando=comando,cnxn=cnxn,cursor=cursor);
        comando = f"SELECT pasta, arquivo,imdb FROM filmes WHERE  codificado = 0 and tamanho != 0 ORDER BY pasta LIMIT 1;";
        retorno = bd.read(comando=comando,cursor=cursor);
#-----------------------
# Main()
#-----------------------    
if __name__ == '__main__':
    [cnxn,cursor] = bd.conexao(host=dzn.host,user=dzn.user,password=dzn.password,database=dzn.databaseFilmes);
    codificacaoDeFilmes_Banco(cursor,cnxn);
    bd.desconexao(cnxn=cnxn,cursor=cursor);
#-----------------------