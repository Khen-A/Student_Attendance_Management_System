# Student Attendance Management System
# Created by: Khen Jomarie L. Alcantara
# Degree: BS Electronics And Communication Engineering
# Level: 1st Year

# Import library
import sqlite3
from datetime import datetime
import msvcrt
import ctypes.wintypes
import os
import sys

# Initialize variable
student_details = []
new_student_details = []
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
temp_schedule = []
current_schedule = []
new_schedule = []
days_of_week = ""
current_str = ""
data = ""
columns = int
checking_attendance = False
in_register_new_student = False
in_update_student_details = False
in_updating_class_schedule = False
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

# Creating Class_Schedule table and column
cursor.execute("CREATE TABLE IF NOT EXISTS Class_Schedule ("
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

# Creating Login_Attempt table and column
cursor.execute("CREATE TABLE IF NOT EXISTS Login_Attempt ("
               "Student_No   TEXT, "
               "_Time         TEXT, "
               "_Count        TEXT)")

# Saving all inquiries
connection.commit()


# Function for requesting administration
def run_as_administrator():
    # Checking current console if not running as administrator
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, os.path.basename(__file__), None, 1)
        sys.exit()


# Function for aligning console to center windows and disable resizing of console
def center_console_window():
    # Define necessary constants
    gwl_style = -16
    ws_size_box = 0x00040000
    ws_maximize_box = 0x00010000

    # Get handle to the console window
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()

    # Get current style
    style = ctypes.windll.user32.GetWindowLongW(hwnd, gwl_style)

    # Restore console style
    original_style = style | ws_size_box | ws_maximize_box
    ctypes.windll.user32.SetWindowLongW(hwnd, gwl_style, original_style)

    # Get screen dimensions
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)

    # Get dimensions of the console window
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    console_width = rect.right - rect.left
    console_height = rect.bottom - rect.top

    # Calculate new position
    x = (screen_width - console_width) // 2
    y = (screen_height - console_height) // 2

    # Set console window position
    ctypes.windll.user32.MoveWindow(hwnd, x, y, console_width, console_height, True)

    # Update console style to disable resizing of console
    new_style = style & ~ws_size_box & ~ws_maximize_box
    ctypes.windll.user32.SetWindowLongW(hwnd, gwl_style, new_style)


# Function for assigning console title
def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


# Function for single instance console application
def is_single_instance(_title):
    # Define necessary Windows types
    lpctstr = ctypes.c_wchar_p

    # Create a mutex
    mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, True, lpctstr(_title))

    # Check if the mutex already exists
    if ctypes.windll.kernel32.GetLastError() == 183 or mutex_handle is None:  # ERROR_ALREADY_EXISTS = 183

        # Find the window by title
        hwnd = ctypes.windll.user32.FindWindowW(None, lpctstr(_title))

        # Bring the window to the foreground
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 1)  # If console is in minimize it will show
            ctypes.windll.user32.SetForegroundWindow(hwnd)

        return False

    return True


