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

student_details = []
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
schedule = []
columns = int


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

# Creating ClassSchedule table and column
cursor.execute("CREATE TABLE IF NOT EXISTS ClassSchedule ("
               "Student_No   TEXT, "
               "_Course      TEXT, "
               "_Day         TEXT, "
               "_Time        TEXT)")

# Creating Attendance table and column
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


def set_window_style():
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


def limit_input(__prompt, __length):
    print(__prompt, end='', flush=True)
    input_str = ""
    cursor_position = 0
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()  # Get a keypress
            if char == b'\r':  # Enter key pressed
                if not input_str:
                    print("\r", end="")
                    print(__prompt, end="", flush=True)
                else:
                    break
            elif char == b'\x08':  # Backspace key pressed
                if len(input_str) == cursor_position > 0:  # For deleting within the maximum text length
                    # Clear the character in input_str
                    input_str = input_str[:cursor_position - 1] + input_str[cursor_position:]
                    # Decrease the cursor position to 1
                    cursor_position -= 1
                    # Clear the display character
                    print('\b \b', end='', flush=True)

                if len(input_str) > cursor_position > 0:  # For deleting between text
                    # Clear the character in input_str
                    input_str = input_str[:cursor_position - 1] + input_str[cursor_position:]
                    # Get the total text to be reprinted
                    chars_to_reprint = len(input_str) - cursor_position
                    # Get the remaining text
                    remaining_text = input_str[cursor_position:] + ' ' * 1
                    # Clearing only the input display
                    print('\r' + __prompt + input_str + ' ' * len(remaining_text) + '\b' *
                          len(remaining_text), end='', flush=True)
                    # Moving the cursor back to it's position
                    print('\033[D' * (chars_to_reprint + 1), end='', flush=True)
                    # Decrease the cursor position to 1
                    cursor_position -= 1

            elif char == b'\xe0':  # Arrow key pressed (Allow user to move the cursor)
                arrow = msvcrt.getch()  # Get the arrow character
                if arrow == b'H':  # Up arrow key
                    pass
                elif arrow == b'P':  # Down arrow key
                    pass
                elif arrow == b'K':  # Left arrow key
                    if cursor_position > 0:
                        print('\033[D', end='', flush=True)
                        cursor_position -= 1
                elif arrow == b'M':  # Right arrow key
                    if len(input_str) > cursor_position >= 0:
                        print('\033[C', end='', flush=True)
                        cursor_position += 1

            elif char == b' ':  # Space key pressed
                if len(input_str) < __length:
                    input_str = input_str[:cursor_position] + ' ' + input_str[cursor_position:]
                    chars_to_reprint = len(input_str) - cursor_position
                    remaining_text = input_str[cursor_position:]  # Get the remaining text after inserting the character
                    print(remaining_text, end='', flush=True)  # Print the character and remaining text
                    print('\033[D' * (chars_to_reprint - 1), end='', flush=True)  # Move cursor forward
                    cursor_position += 1

            elif __length > len(input_str) > cursor_position:  # Allow user to input between text
                # Inserting character between text in input_str
                input_str = input_str[:cursor_position] + char.decode('utf-8') + input_str[cursor_position:]
                chars_to_reprint = len(input_str) - cursor_position
                remaining_text = input_str[cursor_position:]  # Get the remaining text after inserting the character
                print(remaining_text, end='', flush=True)  # Print the character and remaining text
                print('\033[D' * (chars_to_reprint - 1), end='', flush=True)  # Move cursor forward
                cursor_position += 1

            elif cursor_position == len(input_str) < __length:
                input_str += char.decode('utf-8')  # Decode bytes to string
                print(input_str[-1], end='', flush=True)  # Print the character
                cursor_position += 1

    return input_str


def tab_title(title):
    # Get the current date
    current_date = datetime.datetime.now().date().strftime("%B %d, %Y | %A")

    # Get the current time
    current_time = datetime.datetime.now().time().strftime("%I:%M %p")
    print(Text.Color.Foreground.Green, end="")
    print(("╔" + "═" * int(columns - 2) + "╗").center(columns))
    print(("║" + Text.Color.Foreground.Yellow + Text.Style.Bold + f"{title:^{columns-2}}" +
           Text.NONE + Text.Color.Foreground.Green + "║").center(columns + 10))
    print(("║" + Text.Color.Foreground.Light_Cyan + f"{current_date + " " * int(columns - 40) + 
                                                       current_time:^{columns - 2}}"
           + Text.Color.Foreground.Green + "║").center(columns + 10))
    print(Text.Color.Foreground.Green, end="")
    print(("╚" + "═" * int(columns - 2) + "╝").center(columns))
    print(Text.NONE, end="")


