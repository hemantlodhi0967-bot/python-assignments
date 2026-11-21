"""
Assignment-1: Basics of Python Programming
Name    : Hemant Lodhi
Roll No.: 25BME024
"""


# ======================================================================
# Question 1: Basic Python Operations
# Write a Python program to accept two numbers from the user and display their sum, difference, product, quotient and remainder.
# ======================================================================
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

print(f"Sum        : {num1 + num2}")
print(f"Difference : {num1 - num2}")
print(f"Product    : {num1 * num2}")

if num2 != 0:
    print(f"Quotient   : {num1 / num2}")
    print(f"Remainder  : {num1 % num2}")
else:
    print("Quotient and remainder are not defined when the second number is 0.")


# ======================================================================
# Question 2: Lists and Tuples
# Create a list of 10 numbers and add an element, remove an element, insert an element at a specified position, find the maximum and minimum, and convert the list into a tuple.
# ======================================================================
numbers = [12, 45, 7, 23, 89, 34, 56, 3, 71, 18]
print("Original list                  :", numbers)

numbers.append(99)
print("After adding 99                :", numbers)

numbers.remove(7)
print("After removing 7               :", numbers)

numbers.insert(2, 50)
print("After inserting 50 at index 2  :", numbers)

print("Maximum element                :", max(numbers))
print("Minimum element                :", min(numbers))

numbers_tuple = tuple(numbers)
print("List converted to tuple        :", numbers_tuple)
print("Type of result                 :", type(numbers_tuple))


# ======================================================================
# Question 3: Strings
# Write a Python program to accept a string and count its characters, count vowels and consonants, reverse it, and check whether it is a palindrome.
# ======================================================================
def analyse_string(text):
    letters = [ch for ch in text if ch.isalpha()]
    vowel_count = sum(1 for ch in letters if ch.lower() in "aeiou")
    consonant_count = len(letters) - vowel_count

    # Palindrome check ignores spaces, punctuation and upper/lower case
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    is_palindrome = cleaned == cleaned[::-1]

    print(f"Number of characters : {len(text)}")
    print(f"Vowels               : {vowel_count}")
    print(f"Consonants           : {consonant_count}")
    print(f"Reversed string      : {text[::-1]}")
    print(f"Palindrome?          : {'Yes' if is_palindrome else 'No'}")


for _ in range(2):          # run twice to see both a "No" and a "Yes" result
    analyse_string(input("Enter a string: "))
    print("-" * 40)


# ======================================================================
# Question 4: Sets and Dictionaries
# Create two sets of integers and demonstrate union, intersection, difference and symmetric difference. Also create a dictionary containing the names and marks of five students and display the student with the highest marks.
# ======================================================================
set_a = {1, 2, 3, 4, 5, 6}
set_b = {4, 5, 6, 7, 8, 9}
print("Set A                 :", set_a)
print("Set B                 :", set_b)
print("Union                 :", set_a | set_b)
print("Intersection          :", set_a & set_b)
print("Difference (A - B)    :", set_a - set_b)
print("Symmetric difference  :", set_a ^ set_b)

print()
marks = {"Aman": 78, "Riya": 91, "Karan": 66, "Sneha": 85, "Vivek": 73}
print("Student marks:", marks)

top_student = max(marks, key=marks.get)
print(f"Highest marks: {top_student} with {marks[top_student]}")


# ======================================================================
# Question 5: GPA Calculator
# Develop a Python program that accepts the grade / grade point and credit of different courses and calculates the student's SGPA/GPA using GPA = Σ(Grade Point × Credit) / Σ Credits.
# ======================================================================
# 10-point grading scale (change the values if your university uses a different scale)
GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "D": 4, "F": 0}


def to_grade_point(text):
    # Accepts a letter grade (e.g. A+) or a grade point number (e.g. 8.5)
    text = text.strip().upper()
    if text in GRADE_POINTS:
        return GRADE_POINTS[text]
    value = float(text)                      # raises ValueError if not a number
    if not 0 <= value <= 10:
        raise ValueError("grade point must be between 0 and 10")
    return value


num_courses = int(input("Number of courses: "))
total_points = 0
total_credits = 0

for k in range(1, num_courses + 1):
    while True:
        try:
            grade_point = to_grade_point(input(f"Course {k} - grade or grade point: "))
            credit = float(input(f"Course {k} - credits: "))
            if credit <= 0:
                raise ValueError("credits must be positive")
            break
        except ValueError as error:
            print("Invalid input, please try again.", error)
    total_points += grade_point * credit
    total_credits += credit

gpa = total_points / total_credits
print(f"\nΣ(Grade Point × Credit) = {total_points}")
print(f"Σ Credits               = {total_credits}")
print(f"GPA / SGPA              = {gpa:.2f}")