# Function for resizing console
def set_console_size(width: int, height: int):
    os.system(f"mode con cols={width} lines={height}")


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
    current_date = datetime.now().date().strftime("%B %d, %Y | %A")  # Get the current date
    current_time = datetime.now().time().strftime("%I:%M %p")  # Get the current time

    # Display tab header and title
    print(Text.Color.Foreground.Green, end="")
    print(("╔" + "═" * int(columns - 2) + "╗").center(columns))
    print(("║" + Text.Color.Foreground.Yellow + Text.Style.Bold + f"{title:^{columns - 2}}" +
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
    cursor.executemany("INSERT INTO Class_Schedule VALUES (?, ?, ?, ?)", _schedule)


# Function for queuing update student details
def update_student(_student):
    cursor.execute("UPDATE Student_Info SET _Name = ?, _Department = ?, _Degree = ?, _Level = ?, _Signature = ? "
                   "WHERE Student_No = ?", _student[1:] + [_student[0]])


# Function for queuing attendance
def attendance(_attendance):
    cursor.executemany("INSERT INTO Attendance VALUES (?, ?, ?, ?, ?, ?, ?)", _attendance)


def login_attempt(_student):
    cursor.executemany("INSERT INTO Login_Attempt VALUES (?, ?, ?)", _student)


# Function for getting student details
def student(__usage):
    global student_details
    global in_register_new_student
    global in_updating_class_schedule
    global in_update_student_details
    global updating_class_schedule
    global updating_student_details
    global registering_new_student
    student_details.clear()

    updating_class_schedule = False
    updating_student_details = False
    registering_new_student = False

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
        if __usage == "Update Schedule":
            pass
        elif __usage == "Update Student Details":
            pass
        else:
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
                    in_updating_class_schedule = False
                    in_update_student_details = False
                    register_new_student()
                case "3":
                    print("\033[3E", end="")
                    clear(100)
                    in_register_new_student = False
                    in_updating_class_schedule = True
                    in_update_student_details = False
                    update_schedule()
                case "4":
                    print("\033[3E", end="")
                    clear(100)
                    in_register_new_student = False
                    in_updating_class_schedule = False
                    in_update_student_details = True
                    update_student_details()
                case _:
                    print("\033[1F", end="")
                    continue
            break

    print("\033[3E", end="")

    current_time = datetime.now().time().strftime("%I:%M:%S %p")

    cursor.execute("SELECT * FROM Login_Attempt WHERE Student_No = ?", (student_details[0],))  # Searching for student
    _attempt = [x for item in cursor.fetchall() for x in item[0:6]]  # Saving login attempts as array

    try_count = 0

    if not _attempt:  # If _attempt is empty or no record.
        # adding _attempt log to login_attempt database
        time = current_time
        attempt_count = 3
        _attempt = [(student_details[0], time, attempt_count)]
        login_attempt(_attempt)
        connection.commit()
    else:  # _attempt already exist
        time = _attempt[1]
        attempt_count = _attempt[2]

        # Converting time to 24 hrs and whole number
        time = convert_to_24hrs(time)
        current_time = convert_to_24hrs(current_time)

        # Checking for time remaining for log in
        time_remaining = current_time - time
        if attempt_count != 0:  # If all attempts are not used. The user needs to retry after 60 seconds.
            if (60 - time_remaining) > 0:
                clear(100)
                print("\033[23E", end="")
                print(f"MSG: Please try again in {60 - time_remaining} seconds.".center(columns))
                print("\033[f", end="")
                check_attendance()
        else:  # All attempts already used. The user needs to retry after 1 hour.
            if (3600 - time_remaining) > 0:
                clear(100)
                print("\033[23E", end="")
                print(f"MSG: Please try again in {round((3600 - time_remaining) / 60, 2)} minutes."
                      .center(columns))
                print("\033[f", end="")
                check_attendance()

    # Validating signature and try count
    while try_count < 5:  # If try count is not greater than 5
        print(f"│{"":^45}│".center(columns))
        print("\033[1F", end="")
        key_signature = str(limit_input(f"{"":<21}│    Signature   : ", 25))
        if key_signature == student_details[5]:  # If signature is correct
            cursor.execute("DELETE FROM Login_Attempt WHERE Student_No = ?", (student_details[0],))
            connection.commit()
            print("\033[10E", end="")
            clear(100)
            return
        else:  # Signature is wrong
            print("\033[3E", end="")
            print("MSG: Wrong signature. Please try again. ".center(columns))
            print("\033[3F", end="")
            try_count += 1
            clear(1)
            continue
    else:  # It will return to check attendance and display message for attempts
        current_time = datetime.now().time().strftime("%I:%M:%S %p")
        attempt_count -= 1
        _attempt = [student_details[0], current_time, attempt_count]
        cursor.execute("UPDATE Login_Attempt SET _Time = ?, _Count = ? WHERE Student_No = ?",
                       _attempt[1:] + [_attempt[0]])
        connection.commit()
        clear(100)
        print("\033[23E", end="")
        if attempt_count == 0:
            print(f"MSG: All attempts used. Try again in 1 hour.".center(columns))
        elif attempt_count == 1:
            print(f"MSG: Wrong signature. There's only {attempt_count} more attempt to try.".center(columns))
            print(f"{"     Please try again in 60 seconds.":<58}".center(columns))
        else:
            print(f"MSG: Wrong signature. There's only {attempt_count} more attempts to retry.".center(columns))
            print(f"{"     Please try again in 60 seconds.":<60}".center(columns))

        print("\033[f", end="")
        check_attendance()


# Function for displaying student details
def _details(_student):
    # Checking if user not updating student details and not register new student
    if updating_student_details or in_update_student_details or registering_new_student or in_register_new_student:
        print(('╭' + '─' * 84 + '╮').center(columns))
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
    global checking_attendance
    schedule = []
    attendance_log = []
    next_schedule = []
    status = "PENDING"
    today_next_schedule_found = False

    tab_title("CHECK ATTENDANCE")

    if not checking_attendance:
        student("Check Attendance")

        tab_title("CHECK ATTENDANCE")

    stud_no = student_details[0]
    stud_signature = student_details[5]

    _details(student_details)

    # Getting current date and time
    current_date = datetime.now().date().strftime("%m/%d/%y")
    current_day = datetime.now().date().strftime("%A")
    current_time = datetime.now().time().strftime("%I:%M %p")

    if current_time.startswith("0"):  # Removing the starting 0 in hour
        current_time = current_time[1:]

    # Searching for today class schedule in class schedule database
    cursor.execute("SELECT * FROM Class_Schedule WHERE Student_No = ? AND _Day = ?",
                   (stud_no, current_day,))
    schedule.extend(cursor.fetchall())  # Store all search class schedule

    # Checking for current schedule
    for index, (stud_no, course_title, day, time) in enumerate(schedule):
        start_time, end_time = time.split(" - ")

        start_time = convert_to_24hrs(start_time)
        end_time = convert_to_24hrs(end_time)
        time_now = convert_to_24hrs(current_time)

        # if the current time already skip the schedule time, the status will be marked as absent.
        if end_time <= time_now:
            # Searching for skip schedule
            cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                           "AND _Day = ? AND _Time = ? AND _Date = ?",
                           (stud_no, course_title, day, time, current_date))
            attn_log = cursor.fetchall()  # Store the search schedule
            if not attn_log:
                # Store the schedule to attendance log
                attendance_log.append((stud_no, course_title, day, time, current_date, "N/A", "ABSENT"))
                attendance(attendance_log)
                connection.commit()
                attendance_log.clear()

        if start_time <= time_now <= end_time:  # Searching for current schedule
            # Store the current schedule to attendance log
            attendance_log.append([stud_no, course_title, day, time, current_date, current_time])

            # Checking for next schedule
            if index + 1 < len(schedule):
                _next = schedule[index + 1]
                next_schedule.append(_next)
                today_next_schedule_found = True
            break

    # Checking now for attendance
    time_interval = 0
    _attendance = []
    for attn, (stud_no, course_title, day, time, current_date, current_time) in enumerate(attendance_log):
        # Searching for current attendance in attendance
        cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                       "AND _Day = ? AND _Time = ? AND _Date = ?",
                       (stud_no, course_title, day, time, current_date))
        _attendance = cursor.fetchall()  # Store all search schedule

        # If it is not already signed, it will ask user to input their signature.
        while not _attendance:
            for attn_log in attendance_log:
                # Display the current schedule course
                print("┌─────────────────────────────────────────────┐".center(columns))
                print(f"│{"SCHEDULE NOW":^45}│".center(columns))
                print("├─────────────────────────────────────────────┤".center(columns))
                print(f"│ Course Title : {attn_log[1]:<29}│".center(columns))
                print(f"│ Time         : {attn_log[3]:<29}│".center(columns))
                print(f"│ Status       : {status:<29}│".center(columns))
                print("├─────────────────────────────────────────────┤".center(columns))
                print("│                                             │".center(columns))
                print("└─────────────────────────────────────────────┘".center(columns))
                print("NOTE: If you're excused, just type EXCUSE.".center(columns))
                print("\033[3F", end="")
                key_signature = str(limit_input(f"{"":<21}│ Signature: ", 25))

                # Checking if the signature is correct
                if key_signature.upper() == "EXCUSE":  # Allow the user to excuse attendance.
                    status = "PENDING EXCUSE"
                    pass
                elif key_signature != stud_signature:
                    clear(100)
                    print("\033[23E", end="")
                    print("MSG: You entered the wrong signature!".center(columns))
                    print("\033[f", end="")
                    check_attendance()

                # Preparing for queuing the attendance
                attendance_log.clear()

                # Calculate the time interval for checking attendance
                start_time = convert_to_24hrs(attn_log[3].split(" - ")[0])
                current_time = datetime.now().time().strftime("%I:%M %p")
                time_now = convert_to_24hrs(current_time)
                time_interval = int((time_now - start_time) / 60)

                # Condition for Present, Absent, and Late
                if status == "PENDING":
                    if 5 <= time_interval <= 15:
                        status = "LATE"
                    elif time_interval > 15:
                        status = "ABSENT"
                    else:
                        status = "PRESENT"

                if current_time.startswith("0"):  # Removing the starting 0 in hour
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
                print("\033[2E", end="")
                clear(9)
                print("\033[f", end="")
                tab_title("CHECK ATTENDANCE")
                print("\033[8E", end="")

    # Searching again for next
    if not today_next_schedule_found:
        for index, (stud_no, course_title, day, time) in enumerate(schedule):
            next_start_time, next_end_time = time.split(" - ")

            next_start_time = convert_to_24hrs(next_start_time)
            time_now = convert_to_24hrs(current_time)

            if next_start_time >= time_now:
                schedule[index] = (stud_no, course_title, day, time)
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
    else:  # Else if there's no next schedule found. It will display all schedules on that day.
        attendance_count = 0
        if not attendance_log:  # Checking for attendance_log if it is not null array
            # Table title
            print("┌──────────────────────────────────────────────────────────────────────────┐".center(columns))
            print(f"│{"SCHEDULE TODAY":^74}│".center(columns))
            print("├────────────────────┬───────────────────────┬──────────────┬──────────────┤".center(columns))

            # Column title
            print(f"│{"COURSE TITLE":^20}│{"TIME":^23}│{"STATUS":^14}│{"TIME IN":^14}│".center(columns))
            if schedule:
                print("├────────────────────┼───────────────────────┼──────────────┼──────────────┤"
                      .center(columns))
                for attn, (stud_no, course_title, day, time) in enumerate(schedule):
                    # Searching for all attendance in attendance database
                    cursor.execute("SELECT * FROM Attendance WHERE Student_No = ? AND _Course = ? "
                                   "AND _Day = ? AND _Time = ? AND _Date = ?",
                                   (stud_no, course_title, day, time, current_date))
                    _attendance = cursor.fetchall()  # Store all search schedule
                    if _attendance:
                        for log in _attendance:
                            if len(log[1]) > 18:
                                course_title = log[1][:16] + ".."
                            else:
                                course_title = log[1]
                            print(f"│{" " + course_title:<20}│{" " + log[3]:^23}"
                                  f"│{log[6]:^14}│{log[5]:^14}│".center(columns))

                    attendance_count += 1
                print("└────────────────────┴───────────────────────┴──────────────┴──────────────┘"
                      .center(columns))
            else:
                print("├────────────────────┴───────────────────────┴──────────────┴──────────────┤".center(columns))
                print(f"│{"No Schedule":^74}│".center(columns))
                print("└──────────────────────────────────────────────────────────────────────────┘".center(columns))

        next_day = (days.index(current_day) + 1) % len(days)
        next_day = days[next_day]

        # Searching for next day schedule in class schedule database
        cursor.execute("SELECT * FROM Class_Schedule WHERE Student_No = ? AND _Day = ?",
                       (stud_no, next_day,))
        next_day_schedule = cursor.fetchall()  # Store all search schedule

        total_next_schedule = 0
        # If it has next day schedule it will display all schedules.
        print("┌─────────────────────────────────────────────┐".center(columns))
        print(f"│{"NEXT SCHEDULE " + f"[{next_day.upper()}]":^45}│".center(columns))
        print("├─────────────────────────────────────────────┤".center(columns))
        if next_day_schedule:
            for idx, _schedule in enumerate(next_day_schedule):
                print(f"│  Course Title : {_schedule[1]:<28}│".center(columns))
                print(f"│  Time         : {_schedule[3]:<28}│".center(columns))
                if idx < len(next_day_schedule) - 1:
                    print(f"│{"-" * 40:^45}│".center(columns))
                total_next_schedule += 1
        else:
            print(f"│{"No Schedule":^45}│".center(columns))
        print("└─────────────────────────────────────────────┘".center(columns))

        if not checking_attendance:
            if total_next_schedule == 6 and attendance_count >= 2:
                set_console_size(90, 45 + 2 + (attendance_count-3))
            elif attendance_count >= 5 and total_next_schedule >= 5:
                set_console_size(90, 45 + (attendance_count - 4))
            else:
                set_console_size(90, 45)
            center_console_window()
            checking_attendance = True
            check_attendance()

    # Display message
    if attendance_log:
        if status == "ABSENT":
            print(f"MSG: You've been marked as absent for being {time_interval} minutes late.".center(columns))
        elif status == "LATE":
            print(f"MSG: You've been marked as late for being {time_interval} minutes late.".center(columns))
        elif status == "PENDING EXCUSE":
            print("\n", end="")
            print(f"{"NOTE:":<80}".center(columns))
            print("     Your  request  is  now  being  processed,  and  it  will  notify  your".center(columns))
            print("instructor.  Please provide  a valid excuse  letter to  your instructor  so".center(columns))
            print("they   can  consider  your  request.  Ensure  that  your  letter   includes".center(columns))
            print("a  clear  explanation   for  the  need  for  an  excuse  and  provides  any".center(columns))
            print("necessary  supporting  documentation.  Thank you...                        ".center(columns))

    print("\n")
    print(("-" * 80).center(columns))
    while True:
        user = input_key("      Press [N] to check again or [Y] to exit: ")
        match user.upper():
            case "N":
                clear(100)
                set_console_size(90, 45)
                center_console_window()
                checking_attendance = False
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

    # Checking for schedule
    if __schedule:
        for _schedule in __schedule:
            day = _schedule[2]  # Save the day as array

            if day not in day_schedules:  # Checking if day is already exist in day_schedules
                day_schedules[day] = []

            if len(_schedule[1]) > 11:  # Checking if the course title is greater than 11 text
                course_title = _schedule[1][:9] + ".."  # Trim the course title and adding two dot
            else:
                course_title = _schedule[1]

            day_schedules[day].append((course_title, _schedule[3]))

        # Get the maximum number of schedules for any day
        max_schedules = max(len(schedules) for schedules in day_schedules.values())

        # Display the schedules
        for i in range(max_schedules):
            day_schedule = []
            for day in days:
                if day in day_schedules and len(day_schedules[day]) > i:
                    course_title, time = day_schedules[day][i]
                    start, end = time.split(" - ")
                    day_schedule.append((course_title, start, end))
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
    # Split the time into two parts
    _time = time.split(" - ")

    # Check if the time string has two parts
    if len(_time) != 2:
        return False

    # Checking for the time format
    for time in _time:
        try:
            datetime.strptime(time, "%I:%M %p")
        except ValueError:
            return False

    # Return to True if the input time format is correct
    return True