def add_student(stud_no, name, department, degree, level, signature):
    cursor.execute("INSERT INTO Student_Info VALUES (?, ?, ?, ?, ?, ?)",
                   (stud_no, name, department, degree, level, signature))


def add_schedule(sched):
    cursor.executemany("INSERT INTO ClassSchedule VALUES (?, ?, ?, ?)", sched)


def attendance(attdnt):
    cursor.executemany("INSERT INTO Attendance VALUES (?, ?, ?, ?, ?, ?, ?)", attdnt)


def student(__usage):
    global student_details
    student_details.clear()
    print("\n" * 9)
    print("╭─────────────────────────────────────────────╮".center(columns))
    print(f"│{"STUDENT":^45}│".center(columns))
    print("├─────────────────────────────────────────────┤".center(columns))
    print("│                                             │".center(columns))
    print("│                                             │".center(columns))
    print("│                                             │".center(columns))
    print("│                                             │".center(columns))
    print("│                                             │".center(columns))
    print("╰─────────────────────────────────────────────╯".center(columns))

    print("\033[4F", end="")
    if __usage == "Modify Schedule" or __usage == "Modify Student Details":
        print("\033[1E", end="")
        print(f"│    {"Signature   :":<41}│".center(columns))
        print("\033[3F", end="")

    while True:
        stud_no = str(limit_input(f"{"":<21}│    Student No. : ", 8))
        if stud_no:
            if __usage == "Modify Schedule" or __usage == "Modify Student Details":
                print("\033[1F", end="")
            else:
                print("\033[2F", end="")
            break
        else:
            print("\r", end="")
            continue

    cursor.execute("SELECT * FROM Student_Info WHERE Student_No = ?", (stud_no,))
    _student = cursor.fetchall()
    if _student:
        student_details = [x for item in _student for x in item[0:6]]
        if not __usage == "Modify Schedule" and not __usage == "Modify Student Details":
            print("\033[10E", end="")
            clear(100)
            return
        elif not __usage == "Modify Student Details" and not __usage == "Modify Schedule":
            print("\033[10E", end="")
            clear(100)
            return
    else:
        print(f"│  {"OPTION:":<43}│".center(columns))
        if __usage == "Modify Schedule" or __usage == "Modify Student Details":
            print(f"│    {"[1] Check Attendance":<41}│".center(columns))
            print(f"│    {"[2] Register New Student":<41}│".center(columns))
            if __usage == "Modify Schedule":
                print(f"│    {"[3] Modify Student Details":<41}│".center(columns))
            elif __usage == "Modify Student Details":
                print(f"│    {"[3] Modify Schedule":<41}│".center(columns))
            print(f"│    {"[4] Modify Again":<41}│".center(columns))
        else:
            print(f"│    {"[1] Check Again":<41}│".center(columns))
            print(f"│    {"[2] Register New Student":<41}│".center(columns))
            print(f"│    {"[3] Modify Class Schedule":<41}│".center(columns))
            print(f"│    {"[4] Modify Student Details":<41}│".center(columns))
        print(f"│    {"[0] Exit":<41}│".center(columns))
        print(f"│{"":<45}│".center(columns))
        print(f"│{"":<45}│".center(columns))
        print(f"╰{"─" * 45}╯".center(columns))
        print(f"MSG: Student currently not enrolled!!!".center(columns))
        print("\033[3F", end="")

        while True:
            choice = input_key(f"{"":<21}│  Choice: ")
            match choice:
                case "1":
                    print("\033[3E", end="")
                    clear(100)
                    check_attendance()
                case "2":
                    print("\033[3E", end="")
                    clear(100)
                    register_new_student()
                case "3":
                    print("\033[3E", end="")
                    clear(100)
                    if __usage == "Modify Schedule":
                        modify_student_details()
                    elif __usage == "Modify Student Details":
                        modify_schedule()
                    else:
                        modify_schedule()
                case "4":
                    print("\033[3E", end="")
                    clear(100)
                    if __usage == "Modify Schedule":
                        modify_schedule()
                    if __usage == "Modify Student Details":
                        modify_student_details()
                    else:
                        modify_student_details()
                case "0":
                    exit()
                case _:
                    print("\033[1F", end="")
                    continue
            break

    print("\033[3E", end="")
    while True:
        print(f"│{"":^45}│".center(columns))
        print("\033[1F", end="")
        key_signature = str(limit_input(f"{"":<21}│    Signature   : ", 25))
        if key_signature == student_details[5]:
            print("\033[10E", end="")
            clear(100)
            return
        else:
            print("\033[3E", end="")
            print("MSG: Wrong signature.Try again".center(columns))
            print("\033[3F", end="")
            clear(1)
            continue