# ======================================================================
# Question 6: Functions and Iteration
# Write separate Python functions to calculate the factorial of a number, generate the Fibonacci series up to n terms, and check whether a number is prime.
# ======================================================================
def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def fibonacci(n):
    series = []
    a, b = 0, 1
    for _ in range(n):
        series.append(a)
        a, b = b, a + b
    return series


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


n = int(input("Enter a number to find its factorial: "))
print(f"Factorial of {n} = {factorial(n)}")

terms = int(input("How many Fibonacci terms? "))
print(f"First {terms} Fibonacci numbers: {fibonacci(terms)}")

for _ in range(2):
    num = int(input("Enter a number to check for prime: "))
    print(f"{num} is {'a prime' if is_prime(num) else 'not a prime'} number.")

print("All primes up to 30:", [k for k in range(31) if is_prime(k)])


# ======================================================================
# Question 7: File Handling
# Write a Python program to create a text file, write student details into it, and subsequently read and display the contents of the file.
# ======================================================================
filename = "students.txt"
count = int(input("How many students do you want to store? "))

# Create the file and write the details
with open(filename, "w") as file:
    file.write("Roll No | Name | Marks\n")
    file.write("-" * 30 + "\n")
    for _ in range(count):
        roll = input("Roll number: ")
        name = input("Name: ")
        marks = input("Marks: ")
        file.write(f"{roll} | {name} | {marks}\n")

# Read the file back and display it
print(f"\nContents of {filename}:\n")
with open(filename, "r") as file:
    print(file.read())


# ======================================================================
# Question 8: Exception Handling
# Write a program that accepts two numbers and performs division using try-except. Handle the division-by-zero exception appropriately.
# ======================================================================
def divide_numbers():
    try:
        a = float(input("Enter the numerator: "))
        b = float(input("Enter the denominator: "))
        result = a / b
    except ZeroDivisionError:
        print("Error: division by zero is not allowed.")
    except ValueError:
        print("Error: please enter valid numbers only.")
    else:
        print(f"{a} / {b} = {result}")
    finally:
        print("Division attempt finished.\n")


# Three runs: normal, division by zero, invalid input
divide_numbers()
divide_numbers()
divide_numbers()


# ======================================================================
# Question 9: List Comprehension
# Using list comprehension, generate the squares of numbers from 1 to 20, the even numbers from 1 to 50, and the numbers divisible by both 3 and 5 from 1 to 100.
# ======================================================================
squares = [x ** 2 for x in range(1, 21)]
evens = [x for x in range(1, 51) if x % 2 == 0]
div_by_3_and_5 = [x for x in range(1, 101) if x % 3 == 0 and x % 5 == 0]

print("Squares of 1 to 20          :", squares)
print("Even numbers from 1 to 50   :", evens)
print("Divisible by both 3 and 5   :", div_by_3_and_5)


# ======================================================================
# Question 10: Mini Programming Problem (Student Record Menu)
# Develop a menu-driven Python program for maintaining a student record using a dictionary. Options: add a student, update marks, search for a student, delete a student, display all student records.
# ======================================================================
records = {}          # roll number -> {"name": ..., "marks": ...}


def read_marks():
    while True:
        try:
            marks = float(input("Enter marks: "))
            if 0 <= marks <= 100:
                return marks
            print("Marks must be between 0 and 100.")
        except ValueError:
            print("Please enter a number.")


def add_student():
    roll = input("Enter roll number: ").strip()
    if roll in records:
        print("A student with this roll number already exists.")
        return
    name = input("Enter name: ").strip()
    records[roll] = {"name": name, "marks": read_marks()}
    print("Student added.")


def update_marks():
    roll = input("Enter roll number: ").strip()
    if roll not in records:
        print("Student not found.")
        return
    records[roll]["marks"] = read_marks()
    print("Marks updated.")


def search_student():
    roll = input("Enter roll number to search: ").strip()
    if roll in records:
        s = records[roll]
        print(f"Found -> Roll No: {roll}, Name: {s['name']}, Marks: {s['marks']}")
    else:
        print("Student not found.")


def delete_student():
    roll = input("Enter roll number to delete: ").strip()
    if records.pop(roll, None) is not None:
        print("Student deleted.")
    else:
        print("Student not found.")


def display_all():
    if not records:
        print("No records to display.")
        return
    print(f"{'Roll No':<10}{'Name':<20}{'Marks':>6}")
    print("-" * 36)
    for roll, s in records.items():
        print(f"{roll:<10}{s['name']:<20}{s['marks']:>6}")


MENU = """
===== Student Record Menu =====
1. Add a student
2. Update marks
3. Search for a student
4. Delete a student
5. Display all students
6. Exit"""

actions = {"1": add_student, "2": update_marks, "3": search_student,
           "4": delete_student, "5": display_all}

while True:
    print(MENU)
    choice = input("Enter your choice (1-6): ").strip()
    if choice == "6":
        print("Goodbye!")
        break
    elif choice in actions:
        actions[choice]()
    else:
        print("Invalid choice, please try again.")