# Function for converting time from 12 hours to 24 hours
def convert_to_24hrs(time_str):
    # Convert time string from 12-hour format to minutes
    parts = time_str.split()
    hour, minute, second = 0, 0, 0
    try:  # If time has a second
        hour, minute, second = map(int, parts[0].split(':'))
    except ValueError:
        hour, minute = map(int, parts[0].split(':'))

    if parts[1].upper() == 'PM':  # PM Case
        if hour != 12:
            hour += 12
    else:  # AM case
        if hour == 12:
            hour = 0
    return hour * 3600 + minute * 60 + second


# Function for checking conflicts in the class schedule
def check_conflict(schedules, day, time):
    new_start, new_end = map(convert_to_24hrs, time.split(' - '))

    for index, (stud_no, _course, _day, _time) in enumerate(schedules):
        if _day != day:
            continue

        start, end = map(convert_to_24hrs, _time.split(' - '))
        if start <= new_start < end:
            return _course  # Conflict found
        elif start < new_end <= end:
            return _course  # Conflict found
        elif new_start <= start and new_end >= end:
            return _course  # Conflict found

    return None  # No conflict found


# Function for sorting schedule by day and starting time
def sort_schedule(schedule_item):
    day_str, time_str = schedule_item[2], schedule_item[3]
    day_num = str(days.index(day_str) + 1)
    start_time = datetime.strptime(time_str.split(" - ")[0], "%I:%M %p")
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