def _details(_student):
    stud_name = _student[1]
    stud_department = _student[2]
    stud_degree = _student[3]
    stud_level = _student[4]

    print(f"┆  {Text.Style.Underline + "Student Details:" + Text.NONE:<92}┆".center(98))
    print(f"┆{"":<86}┆".center(columns))
    print(f"┆    Name        : {stud_name:<68}┆".center(columns))
    print(f"┆    Department  : {stud_department:<68}┆".center(columns))
    print(f"┆    Degree      : {stud_degree:<68}┆".center(columns))
    print(f"┆    Level       : {stud_level:<68}┆".center(columns))
    print(f"┆{"":<86}┆".center(columns))
    print((f"└" + "–" * 86 + "┘").center(columns))


def check_attendance():
    attendance_log = []
    next_schedule = []
    status = "PENDING"
    today_next_schedule_found = False
    schedule.clear()

    tab_title("CHECK ATTENDANCE")

    student("Check Attendance")

    tab_title("CHECK ATTENDANCE")

    stud_no = student_details[0]
    stud_signature = student_details[5]

    _details(student_details)

    # Getting current date and time
    current_date = datetime.datetime.now().date().strftime("%m/%d/%y")
    current_day = datetime.datetime.now().date().strftime("%A")
    current_time = datetime.datetime.now().time().strftime("%I:%M %p")

    if current_time.startswith("0"):
        current_time = current_time[1:]

    # Searching for today class schedule in class schedule database
    cursor.execute("SELECT * FROM ClassSchedule WHERE Student_No = ? AND _Day = ?",
                   (stud_no, current_day,))
    schedule.extend(cursor.fetchall())  # Store all search class schedule

    # Checking for current schedule
    for index, (stud_no, course, day, time) in enumerate(schedule):
        start_time, end_time = time.split(" - ")

        start_time = convert_to_24hrs(start_time)
        end_time = convert_to_24hrs(end_time)
        time_now = convert_to_24hrs(current_time)

        # if the current time already skip the schedule time, the status will be marked as absent.
        if end_time <= time_now:
            # Searching for skip schedule
            cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                           "AND _Day = ? AND _Time = ? AND _Date = ?",
                           (stud_no, course, day, time, current_date))
            attn_log = cursor.fetchall()  # Store the search schedule
            if not attn_log:
                # Store the schedule to attendance log
                attendance_log.append((stud_no, course, day, time, current_date, "N/A", "ABSENT"))
                attendance(attendance_log)
                connection.commit()
                attendance_log.clear()

        if start_time <= time_now <= end_time:  # Searching for current schedule
            _schedule = (stud_no, course, day, time, current_date, current_time)
            # Store the current schedule to attendance log
            attendance_log.append(_schedule)

            # Checking for next schedule
            if index + 1 < len(schedule):
                _next = schedule[index + 1]
                next_schedule.append(_next)
                today_next_schedule_found = True
            break

    # Checking now for attendance
    _attendance = []
    for attn, (stud_no, course, day, time, current_date, current_time) in enumerate(attendance_log):
        # Searching for current attendance in attendance
        cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                       "AND _Day = ? AND _Time = ? AND _Date = ?",
                       (stud_no, course, day, time, current_date))
        _attendance = cursor.fetchall()  # Store all search schedule

        # If it is not already signed, it will ask user to input their signature.
        while not _attendance:
            max_entry = 3  # Allow user to input only 3 attempts for their signature.
            for attn_log in attendance_log:
                print("┌─────────────────────────────────────────────┐".center(columns))
                print(f"│{"SCHEDULE NOW":^45}│".center(columns))
                print("├─────────────────────────────────────────────┤".center(columns))
                print(f"│ Course Title : {attn_log[1]:<29}│".center(columns))
                print(f"│ Time         : {attn_log[3]:<29}│".center(columns))
                print(f"│ Status       : {status:<29}│".center(columns))
                print("├─────────────────────────────────────────────┤".center(columns))

                # If user reach all attempts their attendance will be marked as absent
                while max_entry > 0:
                    print("│                                             │".center(columns))
                    print("└─────────────────────────────────────────────┘".center(columns))
                    print("\033[2F", end="")
                    key_signature = str(limit_input(f"{"":<21}│ Signature: ", 25))
                    if key_signature == "":
                        print("\r")
                    else:
                        if key_signature == stud_signature:
                            break
                        else:
                            print("\033[3E", end="")
                            if max_entry > 2:
                                print(f"{"":<21}MSG: Wrong signature. You have {max_entry - 1} attempt(s) left.")
                                print("\033[2F", end="")
                                clear(1)
                                print("\033[1F", end="")
                            else:
                                print(f"{"":<21}MSG: Wrong signature. You have {max_entry - 1} attempt(s) left.")
                                print(f"{"":<21}     Otherwise, You will be marked as ABSENT. ")
                                print("\033[3F", end="")
                                clear(1)
                                print("\033[1F", end="")
                            max_entry -= 1

                # Preparing for queuing the attendance
                attendance_log.clear()

                # Splitting and converting time into real number
                current_time = datetime.datetime.now().time().strftime("%I:%M %p")
                start_time, end_time = map(convert_to_24hrs, attn_log[3].split(" - "))
                time_now = convert_to_24hrs(current_time)

                # Condition for Present, Absent, and Late
                if max_entry == 0:
                    status = "ABSENT"
                elif 5 <= (time_now - start_time) <= 15:
                    status = "LATE"
                elif (time_now - start_time) > 15:
                    status = "ABSENT"
                else:
                    status = "PRESENT"

                # Removing the starting 0 in hour
                if current_time.startswith("0"):
                    current_time = current_time[1:]

                # Storing for now in attendance_log variable as array
                attendance_log = [(attn_log[0], attn_log[1], attn_log[2], attn_log[3],
                                   attn_log[4], current_time, status)]

                # Committing or saving the attendance to database
                attendance(attendance_log)
                connection.commit()

                # Storing attendance log to _attendance variable for using it to display
                _attendance = attendance_log

                # Clearing and updating console display
                if max_entry == 0:
                    print("\033[2E", end="")
                    clear(9)
                else:
                    print("\033[2E", end="")
                    clear(9)

                print("\033[f", end="")
                tab_title("CHECK ATTENDANCE")
                print("\033[8E", end="")

    # Searching again for next
    if not today_next_schedule_found:
        for index, (stud_no, course, day, time) in enumerate(schedule):
            next_start_time, next_end_time = time.split(" - ")

            next_start_time = convert_to_24hrs(next_start_time)
            time_now = convert_to_24hrs(current_time)

            if next_start_time >= time_now:
                schedule[index] = (stud_no, course, day, time)
                next_schedule.append(schedule[index])
                today_next_schedule_found = True
                break

    # Displaying attendance and next schedule if next schedule found
    if today_next_schedule_found:
        print("┌─────────────────────────────────────────────┐".center(columns))
        print(f"│{"SCHEDULE NOW":^45}│".center(columns))
        print("├─────────────────────────────────────────────┤".center(columns))
        if _attendance:
            for log in _attendance:
                print(f"│ Course Title : {log[1]:<29}│".center(columns))
                print(f"│ Time         : {log[3]:<29}│".center(columns))
                print(f"│ Status       : {log[6]:<29}│".center(columns))
                print(f"│ Time In      : {log[5]:<29}│".center(columns))
        else:
            print(f"│{"NO SCHEDULE":^45}│".center(columns))
        print("└─────────────────────────────────────────────┘\n".center(columns))

        print("┌─────────────────────────────────────────────┐".center(columns))
        print(f"│{"NEXT SCHEDULE":^45}│".center(columns))
        print("├─────────────────────────────────────────────┤".center(columns))
        for x in next_schedule:
            print(f"│ Course Title : {x[1]:<29}│".center(columns))
            print(f"│ Time         : {x[3]:<29}│".center(columns))
            print("└─────────────────────────────────────────────┘".center(columns))
    else:  # Else if there's no next schedule found. It will display all schedules within the day.
        # If it has schedule today
        if not attendance_log:
            print("┌───────────────────────────────────────────────────────────────────────┐".center(columns))
            print(f"│{"SCHEDULE TODAY":^71}│".center(columns))
            print("├───────────────────┬───────────────────────┬────────────┬──────────────┤".center(columns))
            print((f"│{"COURSE TITLE":^19}".ljust(19) + f"│{"TIME":^23}".ljust(23) +
                   f"│{"STATUS":^12}".ljust(12) + f"│{"TIME IN":^14}".ljust(14) + "│").center(columns))
            if schedule:
                print("├───────────────────┼───────────────────────┼────────────┼──────────────┤"
                      .center(columns))
                for attn, (stud_no, course, day, time) in enumerate(schedule):
                    # Searching for all attendance in attendance database
                    cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                                   "AND _Day = ? AND _Time = ? AND _Date = ?",
                                   (stud_no, course, day, time, current_date))
                    _attendance = cursor.fetchall()  # Store all search schedule
                    if _attendance:
                        for log in _attendance:
                            print((f"│ {log[1]}".ljust(20) + f"│ {log[3]}".ljust(24) +
                                   f"│{log[6]:^12}".ljust(12) + f"│{log[5]:^14}".ljust(14) + "│").center(columns))
                print("└───────────────────┴───────────────────────┴────────────┴──────────────┘"
                      .center(columns))
            else:
                print("├───────────────────┴───────────────────────┴────────────┴──────────────┤".center(columns))
                print(f"│{"No Schedule":^71}│".center(columns))
                print("└───────────────────────────────────────────────────────────────────────┘".center(columns))

        next_day = (days.index(current_day) + 1) % len(days)
        next_day = days[next_day]

        # Searching for next day schedule in class schedule database
        cursor.execute("SELECT * FROM ClassSchedule WHERE Student_No = ? AND _Day = ?",
                       (stud_no, next_day,))
        next_day_sched = cursor.fetchall()  # Store all search schedule

        # If it has next day schedule it will display all schedules.
        print("┌─────────────────────────────────────────────┐".center(columns))
        print(f"│{"NEXT SCHEDULE " + f"[{next_day.upper()}]":^45}│".center(columns))
        print("├─────────────────────────────────────────────┤".center(columns))
        if next_day_sched:
            for idx, sched in enumerate(next_day_sched):
                print(f"│  Course Title : {sched[1]:<28}│".center(columns))
                print(f"│  Time         : {sched[3]:<28}│".center(columns))
                if idx < len(next_day_sched) - 1:
                    print(f"│{"-" * 40:^45}│".center(columns))
        else:
            print(f"│{"No Schedule":^45}│".center(columns))
        print("└─────────────────────────────────────────────┘".center(columns))

    print("\n\n")
    print(("-" * 80).center(columns))
    while True:
        user = input_key("      Press [N] to check again or [Y] to exit: ")
        match user.upper():
            case "N":
                clear(100)
                check_attendance()
                break
            case "Y":
                exit()
            case _:
                print("\033[1F", end="")


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

    if parts[1].upper() == 'PM':  # PM Case
        if hour != 12:
            hour += 12
    else:  # AM case
        if hour == 12:
            hour = 0
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
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("╰" + "─" * 40 + "╯").center(columns))
    print("\033[7F", end="")
    print(f"{"":<24}│ ► {sched_day}")
    print("\033[2E", end="")
    while True:
        try:
            total_course = int(input_key(f"{"":<24}│     Total course MAX(6): "))
            if total_course <= 6:
                print("\033[3E", end="")
                clear(4)
                print(("│" + " " * 40 + "│").center(columns))
                break
            else:
                print("\r", end="")
                print("\033[1F", end="")
        except ValueError:
            print("\r", end="")
            print("\033[1F", end="")

    print("\033[5F")
    print(f"{"":<24}│ ► {sched_day} [{total_course}]")

    num = 0
    while num < total_course:
        print(f"│{"-" * 36:^40}│".center(columns))
        print(f"│{"   Course Title :":<40}│".center(columns))
        print(f"│{"   Time         :":<40}│".center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("╰" + "─" * 40 + "╯").center(columns))

        print("\033[4F", end="")
        sched_course = str(limit_input(f"{"":<24}│   Course Title : ", 19))
        print("\033[1E", end="")
        while True:
            print(("│" + " " * 40 + "│").center(columns))
            print(("│" + " " * 40 + "│").center(columns))
            print(("╰" + "─" * 40 + "╯").center(columns))
            print("\033[3F", end="")

            sched_time = str(limit_input(f"{"":<24}│   Time         : ", 19).upper())
            if validate_time_format(sched_time):
                start, end = map(convert_to_24hrs, sched_time.split(' - '))
                if (end - start) > 0:
                    break
                else:
                    print("\033[3E", end="")
                    msg = input_key(f"{"":<24}MSG: Wrong time schedule. ")
                    if msg:
                        clear(4)
            else:
                print("\033[3E", end="")
                msg = input_key(f"{"":<19}MSG: Invalid time format.\n"
                                f"{"":<19}     Please follow the format: 10:00 AM - 12:00 PM ")
                if msg:
                    clear(5)

        conflict = check_conflict(schedule, sched_day, sched_time)
        if conflict is None:
            schedule.append((stud_no, sched_course, sched_day, sched_time))
            num += 1
            print("\033[1E", end="")
        else:
            print("\033[3E", end="")
            msg = input_key(f"{"":<24}MSG: conflict schedule with {conflict.upper()}. ")
            if msg:
                clear(6)

    print("\033[2E", end="")
    clear((3 * num) + 3)


