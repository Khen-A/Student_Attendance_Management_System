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

# Initialize variable
student_details = []
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
days_of_week = ""
schedule = []
new_schedule = []
current_str = ""
data = ""
columns = int
in_register_new_student = False
in_update_student_details = False
registering_new_student = False
updating_student_details = False
updating_class_schedule = False


# Class Text Style and Color
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


# Function for requesting administration
def run_as_administrator():
    # Checking current console if not running as administrator
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, os.path.basename(__file__), None, 1)
        sys.exit()


# Function for aligning console to center windows
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


# Function for assigning console title
def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


# Function for resizing console
def set_console_size(width: int, height: int):
    os.system(f"mode con cols={width} lines={height}")


# Function for not allowing user to resize and maximizing the console
def set_window_style():
    # Define necessary constants
    gwl_style = -16
    ws_sizebox = 0x00040000
    ws_maximizebox = 0x00010000

    # Get handle to the console window
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()

    # update the window style to remove the sizing border
    if hwnd != 0:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, gwl_style)
        style &= ~ws_sizebox
        style &= ~ws_maximizebox
        ctypes.windll.user32.SetWindowLongW(hwnd, gwl_style, style)


# Function for clearing/deleting a line
def clear(line):
    for _ in range(line):
        print("\x1b[1A\x1b[2K", end="\r")


# Function for key-pressed
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


# Function for limiting user input
def limit_input(_prompt: str, _length: int):
    # Current_str is the current input of the user. This will be used to update the class schedule and student details.
    global current_str
    print(_prompt, end='', flush=True)  # Print the prompt without a newline
    input_str = current_str
    print(input_str, end='', flush=True)
    cursor_position = len(input_str)
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()  # Get a keypress
            if char == b'\r':  # Enter key pressed
                if input_str:
                    break
            elif char == b'\x08':  # Backspace key pressed
                if len(input_str) == cursor_position > 0:  # For deleting within the maximum text length
                    input_str = input_str[:cursor_position - 1] + input_str[cursor_position:]
                    cursor_position -= 1
                    print('\b \b', end='', flush=True)

                if len(input_str) > cursor_position > 0:  # For deleting between text
                    total_input_str = len(input_str)
                    input_str = input_str[:cursor_position - 1] + input_str[cursor_position:]
                    chars_to_reprint = len(input_str) - cursor_position
                    print('\033[C' * (chars_to_reprint + 1) + '\b \b' * total_input_str + input_str, end='', flush=True)
                    print('\033[D' * (chars_to_reprint + 2) + '\033[C', end='', flush=True)
                    cursor_position -= 1

            elif char == b'\xe0':  # Arrow key pressed (Allow user to move the cursor)
                arrow = msvcrt.getch()  # Get the arrow character
                if arrow == b'H':  # Up arrow key
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
                if len(input_str) < _length:
                    input_str = input_str[:cursor_position] + ' ' + input_str[cursor_position:]
                    chars_to_reprint = len(input_str) - cursor_position
                    remaining_text = input_str[cursor_position:]
                    print(remaining_text, end='', flush=True)
                    print('\033[D' * (chars_to_reprint - 1), end='', flush=True)
                    cursor_position += 1

            elif char == b'\t':  # Disable tab key
                pass

            elif char == b'\x00':  # Num-Lock is off
                next_char = msvcrt.getch()
                if next_char:
                    pass

            elif char.isalpha() or char.isalnum() or char.isascii():
                if _length > len(input_str) > cursor_position:  # Allow user to input between text
                    input_str = input_str[:cursor_position] + char.decode('utf-8') + input_str[cursor_position:]
                    chars_to_reprint = len(input_str) - cursor_position
                    remaining_text = input_str[cursor_position:]
                    print(remaining_text, end='', flush=True)
                    print('\033[D' * (chars_to_reprint - 1), end='', flush=True)
                    cursor_position += 1
                elif cursor_position == len(input_str) < _length:
                    input_str += char.decode('utf-8')
                    print(input_str[-1], end='', flush=True)
                    cursor_position += 1
    return input_str


