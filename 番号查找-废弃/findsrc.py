import sqlite3
from os import startfile
from traceback import print_exc

IS_DEBUG=False

def debug(*args):
    if IS_DEBUG:
        print('debug: ',*args)

def show_label(option,conn):
    if option is None:
        sql='select type,group_concat(label) as labels from LABEL_TBL group by type'
    else:
        pair=option.split('=',maxsplit=1)
        if pair[0].strip() == 'type' or pair[0].strip() == 't':
            values=[ e.strip() for e in pair[1].split(',') if len(e) > 0 and not e.isspace() ]
            debug('<show_label> values =',values)
            sql='select type,group_concat(label) as labels from LABEL_TBL group by type'
            if len(values)>0:
                sql="{} having type in ({})".format(sql,str(values)[1:-1])
        else:
            sql="select label from LABEL_TBL where label = '{}'".format(option)

    debug('<show_label> sql语句为',sql)
    cursor=conn.execute(sql)
    for e in cursor.fetchall():
        if len(e) == 1:
            print(e['label'])
        else:
            print(e['type'],'：',e['labels'])
    cursor.close()

def search_res(option,conn):
    sql='select * from RES_TBL where actress '
    ops=option.split(maxsplit=1)
    if len(ops) != 2:
        print('error: 请输入正确的查询格式')
        return
    if ops[0] == r'*':
        sql+="like '%'"
    else:
        op1=ops[0].split(',')
        # 列表['1','2'] -> 字符串'1','2'
        sql='{}in ({})'.format(sql,str(op1)[1:-1])
        debug('<search_res> actress = ', op1)
    cursor=conn.execute(sql)
    data1=cursor.fetchall()
    cursor.close()
    if ops[1] == r'*':
        reusult=data1
    else:
        if ops[1].startswith('+'):
            operator='and'
            op2=set(ops[1].replace('+','',1).split(','))
        else:
            operator='or'
            op2=set(ops[1].split(','))
        debug('<search_res> label = ', op2, '逻辑运算符为',operator)
        reusult=list()
        for r in data1:
            labels=set(r['label'].split())
            if operator == 'and':
                if labels >= op2:
                    reusult.append(r)
            elif operator == 'or':
                if labels & op2:
                   reusult.append(r) 

    for e in reusult:
        print('({})  ({})  ({})  ({})'.format(e['id'],e['title'],e['actress'],e['label']))

    while True:
        command=input('search > ').lower().split(maxsplit=1)
        if command[0] == 'q' or command[0] == 'quit':
            break
        if len(command) < 2:
            continue
        name,opt=command[0],int(command[1])
        for r in reusult:
            if r['id'] == opt:
                if name == 'desc':
                    print('编号: {}\n番号: {}\n标题: {}\n女优: {}\n标签: {}\n路径: {}\n'.format(r['id'],r['no.'],r['title'],r['actress'],r['label'],r['path']))
                elif name == 'open':
                    startfile(r['path']) 

def main():
    with sqlite3.connect('data.db') as conn:
        conn.row_factory = sqlite3.Row
        while True:
            command=input('main > ').lower().split(maxsplit=1)
            if len(command)==0:
                continue
            cname=command[0]
            option=command[1] if len(command) > 1 else None
            debug('<main> 命令拆分为 ({}) , ({})'.format(cname,option))
            
            if cname == 'quit' or cname == 'q':
                break
            elif cname == 'label' or cname == 'l':
                show_label(option,conn)
            elif cname == 'search' or cname == 's':
                try:
                    search_res(option,conn)
                except KeyboardInterrupt:
                    print_exc()
                    break
                except:
                    print_exc()
                    print('<main> search_res函数发生异常，请检查输入的查询语句是否符合规范。')

if __name__ == '__main__':
    main()