# Function for inputting total course for each day
def total_course():
    while True:  # Validate key_pressed
        try:
            _total_course = int(input_key(f"{"":<24}│     Total course MAX(6): "))
            if _total_course <= 6:  # Check if user input is between 1-6
                print("\033[3E", end="")
                clear(4)
                print(("│" + " " * 40 + "│").center(columns))
                break
            else:
                print("\r", end="")
                print("\033[1F", end="")
        except ValueError:  # Check if user input is not integer
            print("\r", end="")
            print("\033[1F", end="")
    return _total_course


# Function for adding course
def add_course(stud_no, schedule_day):
    print(("├" + "─" * 40 + "┤").center(columns))
    print(('│' + " " * 40 + '│').center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + ' ' * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(('│' + ' ' * 40 + '│').center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("╰" + "─" * 40 + "╯").center(columns))
    print("\033[7F", end="")
    print(f"{"":<24}│ ► {schedule_day}")
    print("\033[2E", end="")

    _total_course = total_course()
    _course_entry = []

    if _total_course > 0:  # Check if total_course is not zero
        print("\033[5F")
        print(f"{"":<24}│ ► {schedule_day} [{_total_course}]")

        count = 0
        _course_entry.extend(course_entry(stud_no, _total_course, schedule_day, count, None))
    else:
        clear(5)

    return _course_entry


# Function for inputting course title and time
def course_entry(stud_no, _total_course, _schedule_day, _count, _update_schedule):
    _schedule = []
    while _count < _total_course:  # If num is less than the set total_course the loop will continue to execute
        # Adding course and time design
        print(f"│{"-" * 36:^40}│".center(columns))
        print(f"│{"   Course Title :":<40}│".center(columns))
        print(f"│{"   Time         :":<40}│".center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("╰" + "─" * 40 + "╯").center(columns))

        print("\033[4F", end="")
        schedule_course = str(limit_input(f"{"":<24}│   Course Title : ", 19))
        print("\033[1E", end="")

        schedule_time = time_entry()

        # Checking for conflict schedule
        if _update_schedule:  # If schedule to modify is not empty
            conflict = check_conflict(_update_schedule, _schedule_day, schedule_time)
        else:
            conflict = check_conflict(_schedule, _schedule_day, schedule_time)

        if conflict is None:
            _schedule.append((stud_no, schedule_course, _schedule_day, schedule_time))
            _count += 1
            print("\033[1E", end="")
        else:
            print("\033[3E", end="")
            msg = input_key((f"MSG: Conflict schedule with {conflict.upper()}.  ".center(columns)) +
                            "\033[D" * (45 - int((31 + len(conflict)) / 2)))
            if msg:
                clear(6)

    print("\033[2E", end="")
    clear((3 * _count) + 4)

    return _schedule


# Function for updating course
def update_course(_stud_no, _schedule_day, _current_total_course, _day_to_update, _schedule):
    global current_str
    _update_schedule = []
    count = 0

    print(("├" + "─" * 40 + "┤").center(columns))
    print(('│' + " " * 40 + "│").center(columns))
    print(('│' + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("│" + " " * 40 + '│').center(columns))
    print(('│' + ' ' * 40 + "│").center(columns))
    print(("│" + " " * 40 + "│").center(columns))
    print(("╰" + "─" * 40 + "╯").center(columns))
    print("\033[7F", end="")
    print(f"{"":<24}│ ► {_schedule_day} {[_current_total_course]}")
    print("\033[2E", end="")

    # Request for the total course in a day
    _total_course = total_course()

    if _total_course > 0:  # Check if total_course is not zero
        # Display the total course
        print("\033[5E", end="")
        clear(9)
        print(f"│{f"{" ► " + _schedule_day} {[_total_course]}":<40}│".center(columns))

        # Getting each schedule in day_to_update
        for _new_schedule in _day_to_update[:_total_course]:
            while True:
                # Design for course and time and display the current course
                print(f"│{"-" * 36:^40}│".center(columns))
                print(f"│{f"   Course Title : {_new_schedule[1]}":<40}│".center(columns))
                print(f"│{f"   Time         : {_new_schedule[3]}":<40}│".center(columns))
                print(("│" + " " * 40 + "│").center(columns))
                print(("╰" + "─" * 40 + "╯").center(columns))

                print("\033[4F", end="")
                current_str = _new_schedule[1]
                schedule_course = str(limit_input(f"{"":<24}│   Course Title : ", 19))
                print("\033[1E", end="")
                current_str = _new_schedule[3]
                schedule_time = time_entry()
                current_str = ""

                # Checking for conflict schedule
                conflict = check_conflict(_update_schedule, _schedule_day, schedule_time)
                if conflict:
                    print("\033[3E", end="")
                    msg = input_key((f"MSG: Conflict schedule with {conflict.upper()}.  ".center(columns)) +
                                    "\033[D" * (45 - int((31 + len(conflict)) / 2)))
                    if msg:
                        clear(6)
                        continue

                _update_schedule.append((_stud_no, schedule_course, _schedule_day, schedule_time))

                count += 1
                print("\033[1E", end="")
                break

        if count != _total_course:
            _update_schedule.extend(course_entry(_stud_no, _total_course, _schedule_day,
                                                 count, _update_schedule))
        else:
            print("\033[2E", end="")
            clear((3 * count) + 4)
    else:
        clear(5)

    return _update_schedule


# Function for inputting and validating time
def time_entry():
    while True:
        print(('│' + " " * 40 + '│').center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("╰" + "─" * 40 + "╯").center(columns))
        print("\033[3F", end="")

        # User input
        _schedule_time = str(limit_input(f"{"":<24}│   Time         : ", 19).upper())
        # Check the format of input time
        if validate_time_format(_schedule_time):  # If time format is correct
            start, end = map(convert_to_24hrs, _schedule_time.split(' - '))
            if end > start:  # Check if end time is greater than to start time
                break
            else:  # Show message if false
                print("\033[3E", end="")
                msg = input_key((f"MSG: Wrong time schedule.  ".center(columns)) + "\033[32D")
                if msg:
                    clear(4)
        else:  # Show message if false
            print("\033[3E", end="")
            msg = input_key(f"{"":<19}MSG: Invalid time format.\n"
                            f"{"":<19}     Please follow the format: 10:00 AM - 12:00 PM ")
            if msg:
                clear(5)
    return _schedule_time


# Function for displaying student_details and class_schedule
def display_student_and_class_schedule(_class_schedule):
    global columns
    max_schedule = max_schedule_day(_class_schedule)
    # Resize the console height based on largest maximum count of schedule
    if max_schedule == 6:
        if in_register_new_student or in_update_student_details:
            set_console_size(120, 53)
        else:
            set_console_size(120, 49)
    elif max_schedule == 5:
        if in_register_new_student or in_update_student_details:
            set_console_size(120, 49)
        else:
            set_console_size(120, 45)
    else:
        set_console_size(120, 45)

    center_console_window()  # Center the console
    columns = os.get_terminal_size().columns  # Save the size of console width

    # Checking again if not in update student details
    if in_register_new_student:
        tab_title("REGISTER NEW STUDENT")
    elif in_updating_class_schedule:
        tab_title("UPDATE SCHEDULE")
    elif in_update_student_details:
        tab_title("UPDATE STUDENT DETAILS")

    # Display student details
    _details(student_details)

    # Display the new class schedule
    class_schedule(_class_schedule)


# Function for registration of new students
def register_new_student():
    global registering_new_student
    global updating_student_details
    global student_details
    global current_schedule
    global new_schedule
    global temp_schedule
    global days_of_week
    global data
    global columns

    tab_title("REGISTER NEW STUDENT")
    if not registering_new_student and not updating_student_details:
        days_of_week = ""
        new_schedule.clear()

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

        print("\033[3E", end="")

        # design for adding class schedule
        print(("╭" + "─" * 40 + "╮").center(columns))
        print(f"│{"CLASS SCHEDULE:":^40}│".center(columns))
        print(("├" + "─" * 40 + "┤").center(columns))
        print(('│' + ' ' * 40 + '│').center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("│" + ' ' * 40 + "│").center(columns))
        print(("│" + " " * 40 + "│").center(columns))
        print(("╰" + "─" * 40 + "╯").center(columns))

        # Display option
        while not days_of_week:
            # Allow user to choose weekdays only or include weekends
            print("\033[7F", end="")
            print(f"{"":<24}│  Option:")
            print(f"{"":<24}│     [1] Weekdays only")
            print(f"{"":<24}│     [2] Include weekends\n\n")

            while True:  # Validate key_pressed
                key_pressed1 = input_key(f"{"":<24}│  Select: ")
                match key_pressed1:
                    case "1":
                        days_of_week = "Weekdays only"
                    case "2":
                        days_of_week = "Include weekends"
                    case _:
                        print("\033[1F", end="")
                        print("\r", end="")
                        continue
                clear(8)
                print(f"│{f"CLASS SCHEDULE [{days_of_week}]":^40}│".center(columns))
                break

        # Adding courses
        while True:
            if days_of_week == "Weekdays only":
                for day in days[:5]:
                    new_schedule.extend(add_course(stud_no, day))
                break
            if days_of_week == "Include weekends":
                for day in days:
                    new_schedule.extend(add_course(stud_no, day))
                break

    # Sorting the schedule
    new_schedule = sorted(new_schedule, key=sort_schedule)

    display_student_and_class_schedule(new_schedule)

    # Check if no schedule and display a note
    if not new_schedule:
        print(f"{"":5}NOTE: We see that there's no schedule.")

    # Allow user to choose what next to execute
    print("\n", end="")
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
                current_schedule.extend(new_schedule)
                temp_schedule = current_schedule
                registering_new_student = True
                update_schedule()
                current_schedule.clear()
                clear(100)
                register_new_student()
            case "D":
                clear(100)
                os.system(f"mode con cols={90} lines={45}")
                columns = os.get_terminal_size().columns
                center_console_window()
                registering_new_student = True
                updating_student_details = True
                update_student_details()
                updating_student_details = False
                register_new_student()
            case "Y":
                add_student(student_details)
                add_schedule(new_schedule)
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
    new_schedule.clear()
    check_attendance()


# Function for updating student details
def update_student_details():
    global student_details
    global new_student_details
    global data
    global columns
    global current_str
    global in_update_student_details
    global in_updating_class_schedule
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
        print("\033[8F", end="")
        current_str = student_details[0]
        stud_no = str(limit_input(f"  │  Student No.: ", 8).upper())
        current_str = ""

        # Searching for the student if already exist or registered in database
        cursor.execute(f"SELECT Student_No FROM Student_Info WHERE Student_No = ?", (stud_no,))
        data = cursor.fetchone()

        if data:
            clear(4)
            _details(student_details)
            print(f"{"":<5}MSG: Student({stud_no}) already registered.\n")
            print(("-" * 86).center(90))

            while True:
                key_pressed = input_key(f"{"":<5}Press [Y] to discard changes or [N] to update again. ")
                match key_pressed.upper():
                    case "Y":
                        return
                    case "N":
                        clear(100)
                        return update_student_details()
                    case _:
                        clear(1)
        print("\033[1E", end="")
    else:
        print("\033[7F", end="")

    if not in_updating_class_schedule:
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

        new_student_details = [stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature]

        # Checking if in_register_new_student
        if in_register_new_student:
            student_details = new_student_details
            return
    else:
        print("\033[4E", end="")

    # Checking for changes
    changes = False
    if new_student_details[1] != student_details[1]:
        changes = True
    elif new_student_details[2] != student_details[2]:
        changes = True
    elif new_student_details[3] != student_details[3]:
        changes = True
    elif new_student_details[4] != student_details[4]:
        changes = True
    elif new_student_details[5] != student_details[5]:
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
            case "S":
                student_details = [stud_no, stud_name, stud_department, stud_degree, stud_level, stud_signature]
                update_student(student_details)
                in_updating_class_schedule = True
                update_schedule()
                update_student_details()
            case "N":
                clear(100)
                update_student_details()
            case _:
                clear(1)


# Function for updating schedule
def update_schedule():
    global columns
    global in_update_student_details
    global updating_student_details
    global updating_class_schedule
    global new_schedule
    global current_schedule
    global temp_schedule
    _update_schedule = []

    if not updating_class_schedule and not registering_new_student:  # User not already in updating class schedule
        if not updating_student_details:  # Check if user not in update student details
            current_schedule.clear()
            tab_title("UPDATE SCHEDULE")
            student("Update Schedule")

        # Searching for the schedule of the student
        cursor.execute("SELECT * FROM Class_Schedule WHERE Student_No = ?", (student_details[0],))
        current_schedule = cursor.fetchall()  # Store it as array list
        temp_schedule = current_schedule

        # Display student_details and class_schedule
        display_student_and_class_schedule(current_schedule)

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
                    if in_update_student_details:
                        return
                    else:
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

    print("\033[2E", end="")  # Move cursor down
    clear(9)

    # updating now each class schedule
    for _day in _days:
        _total = 0
        _to_update = []
        for _schedule in current_schedule:
            if _schedule[2] == _day:
                _total += 1
                _to_update.append(_schedule)
        # Calling for function to for updating each course
        _update_schedule.extend(update_course(student_details[0], _day, _total, _to_update, current_schedule))

    # Getting for the other not modified schedule
    for _schedule in temp_schedule:
        if _schedule[2] not in _days:
            _update_schedule.append(_schedule)

    # Temporarily store the updated schedule
    temp_schedule = _update_schedule

    # Sorting the schedule
    _update_schedule = sorted(_update_schedule, key=sort_schedule)

    # If registering_new_student it will return to registration
    if registering_new_student:
        new_schedule = _update_schedule
        return

    # Display student_details and class_schedule
    display_student_and_class_schedule(_update_schedule)

    # Checking now if no schedule has been modified
    changes = False
    if set(_update_schedule) != set(current_schedule):
        changes = True

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
                cursor.execute("DELETE FROM Class_Schedule WHERE Student_No = ?", (student_details[0],))
                add_schedule(_update_schedule)
                connection.commit()
                temp_schedule.clear()
                current_schedule.clear()
                new_schedule.clear()
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
    # Title of console
    console_title = "Student Attendance Management System"

    run_as_administrator()  # Request for administration privilege

    # Check for single instances
    if not is_single_instance(console_title):
        exit()

    set_console_title(console_title)  # Set the title of console
    set_console_size(90, 45)  # Resizing of console
    columns = os.get_terminal_size().columns  # Save the new column size
    center_console_window()  # Align the console to center
    check_attendance()  # Calling now the check_attendance function