# Function for allowing the user to input only integers and allowing them to decide what numbers should be pressed
def int_input(_prompt: str, _range: int):
    print(_prompt, end='', flush=True)  # Print the prompt without a newline
    input_str = ""
    cursor_position = len(input_str)
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()  # Get a keypress
            if char == b'\r':  # Enter key pressed
                if input_str:
                    break

            elif char == b'\x08':  # Backspace key pressed
                if len(input_str) == cursor_position > 0:
                    input_str = input_str[:cursor_position - 1] + input_str[cursor_position:]
                    cursor_position -= 1
                    print('\b \b', end='', flush=True)

            elif char == b'\xe0':  # Disable arrow key
                arrow = msvcrt.getch()
                if arrow:
                    pass

            elif char == b' ' or char == b'\t':  # Disable space and tab key
                pass

            elif char == b'\x00':  # Num-Lock is off
                next_char = msvcrt.getch()
                if next_char:
                    pass

            elif char.isalpha() or char.isascii() and not char.isalnum():  # Disable all letters and symbols
                pass

            elif char.isalnum():  # Numbers key
                if char.decode('utf-8') in input_str:
                    pass
                else:
                    if char.decode('utf-8') in map(str, range(1, _range + 1)):
                        input_str += char.decode('utf-8')  # Decode bytes to string
                        print(input_str[-1], end='', flush=True)  # Print the character
                        cursor_position += 1
    return input_str


# Function tab header and title
def tab_title(title):
    current_date = datetime.datetime.now().date().strftime("%B %d, %Y | %A")  # Get the current date
    current_time = datetime.datetime.now().time().strftime("%I:%M %p")  # Get the current time

    # Display tab header and title
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


# Function for queuing new student details
def add_student(_student):
    cursor.execute("INSERT INTO Student_Info VALUES (?, ?, ?, ?, ?, ?)", _student)


# Function for queuing new class schedule
def add_schedule(_schedule):
    cursor.executemany("INSERT INTO ClassSchedule VALUES (?, ?, ?, ?)", _schedule)


# Function for queuing update student details
def update_student(_student):
    cursor.execute("UPDATE Student_Info SET _Name = ?, _Department = ?, _Degree = ?, _Level = ?, _Signature = ? "
                   "WHERE Student_No = ?", _student[1:] + [_student[0]])


# Function for queuing attendance
def attendance(_attendance):
    cursor.executemany("INSERT INTO Attendance VALUES (?, ?, ?, ?, ?, ?, ?)", _attendance)


