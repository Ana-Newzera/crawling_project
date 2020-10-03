import mariadb

def sql_connection():
    try:
        con = mariadb.connect(
        user="uadmin",
        password="admin",
        host="127.0.0.1",
        port=3306,
        database="archivecrawler")
        return con
    except Error:
        print(Error)

def create_table():
    con = sql_connection()
    cursorObj = con.cursor()
    query = "CREATE TABLE `article-state-01`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-02`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-03`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-04`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-05`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-06`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-07`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-08`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-09`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-10`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-11`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE TABLE `article-state-12`(url_hash varchar(1000), url varchar(1000), publisher varchar(200), publish_date varchar(200), state varchar(20))" 
    cursorObj.execute(query)
    query = "CREATE Index d1 on `article-state-01`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d2 on `article-state-02`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d3 on `article-state-03`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d4 on `article-state-04`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d5 on `article-state-05`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d6 on `article-state-06`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d7 on `article-state-07`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d8 on `article-state-08`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d9 on `article-state-09`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d10 on `article-state-10`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d11 on `article-state-11`(url_hash)" 
    cursorObj.execute(query)
    query = "CREATE Index d12 on `article-state-12`(url_hash)" 
    cursorObj.execute(query)
    con.commit()
    con.close()

create_table()