def register_new_student():
    tab_title("REGISTER NEW STUDENT")
    global student_details
    global schedule
    global columns
    print(("╭" + "─" * 84 + "╮").center(columns))
    print(f"│{"STUDENT DETAILS:":^84}│".center(columns))
    print(("├" + "─" * 84 + "┤").center(columns))
    print(("│" + " " * 84 + "│").center(columns))
    print(f"│  {"Student No.: ":<82}│".center(columns))
    print(f"│  {"Name       : ":<82}│".center(columns))
    print(f"│  {"Department : ":<82}│".center(columns))
    print(f"│  {"Degree     : ":<82}│".center(columns))
    print(f"│  {"Year Level : ":<82}│".center(columns))
    print(f"│  {"Signature  : ":<82}│".center(columns))
    print(("│" + " " * 84 + "│").center(columns))
    print(("╰" + "─" * 84 + "╯").center(columns))

    print("\033[8F", end="")
    while True:
        stud_no = str(limit_input(f"  │  Student No.: ", 8))
        if not stud_no:
            print("\r", end="")
            continue
        else:
            break

    cursor.execute(f"SELECT Student_No FROM Student_Info WHERE Student_No = ?", (stud_no,))
    data = cursor.fetchone()

    days_of_week = None
    if not data:
        print("\033[1E", end="")
        stud_name = str(limit_input(f"  │  Name       : ", 67))
        print("\033[1E", end="")
        stud_department = str(limit_input(f"  │  Department : ", 67))
        print("\033[1E", end="")
        stud_degree = str(limit_input(f"  │  Degree     : ", 67))
        print("\033[1E", end="")
        stud_level = str(limit_input(f"  │  Year Level : ", 67))
        print("\033[1E", end="")
        stud_signature = str(limit_input(f"  │  Signature  : ", 25))

        print("\033[3E", end="")
        print(("╭" + "─" * 40 + "╮").center(columns))
        print(f"│{"CLASS SCHEDULE:":^40}│".center(columns))
        print(("├" + "─" * 40 + "┤").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("╰" + "─" * 40 + "╯").center(columns))

        print("\033[7F", end="")
        print(f"{"":<24}│  Option:")
        print(f"{"":<24}│     [1] Weekdays only")
        print(f"{"":<24}│     [2] Include weekends")
        print(f"{"":<24}│     [0] Return to Home\n")

        while True:
            choice1 = input_key(f"{"":<24}│  Choice: ")
            match choice1:
                case "0":
                    clear(100)
                    student("Check Attendance")
                case "1":
                    clear(8)
                    days_of_week = "Weekdays only"
                    print(f"│{f"CLASS SCHEDULE [{days_of_week}]":^40}│".center(columns))
                case "2":
                    clear(8)
                    days_of_week = "Include weekends"
                    print(f"│{f"CLASS SCHEDULE [{days_of_week}]":^40}│".center(columns))
                case _:
                    print("\033[1F", end="")
                    print("\r", end="")
                    continue
            break

        print(("├" + "─" * 40 + "┤").center(columns), end="")
        print("\033[1E", end="")
        while True:
            if days_of_week == "Weekdays only":
                for day in days[:5]:
                    add_course(stud_no, day)
                break
            if days_of_week == "Include weekends":
                for day in days:
                    add_course(stud_no, day)
                break

        schedule1 = sorted(schedule, key=sort_time)
        stud = [stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature]

        max_count = 0
        if schedule1:
            day_counts = {}  # Dictionary to store counts of schedules for each day

            for entry in schedule1:
                day = entry[2]  # Get the day from the entry
                if day in day_counts:
                    day_counts[day] += 1  # Increment the count for this day
                else:
                    day_counts[day] = 1  # Initialize the count for this day

            # Find the day with the maximum count of schedules
            max_day = max(day_counts, key=day_counts.get)
            max_count = day_counts[max_day]

        if max_count == 6:
            os.system(f"mode con cols={120} lines={53}")
        else:
            os.system(f"mode con cols={120} lines={45}")

        center_console_window()
        columns = os.get_terminal_size().columns
        clear(100)
        tab_title("REGISTER NEW STUDENT")
        print(("╭" + "─" * 84 + "╮").center(columns))
        print(f"│{"STUDENT DETAILS:":^84}│".center(columns))
        print(("├" + "─" * 84 + "┤").center(columns))
        print(("│" + " " * 84 + "│").center(columns))
        print(f"│  Student No.: {stud[0]:<69}│".center(columns))
        print(f"│  Name       : {stud[1]:<69}│".center(columns))
        print(f"│  Department : {stud[2]:<69}│".center(columns))
        print(f"│  Degree     : {stud[3]:<69}│".center(columns))
        print(f"│  Year Level : {stud[4]:<69}│".center(columns))
        print(f"│  Signature  : {stud[5]:<69}│".center(columns))
        print(("│" + " " * 84 + "│").center(columns))
        print(("╰" + "─" * 84 + "╯").center(columns))

        class_schedule(schedule1)
        if schedule1:
            print("\n")
            print(("-" * int(columns - 4)).center(columns))
            print(f"[S] Modify Schedule{"":<26}[D] Modify Student Details\n".center(columns))
            while True:
                option = input_key(f"{"":<5}Are you sure you want to save? Press [Y] to save. ")
                match option.upper():
                    case "S":
                        modify_schedule()
                    case "D":
                        modify_schedule()
                    case "Y":
                        # add_student(stud[0], stud[1], stud[2], stud[3], stud[4], stud[5])
                        # add_schedule(schedule1)
                        # connection.commit()
                        break
                    case _:
                        clear(1)

            os.system(f"mode con cols={90} lines={45}")
            center_console_window()
            columns = os.get_terminal_size().columns
            clear(100)
            print("\033[23E", end="")
            print("MSG: Student successfully registered".center(columns))
            print("\033[f", end="")
            student_details.clear()
            schedule.clear()
            check_attendance()

        else:
            print(f"{"":5}NOTE: We see that there's no schedule.\n")
            print(("-" * int(columns - 4)).center(columns))
            print(f"[S] Modify Schedule{"":<26}[D] Modify Student Details\n".center(columns))
            while True:
                option = input_key(f"{"":<5}Press [N] to register again. ")
                match option.upper():
                    case "S":
                        modify_schedule()
                    case "D":
                        modify_student_details()
                    case "N":
                        clear(100)
                        os.system(f"mode con cols={90} lines={45}")
                        center_console_window()
                        columns = os.get_terminal_size().columns
                        register_new_student()
                    case _:
                        clear(1)

    else:
        print("\033[8E", end="")
        print("  MSG: Student already registered.")
        print("\033[10F", end="")
        print(f"│  {"OPTION:":<82}│".center(columns))
        print(f"│  {"   [1] Check Attendance":<82}│".center(columns))
        print(f"│  {"   [2] Modify Schedule":<82}│".center(columns))
        print(f"│  {"   [3] Modify Student Details":<82}│".center(columns))
        print(f"│  {"   [4] Register Again":<82}│".center(columns))
        print(f"│  {"   [0] Exit":<82}│".center(columns))
        print(("│" + " " * 84 + "│").center(columns))
        while True:
            key = input_key(f"  │  Choice: ")
            match key.upper():
                case "1":
                    print("\033[5E", end="")
                    clear(100)
                    check_attendance()
                case "2":
                    print("\033[5E", end="")
                    clear(100)
                    modify_schedule()
                case "3":
                    print("\033[5E", end="")
                    clear(100)
                    modify_student_details()
                case "4":
                    print("\033[5E", end="")
                    clear(100)
                    register_new_student()
                case "0":
                    exit()
                case _:
                    print("\033[1F", end="")
                    continue
            break