# Function for getting student details
def student(__usage):
    global student_details
    global in_register_new_student
    global in_update_student_details
    student_details.clear()

    # Login display design
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
    if __usage == "Update Schedule" or __usage == "Update Student Details":
        print("\033[1E", end="")
        print(f"│    {"Signature   :":<41}│".center(columns))
        print("\033[3F", end="")

    while True:  # Validate student_no input
        stud_no = str(limit_input(f"{"":<21}│    Student No. : ", 8))
        if stud_no:
            if __usage == "Update Schedule" or __usage == "Update Student Details":
                print("\033[1F", end="")
            else:
                print("\033[2F", end="")
            break
        else:
            print("\r", end="")
            continue

    cursor.execute("SELECT * FROM Student_Info WHERE Student_No = ?", (stud_no,))  # Searching for student
    _student = cursor.fetchall()  # Saving temporarily the search student details
    if _student:  # Checking if student exist
        student_details = [x for item in _student for x in item[0:6]]  # Saving student details as array
        if not __usage == "Update Schedule" and not __usage == "Update Student Details":
            print("\033[10E", end="")
            clear(100)
            return
    else:  # if student not exist
        # Option display design
        print(f"│  {"OPTION:":<43}│".center(columns))
        print(f"│    {"[1] Home":<41}│".center(columns))
        print(f"│    {"[2] Register New Student":<41}│".center(columns))
        print(f"│    {"[3] Update Class Schedule":<41}│".center(columns))
        print(f"│    {"[4] Update Student Details":<41}│".center(columns))
        print(f"│{"":<45}│".center(columns))
        print(f"│{"":<45}│".center(columns))
        print(f"│{"":<45}│".center(columns))
        print(f"╰{"─" * 45}╯".center(columns))
        print(f"MSG: Student currently not enrolled!!!".center(columns))
        print("\033[3F", end="")

        while True:  # Validate key_pressed
            key_pressed = input_key(f"{"":<21}│  Select: ")
            match key_pressed:
                case "1":
                    print("\033[3E", end="")
                    clear(100)
                    check_attendance()
                case "2":
                    print("\033[3E", end="")
                    clear(100)
                    in_register_new_student = True
                    register_new_student()
                case "3":
                    print("\033[3E", end="")
                    clear(100)
                    update_schedule()
                case "4":
                    print("\033[3E", end="")
                    clear(100)
                    in_update_student_details = True
                    update_student_details()
                case _:
                    print("\033[1F", end="")
                    continue
            break

    print("\033[3E", end="")
    while True:  # Validate signature
        print(f"│{"":^45}│".center(columns))
        print("\033[1F", end="")
        key_signature = str(limit_input(f"{"":<21}│    Signature   : ", 25))
        if key_signature == student_details[5]:
            print("\033[10E", end="")
            clear(100)
            return
        else:
            print("\033[3E", end="")
            print("MSG: Wrong signature. Please try again. ".center(columns))
            print("\033[3F", end="")
            clear(1)
            continue


# Function for displaying student details
def _details(_student):
    # Checking if user not updating student details and not register new student
    if updating_student_details or in_update_student_details or registering_new_student or in_register_new_student:
        print(("╭" + "─" * 84 + "╮").center(columns))
        print(f"│{"STUDENT DETAILS:":^84}│".center(columns))
        print(("├" + "─" * 84 + "┤").center(columns))
        print(("│" + " " * 84 + "│").center(columns))
        print(f"│  Student No.: {_student[0]:<69}│".center(columns))
        print(f"│  Name       : {_student[1]:<69}│".center(columns))
        print(f"│  Department : {_student[2]:<69}│".center(columns))
        print(f"│  Degree     : {_student[3]:<69}│".center(columns))
        print(f"│  Year Level : {_student[4]:<69}│".center(columns))
        print(f"│  Signature  : {_student[5]:<69}│".center(columns))
        print(("│" + " " * 84 + "│").center(columns))
        print(("╰" + "─" * 84 + "╯").center(columns))
    else:
        print(f"┆  {Text.Style.Underline + "Student Details:" + Text.NONE:<92}┆".center(columns + 8))
        print(f"┆{"":<86}┆".center(columns))
        print(f"┆    Name        : {_student[1]:<68}┆".center(columns))
        print(f"┆    Department  : {_student[2]:<68}┆".center(columns))
        print(f"┆    Degree      : {_student[3]:<68}┆".center(columns))
        print(f"┆    Level       : {_student[4]:<68}┆".center(columns))
        print(f"┆{"":<86}┆".center(columns))
        print((f"└" + "–" * 86 + "┘").center(columns))


# Function for checking attendance
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

    if current_time.startswith("0"):    # Removing the starting 0 in hour
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

                if current_time.startswith("0"):    # Removing the starting 0 in hour
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
        if not attendance_log:  # Checking for attendance_log if it has no value
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


# Function for displaying all class schedule
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


# Function for validating the time format
def validate_time_format(time):
    # Define the regex pattern to match the time format
    pattern = r'^\d{1,2}:\d{2} [AP]M - \d{1,2}:\d{2} [AP]M$'

    # Check if the input matches the pattern
    if re.match(pattern, time):
        return True
    else:
        return False


# Function for converting time from 12 hours to 24 hours
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


