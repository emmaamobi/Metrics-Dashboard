import sqlite3 
from sqlite3 import Cursor, Connection
import datetime as dt
import sys
class Calculations:
    def __init__(self, db_file: str) -> None:
        ''' 
        Initialize class variables
        :param db_file: The db file to be used by the class
        '''
        self.conn = self.create_connection(db_file)

    def create_connection(self,db_file: str) -> Connection:
        ''' 
        Creates a connection with the db
        :param db_file: The db file to create connection with
        '''
        conn = None 
        try: 
            conn = sqlite3.connect(db_file)
        except Error as e: 
            print(e)

        return conn

    def get_total_issues(self,conn: Connection) -> int:
        ''' 
        Returns the total number of issues
        :param conn: The db connection
        '''
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) from ISSUES ")
        result = cur.fetchall()[0][0] # get first item in tuple
        cur.close()
        return result

    def count_rows_by_col_value(self,col: str, value: str, conn: Connection) -> int:
        ''' 
        counts rows filtered by given column and specified value
        :param col: The column name
        :param value: The value for filtering
        :param conn: The db connection
        '''
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) {columnS} from ISSUES where {columnS}='{valueS}'".format(valueS=value,columnS=col))
        result = cur.fetchall()[0][0] # get first item in tuple
        cur.close()
        return result

    def get_open_count(self,conn: Connection) -> int:
        ''' 
        Returns the total number of open issues
        :param conn: The db connection
        '''
        open_count = self.count_rows_by_col_value("state","open",conn)
        return open_count

    def get_closed_count(self,conn: Connection):
        ''' 
        Returns the total number of closed issues
        :param conn: The db connection
        '''
        closed_count = self.count_rows_by_col_value("state","closed",conn)
        return closed_count

    def get_closed_to_open_ratio(self,conn: Connection) -> float:
        ''' 
        Returns the ratio of closed to opened issues
        :param conn: The db connection
        '''
        open_count = self.get_open_count(conn)
        closed_count = self.get_closed_count(conn)
        ratio = round((closed_count/ open_count),2) if open_count > 0 else 0
        return ratio

    def get_closing_efficiency(self,conn: Connection) -> str:
        ''' 
        Returns efficiency, efficiency = output/input, where output = closed issues, input = total issues
        :param conn: The db connection
        '''
        total = self.get_total_issues(conn)
        closed_count = self.get_closed_count(conn)
        closing_efficiency = round((closed_count / total),2) if total > 0 else 0
        closing_efficiency_percent = closing_efficiency * 100
        result = str(closing_efficiency_percent) + "%"
        return result

    # deprecated team_effort
    # def get_team_effort(self,conn: Connection) -> float: 
    #     ''' 
    #     Returns TeamEffort, = T(lastCommit) - T(firstCommit)
    #     :param conn: The db connection
    #     '''
    #     cur = conn.cursor()
    #     cur.execute("SELECT MIN(Commit_Date) from Commits ")
    #     first_commit = cur.fetchall()[0][0]
    #     date_first_commit = dt.datetime.strptime(first_commit, "%Y-%m-%dT%H:%M:%SZ")
    #     cur.execute("SELECT MAX(Commit_Date) from Commits ")
    #     last_commit = cur.fetchall()[0][0]
    #     date_last_commit = dt.datetime.strptime(last_commit, "%Y-%m-%dT%H:%M:%SZ")
    #     time_difference = date_last_commit - date_first_commit
    #     # print("TIME DIFFERENCE: ", time_difference)
    #     time_difference = time_difference.total_seconds()
    #     return time_difference

    def team_effort_per_commit(self,conn: Connection) -> list:
        '''
        Returns Team Effort per commit = T(last commit) - T(first commit)
        '''
        # helper func, take two times, ti(initial time) and tf(end time), and get the diff in seconds:
        def do_time_diff(ti,tf):
            date_ti = dt.datetime.strptime(ti, "%Y-%m-%dT%H:%M:%SZ")
            date_tf = dt.datetime.strptime(tf, "%Y-%m-%dT%H:%M:%SZ")
            time_diff = date_tf - date_ti
            return time_diff.total_seconds()


        cur = conn.cursor()
        cur.execute("SELECT Commit_SHA,MIN(Commit_Date) from Commits ")
        # first_commit = cur.fetchall()[0][0]
        first_commit = cur.fetchall()[0]  # (commit_sha, date)
        date_first_commit = dt.datetime.strptime(first_commit[1], "%Y-%m-%dT%H:%M:%SZ")
        cur.execute("SELECT Commit_SHA,Commit_Date from Commits ")
        # commits = cur.fetchall()[0][0]
        commits = cur.fetchall()
        effort = [(i[0], do_time_diff(first_commit[1],i[1])) for i in commits] # populate effort (commit_sha, team_effort)
        return effort

    # deprecated, will be implemented as a function of time or per commit
    def calculate_issue_density(self, conn:Connection) -> list: 
        '''
        Returns Issue density per kloc
        :param conn: The db connection
        '''
        def to_dt(time_str):
            return dt.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
        # Get issues
        cur = conn.cursor()
        cur.execute("SELECT ID, Created_At_Date,Closed_At_Date from Issues")
        issues = cur.fetchall()
        issues = [(i[0],to_dt(i[1]),to_dt(i[2]) if i[2] else i[2]) for i in issues ] # convert to datetime obj
        # Get commits
        cur = conn.cursor()
        cur.execute("SELECT Commit_SHA,Commit_Date from Commits")
        commits = cur.fetchall()
        # commits = [(i[0],to_dt(i[1]),"commit") for i in commits] # convert to datetime obj, "commit" means it's a commit
        commits = [[i[0],to_dt(i[1]),0, 0] for i in commits] # convert to datetime obj, "commit" means it's a commit
        # issues_x_commits = issues + commits # join issues and commits 
        # issues_x_commits = sorted(issues_x_commits, key=lambda x: x[1])#sort by date
        commits = sorted(commits, key=lambda x:x[1])
        issues = sorted(issues, key=lambda x:x[1])

        #  Track and update issues per commit
        for commit in commits:
            issue_count = 0
            i = 0
            while issues[i][1] < commit[1]: # issue opened before commit date
                if not issues[i][2]: # if issue hasn't been closed
                    issue_count += 1
                else:
                    if issues[i][2] >= commit[1]: # if issue closed date is after commit date
                        issue_count += 1
                i += 1

            commit[2] = issue_count # total active issues for commit
            issue_count = 0 # reset issue count

            
        # TODO: put code size in 4th space in commits, i[3]
        def do_iss_density(issue_count,code_size):
            return round((issue_count/code_size),2)
        # TODO calculate issue density per commit
        issue_density = [(i[0],i[1],do_iss_density(i[2],i[3])) for i in commits]
        return issue_density


    def get_avg_days_to_close_issue(self,conn: Connection) -> float:
        ''' 
        Returns average number of days it takes to close an Issue
        :param conn: The db connection
        '''
        cur = conn.cursor()
        query = "SELECT julianday(Closed_At_Date) - julianday(Created_At_Date) from ISSUES where state='closed'"
        cur.execute(query)
        result = cur.fetchall()
        days = [i[0] for i in result]
        avg = round((sum(days) / len(days)),2) if len(days) > 0 else 0
        cur.close()
        return avg
        
    def __str__(self) -> str:
        ''' 
        String representation of the class Calculations
        '''
        opened = str(self.get_open_count(self.conn))
        closed = str(self.get_closed_count(self.conn))
        total = str(self.get_total_issues(self.conn))
        ratio = str(self.get_closed_to_open_ratio(self.conn))
        closing_efficiency = str(self.get_closing_efficiency(self.conn))
        average_close_time = str(self.get_avg_days_to_close_issue(self.conn))
        result = "Number of opened issues: " + opened + "\n"
        result += "Number of closed issues: " + closed + "\n"
        result += "Total number of issues: " + total + "\n"
        result += "Closed to open ratio: " + ratio + "\n"
        result += "closing_efficiency: " + closing_efficiency + "\n"
        result += "Average time taken to close issues: " + average_close_time +" days" "\n"
        return result

