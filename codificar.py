#-----------------------
# BIBLIOTECAS
#-----------------------
import os
import csv
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

def codificacaoDeFilmes() -> None:
    with open(ARQUIVO,'w',newline='') as file:
        escrever = csv.writer(file);
        escrever.writerow(['Filme','Pasta','Tamanho']);
        for pasta in PASTAS_DE_FILMES:
            [arqMkv,arqMp4,arqAvi] = buscaFilmes(pasta);
            for tipo in [arqMkv,arqMp4,arqAvi]:
                for arq in tipo:
                    pasta   = arq[:arq.index(')/')+2];
                    nome    = arq[arq.index(')/')+2:];
                    tmp     = pasta+'tmp/';
                    tmpArq    = tmp+nome;
                    if(os.path.isfile(arq)):
                        print('ffmpeg -i "'+arq+'" -c:v hevc_nvenc -c:a copy "'+tmpArq+'"'); 
                        if(os.path.getsize(arq) >= TAMANHO_MINIMO):
                            os.system('mkdir "'+tmp+'"');
                            if(CODIFICADOR == 'HEVC'):
                                os.system('ffmpeg -i "'+arq+'" -c:v hevc_nvenc -c:a copy "'+tmpArq+'"');
                            elif(CODIFICADOR == 'H265'):
                                os.system('ffmpeg -i "'+arq+'" -c:v libx265 -c:a copy "'+tmpArq+'"');
                            else:
                                os.system('ffmpeg -i "'+arq+'" -vcodec h264 -acodec mp3 "'+tmpArq+'"');
                        if(os.path.isfile(tmpArq)):
                            if((os.path.getsize(tmpArq) <= os.path.getsize(arq)) and (os.path.getsize(tmpArq) > TAMANHO_MINIMO)):
                                os.system('mv "'+tmpArq+'" "'+pasta+'"');
                        if(os.path.exists(tmp)):
                            os.system('rm -r "'+tmp+'"');
                        linha = [];linha.append(nome);linha.append(pasta);linha.append(str(os.path.getsize(arq)));
                        escrever.writerow(linha);
#-----------------------
# Main()
#-----------------------    
if __name__ == '__main__':
    codificacaoDeFilmes();
#-----------------------