# Function for checking conflicts in the class schedule
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


# Function for sorting schedule by day and starting time
def sort_schedule(schedule_item):
    day_str, time_str = schedule_item[2], schedule_item[3]
    day_num = str(days.index(day_str) + 1)
    start_time = datetime.datetime.strptime(time_str.split(" - ")[0], "%I:%M %p")
    return day_num, start_time


# Function for getting the largest total count of schedule
def max_schedule_day(__schedule):
    max_count = 0
    if __schedule:
        day_counts = {}  # Dictionary to store counts of schedules for each day

        for entry in __schedule:
            day = entry[2]  # Get the day from the entry
            if day in day_counts:
                day_counts[day] += 1  # Increment the count for that day
            else:
                day_counts[day] = 1  # Initialize the count for that day

        # Find the day with the maximum count of schedules
        max_day = max(day_counts, key=day_counts.get)
        max_count = day_counts[max_day]
    return max_count


# Function for adding new course and saving it in schedule
def add_course(stud_no, sched_day):
    # Design for adding new course
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
    while True:  # Validate key_pressed
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

    num = 0  # Num is for current total course in a day
    while num < total_course:  # If num is less than the set total_course the loop will continue to execute
        # Adding course and time design
        print(f"│{"-" * 36:^40}│".center(columns))
        print(f"│{"   Course Title :":<40}│".center(columns))
        print(f"│{"   Time         :":<40}│".center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("╰" + "─" * 40 + "╯").center(columns))

        print("\033[4F", end="")
        sched_course = str(limit_input(f"{"":<24}│   Course Title : ", 19))
        print("\033[1E", end="")
        while True:  # Checking for time format
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

        # Checking for conflict schedule
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


# Function for updating course
def update_course(stud_no, sched_day, current_total_course, day_to_update):
    global new_schedule
    global current_str
    num = 0

    # Design for updating course
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("╰" + "─" * 40 + "╯").center(columns))

    print("\033[8F", end="")
    print(f"{"":<24}│ ► {sched_day} {[current_total_course]}")
    print("\033[2E", end="")

    # Request for the total course in a day
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

    # Display the total course
    print("\033[5E", end="")
    clear(9)
    print(f"│{f"{" ► " + sched_day} {[total_course]}":<40}│".center(columns))

    # Getting each schedule in day_to_update
    for sched in day_to_update:
        if num == total_course:  # Check if the total count of sched not exceed to total_course
            break

        # Design for course and time and display the current course
        print(f"│{"-" * 36:^40}│".center(columns))
        print(f"│{f"   Course Title : {sched[1]}":<40}│".center(columns))
        print(f"│{f"   Time         : {sched[3]}":<40}│".center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("╰" + "─" * 40 + "╯").center(columns))

        print("\033[4F", end="")
        current_str = sched[1]
        sched_course = str(limit_input(f"{"":<24}│   Course Title : ", 19))
        print("\033[1E", end="")
        current_str = sched[3]
        while True:
            print(("│" + " " * 40 + "│").center(columns))
            print(("│" + " " * 40 + "│").center(columns))
            print(("╰" + "─" * 40 + "╯").center(columns))
            print("\033[3F", end="")

            sched_time = str(limit_input(f"{"":<24}│   Time         : ", 19).upper())
            # Check the format of input time
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

        # Checking for conflict schedule
        conflict = check_conflict(new_schedule, sched_day, sched_time)
        if conflict is None:
            new_schedule.append((stud_no, sched_course, sched_day, sched_time))
            num += 1
            print("\033[1E", end="")
            pass
        else:
            print("\033[3E", end="")
            msg = input_key(f"{"":<24}MSG: conflict schedule with {conflict.upper()}. ")
            if msg:
                clear(6)

    current_str = ""
    while num < total_course:  # If day_to_update less than to the total course
        # Design for course and time
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
            # Check the format of input time
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

        # Checking for conflict schedule
        conflict = check_conflict(schedule, sched_day, sched_time)
        if conflict is None:
            new_schedule.append((stud_no, sched_course, sched_day, sched_time))
            num += 1
            print("\033[1E", end="")
        else:
            print("\033[3E", end="")
            msg = input_key(f"{"":<24}MSG: conflict schedule with {conflict.upper()}. ")
            if msg:
                clear(6)

    # Clearing display for each day after updating
    print("\033[2E", end="")
    clear((3 * num) + 3)


