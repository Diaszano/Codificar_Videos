#-----------------------
# BIBLIOTECAS
#-----------------------
import os
import csv
from pickle import TRUE
import CRUD as bd
from dados import Banco as dzn
#-----------------------
# CONSTANTES
#-----------------------
TAMANHO_MINIMO=104857600;
CODIFICADOR='H264'; # OPÇÕES ['HEVC','H265','H264'];
PASTAS_DE_FILMES=['/nfs/Streaming-HDD0/Filmes','/nfs/Streaming-HDD1/Filmes-HDD1','/nfs/Streaming-SSD/Filmes'];
PASTAS_DE_SERIES=['/nfs/Streaming-HDD1/Séries','/nfs/Streaming-HDD2/Séries','/nfs/Streaming-SSD/Séries'];
ARQUIVO='logCodificacao.csv';
ARQUIVO_RESERVA='logReserva.csv'
#-----------------------
# FUNÇÕES
#-----------------------
def buscaFilmes(pasta:str = '') -> list:
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

def limparPastasTmp(cursor,cnxn):
    for i in range(1):
        comando = f"SELECT pasta, arquivo,imdb FROM filmes WHERE  codificado = {i} and tamanho != 0 ORDER BY tamanho LIMIT 1;";
        retorno = bd.read(comando=comando,cursor=cursor);
        while retorno != []:
            retorno                 = retorno[0];
            [pasta,arquivo,imdb]    = [retorno[0],retorno[1],retorno[2]];
            tmpPasta                = f'{pasta}tmp/';
            if(os.path.exists(f'{tmpPasta}')):
                os.system(f'rm -r "{tmpPasta}"');
                print(f"Pasta {tmpPasta} excluída");
            comando = f'UPDATE filmes.filmes SET codificado={i+3} WHERE imdb="{imdb}";';
            bd.update(comando=comando,cnxn=cnxn,cursor=cursor);
            comando = f"SELECT pasta, arquivo,imdb FROM filmes WHERE  codificado = {i} and tamanho != 0 ORDER BY tamanho LIMIT 1;";
            retorno = bd.read(comando=comando,cursor=cursor);
    for i in range(1):
        comando = f'UPDATE filmes.filmes SET codificado={i} WHERE codificado={i+3};';
        bd.update(comando=comando,cnxn=cnxn,cursor=cursor);

def atualizarBanco(cursor,cnxn):
    for pasta in PASTAS_DE_FILMES:
        [arqMkv,arqMp4,arqAvi] = buscaFilmes(pasta);
        for tipo in [arqMkv,arqMp4,arqAvi]:
            for arq in tipo:
                [pasta_filme,nome,arquivo,imdb,tmpPasta,tmpArq,localDoArquivo] = correcaoFilmes(arq);
                comando = f"SELECT ta filmes WHERE  codificado = 0 and tamanho != 0 ORDER BY tamanho LIMIT 1;";
                retorno = bd.read(comando=comando,cursor=cursor);
                if retorno != []:
                    retorno = int(retorno[0]);
                    if retorno == 0:
                        comando = f'''  UPDATE filmes.filmes SET tamanho="{os.path.getsize(localDoArquivo)}", 
                                        pasta="{pasta_filme}", arquivo="{arquivo}" WHERE imdb="{imdb}";''';
                        bd.update(comando=comando,cnxn=cnxn,cursor=cursor);
                else:
                    comando = f'''  INSERT INTO filmes.filmes (nome, imdb, tamanho, codificado, pasta, arquivo)
                                    VALUES("{nome}","{imdb}",{os.path.getsize(localDoArquivo)}, 0,"{pasta_filme}","{arquivo}");''';
                    bd.create(comando=comando,cnxn=cnxn,cursor=cursor);


def codificacaoDeFilmes_Locais() -> None:
    with open(ARQUIVO,'w',newline='') as file:
        escrever = csv.writer(file);
        escrever.writerow(['Nome','Arquivo','imdb','Pasta','Tamanho']);
        for pasta in PASTAS_DE_FILMES:
            [arqMkv,arqMp4,arqAvi] = buscaFilmes(pasta);
            for tipo in [arqMkv,arqMp4,arqAvi]:
                for arq in tipo:
                    [pasta_filme,nome,arquivo,imdb,tmpPasta,tmpArq,localDoArquivo] = correcaoFilmes(arq);
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
                                linhaDeComando = f'''   ffmpeg -hwaccel cuda -hwaccel_output_format cuda  
                                                        -i "{localDoArquivo}" -c:v h264_nvenc -crf 20 -c:a 
                                                        copy "{tmpArq}"''';
                            os.system("clear");
                            print(linhaDeComando);
                            os.system(linhaDeComando);
                        if(os.path.isfile(tmpArq)):
                            if(os.path.getsize(tmpArq) <= os.path.getsize(localDoArquivo) and (os.path.getsize(tmpArq) > TAMANHO_MINIMO)):
                                os.system(f'mv "{tmpArq}" "{pasta_filme}"');
                        if(os.path.exists(f'{tmpPasta}')):
                            os.system(f'rm -r "{tmpPasta}"');
                    escrever.writerow(['Nome','Arquivo','imdb','Pasta','Tamanho']);
                    linha = [nome,arquivo,imdb,pasta_filme,str(os.path.getsize(localDoArquivo))];
                    escrever.writerow(linha);

def codificacaoDeFilmes_Banco(cursor,cnxn,maior:bool = True) -> None:
    if maior:
        ordem = 'DESC';
    else:
        ordem = '';
    comando = f"SELECT pasta, arquivo,imdb FROM filmes WHERE  codificado = 0 and tamanho != 0 ORDER BY tamanho {ordem} LIMIT 1;";
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
                    linhaDeComando = f'''ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i "{localDoArquivo}" -c:v h264_nvenc -crf 20 -c:a copy "{tmpArq}"''';
                os.system("clear");
                print(linhaDeComando);
                os.system(linhaDeComando);
            if(os.path.isfile(tmpArq)):
                if(os.path.getsize(tmpArq) <= os.path.getsize(localDoArquivo) and (os.path.getsize(tmpArq) > TAMANHO_MINIMO)):
                    os.system(f'mv "{tmpArq}" "{pasta}"');
            if(os.path.exists(f'{tmpPasta}')):
                os.system(f'rm -r "{tmpPasta}"');
            comando = f'UPDATE filmes.filmes SET tamanho="{os.path.getsize(localDoArquivo)}", codificado=1 WHERE imdb="{imdb}";';
            bd.update(comando=comando,cnxn=cnxn,cursor=cursor);
        comando = f"SELECT pasta, arquivo,imdb FROM filmes WHERE  codificado = 0 and tamanho != 0 ORDER BY tamanho {ordem} LIMIT 1;";
        retorno = bd.read(comando=comando,cursor=cursor);
#-----------------------
# Main()
#-----------------------    
if __name__ == '__main__':
    [cnxn,cursor] = bd.conexao(host=dzn.host,user=dzn.user,password=dzn.password,database=dzn.databaseFilmes);
    codificacaoDeFilmes_Banco(cnxn=cnxn,cursor=cursor);
    bd.desconexao(cnxn=cnxn,cursor=cursor);
#-----------------------