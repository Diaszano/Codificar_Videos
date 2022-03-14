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
PASTAS=['/nfs/Servidor/Streaming/Filmes/',];
ARQUIVO='./logCodificacao.csv';
#-----------------------
# FUNÇÕES
#-----------------------
def buscaFilmes(pasta):
    arqMkv = [];
    arqMp4 = [];
    arqAvi = [];
    for diretorio, subpastas, arquivos in os.walk(pasta):
        for dir, sub, arq in os.walk(diretorio):
            for a in arq:
                if '.mkv' in a:
                    arqMkv.append(dir+'/'+a);
                elif '.mp4' in a:
                    arqMp4.append(dir+'/'+a);
                elif '.avi' in a:
                    arqAvi.append(dir+'/'+a);
    return [arqMkv,arqMp4,arqAvi];
#-----------------------
# Main()
#-----------------------    
if __name__ == '__main__':
    for pasta in PASTAS:
        [arqMkv,arqMp4,arqAvi] = buscaFilmes(pasta);
        with open(ARQUIVO,'w',newline='') as file:
            escrever = csv.writer(file);
            escrever.writerow(['Filme','Pasta','Tamanho']);
            for tipo in [arqMkv,arqMp4,arqAvi]:
                for arq in tipo:
                    pasta   = arq[:arq.index(')/')+2];
                    nome    = arq[arq.index(')/')+2:];
                    tmp     = pasta+'tmp/';
                    tmpArq    = tmp+nome;
                    if(os.path.isfile(arq)): # Estava dando erro sem esse if irei verificar depois
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