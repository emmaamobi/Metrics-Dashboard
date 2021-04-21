import sqlite3 
from sqlite3 import Cursor, Connection
from NewCalculations import Calculations
import sys
def main():
    db_file = sys.argv[1]
    calc = Calculations(db_file)
    conn = calc.create_connection(db_file)
    cursor= conn.cursor()
    cursor.execute(
        "DROP TABLE IF EXISTS CALCULATIONS;"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS CALCULATIONS (calc_name VARCHAR(3000), value VARCHAR(3000));"
    )

    data = [
        ('closed to open ratio',calc.get_closed_to_open_ratio(conn)),
        ('closing efficiency (%)',calc.get_closing_efficiency(conn)),
        ('average days to close issues(days)',calc.get_avg_days_to_close_issue(conn)),
    ]
    sql = 'insert into CALCULATIONS(calc_name,value) VALUES(?,?);'
    cursor.executemany(sql,data)
    conn.commit()
    ####################
    ## team effort per commit
    cursor.execute(
        "DROP TABLE IF EXISTS Team_Effort"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Team_Effort (commit_sha VARCHAR(3000), team_effort VARCHAR(3000));"
    )
    data = calc.team_effort_per_commit(conn)
    sql = 'insert into Team_Effort(commit_sha, team_effort) VALUES(?,?);'
    cursor.executemany(sql,data)
    conn.commit()
    sys.exit(0)

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS issue_Density (commit_sha VARCHAR(3000), commit_date VARCHAR(100) issue_density VARCHAR(3000));"
    )
    data = calc.calculate_issue_density(conn)
    sql = 'insert into issue_Density(commit_sha, commit_date, issue_density) VALUES(?,?,?);'
    cursor.executemany(sql,data)
    conn.commit()
    # insert calculations into table
    print("Inserted calculations into table")

if __name__ == '__main__':
    main()