def sort_time(schedule_item):
    day_str, time_str = schedule_item[2], schedule_item[3]
    return datetime.datetime.strptime(day_str + " " + time_str.split(" - ")[0], "%A %I:%M %p")


def class_schedule(__schedule):
    # Group schedules by day
    day_schedules = {}
    # Display the table header
    print(("╭" + "─" * 111 + "╮").center(columns))
    print(f"│{"CLASS SCHEDULE":^111}│".center(columns))
    print(
        f"├{"─" * 15:^15}┬{"─" * 15:^15}┬{"─" * 15:^15}┬{"─" * 15:^15}┬{"─" * 15:^15}┬{"─" * 15:^15}┬{"─" * 15:^15}┤"
        .center(columns))
    print(
        f"│{"MONDAY":^15}│{"TUESDAY":^15}│{"WEDNESDAY":^15}│{"THURSDAY":^15}│{"FRIDAY":^15}│{"SATURDAY":^15}│"
        f"{"SUNDAY":^15}│".center(columns))
    print(
        f"├{"─" * 15:^15}┼{"─" * 15:^15}┼{"─" * 15:^15}┼{"─" * 15:^15}┼{"─" * 15:^15}┼{"─" * 15:^15}┼{"─" * 15:^15}┤"
        .center(columns))

    if __schedule:
        for entry in __schedule:
            day = entry[2]
            if day not in day_schedules:
                day_schedules[day] = []
            day_schedules[day].append((entry[1], entry[3]))

        # Get the maximum number of schedules for any day
        max_schedules = max(len(schedules) for schedules in day_schedules.values())

        # Display the schedules
        for i in range(max_schedules):
            day_schedule = []
            for day in days:
                if day in day_schedules and len(day_schedules[day]) > i:
                    course, time = day_schedules[day][i]
                    start, end = time.split(" - ")
                    day_schedule.append((course, start, end))
                else:
                    day_schedule.append(("", "", ""))
            print(f"│{day_schedule[0][0]:^15}│{day_schedule[1][0]:^15}│{day_schedule[2][0]:^15}"
                  f"│{day_schedule[3][0]:^15}│{day_schedule[4][0]:^15}│{day_schedule[5][0]:^15}"
                  f"│{day_schedule[6][0]:^15}│".center(columns))
            print(f"│{day_schedule[0][1]:^15}│{day_schedule[1][1]:^15}│{day_schedule[2][1]:^15}"
                  f"│{day_schedule[3][1]:^15}│{day_schedule[4][1]:^15}│{day_schedule[5][1]:^15}"
                  f"│{day_schedule[6][1]:^15}│".center(columns))
            print(f"│{day_schedule[0][2]:^15}│{day_schedule[1][2]:^15}│{day_schedule[2][2]:^15}"
                  f"│{day_schedule[3][2]:^15}│{day_schedule[4][2]:^15}│{day_schedule[5][2]:^15}"
                  f"│{day_schedule[6][2]:^15}│".center(columns))
            if i < max_schedules - 1:
                print(
                    f"│{"-" * 15:^15}│{"-" * 15:^15}│{"-" * 15:^15}│{"-" * 15:^15}│{"-" * 15:^15}│{"-" * 15:^15}│"
                    f"{"-" * 15:^15}│".center(columns))
    else:
        print(f"│{"":^15}│{"":^15}│{"":^15}│{"":^15}│{"":^15}│{"":^15}│{"":^15}│".center(columns))
    print(
        f"╰{"─" * 15:^15}┴{"─" * 15:^15}┴{"─" * 15:^15}┴{"─" * 15:^15}┴{"─" * 15:^15}┴{"─" * 15:^15}┴{"─" * 15:^15}╯"
        .center(columns))


def modify_student_details():
    tab_title("MODIFY STUDENT DETAILS")

    student("Modify Student Details")

    tab_title("MODIFY STUDENT DETAILS")

    msg = input_key("Currently not available... ")
    if msg:
        clear(100)
        check_attendance()


def modify_schedule():
    tab_title("MODIFY SCHEDULE")

    student("Modify Schedule")

    tab_title("MODIFY SCHEDULE")

    msg = input_key("Currently not available... ")
    if msg:
        clear(100)
        check_attendance()


if __name__ == "__main__":
    run_as_administrator()
    set_console_title("Student Attendance Management System")
    set_window_style()
    set_console_size(90, 45)
    columns = os.get_terminal_size().columns
    center_console_window()
    check_attendance()