# Function for registration of new students
def register_new_student():
    global registering_new_student
    global student_details
    global days_of_week
    global schedule
    global data
    global columns

    tab_title("REGISTER NEW STUDENT")
    if not registering_new_student:
        # Registration design
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
        # Request the user to input the student number first
        stud_no = str(limit_input(f"  │  Student No.: ", 8))

        # Searching for the student if already exist or registered in database
        cursor.execute(f"SELECT Student_No FROM Student_Info WHERE Student_No = ?", (stud_no,))
        data = cursor.fetchone()

        if data:  # If the student already exist, registration will stop
            print("\033[8E", end="")
            clear(100)
            print("\033[23E", end="")
            print("MSG: Student already registered.".center(columns))
            print("\033[f", end="")
            check_attendance()

        # User input
        print("\033[1E", end="")
        stud_name = str(limit_input(f"  │  Name       : ", 67).upper())
        print("\033[1E", end="")
        stud_department = str(limit_input(f"  │  Department : ", 67).title())
        print("\033[1E", end="")
        stud_degree = str(limit_input(f"  │  Degree     : ", 67).title())
        print("\033[1E", end="")
        stud_level = str(limit_input(f"  │  Year Level : ", 67))
        print("\033[1E", end="")
        stud_signature = str(limit_input(f"  │  Signature  : ", 25))

        # Storing the student details as array list
        student_details = [stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature]

        # Display option
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

        # Allow user to choose weekdays only or include weekends
        print("\033[7F", end="")
        print(f"{"":<24}│  Option:")
        print(f"{"":<24}│     [1] Weekdays only")
        print(f"{"":<24}│     [2] Include weekends\n\n")

        while True:  # Validate key_pressed
            key_pressed1 = input_key(f"{"":<24}│  Select: ")
            match key_pressed1:
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

        # Adding courses
        while True:
            if days_of_week == "Weekdays only":
                for day in days[:5]:
                    add_course(stud_no, day)
                break
            if days_of_week == "Include weekends":
                for day in days:
                    add_course(stud_no, day)
                break

    # Sorting the schedule
    schedule = sorted(schedule, key=sort_schedule)

    max_count = max_schedule_day(schedule)  # Calculating the total course list and save the largest count

    # Resizing console if the total max_count is 6
    if max_count == 6:
        os.system(f"mode con cols={120} lines={53}")
    else:
        os.system(f"mode con cols={120} lines={45}")

    center_console_window()  # Center console
    columns = os.get_terminal_size().columns   # Save the size width
    clear(100)  # Clear display
    tab_title("REGISTER NEW STUDENT")

    # Display student details
    _details(student_details)

    # Display class schedule
    class_schedule(schedule)

    # Check if no schedule and display a note
    if not schedule:
        print(f"{"":5}NOTE: We see that there's no schedule.")

    # Allow user to choose what next to execute
    print("\n")
    print(("-" * int(columns - 4)).center(columns))
    print(f"[S] Update Schedule{"":<26}[D] Update Student Details\n".center(columns))
    while True:  # Validating key pressed
        key_pressed = input_key(f"{"":<5}Are you sure you want to save? Press [Y] to save. ")
        match key_pressed.upper():
            case "S":
                clear(100)
                os.system(f"mode con cols={90} lines={45}")
                columns = os.get_terminal_size().columns
                center_console_window()
                registering_new_student = True
                update_schedule()
                clear(100)
                register_new_student()
            case "D":
                clear(100)
                os.system(f"mode con cols={90} lines={45}")
                columns = os.get_terminal_size().columns
                center_console_window()
                registering_new_student = True
                update_student_details()
                if data:
                    print("\033[8E", end="")
                    clear(100)
                    print("\033[23E", end="")
                    print("MSG: Student already registered.".center(columns))
                    print("\033[f", end="")
                    check_attendance()
                clear(100)
                register_new_student()
            case "Y":
                add_student(student_details)
                add_schedule(schedule)
                connection.commit()  # Saving registration
                break
            case _:
                clear(1)

    # Restore console size and clear display
    os.system(f"mode con cols={90} lines={45}")
    center_console_window()
    columns = os.get_terminal_size().columns
    clear(100)

    # Show successful message
    print("\033[23E", end="")
    print("MSG: Student successfully registered".center(columns))
    print("\033[f", end="")

    # Clear variable and return to check attendance
    student_details.clear()
    schedule.clear()
    check_attendance()


