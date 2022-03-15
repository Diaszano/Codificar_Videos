#-----------------------
# BIBLIOTECAS
#-----------------------
import mysql.connector as mariadb
#-----------------------
# FUNÇÕES
#-----------------------
def conexao(host:str,user:str,password:str,database:str) -> list:
    cnxn = mariadb.connect(
        host=host,
        user=user,
        password=password,
        database=database,
    );
    cursor = cnxn.cursor();
    return[cnxn,cursor];

def create(comando:str,cnxn,cursor) -> None:
    cursor.execute(comando);
    cnxn.commit();

def read(comando:str,cursor) -> list:
    cursor.execute(comando);
    resultado = cursor.fetchall();
    return resultado;

def update(comando:str,cnxn,cursor) -> None:
    cursor.execute(comando);
    cnxn.commit();

def delete(comando:str,cnxn,cursor) -> None:
    cursor.execute(comando);
    cnxn.commit();

def desconexao(cnxn,cursor) -> None:
    cursor.close();
    cnxn.close();
#-----------------------
# Main()
#-----------------------    
if __name__ == '__main__':
    # Dados o Banco
    host='localhost';
    database='db_Teste';
    user='root';
    password='123**';
    #Conexão com o banco
    [cnxn,cursor] = conexao(host=host,database=database,user=user,password=password);
    # Requisição ao banco
    comando = f'select * from teste;';
    print(read(comando=comando,cursor=cursor));
    # Desconexão com o banco
    desconexao(cnxn,cursor);
#-----------------------
