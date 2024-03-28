# Student Attendance Management System
# Created by: Khen Jomarie L. Alcantara
# Degree: BS Electronics And Communication Engineering
# Level: 1st Year

# Import library
import sqlite3
import datetime
import msvcrt
import ctypes.wintypes
import os
import sys
import re
import textwrap
import time

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
schedule = []


class text:
    none = "\033[0m"

    class color:
        class foreground:
            black = "\033[30m"
            red = "\033[31m"
            green = "\033[32m"
            yellow = "\033[33m"
            blue = "\033[34m"
            magenta = "\033[35m"
            cyan = "\033[36m"
            light_gray = "\033[37m"
            dark_gray = "\033[90m"
            light_red = "\033[91m"
            light_green = "\033[92m"
            light_yellow = "\033[93m"
            light_blue = "\033[94m"
            light_magenta = "\033[95m"
            light_cyan = "\033[96m"
            white = "\033[97m"

        class background:
            black = "\033[40m"
            red = "\033[41m"
            green = "\033[42m"
            yellow = "\033[43m"
            blue = "\033[44m"
            magenta = "\033[45m"
            cyan = "\033[46m"
            light_gray = "\033[47m"
            dark_gray = "\033[100m"
            light_red = "\033[101m"
            light_green = "\033[102m"
            light_yellow = "\033[103m"
            light_blue = "\033[104m"
            light_magenta = "\033[105m"
            light_cyan = "\033[106m"
            white = "\033[107m"

    class style:
        bold = "\033[1m"
        underline = "\033[4m"
        no_underline = "\033[24m"
        reverse = "\033[7m"
        not_reverse = "\033[27m"


# Setting up connection with SAData.db file
connection = sqlite3.connect('SAData.db')

# Assigning cursor for executing sqlite3 inquiries
cursor = connection.cursor()

# Creating Student_info table and column if not exist
cursor.execute("CREATE TABLE IF NOT EXISTS Student_Info ("
               "Student_No  ANY UNIQUE PRIMARY KEY, "
               "_Name        TEXT, "
               "_Department  TEXT, "
               "_Degree      TEXT, "
               "_Level       TEXT, "
               "_Signature   TEXT)")

# Creating another ClassSchedule table and column
cursor.execute("CREATE TABLE IF NOT EXISTS ClassSchedule ("
               "Student_No  ANY, "
               "_Course     TEXT, "
               "_Day         Text, "
               "_Time        TEXT)")

# Creating another attendance table and column
cursor.execute("CREATE TABLE IF NOT EXISTS Attendance ("
               "Student_No  ANY, "
               "_Course    TEXT, "
               "_Time        TEXT, "
               "_Date        TEXT, "
               "_Status      ANY)")

# Saving all inquiries
connection.commit()


def run_as_administrator():
    # Checking current console if not running as administrator
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, os.path.basename(__file__), None, 1)
        sys.exit()


def center_console_window():
    # Get handle to the console window
    console_handle = ctypes.windll.kernel32.GetConsoleWindow()
    if console_handle != 0:
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)

        # Get dimensions of the console window
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(console_handle, ctypes.byref(rect))
        console_width = rect.right - rect.left
        console_height = rect.bottom - rect.top

        # Calculate new position
        x = (screen_width - console_width) // 2
        y = (screen_height - console_height) // 2

        # Set console window position
        ctypes.windll.user32.MoveWindow(console_handle, x, y, console_width, console_height, True)


def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


def set_console_size(width: int, height: int):
    os.system(f"mode con cols={width} lines={height}")

    # Define necessary constants
    GWL_STYLE = -16
    WS_SIZEBOX = 0x00040000
    WS_MAXIMIZEBOX = 0x00010000

    # Get handle to the console window
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()

    # Modify the window style to remove the sizing border
    if hwnd != 0:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style &= ~WS_SIZEBOX
        style &= ~WS_MAXIMIZEBOX
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)


def clear(line):
    for _ in range(line):
        print("\x1b[1A\x1b[2K", end="\r")


def input_key(__prompt):
    print(__prompt, end='', flush=True)  # Print the prompt without a newline
    while True:
        key = msvcrt.getch().decode()
        if key:
            print("\n", end='')
            return key


def not_empty_input(__prompt):
    while True:
        user_input = input(__prompt)
        if user_input:
            return user_input
        else:
            clear(1)


def tab_title(title):
    # Get the current date
    current_date = datetime.datetime.now().date().strftime("%B %d, %Y | %A")

    # Get the current time
    current_time = datetime.datetime.now().time().strftime("%I:%M %p")
    print(text.color.foreground.green, end="")
    print("==========================================================================================".center(90))
    print(text.color.foreground.yellow, end="")
    print(text.style.bold + title.center(90) + text.none)
    print(text.color.foreground.light_cyan, end="")
    print(f"{current_date}                                                  {current_time}".center(90))
    print(text.color.foreground.green, end="")
    print("==========================================================================================".center(90))
    print(text.none, end="")


def main():
    tab_title("STUDENT ATTENDACE")
    while True:
        print("   OPTION:")
        print("      [1] Check Attendance")
        print("      [2] Register New Student")
        print("      [3] Modify Class Schedule")
        print("      [4] Modify Student Details")
        print("      [0] Exit\n")

        choice2 = input_key("   Choice: ")

        match choice2:
            case "0":
                exit()
            case "1":
                clear(12)
                check_attendance()
                break
            case "2":
                clear(12)
                register_new_student()
                break
            case "3":
                print("Invalid Choice")
            case "4":
                print("Invalid Choice")
            case _:
                clear(8)
                continue
        break


def add_student(no, name, department, degree, level, signature):
    cursor.execute("INSERT INTO Student_Info VALUES (?, ?, ?, ?, ?, ?)",
                   (no, name, department, degree, level, signature))