# Function for updating student details
def update_student_details():
    global student_details
    global data
    global columns
    global current_str
    global in_update_student_details
    global updating_student_details

    if not updating_student_details and not in_register_new_student:  # Check if user not updating student details
        student_details.clear()
        tab_title("UPDATE STUDENT DETAILS")
        student("Update Student Details")
        tab_title("UPDATE STUDENT DETAILS")

        _details(student_details)

        # Allow the user to choose what to execute next.
        print("\n", end="")
        print(("-" * int(columns - 4)).center(columns))
        print(f"[Y] Yes{"":<26}[N] No\n".center(columns))
        while True:  # Validate key pressed
            key_pressed = input_key(f"{"":<5}Are you sure you want to update it? ")
            match key_pressed.upper():
                case "N":
                    clear(100)
                    in_update_student_details = False
                    check_attendance()
                case "Y":
                    clear(100)
                    updating_student_details = True
                    update_student_details()
                case _:
                    clear(1)

    # Checking if not in_register_new_student
    if not in_register_new_student:
        tab_title("UPDATE STUDENT DETAILS")
    else:
        tab_title("REGISTER NEW STUDENT")

    # Assign each variable
    stud_no = student_details[0]
    stud_name = student_details[1]
    stud_department = student_details[2]
    stud_degree = student_details[3]
    stud_level = student_details[4]
    stud_signature = student_details[5]

    _details(student_details)  # Display student details

    # Checking if in_register_new_student
    if in_register_new_student:
        current_str = stud_no
        print("\033[8F", end="")
        stud_no = str(limit_input(f"  │  Student No.: ", 67).upper())
        print("\033[1E", end="")

        # Searching for the student if already exist or registered in database
        cursor.execute(f"SELECT Student_No FROM Student_Info WHERE Student_No = ?", (stud_no,))
        data = cursor.fetchone()

        if data:
            current_str = ""
            return
    else:
        print("\033[7F", end="")

    current_str = stud_name
    stud_name = str(limit_input(f"  │  Name       : ", 67).upper())
    print("\033[1E", end="")
    current_str = stud_department
    stud_department = str(limit_input(f"  │  Department : ", 67).title())
    print("\033[1E", end="")
    current_str = stud_degree
    stud_degree = str(limit_input(f"  │  Degree     : ", 67).title())
    print("\033[1E", end="")
    current_str = stud_level
    stud_level = str(limit_input(f"  │  Year Level : ", 67))
    print("\033[1E", end="")
    current_str = stud_signature
    stud_signature = str(limit_input(f"  │  Signature  : ", 25))
    current_str = ""

    # Checking if in_register_new_student
    if in_register_new_student:
        student_details = [stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature]
        return

    # Checking for changes
    changes = False
    if stud_name != student_details[1]:
        changes = True
    elif stud_department != student_details[2]:
        changes = True
    elif stud_degree != student_details[3]:
        changes = True
    elif stud_level != student_details[4]:
        changes = True
    elif stud_signature != student_details[5]:
        changes = True

    # Show message if no changes
    print("\033[3E", end="")
    if not changes:
        print(f"{"":<5}NOTE: No changes have been made.")

    # Allow the user to choose what to execute next.
    print("\n", end="")
    print(("-" * 86).center(90))
    print(f"[S] Save & Update Class Schedule{"":<20}[N] Update Again\n".center(columns))
    while True:  # Validate key pressed
        key_pressed = input_key(f"{"":<5}Are you sure you want to save? Press [Y] to save. ")
        match key_pressed.upper():
            case "Y":
                student_details = [stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature]
                update_student(student_details)
                connection.commit()  # Save modified student details
                clear(100)
                print("\033[23E", end="")
                print("MSG: Student details were successfully updated.".center(columns))
                print("\033[f", end="")
                in_update_student_details = False
                updating_student_details = False
                check_attendance()
            case "N":
                clear(100)
                update_student_details()
            case "S":
                student_details = [stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature]
                update_student(student_details)
                update_schedule()
            case _:
                clear(1)


