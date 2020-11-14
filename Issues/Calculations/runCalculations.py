from IssuesCalculation import Calculations
import sys
def main():
    db_file = sys.argv([1])
    calc = Calculations(db_file)
    print(calc)

if __name__ == '__main__':
    main()
