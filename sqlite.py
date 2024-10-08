import sqlite3


#connect to sqllite 
connection = sqlite3.Connection("student.db")


##create a cursor object to insert, create table
cursor = connection.cursor()

##create the table

table_info = """
    create table STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),
    SECTION VARCHAR(25),MARKS INT)
"""

cursor.execute(table_info)

##Inser some more records

cursor.execute('''Insert Into STUDENT values('Prajwal','GenAI','A',90)''')
cursor.execute('''Insert Into STUDENT values('Shubham','Data Science','B',95)''')
cursor.execute('''Insert Into STUDENT values('Pratik','DevOPS','A',85)''')
cursor.execute('''Insert Into STUDENT values('Suyash','Data Analyst','C',98)''')
cursor.execute('''Insert Into STUDENT values('Akshay','GenAI','B',92)''')

##Display all the records 
print("The inserted records are ")
data = cursor.execute('''Select * from STUDENT''')
for row in data :
    print(row)


##Commit changes in databases
connection.commit()
connection.close()