# Function for updating schedule
def update_schedule():
    global columns
    global schedule
    global in_update_student_details
    global updating_student_details
    global updating_class_schedule
    new_schedule.clear()

    if not updating_class_schedule and not registering_new_student:  # User not already in updating class schedule
        schedule.clear()

        if not updating_student_details:  # Check if user not in update student details
            schedule.clear()
            tab_title("UPDATE SCHEDULE")
            student("Update Schedule")

        # Searching for the schedule of the student
        cursor.execute("SELECT * FROM ClassSchedule WHERE Student_No = ?", (student_details[0],))
        schedule.extend(cursor.fetchall())  # Store it as array list

        # Getting the largest total count of schedule
        max_sched = max_schedule_day(schedule)
        if max_sched == 6:  # If the total count is equal to 6 it will resize the console height
            os.system(f"mode con cols={120} lines={53}")
        else:  # Else the console will resize the width only
            os.system(f"mode con cols={120} lines={45}")

        center_console_window()  # Center the console
        columns = os.get_terminal_size().columns  # Saving the size of console width

        # Checking if user not in notifying student details
        if updating_student_details:
            tab_title("UPDATE STUDENT DETAILS")
        else:
            tab_title("UPDATE SCHEDULE")

        # Display the student details
        _details(student_details)

        # Display all class schedule
        class_schedule(schedule)

        # Allow user to choose if they want to update the schedule
        print("\n", end="")
        print(("-" * int(columns - 4)).center(columns))
        print(f"[Y] Yes{"":<26}[N] No\n".center(columns))
        while True:
            key_pressed = input_key(f"{"":<5}Are you sure you want to update it? ")
            match key_pressed.upper():
                case "N":  # It will return to check attendance
                    clear(100)
                    os.system(f"mode con cols={90} lines={45}")
                    columns = os.get_terminal_size().columns
                    center_console_window()
                    check_attendance()
                case "Y":  # It will continue to update the class schedule
                    os.system(f"mode con cols={90} lines={45}")
                    columns = os.get_terminal_size().columns
                    center_console_window()
                    updating_class_schedule = True
                    update_schedule()  # Return to update schedule
                case _:
                    clear(1)

    if updating_student_details:  # If user updating student details
        tab_title("UPDATE STUDENT DETAILS")
    elif registering_new_student:  # If user register new student
        tab_title("REGISTER NEW STUDENT")
    else:  # If user updating class schedule
        tab_title("UPDATE SCHEDULE")

    # Display the student details
    _details(student_details)

    _days = []
    print(("╭" + "─" * 40 + "╮").center(columns))
    print(f"│{"CLASS SCHEDULE:":^40}│".center(columns))
    print(("├" + "─" * 40 + "┤").center(columns))
    if not registering_new_student:
        # Allow user to select what those days are to be modified
        print(f"│{"  Select a day you want to update.":<40}│".center(columns))
        print(f"│{"     " + f"{"[1] Monday":<20}[5] Friday":<40}│".center(columns))
        print(f"│{"     " + f"{"[2] Tuesday":<20}[6] Saturday":<40}│".center(columns))
        print(f"│{"     " + f"{"[3] Wednesday":<20}[7] Sunday":<40}│".center(columns))
        print(f"│{"     [4] Thursday":<40}│".center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("╰" + "─" * 40 + "╯").center(columns))

        print("\033[2F", end="")
        key_pressed = int_input(f"{"":<24}│  Select: ", 7)

        # Converting the selected numbers as days and storing it as array
        for day in key_pressed:
            _days.append(days[int(day) - 1])

        # Sorting the days
        _days.sort(key=lambda x: days.index(x))

        print("\033[6F", end="")  # Move cursor up
    else:
        if days_of_week == "Weekdays only":
            _days = days[:5]
        if days_of_week == "Include weekends":
            _days = days

    # updating now each class schedule
    for _day in _days:
        _total = 0
        _to_update = []
        for sched in schedule:
            if sched[2] == _day:
                _total += 1
                _to_update.append(sched)
        # Calling for function to for updating each course
        update_course(student_details[0], _day, _total, _to_update)

    # Getting for the other not modified schedule
    for sched in schedule:
        if sched[2] not in _days:
            new_schedule.append(sched)

    # Sorting the schedule
    schedule = sorted(new_schedule, key=sort_schedule)

    # If registering_new_student it will return to registration
    if registering_new_student:
        return

    # Getting the largest total count of schedule
    max_sched = max_schedule_day(schedule)
    if max_sched == 6:  # If the total count is equal to 6 it will resize the console height
        os.system(f"mode con cols={120} lines={53}")
    else:  # Else the console will resize the width only
        os.system(f"mode con cols={120} lines={45}")

    center_console_window()  # Center the console
    columns = os.get_terminal_size().columns  # Save the size of console width

    # Checking again if not in update student details
    if updating_student_details:
        tab_title("UPDATE STUDENT DETAILS")
    else:
        tab_title("UPDATE SCHEDULE")

    # Display student details
    _details(student_details)

    # Display the new class schedule
    class_schedule(schedule)

    # Checking now if no schedule has been modified
    changes = False
    for sched in schedule:
        if sched not in schedule:
            changes = True
            break

    # If no schedule has been modified it will show note
    if not changes:
        print(f"{"":<5}NOTE: No changes have been made.")

    # Allow user to choose if they want to update again or just save it
    print("\n", end="")
    print(("-" * int(columns - 4)).center(columns))
    print(f"[Y] Save{"":<26}[N] Update Again\n".center(columns))
    while True:
        key_pressed = input_key(f"{"":<5}Are you sure you want to save? ")
        match key_pressed.upper():
            case "N":
                clear(100)
                os.system(f"mode con cols={90} lines={45}")
                columns = os.get_terminal_size().columns
                center_console_window()
                update_schedule()
            case "Y":
                cursor.execute("DELETE FROM ClassSchedule WHERE Student_No = ?", (student_details[0],))
                add_schedule(schedule)
                connection.commit()
                clear(100)
                os.system(f"mode con cols={90} lines={45}")
                columns = os.get_terminal_size().columns
                center_console_window()
                print("\033[23E", end="")
                # Display message after updating
                if updating_student_details and updating_class_schedule:
                    print("MSG: Student details and the class schedule were successfully updated.".center(columns))
                    updating_student_details = False
                    updating_class_schedule = False
                elif updating_class_schedule:
                    print("MSG: Class schedule successfully updated.".center(columns))
                    updating_class_schedule = False
                print("\033[f", end="")
                in_update_student_details = False
                check_attendance()
            case _:
                clear(1)


if __name__ == "__main__":
    run_as_administrator()
    set_console_title("Student Attendance Management System")
    set_window_style()
    set_console_size(90, 45)
    columns = os.get_terminal_size().columns
    center_console_window()
    check_attendance()
