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

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
schedule = []


class Text:
    NONE = "\033[0m"

    class Color:
        class Foreground:
            Black = "\033[30m"
            Red = "\033[31m"
            Green = "\033[32m"
            Yellow = "\033[33m"
            Blue = "\033[34m"
            Magenta = "\033[35m"
            Cyan = "\033[36m"
            Light_Gray = "\033[37m"
            Dark_Gray = "\033[90m"
            Light_Red = "\033[91m"
            Light_Green = "\033[92m"
            Light_Yellow = "\033[93m"
            Light_Blue = "\033[94m"
            Light_Magenta = "\033[95m"
            Light_Cyan = "\033[96m"
            White = "\033[97m"

        class Background:
            Black = "\033[40m"
            Red = "\033[41m"
            Green = "\033[42m"
            Yellow = "\033[43m"
            Blue = "\033[44m"
            Magenta = "\033[45m"
            Cyan = "\033[46m"
            Light_Gray = "\033[47m"
            Dark_Gray = "\033[100m"
            Light_Red = "\033[101m"
            Light_Green = "\033[102m"
            Light_Yellow = "\033[103m"
            Light_Blue = "\033[104m"
            Light_Magenta = "\033[105m"
            Light_Cyan = "\033[106m"
            White = "\033[107m"

    class Style:
        Bold = "\033[1m"
        Underline = "\033[4m"
        No_Underline = "\033[24m"
        Reverse = "\033[7m"
        Not_Reverse = "\033[27m"


# Setting up connection with SAData.db file
connection = sqlite3.connect('SAData.db')

# Assigning cursor for executing sqlite3 inquiries
cursor = connection.cursor()

# Creating Student_info table and column if not exist
cursor.execute("CREATE TABLE IF NOT EXISTS Student_Info ("
               "Student_No   TEXT UNIQUE PRIMARY KEY, "
               "_Name        TEXT, "
               "_Department  TEXT, "
               "_Degree      TEXT, "
               "_Level       TEXT, "
               "_Signature   TEXT)")

# Creating another ClassSchedule table and column
cursor.execute("CREATE TABLE IF NOT EXISTS ClassSchedule ("
               "Student_No   TEXT, "
               "_Course      TEXT, "
               "_Day         TEXT, "
               "_Time        TEXT)")

# Creating another Attendance table and column
cursor.execute("CREATE TABLE IF NOT EXISTS Attendance ("
               "Student_No   TEXT, "
               "_Course      TEXT, "
               "_Day         TEXT, "
               "_Time        TEXT, "
               "_Date        TEXT, "
               "_TimeIn      TEXT, "
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
    gwl_style = -16
    ws_sizebox = 0x00040000
    ws_maximizebox = 0x00010000

    # Get handle to the console window
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()

    # Modify the window style to remove the sizing border
    if hwnd != 0:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, gwl_style)
        style &= ~ws_sizebox
        style &= ~ws_maximizebox
        ctypes.windll.user32.SetWindowLongW(hwnd, gwl_style, style)


def clear(line):
    for _ in range(line):
        print("\x1b[1A\x1b[2K", end="\r")


def input_key(__prompt):
    print(__prompt, end='', flush=True)  # Print the prompt without a newline
    while True:
        try:
            key = msvcrt.getch().decode()
            if key:
                print("\n", end='')
                return key
        except UnicodeDecodeError:
            continue


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
    print(Text.Color.Foreground.Green, end="")
    print("==========================================================================================".center(90))
    print(Text.Color.Foreground.Yellow, end="")
    print(Text.Style.Bold + title.center(90) + Text.NONE)
    print(Text.Color.Foreground.Light_Cyan, end="")
    print(f"{current_date}                                                  {current_time}".center(90))
    print(Text.Color.Foreground.Green, end="")
    print("==========================================================================================".center(90))
    print(Text.NONE, end="")


def main():
    tab_title("STUDENT ATTENDANCE")
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


def add_student(stud_no, name, department, degree, level, signature):
    cursor.execute("INSERT INTO Student_Info VALUES (?, ?, ?, ?, ?, ?)",
                   (stud_no, name, department, degree, level, signature))


def add_schedule(sched):
    cursor.executemany("INSERT INTO ClassSchedule VALUES (?, ?, ?, ?)", sched)


def attendance(attdnt):
    cursor.executemany("INSERT INTO Attendance VALUES (?, ?, ?, ?, ?, ?, ?)", attdnt)


