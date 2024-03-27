# Student Attendance Management System
# Created by: Khen Jomarie L. Alcantara
# Degree: BS Electronics And Communication Engineering
# Level: 1st Year

# Import library
import sqlite3
import msvcrt
import ctypes.wintypes
import os
import sys
import re

schedule = []

# Setting up connection with SAData.db file
connection = sqlite3.connect('SAData.db')

# Assigning cursor for executing sqlite3 inquiries
cursor = connection.cursor()

# Creating Student_info table and column if not exist
cursor.execute("CREATE TABLE IF NOT EXISTS Student_Info ("
               "Student_No  ANY UNIQUE PRIMARY KEY, "
               "Name        TEXT, "
               "Department  TEXT, "
               "Degree      TEXT, "
               "Level       TEXT, "
               "Signature   TEXT)")

# Creating another ClassSchedule table and column
cursor.execute("CREATE TABLE IF NOT EXISTS ClassSchedule ("
               "Student_No  ANY, "
               "Course     TEXT, "
               "Day         Text, "
               "Time        TEXT)")

# Creating another attendance table and column
cursor.execute("CREATE TABLE IF NOT EXISTS Attendance ("
               "Student_No  ANY, "
               "Course     TEXT, "
               "Time        TEXT, "
               "Date        TEXT, "
               "Status      ANY)")

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

    # Get handle to the console window
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()

    # Modify the window style to remove the sizing border
    if hwnd != 0:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style &= ~WS_SIZEBOX
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
    print("================================================================================".center(80))
    print(title.center(80))
    print("================================================================================".center(80))


def main():
    tab_title("STUDENT ATTENDANCE")
    while True:
        print("   OPTION:")
        print("      [1] Check Attendance")
        print("      [2] Register New Student")
        print("      [3] Modify Class Schedule")
        print("      [0] Exit\n")

        choice2 = input_key("   Choice: ")

        match choice2:
            case "0":
                exit()
            case "1":
                clear(9)
                check_attendance()
                break
            case "2":
                clear(11)
                register_new_student()
            case "3":
                print("Invalid Choice")
            case _:
                # Deleting current menu option after entering invalid input
                clear(9)
                continue
        break


def get_students_info(student_no):
    cursor.execute("SELECT * FROM Student_Info WHERE Student_No = ?", (student_no,))
    data = cursor.fetchall()

    if data:
        for val in data:
            print(f"   Name\t\t\t: {val[1]}\n"
                  f"   Department\t: {val[2]}\n"
                  f"   Degree\t\t: {val[3]}\n"
                  f"   Level\t\t: {val[4]}")
    else:
        clear(1)
        print("OPTION:")
        print("   [1] Check again")
        print("   [0] Return to Home\n")
        print("MSG: Student currently not enrolled!!!")

        choice = input_key("choice: ")
        match choice:
            case("0"):
                clear(8)
                main()
            case("1"):
                clear(8)
                check_attendance()
            case _:
                clear(5)
                get_students_info(choice)
        return


def add_student(no, name, department, degree, level, signature):
    cursor.execute("INSERT INTO Student_Info VALUES (?, ?, ?, ?, ?, ?)",
                   (no, name, department, degree, level, signature))


def add_schedule(test):
    cursor.executemany("INSERT INTO ClassSchedule VALUES (?, ?, ?, ?)", test)


def check_attendance():
    while True:
        print("Check attendance")
        print("﹉﹉﹉﹉﹉﹉﹉﹉﹉")
        student_no = str(input("   Student No.\t: "))

        if student_no == "":
            clear(3)
            continue

        get_students_info(student_no)
        break


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


def check_conflict(schedules, time):
    new_start, new_end = map(convert_to_24Hrs, time.split('-'))

    for index, (stud_no, sched_course, sched_day, sched_time) in enumerate(schedules):
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

        conflict = check_conflict(schedule, sched_time)
        if conflict is None:
            schedule.append((stud_no, sched_course, sched_day, sched_time))
            num += 1
        else:
            msg = input_key(f"\n      MSG: conflict schedule with {conflict.upper()}. ")
            if msg:
                clear(5)


def register_new_student():
    tab_title("REGISTER NEW STUDENT")
    print("   Student Information")
    print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")

    while True:
        stud_no = str(not_empty_input("      Student No. : "))
        try:
            cursor.execute(f"SELECT * FROM Student_Info WHERE Student_No = {stud_no}")

            msg = input_key("\n   MSG: Student already registered. Press[M] to modify schedule. ")
            if msg:
                clear(3)

        except sqlite3.OperationalError:
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

        days = None
        match choice1:
            case "0":
                clear(17)
                main()
                break
            case "1":
                clear(8)
                days = "Weekdays only"
                print(f"   Class Schedule [{days}]")
                print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
            case "2":
                clear(8)
                days = "Include weekends"
                print(f"   Class Schedule [{days}]")
                print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
            case _:
                clear(6)
                continue
        break

    while True:
        if days == "Weekdays only":
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                print(f"      ► {day}")
                add_course(stud_no, day)
            break
        if days == "Include weekends":
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                print(f"      ► {day}")
                add_course(stud_no, day)
            break

    try:
        add_student(stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature)
        add_schedule(schedule)
        connection.commit()
    except sqlite3.IntegrityError:
        print("Already Exists")


run_as_administrator()
set_console_title("Student Attendance Management System")
set_console_size(80, 40)
center_console_window()

if __name__ == "__main__":
    main()

cursor.execute("SELECT * FROM Student_Info")
rows = cursor.fetchall()

for row in rows:
    print(row)