def add_schedule(test):
    cursor.executemany("INSERT INTO ClassSchedule VALUES (?, ?, ?, ?)", test)


def check_attendance():
    tab_title("Check attendance")
    print("   Student Details")
    print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
    stud_no = str(not_empty_input("      Student No. : "))

    cursor.execute("SELECT * FROM Student_Info WHERE Student_No = ?", (stud_no,))
    data = cursor.fetchall()

    if data:
        for val in data:
            print(f"      Name        : {val[1]}\n"
                  f"      Department  : {val[2]}\n"
                  f"      Degree      : {val[3]}\n"
                  f"      Level       : {val[4]}")

            current_day = datetime.datetime.now().date().strftime("%A")
            cursor.execute("SELECT * FROM ClassSchedule WHERE Student_No = ? AND _Day = ?", (stud_no, current_day,))
            sched = cursor.fetchall()
            if sched:
                for sch in sched:
                    print(f"      Course     : {sch[1]}\n")
                    print(f"      Time       : {sch[3]}\n")
            os.system("pause")
    else:
        while True:
            clear(3)
            print("   OPTION:")
            print("      [1] Check again")
            print("      [2] Register new student")
            print("      [0] Return to Home\n")
            print("   MSG: Student currently not enrolled!!!")

            choice = input_key("   choice: ")
            match choice:
                case ("0"):
                    clear(11)
                    main()
                    break
                case ("1"):
                    clear(11)
                    check_attendance()
                    break
                case ("2"):
                    clear(11)
                    register_new_student()
                    break
                case _:
                    clear(4)
        return


def validate_time_format(time):
    # Define the regex pattern to match the time format
    pattern = r'^\d{1,2}:\d{2} [AP]M - \d{1,2}:\d{2} [AP]M$'

    # Check if the input matches the pattern
    if re.match(pattern, time):
        return True
    else:
        return False


def convert_to_24Hrs(time_str):
    # Convert time string from 12-hour format to minutes
    parts = time_str.split()
    hour, minute = map(int, parts[0].split(':'))
    if parts[1].upper() == 'PM' and hour != 12:
        hour += 12
    return hour * 60 + minute


def check_conflict(schedules, day, time):
    new_start, new_end = map(convert_to_24Hrs, time.split(' - '))

    for index, (stud_no, sched_course, sched_day, sched_time) in enumerate(schedules):
        if sched_day != day:
            continue

        start, end = map(convert_to_24Hrs, sched_time.split(' - '))
        if start <= new_start < end:
            return sched_course  # Conflict found
        elif start < new_end <= end:
            return sched_course  # Conflict found
        elif new_start <= start and new_end >= end:
            return sched_course  # Conflict found

    return None  # No conflict found


def add_course(stud_no, sched_day):
    while True:
        try:
            total_course = int(input("         Total course: "))
            break
        except ValueError:
            clear(1)
            pass

    num = 0
    while num < total_course:
        print("         --------------------")

        sched_course = str(not_empty_input("         course\t: "))

        while True:
            sched_time = str(not_empty_input("         Time\t: ").upper())
            if validate_time_format(sched_time):
                break
            else:
                msg = input_key("\n      MSG: Invalid time format."
                                "\n           Please follow the format: 10:00 AM - 12:00 PM")
                if msg:
                    clear(4)

        conflict = check_conflict(schedule, sched_day, sched_time)
        if conflict is None:
            schedule.append((stud_no, sched_course, sched_day, sched_time))
            num += 1
        else:
            msg = input_key(f"\n      MSG: conflict schedule with {conflict.upper()}. ")
            if msg:
                clear(5)


def register_new_student():
    tab_title("REGISTER NEW STUDENT")
    print("   Student Details")
    print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")

    while True:
        stud_no = str(not_empty_input("      Student No. : "))

        cursor.execute(f"SELECT * FROM Student_Info WHERE Student_No = {stud_no}")
        data = cursor.fetchall()
        if data:
            msg = input_key("\n   MSG: Student already registered. Press[M] to modify schedule. ")
            if msg:
                clear(3)
        else:
            break

    stud_name = str(not_empty_input("      Name        : ").upper())
    stud_department = str(not_empty_input("      Department  : ").title())
    stud_degree = str(not_empty_input("      Degree      : ").title())
    stud_level = str(not_empty_input("      Year Level  : "))
    stud_signature = str(not_empty_input("      Signature   : "))

    print("\n   Class Schedule")
    print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
    while True:
        print("   Option:")
        print("      [1] Weekdays only")
        print("      [2] Include weekends")
        print("      [0] Return to Home\n")

        choice1 = input_key("   Choice: ")

        days_of_week = None
        match choice1:
            case "0":
                clear(100)
                main()
                break
            case "1":
                clear(8)
                days_of_week = "Weekdays only"
                print(f"   Class Schedule [{days_of_week}]")
                print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
            case "2":
                clear(8)
                days_of_week = "Include weekends"
                print(f"   Class Schedule [{days_of_week}]")
                print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
            case _:
                clear(6)
                continue
        break

    while True:
        if days_of_week == "Weekdays only":
            for day in days[:5]:
                print(f"      ► {day}")
                add_course(stud_no, day)
            break
        if days_of_week == "Include weekends":
            for day in days:
                print(f"      ► {day}")
                add_course(stud_no, day)
            break

    try:
        add_student(stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature)
        add_schedule(schedule)
        connection.commit()
    except sqlite3.IntegrityError:
        print("Already Exists")


if __name__ == "__main__":
    run_as_administrator()
    set_console_title("Student Attendance Management System")
    set_console_size(90, 45)
    center_console_window()
    main()