def check_attendance():
    tab_title("Check attendance")
    print("   Student Details")
    print("   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")

    attendance_log = []
    next_schedule = []
    status = "PENDING"
    next_schedule_found = False
    schedule.clear()

    stud_no = str(not_empty_input("      Student No. : "))

    cursor.execute("SELECT * FROM Student_Info WHERE Student_No = ?", (stud_no,))
    data = cursor.fetchall()

    if data:
        for val in data:
            print(f"      Name        : {val[1]}\n"
                  f"      Department  : {val[2]}\n"
                  f"      Degree      : {val[3]}\n"
                  f"      Level       : {val[4]}\n")

            current_date = datetime.datetime.now().date().strftime("%m/%d/%y")
            current_day = datetime.datetime.now().date().strftime("%A")
            current_time = datetime.datetime.now().time().strftime("%I:%M %p")

            if current_time.startswith("0"):
                current_time = current_time[1:]

            cursor.execute("SELECT * FROM ClassSchedule WHERE Student_No = ? AND _Day = ?",
                           (stud_no, current_day,))
            sched = cursor.fetchall()

            if sched:
                for sched_now in sched:
                    schedule.append(sched_now)
            else:
                print("No schedule")
                os.system("pause")
                break

            # _log = None
            for index, (stud_no, course, day, time) in enumerate(schedule):
                start_time, end_time = time.split(" - ")

                start_time = convert_to_24hrs(start_time)
                end_time = convert_to_24hrs(end_time)
                time_now = convert_to_24hrs(current_time)

                if end_time <= time_now:
                    # Store the schedule in the attendance log
                    cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                                   "AND _Day = ? AND _Time = ? AND _Date = ?",
                                   (stud_no, course, day, time, current_date))
                    attn_log = cursor.fetchall()
                    if not attn_log:
                        attendance_log.append((stud_no, course, day, time, current_date, "N/A", "ABSENT"))
                        attendance(attendance_log)
                        connection.commit()
                        attendance_log.clear()

                if start_time <= time_now <= end_time:
                    # Searching for current schedule
                    schedule[index] = (stud_no, course, day, time, current_date, current_time)
                    # Store the schedule in the attendance log
                    attendance_log.append(schedule[index])

                    if index + 1 < len(schedule):
                        _next = schedule[index + 1]
                        next_schedule.append(_next)
                    break
            else:
                for index, (stud_no, course, day, time) in enumerate(schedule):
                    next_start_time, next_end_time = time.split(" - ")

                    next_start_time = convert_to_24hrs(next_start_time)
                    time_now = convert_to_24hrs(current_time)

                    if next_start_time >= time_now:
                        schedule[index] = (stud_no, course, day, time)
                        next_schedule.append(schedule[index])
                        next_schedule_found = True
                        break

                if next_schedule_found:
                    print("┌─────────────────────────────────────────────┐".center(90))
                    print(f"│{"NEXT SCHEDULE":^45}│".center(90))
                    print("├─────────────────────────────────────────────┤".center(90))
                    for x in next_schedule:
                        print(f"│ Course Title : {x[1]:<29}│".center(90))
                        print(f"│ Time         : {x[3]:<29}│".center(90))
                        print("└─────────────────────────────────────────────┘\n".center(90))
                else:
                    print("┌───────────────────────────────────────────────────────────────────────┐".center(90))
                    print(f"│{"SCHEDULE TODAY":^71}│".center(90))
                    print("├───────────────────┬───────────────────────┬────────────┬──────────────┤".center(90))
                    print((f"│{"COURSE TITLE":^19}".ljust(19) + f"│{"TIME":^23}".ljust(23) +
                          f"│{"STATUS":^12}".ljust(12) + f"│{"TIME IN":^14}".ljust(14) + "│").center(90))
                    print("├───────────────────┼───────────────────────┼────────────┼──────────────┤"
                          .center(90))
                    for attn, (stud_no, course, day, time) in enumerate(schedule):
                        cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                                       "AND _Day = ? AND _Time = ? AND _Date = ?",
                                       (stud_no, course, day, time, current_date))
                        _attendance = cursor.fetchall()
                        if _attendance:
                            for log in _attendance:
                                print((f"│ {log[1]}".ljust(20) + f"│ {log[3]}".ljust(24) +
                                       f"│{log[6]:^12}".ljust(12) + f"│{log[5]:^14}".ljust(14) + "│").center(90))
                    print("└───────────────────┴───────────────────────┴────────────┴──────────────┘"
                          .center(90))

                while True:
                    user = input_key("      Press[N] to check again or [Y] to Exit: ")
                    match user.upper():
                        case "N":
                            clear(100)
                            check_attendance()
                            break
                        case "Y":
                            exit()
                    clear(1)

            for attn, (stud_no, course, day, time, current_date, current_time) in enumerate(attendance_log):
                cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                               "AND _Day = ? AND _Time = ? AND _Date = ?",
                               (stud_no, course, day, time, current_date))
                _attendance = cursor.fetchall()

                while not _attendance:
                    cursor.execute("SELECT _Signature FROM Student_Info WHERE Student_No = ?", (stud_no,))
                    info = cursor.fetchone()

                    signature = info[0]
                    max_entry = 3
                    for attn_log in attendance_log:
                        print("┌─────────────────────────────────────────────┐".center(90))
                        print(f"│{"SCHEDULE NOW":^45}│".center(90))
                        print("├─────────────────────────────────────────────┤".center(90))
                        print(f"│ Course Title : {attn_log[1]:<29}│".center(90))
                        print(f"│ Time         : {attn_log[3]:<29}│".center(90))
                        print(f"│ Status       : {status:<29}│".center(90))
                        print("├─────────────────────────────────────────────┤".center(90))

                        while max_entry > 0:
                            print("│                                             │".center(90))
                            print("└─────────────────────────────────────────────┘".center(90))
                            print("\033[2F", end="")
                            key_signature = input(f"{"":<21}│ Signature: ")
                            if key_signature == "":
                                clear(1)
                            else:
                                if key_signature == signature:
                                    status = "PRESENT"
                                    break
                                else:
                                    print("\033[3E", end="")
                                    if max_entry > 1:
                                        print(f"{"":<6}MSG: Wrong signature. You have {max_entry - 1} attempt(s) left.")
                                    else:
                                        print(f"{"":<6}MSG: All attempts used. You're marked as ABSENT. ")
                                    print("\033[5F", end="")
                                    max_entry -= 1

                                    if max_entry == 0:
                                        status = "ABSENT"
                                        break

                        attendance_log.clear()
                        current_time = datetime.datetime.now().time().strftime("%I:%M %p")

                        if current_time.startswith("0"):
                            current_time = current_time[1:]

                        attendance_log = [(attn_log[0], attn_log[1], attn_log[2], attn_log[3],
                                           attn_log[4], current_time, status)]

                        attendance(attendance_log)
                        connection.commit()

                        _attendance = attendance_log
                        print("\033[1E", end="")
                        clear(9)
                else:
                    for log in _attendance:
                        print("┌─────────────────────────────────────────────┐".center(90))
                        print(f"│{"SCHEDULE NOW":^45}│".center(90))
                        print("├─────────────────────────────────────────────┤".center(90))
                        print(f"│ Course Title : {log[1]:<29}│".center(90))
                        print(f"│ Time         : {log[3]:<29}│".center(90))
                        print(f"│ Status       : {log[6]:<29}│".center(90))
                        print(f"│ Time In      : {log[5]:<29}│".center(90))
                        print("└─────────────────────────────────────────────┘\n".center(90))

                    if next_schedule:
                        for _schedule in next_schedule:
                            print("┌─────────────────────────────────────────────┐".center(90))
                            print(f"│{"NEXT SCHEDULE":^45}│".center(90))
                            print("├─────────────────────────────────────────────┤".center(90))
                            print(f"│ Course Title : {_schedule[1]:<29}│".center(90))
                            print(f"│ Time         : {_schedule[3]:<29}│".center(90))
                            print("└─────────────────────────────────────────────┘\n".center(90))

                    while True:
                        user = input_key("      Press[N] to check again or [Y] to Exit: ")
                        match user.upper():
                            case "N":
                                clear(100)
                                check_attendance()
                                break
                            case "Y":
                                exit()
                        clear(1)
                    break

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


def convert_to_24hrs(time_str):
    # Convert time string from 12-hour format to minutes
    parts = time_str.split()
    hour, minute = map(int, parts[0].split(':'))
    if parts[1].upper() == 'PM' and hour != 12:
        hour += 12
    return hour * 60 + minute


def check_conflict(schedules, day, time):
    new_start, new_end = map(convert_to_24hrs, time.split(' - '))

    for index, (stud_no, sched_course, sched_day, sched_time) in enumerate(schedules):
        if sched_day != day:
            continue

        start, end = map(convert_to_24hrs, sched_time.split(' - '))
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
