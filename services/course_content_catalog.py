"""Comprehensive syllabus, concept breakdowns, code examples, coding questions, test cases, and quizzes for popular topics."""
import re
from typing import Dict, Any, List

SYLLABUS_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "java": {
        "name": "Java Programming & Object-Oriented Development",
        "category": "Software & Coding",
        "summary": "Master core Java from basic syntax, data types, and control flow to Object-Oriented Programming (OOP), Collections Framework, and hands-on algorithms.",
        "chapters": [
            {
                "chapter_id": 1,
                "name": "Java Basics: Syntax, Data Types & Variables",
                "about": "Understand JVM, JDK, JRE architecture, primitive and reference types, variables, operators, and basic console I/O.",
                "duration": "15 mins",
                "explanation": "Java is a class-based, object-oriented language designed for high portability via the JVM (Write Once, Run Anywhere). In Java, every application begins execution inside a public static void main(String[] args) method. Variables are strongly typed: primitive types include int, double, boolean, char, and reference types include String, arrays, and objects.",
                "key_takeaways": [
                    "Java requires static typing: variables must declare their type upfront.",
                    "Source code compiles to .class bytecode executed by the Java Virtual Machine (JVM).",
                    "String is immutable in Java; StringBuilder is used for heavy concatenations.",
                    "System.out.println() prints to standard output."
                ],
                "code_examples": [
                    {
                        "title": "Java Fundamentals & Type Casting",
                        "language": "java",
                        "code": """public class Main {
    public static void main(String[] args) {
        int score = 95;
        double gpa = 3.85;
        boolean isEnrolled = true;
        char grade = 'A';
        String studentName = "John Doe";

        System.out.println("Student: " + studentName);
        System.out.println("Score: " + score + ", Grade: " + grade);
        System.out.println("Enrolled: " + isEnrolled);
    }
}""",
                        "explanation": "Demonstrates declaration of primitive types and string concatenation for console output."
                    }
                ],
                "coding_challenge": {
                    "title": "Check Even or Odd",
                    "description": "Write a Java method that accepts an integer number and returns 'Even' if the number is even, and 'Odd' if it is odd.",
                    "starter_code": """public class Solution {
    public static String checkEvenOdd(int n) {
        if (n % 2 == 0) {
            return "Even";
        }
        return "Odd";
    }

    public static void main(String[] args) {
        System.out.println(checkEvenOdd(4));
    }
}""",
                    "language": "java",
                    "test_cases": [
                        {"input": "4", "expected_output": "Even"},
                        {"input": "7", "expected_output": "Odd"},
                        {"input": "0", "expected_output": "Even"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which component of the Java ecosystem is responsible for executing compiled bytecode on the host OS?",
                        "options": ["JDK (Java Development Kit)", "JVM (Java Virtual Machine)", "Javac Compiler", "Java API Library"],
                        "correct_answer": 1,
                        "explanation": "The JVM (Java Virtual Machine) interprets and executes the bytecode (.class files) on the underlying platform, enabling cross-platform portability."
                    },
                    {
                        "question": "What is the key characteristic of Java's String class?",
                        "options": ["Mutable by default", "Immutable", "Inherits from Throwable", "Primitive data type"],
                        "correct_answer": 1,
                        "explanation": "Strings in Java are immutable; any modification creates a new String object in the string pool."
                    }
                ]
            },
            {
                "chapter_id": 2,
                "name": "Control Flow: Conditionals & Loops",
                "about": "Master if-else statements, switch-case constructs, for loops, while loops, and enhanced for-each iterations.",
                "duration": "20 mins",
                "explanation": "Control flow statements direct the order of program execution. Java supports branching via if/else-if/else blocks and switch expressions. Repetition is achieved using while loops (checked before loop), do-while loops (checked after execution), standard for loops (counted loops), and enhanced for-each loops for traversing arrays and collections.",
                "key_takeaways": [
                    "Use if/else for range and boolean conditions, switch for discrete value matching.",
                    "for-each loop syntax: for (Type item : collection) prevents off-by-one errors.",
                    "break immediately terminates the current loop; continue skips to the next iteration."
                ],
                "code_examples": [
                    {
                        "title": "Loops and Array Traversal",
                        "language": "java",
                        "code": """public class LoopsDemo {
    public static void main(String[] args) {
        int[] numbers = {10, 20, 30, 40, 50};
        int sum = 0;

        for (int num : numbers) {
            sum += num;
        }

        System.out.println("Total Sum: " + sum);
        System.out.println("Average: " + (double) sum / numbers.length);
    }
}""",
                        "explanation": "Uses an enhanced for-each loop to calculate the sum and average of an array."
                    }
                ],
                "coding_challenge": {
                    "title": "Factorial Calculator",
                    "description": "Write a Java program to compute the factorial of a non-negative integer n. (0! = 1, 5! = 120).",
                    "starter_code": """public class Solution {
    public static long factorial(int n) {
        long result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(factorial(5));
    }
}""",
                    "language": "java",
                    "test_cases": [
                        {"input": "5", "expected_output": "120"},
                        {"input": "0", "expected_output": "1"},
                        {"input": "3", "expected_output": "6"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which loop guarantees execution of its block at least once regardless of condition?",
                        "options": ["for loop", "while loop", "do-while loop", "for-each loop"],
                        "correct_answer": 2,
                        "explanation": "In a do-while loop, the condition is evaluated after the body executes, ensuring at least one run."
                    },
                    {
                        "question": "What does the 'continue' keyword do inside a loop in Java?",
                        "options": ["Terminates the program", "Skips to the next iteration of the loop", "Exits the loop entirely", "Restarts the loop from index 0"],
                        "correct_answer": 1,
                        "explanation": "'continue' halts the current iteration and jumps directly to the loop condition/increment step."
                    }
                ]
            },
            {
                "chapter_id": 3,
                "name": "Object-Oriented Programming (OOP) in Java",
                "about": "Learn the 4 core pillars of OOP: Encapsulation, Inheritance, Polymorphism, and Abstraction.",
                "duration": "25 mins",
                "explanation": "Java is intrinsically object-oriented. Encapsulation protects object state using private variables and public getters/setters. Inheritance allows code reuse via the extends keyword. Polymorphism allows methods to behave differently based on the calling object (method overloading and method overriding with @Override). Abstraction hides internal complexity using abstract classes and interfaces.",
                "key_takeaways": [
                    "Encapsulation restricts direct variable access and validates mutations.",
                    "Java supports single class inheritance and multiple interface implementations.",
                    "Method overriding requires identical signatures; @Override annotation prevents signature mismatch bugs.",
                    "Interfaces declare contracts without implementation details (prior to Java 8 default methods)."
                ],
                "code_examples": [
                    {
                        "title": "Polymorphism & Inheritance Hierarchy",
                        "language": "java",
                        "code": """abstract class Shape {
    abstract double area();
}

class Circle extends Shape {
    private double radius;
    public Circle(double radius) { this.radius = radius; }
    @Override
    double area() { return Math.PI * radius * radius; }
}

public class OOPDemo {
    public static void main(String[] args) {
        Shape c = new Circle(5.0);
        System.out.printf("Circle Area: %.2f\\n", c.area());
    }
}""",
                        "explanation": "Illustrates runtime polymorphism where an abstract Shape reference holds a Circle instance."
                    }
                ],
                "coding_challenge": {
                    "title": "Reverse an Array In-Place",
                    "description": "Reverse an array of integers in-place without allocating an extra array.",
                    "starter_code": """import java.util.Arrays;

public class Solution {
    public static void reverseArray(int[] arr) {
        int left = 0, right = arr.length - 1;
        while (left < right) {
            int temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;
            left++;
            right--;
        }
    }

    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 4, 5};
        reverseArray(arr);
        System.out.println(Arrays.toString(arr));
    }
}""",
                    "language": "java",
                    "test_cases": [
                        {"input": "[1, 2, 3, 4, 5]", "expected_output": "[5, 4, 3, 2, 1]"},
                        {"input": "[10, 20]", "expected_output": "[20, 10]"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which OOP principle focuses on bundling data and methods while hiding internal representation?",
                        "options": ["Inheritance", "Polymorphism", "Encapsulation", "Recursion"],
                        "correct_answer": 2,
                        "explanation": "Encapsulation restricts direct external access to internal object fields by providing getter and setter methods."
                    },
                    {
                        "question": "Can a Java class extend multiple classes simultaneously?",
                        "options": ["Yes, using the 'extends' keyword with comma separation", "No, Java supports single class inheritance only", "Yes, if both classes are abstract", "Only in Java 17 and above"],
                        "correct_answer": 1,
                        "explanation": "Java prevents multiple class inheritance to avoid the diamond problem, but allows implementing multiple interfaces."
                    }
                ]
            },
            {
                "chapter_id": 4,
                "name": "Java Collections Framework: Lists, Sets & Maps",
                "about": "Harness powerful generic data structures: ArrayList, LinkedList, HashSet, TreeSet, HashMap, and TreeMap.",
                "duration": "25 mins",
                "explanation": "The Collections Framework provides pre-built, high-performance data structures and algorithms. List preserves insertion order and allows duplicates (ArrayList offers O(1) random access; LinkedList is optimal for insertions/deletions). Set guarantees uniqueness (HashSet provides O(1) average lookup using hashing; TreeSet keeps elements sorted via red-black tree). Map stores key-value pairs (HashMap gives O(1) average access).",
                "key_takeaways": [
                    "ArrayList uses dynamic resizing arrays: O(1) indexed reads, O(n) worst-case insertions.",
                    "HashSet relies on hashCode() and equals() to enforce uniqueness.",
                    "HashMap does not maintain order; use LinkedHashMap for insertion order or TreeMap for natural sorting.",
                    "Collections.sort() uses dual-pivot Quicksort/Timsort."
                ],
                "code_examples": [
                    {
                        "title": "Word Frequency Counter with HashMap",
                        "language": "java",
                        "code": """import java.util.HashMap;
import java.util.Map;

public class CollectionsDemo {
    public static void main(String[] args) {
        String[] words = {"apple", "banana", "apple", "cherry", "banana", "apple"};
        Map<String, Integer> counts = new HashMap<>();

        for (String w : words) {
            counts.put(w, counts.getOrDefault(w, 0) + 1);
        }

        System.out.println("Word frequencies: " + counts);
    }
}""",
                        "explanation": "Demonstrates HashMap with getOrDefault() for clean frequency counting."
                    }
                ],
                "coding_challenge": {
                    "title": "Find Maximum in Array",
                    "description": "Find and return the maximum value in an integer array.",
                    "starter_code": """public class Solution {
    public static int findMax(int[] nums) {
        int max = nums[0];
        for (int n : nums) {
            if (n > max) max = n;
        }
        return max;
    }

    public static void main(String[] args) {
        System.out.println(findMax(new int[]{3, 7, 2, 9, 5}));
    }
}""",
                    "language": "java",
                    "test_cases": [
                        {"input": "[3, 7, 2, 9, 5]", "expected_output": "9"},
                        {"input": "[-5, -1, -8]", "expected_output": "-1"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the average time complexity for searching a key in a HashMap in Java?",
                        "options": ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
                        "correct_answer": 2,
                        "explanation": "HashMap uses hash buckets to provide average constant time O(1) retrieval."
                    },
                    {
                        "question": "Which collection should be chosen when element uniqueness is strictly required?",
                        "options": ["ArrayList", "LinkedList", "HashSet", "Vector"],
                        "correct_answer": 2,
                        "explanation": "HashSet implements the Set interface, which strictly prohibits duplicate elements."
                    }
                ]
            },
            {
                "chapter_id": 5,
                "name": "Exception Handling & Robust Systems",
                "about": "Master try-catch-finally, checked vs unchecked exceptions, throw/throws, and custom exceptions.",
                "duration": "20 mins",
                "explanation": "Exception handling in Java separates error-handling code from regular logic. Checked exceptions (subclasses of Exception excluding RuntimeException) are verified at compile-time and must be caught or declared. Unchecked exceptions (subclasses of RuntimeException and Error) occur during execution. The finally block always executes, ideal for closing resources (or use try-with-resources with AutoCloseable).",
                "key_takeaways": [
                    "Checked exceptions force developers to anticipate recoverability at compile-time.",
                    "try-with-resources automatically closes connections, sockets, and file streams.",
                    "Never catch generic Throwable or suppress exceptions with empty catch blocks.",
                    "Custom exceptions should extend Exception (checked) or RuntimeException (unchecked)."
                ],
                "code_examples": [
                    {
                        "title": "Try-With-Resources and Custom Handling",
                        "language": "java",
                        "code": """public class ExceptionDemo {
    public static void validateAge(int age) {
        if (age < 18) {
            throw new IllegalArgumentException("Age must be 18 or older. Provided: " + age);
        }
        System.out.println("Age verified successfully: " + age);
    }

    public static void main(String[] args) {
        try {
            validateAge(15);
        } catch (IllegalArgumentException e) {
            System.out.println("Caught Expected Error: " + e.getMessage());
        } finally {
            System.out.println("Cleanup completed.");
        }
    }
}""",
                        "explanation": "Throws and handles IllegalArgumentException with a guaranteed finally block."
                    }
                ],
                "coding_challenge": {
                    "title": "Palindrome Checker",
                    "description": "Determine if an alphanumeric string is a palindrome (reads identical forwards and backwards), ignoring case.",
                    "starter_code": """public class Solution {
    public static boolean isPalindrome(String s) {
        String clean = s.replaceAll("[^a-zA-Z0-9]", "").toLowerCase();
        int left = 0, right = clean.length() - 1;
        while (left < right) {
            if (clean.charAt(left) != clean.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(isPalindrome("racecar"));
    }
}""",
                    "language": "java",
                    "test_cases": [
                        {"input": "racecar", "expected_output": "true"},
                        {"input": "hello", "expected_output": "false"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which block is guaranteed to execute whether an exception is thrown or caught?",
                        "options": ["catch block", "finally block", "throws block", "try block"],
                        "correct_answer": 1,
                        "explanation": "The 'finally' block always executes after try/catch, guaranteeing cleanup operations."
                    },
                    {
                        "question": "Which of the following is an unchecked (Runtime) exception in Java?",
                        "options": ["IOException", "SQLException", "NullPointerException", "ClassNotFoundException"],
                        "correct_answer": 2,
                        "explanation": "NullPointerException extends RuntimeException and does not need to be explicitly declared in method signatures."
                    }
                ]
            }
        ]
    },
    "python": {
        "name": "Python for Data Science & Backend Development",
        "category": "Technology & Science",
        "summary": "From Python core syntax to list comprehensions, functional programming, data structures, and algorithmic coding challenges.",
        "chapters": [
            {
                "chapter_id": 1,
                "name": "Python Core Syntax, Variables & Data Structures",
                "about": "Learn variables, dynamic typing, lists, tuples, dictionaries, and sets.",
                "duration": "15 mins",
                "explanation": "Python is an interpreted, high-level, dynamically typed language emphasizing code readability. Core collection types include ordered mutable lists, immutable tuples, key-value dictionaries, and unique-element sets.",
                "key_takeaways": [
                    "Dynamic typing: variables are bound to types at runtime.",
                    "Indentation defines block scope instead of curly braces.",
                    "List comprehensions provide concise collection transformations."
                ],
                "code_examples": [
                    {
                        "title": "Dictionary & List Comprehensions",
                        "language": "python",
                        "code": """numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_squares = [x**2 for x in numbers if x % 2 == 0]
print(f"Even squares: {even_squares}")

square_map = {x: x**2 for x in numbers[:5]}
print(f"Square mapping: {square_map}")""",
                        "explanation": "Demonstrates pythonic list and dictionary comprehensions."
                    }
                ],
                "coding_challenge": {
                    "title": "Two Sum Problem",
                    "description": "Given a list of integers and a target sum, return indices of the two numbers that add up to target.",
                    "starter_code": """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

print(two_sum([2, 7, 11, 15], 9))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "nums=[2, 7, 11, 15], target=9", "expected_output": "[0, 1]"},
                        {"input": "nums=[3, 2, 4], target=6", "expected_output": "[1, 2]"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the primary difference between a Python list and a tuple?",
                        "options": ["Lists are immutable; tuples are mutable", "Lists are mutable; tuples are immutable", "Tuples cannot store integers", "Lists require type annotations"],
                        "correct_answer": 1,
                        "explanation": "Lists can have elements modified, added, or removed in place, whereas tuples cannot be modified once created."
                    },
                    {
                        "question": "What is the output of len(set([1, 2, 2, 3, 3, 3]))?",
                        "options": ["6", "3", "1", "Error"],
                        "correct_answer": 1,
                        "explanation": "Sets only store unique elements, so duplicate values are automatically discarded, leaving {1, 2, 3}."
                    }
                ]
            },
            {
                "chapter_id": 2,
                "name": "Functions, Lambdas & Modular Programming",
                "about": "Master *args, **kwargs, decorators, generator expressions, and modules.",
                "duration": "20 mins",
                "explanation": "Functions in Python are first-class citizens. They can be passed as arguments, assigned to variables, and returned from other functions. Decorators wrap functions to add cross-cutting behavior like logging, timing, and authentication.",
                "key_takeaways": [
                    "Functions use def keyword; lambdas are anonymous single-expression functions.",
                    "Use *args for variable positional arguments and **kwargs for keyword arguments.",
                    "Generators use yield for memory-efficient lazy evaluation."
                ],
                "code_examples": [
                    {
                        "title": "Custom Decorator for Function Timing",
                        "language": "python",
                        "code": """import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"[{func.__name__}] took {duration:.6f}s")
        return result
    return wrapper

@timing_decorator
def compute_sum(n):
    return sum(range(n))

print(f"Result: {compute_sum(100000)}")""",
                        "explanation": "Shows how Python decorators enhance function behavior transparently."
                    }
                ],
                "coding_challenge": {
                    "title": "Valid Anagram",
                    "description": "Given two strings s and t, return True if t is an anagram of s, and False otherwise.",
                    "starter_code": """def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    for char in t:
        if char not in counts or counts[char] == 0:
            return False
        counts[char] -= 1
    return True

print(is_anagram("anagram", "nagaram"))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "s='anagram', t='nagaram'", "expected_output": "True"},
                        {"input": "s='rat', t='car'", "expected_output": "False"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the main benefit of using a generator function with 'yield'?",
                        "options": ["Faster compile time", "Memory-efficient lazy evaluation", "Automatic multithreading", "Type safety enforcement"],
                        "correct_answer": 1,
                        "explanation": "'yield' produces values on demand one at a time, avoiding storing entire large sequences in memory."
                    },
                    {
                        "question": "In Python function signatures, what does **kwargs collect?",
                        "options": ["Arbitrary positional arguments as a tuple", "Arbitrary keyword arguments as a dictionary", "Global variables", "Return types"],
                        "correct_answer": 1,
                        "explanation": "**kwargs packages any extra named keyword arguments passed to the function into a dictionary."
                    }
                ]
            },
            {
                "chapter_id": 3,
                "name": "Object-Oriented Python: Classes & Dunder Methods",
                "about": "Master class definitions, __init__, __str__, __repr__, inheritance, and encapsulation with properties.",
                "duration": "25 mins",
                "explanation": "Everything in Python is an object. Classes define blueprints with attributes and methods. Special double-underscore ('dunder') methods allow classes to hook into Python operators like string representation (__str__), equality (__eq__), and length (__len__).",
                "key_takeaways": [
                    "__init__ is the instance constructor called on creation.",
                    "self explicitly represents the instance accessing attributes and methods.",
                    "@property allows defining getters and setters cleanly."
                ],
                "code_examples": [
                    {
                        "title": "Custom Class with Properties and Dunder Methods",
                        "language": "python",
                        "code": """class BankAccount:
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float):
        if amount > 0:
            self._balance += amount

    def __str__(self):
        return f"Account({self.owner}, Balance: ${self._balance:.2f})"

acc = BankAccount("Alice", 250.0)
acc.deposit(50.0)
print(acc)""",
                        "explanation": "Demonstrates @property decorator and custom __str__ method."
                    }
                ],
                "coding_challenge": {
                    "title": "Reverse a String",
                    "description": "Write a Python function that takes a string and returns it reversed.",
                    "starter_code": """def reverse_string(s: str) -> str:
    return s[::-1]

print(reverse_string('developer'))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "developer", "expected_output": "repoleved"},
                        {"input": "python", "expected_output": "nohtyp"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which method is automatically called when creating a new object instance in Python?",
                        "options": ["__call__", "__init__", "__new__", "__start__"],
                        "correct_answer": 1,
                        "explanation": "__init__ serves as the class constructor in Python to initialize instance attributes."
                    },
                    {
                        "question": "What does the @property decorator enable?",
                        "options": ["Defines a method to be accessed like an attribute", "Makes a method static", "Caches return values in Redis", "Protects class from inheritance"],
                        "correct_answer": 0,
                        "explanation": "@property turns a method into a getter, allowing attribute-style access with validation logic."
                    }
                ]
            }
,
            {
                "chapter_id": 4,
                "name": "File Handling, Context Managers & Exception Management",
                "about": "Master reading and writing files safely with 'with' statements, creating custom context managers, and handling exceptions.",
                "duration": "20 mins",
                "explanation": "Resource management in Python is cleanly handled using context managers (the 'with' keyword). This ensures file descriptors, network sockets, and database connections are deterministically closed even if an unhandled exception occurs.",
                "key_takeaways": [
                    "Use 'with open(...) as f' to guarantee automatic file closing.",
                    "Handle specific exceptions first using try/except/else/finally blocks.",
                    "Implement __enter__ and __exit__ to define custom context managers."
                ],
                "code_examples": [
                    {
                        "title": "Safe File I/O and Custom Context Manager",
                        "language": "python",
                        "code": """class ManagedFile:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.file = open(self.filename, 'w')
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

with ManagedFile('output.txt') as f:
    f.write('Python context managers guarantee deterministic cleanup.')
print('File written and closed safely.')""",
                        "explanation": "Illustrates custom context manager protocols and resource safety."
                    }
                ],
                "coding_challenge": {
                    "title": "Safe Integer Conversion",
                    "description": "Write a function that safely converts a string to an integer, returning None if ValueError is raised.",
                    "starter_code": """def safe_int(value: str):
    try:
        return int(value)
    except ValueError:
        return None

print(safe_int('123'))
print(safe_int('invalid'))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "value='42'", "expected_output": "42"},
                        {"input": "value='abc'", "expected_output": "None"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which special methods must a class implement to support the 'with' statement?",
                        "options": ["__start__ and __stop__", "__enter__ and __exit__", "__open__ and __close__", "__init__ and __del__"],
                        "correct_answer": 1,
                        "explanation": "The context management protocol requires defining __enter__ and __exit__ methods."
                    },
                    {
                        "question": "When does the 'else' block of a try-except structure execute?",
                        "options": ["Always", "Only if an exception is caught", "Only if no exception was raised in the try block", "Never"],
                        "correct_answer": 2,
                        "explanation": "The 'else' block executes only if the 'try' block completes successfully without raising any exceptions."
                    }
                ]
            },
            {
                "chapter_id": 5,
                "name": "Advanced Python: Iterators, Generators & Functional Tools",
                "about": "Explore iterator protocols, infinite stream generators, functools (lru_cache, partial), and high-performance list comprehension.",
                "duration": "25 mins",
                "explanation": "Advanced Python leverages lazy evaluation through generators, memoization with @functools.lru_cache, and first-class functions. Writing performant Python requires minimizing unnecessary memory allocations and taking advantage of built-in C-optimized iteration protocols.",
                "key_takeaways": [
                    "Generators yield one item at a time, keeping memory footprint constant regardless of dataset size.",
                    "@functools.lru_cache transparently caches expensive function results for fast repeated lookups.",
                    "Itertools provides composable combinatoric and streaming iteration utilities."
                ],
                "code_examples": [
                    {
                        "title": "Infinite Fibonacci Generator and LRU Cache",
                        "language": "python",
                        "code": """import functools

@functools.lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def fib_stream(limit: int):
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b

print('First 6 Fibonacci numbers:', list(fib_stream(6)))
print('Fibonacci(30):', fibonacci(30))""",
                        "explanation": "Combines a lazy generator function with memoized recursion via @lru_cache."
                    }
                ],
                "coding_challenge": {
                    "title": "Prime Number Generator",
                    "description": "Write a generator function that yields prime numbers up to n.",
                    "starter_code": """def generate_primes(n: int):
    for num in range(2, n + 1):
        if all(num % i != 0 for i in range(2, int(num**0.5) + 1)):
            yield num

print(list(generate_primes(20)))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "n=10", "expected_output": "[2, 3, 5, 7]"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the primary benefit of @functools.lru_cache?",
                        "options": ["Compresses string inputs", "Saves and reuses previous function return values to eliminate redundant computation", "Forces multiprocessing", "Encrypts return values"],
                        "correct_answer": 1,
                        "explanation": "LRU (Least Recently Used) cache stores the results of function calls keyed by arguments, preventing duplicate work."
                    },
                    {
                        "question": "Which built-in function advances an iterator to retrieve its next value?",
                        "options": ["advance()", "step()", "next()", "yield()"],
                        "correct_answer": 2,
                        "explanation": "Calling next(iterator) invokes the iterator's __next__() method to yield the next available item."
                    }
                ]
            }
        ]
    },
    "javascript": {
        "name": "Modern JavaScript (ES6+) & Frontend Architecture",
        "category": "Web & Software",
        "summary": "Master modern JavaScript from arrow functions, destructuring, and closures to Promises, Async/Await, and DOM manipulation.",
        "chapters": [
            {
                "chapter_id": 1,
                "name": "Modern JS Syntax: ES6+, Destructuring & Closures",
                "about": "Understand let/const scoping, template literals, destructuring, spread/rest operators, and lexical closures.",
                "duration": "20 mins",
                "explanation": "ES6 revolutionized JavaScript by introducing block-scoped declarations (let and const), concise arrow functions that preserve lexical 'this', destructuring assignment for extracting object/array values, and closures where functions retain access to their outer lexical environment.",
                "key_takeaways": [
                    "Prefer const by default, let when reassigning; avoid var due to hoisting pitfalls.",
                    "Arrow functions do not bind their own 'this' or 'arguments'.",
                    "Destructuring cleanly extracts properties into standalone variables."
                ],
                "code_examples": [
                    {
                        "title": "ES6 Destructuring and Spread Operators",
                        "language": "javascript",
                        "code": """const user = { id: 101, username: 'dev_pro', role: 'Engineer' };
const { username, role } = user;
console.log(`User: ${username}, Role: ${role}`);

const skills = ['React', 'Node.js'];
const expandedSkills = [...skills, 'TypeScript', 'Docker'];
console.log(expandedSkills);""",
                        "explanation": "Illustrates object destructuring and array spreading."
                    }
                ],
                "coding_challenge": {
                    "title": "Array Filter and Map",
                    "description": "Write a JavaScript function that doubles all positive numbers in an array and returns the new array.",
                    "starter_code": """function doublePositives(arr) {
    return arr.filter(n => n > 0).map(n => n * 2);
}

console.log(JSON.stringify(doublePositives([-2, 3, 5, -1, 4])));""",
                    "language": "javascript",
                    "test_cases": [
                        {"input": "[-2, 3, 5, -1, 4]", "expected_output": "[6,10,8]"},
                        {"input": "[-1, -2]", "expected_output": "[]"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the main difference between 'let' and 'const' in JavaScript?",
                        "options": ["let is function-scoped; const is block-scoped", "const cannot be reassigned; let can be reassigned", "const is hoisted; let is not", "let only stores numbers"],
                        "correct_answer": 1,
                        "explanation": "Variables declared with 'const' cannot be reassigned after declaration, while 'let' allows reassignment."
                    },
                    {
                        "question": "What does a closure in JavaScript represent?",
                        "options": ["A function bundled with references to its surrounding lexical state", "A database connection pool", "An HTML event listener", "An encrypted token"],
                        "correct_answer": 0,
                        "explanation": "A closure gives an inner function access to its outer enclosing scope even after the outer function has finished executing."
                    }
                ]
            },
            {
                "chapter_id": 2,
                "name": "Asynchronous Programming: Promises & Async/Await",
                "about": "Master the JavaScript event loop, microtask queue, Promise chaining, and async/await error handling.",
                "duration": "25 mins",
                "explanation": "JavaScript is single-threaded and non-blocking, orchestrated by the Event Loop. Asynchronous operations like HTTP requests (fetch) and file I/O execute via Promises. Async/await provides synchronous-looking syntax over Promises with standard try/catch blocks.",
                "key_takeaways": [
                    "Promises have 3 states: Pending, Fulfilled, and Rejected.",
                    "async functions always return a Promise implicitly.",
                    "Use Promise.all() to run concurrent independent asynchronous operations."
                ],
                "code_examples": [
                    {
                        "title": "Async/Await with Error Handling",
                        "language": "javascript",
                        "code": """async function fetchUserData(userId) {
    try {
        console.log(`Fetching profile for ${userId}...`);
        const mockResponse = { id: userId, status: 'Active', score: 98 };
        return mockResponse;
    } catch (err) {
        console.error('Fetch error:', err);
    }
}

fetchUserData(42).then(data => console.log('Loaded:', data));""",
                        "explanation": "Shows an async function returning a Promise and structured with try/catch."
                    }
                ],
                "coding_challenge": {
                    "title": "Count Vowels in String",
                    "description": "Write a JavaScript function that counts how many vowels (a, e, i, o, u) exist in a string.",
                    "starter_code": """function countVowels(str) {
    const vowels = 'aeiouAEIOU';
    let count = 0;
    for (let char of str) {
        if (vowels.includes(char)) count++;
    }
    return count;
}

console.log(countVowels('JavaScript'));""",
                    "language": "javascript",
                    "test_cases": [
                        {"input": "JavaScript", "expected_output": "3"},
                        {"input": "xyz", "expected_output": "0"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What does an 'async' keyword in front of a function declaration guarantee?",
                        "options": ["The function runs on a separate CPU thread", "The function automatically returns a Promise", "The function executes synchronously", "It ignores runtime exceptions"],
                        "correct_answer": 1,
                        "explanation": "Marking a function 'async' guarantees that its return value is wrapped in a resolved Promise."
                    },
                    {
                        "question": "Which method is best for executing multiple promises in parallel and failing fast if any fails?",
                        "options": ["Promise.all()", "Promise.race()", "Promise.resolve()", "Promise.any()"],
                        "correct_answer": 0,
                        "explanation": "Promise.all() accepts an iterable of promises and fulfills when all fulfill, or rejects as soon as one rejects."
                    }
                ]
            }
,
            {
                "chapter_id": 3,
                "name": "DOM Manipulation, Event Bubbling & Browser APIs",
                "about": "Learn document query selection, event listeners, bubbling vs capturing, and local storage state persistence.",
                "duration": "20 mins",
                "explanation": "The Document Object Model (DOM) represents the page hierarchy as a tree of nodes. Efficient web applications minimize direct layout thrashing, leverage event delegation on parent containers, and store lightweight client state using localStorage and sessionStorage.",
                "key_takeaways": [
                    "Event bubbling propagates events upwards from target element to root document.",
                    "Use event delegation on parent elements to handle dynamic child elements efficiently.",
                    "localStorage persists across sessions; sessionStorage clears when tab closes."
                ],
                "code_examples": [
                    {
                        "title": "Event Delegation Pattern",
                        "language": "javascript",
                        "code": """// Event delegation on a list container
const listContainer = document.querySelector('#todoList');
if (listContainer) {
    listContainer.addEventListener('click', (event) => {
        if (event.target && event.target.matches('button.delete-btn')) {
            const itemId = event.target.dataset.id;
            console.log(`Deleting item ${itemId}`);
        }
    });
}""",
                        "explanation": "Single event listener handles clicks for all current and future child buttons."
                    }
                ],
                "coding_challenge": {
                    "title": "Parse Query String",
                    "description": "Write a JavaScript function that parses a query string into a key-value object.",
                    "starter_code": """function parseQuery(queryString) {
    const params = new URLSearchParams(queryString);
    return Object.fromEntries(params.entries());
}

console.log(parseQuery('?name=Alex&role=Engineer'));""",
                    "language": "javascript",
                    "test_cases": [
                        {"input": "'?topic=react&level=pro'", "expected_output": "{'topic':'react','level':'pro'}"}
                    ]
                },
                "quiz": [
                    {
                        "question": "In the standard DOM event flow, which phase executes first?",
                        "options": ["Bubbling phase", "Capturing phase", "Target phase", "Dispatch phase"],
                        "correct_answer": 1,
                        "explanation": "Events first travel down from the window to the target in the Capturing phase, then reach the target, and finally bubble upwards."
                    },
                    {
                        "question": "What is the primary architectural benefit of event delegation?",
                        "options": ["Reduces memory overhead by avoiding attaching listeners to every individual element", "Enables multithreading in V8", "Disables browser caching", "Encrypts DOM nodes"],
                        "correct_answer": 0,
                        "explanation": "Attaching one listener to a parent avoids hundreds of individual listeners on dynamic children."
                    }
                ]
            },
            {
                "chapter_id": 4,
                "name": "Node.js Runtime Architecture, Modules & Express APIs",
                "about": "Master the Node.js V8 engine, CommonJS vs ES Modules, file system (fs) streams, and building REST APIs with Express.",
                "duration": "25 mins",
                "explanation": "Node.js provides an asynchronous, event-driven JavaScript runtime outside the browser. With non-blocking libuv I/O and the Express.js framework, developers build high-throughput microservices and RESTful APIs.",
                "key_takeaways": [
                    "Node.js uses the libuv thread pool for asynchronous background I/O.",
                    "Express middleware functions process requests sequentially via the next() function.",
                    "Always sanitize and validate incoming request payloads before business logic execution."
                ],
                "code_examples": [
                    {
                        "title": "Express.js RESTful Router with Middleware",
                        "language": "javascript",
                        "code": """const express = require('express');
const app = express();
app.use(express.json());

app.get('/api/users/:id', (req, res) => {
    const userId = req.params.id;
    res.json({ id: userId, username: 'dev_user', status: 'Active' });
});

app.post('/api/users', (req, res) => {
    const { name, email } = req.body;
    if (!name || !email) {
        return res.status(400).json({ error: 'Name and email are required' });
    }
    res.status(201).json({ id: 101, name, email });
});""",
                        "explanation": "Defines parameterized GET and validated POST endpoints in Express."
                    }
                ],
                "coding_challenge": {
                    "title": "Validate Email Format",
                    "description": "Write a function that returns true if a given email has valid format, false otherwise.",
                    "starter_code": """function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

console.log(isValidEmail('test@example.com'));""",
                    "language": "javascript",
                    "test_cases": [
                        {"input": "'alex@gmail.com'", "expected_output": "true"},
                        {"input": "'invalid-email'", "expected_output": "false"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which C++ library provides the event loop and asynchronous thread pool in Node.js?",
                        "options": ["Boost", "libuv", "glibc", "V8 Engine"],
                        "correct_answer": 1,
                        "explanation": "libuv is the multi-platform support library focusing on asynchronous I/O and the thread pool in Node.js."
                    },
                    {
                        "question": "What is the purpose of the 'next()' function in Express middleware?",
                        "options": ["Terminates the HTTP connection", "Passes control to the next middleware function in the stack", "Restarts the server", "Flushes the Redis cache"],
                        "correct_answer": 1,
                        "explanation": "Calling next() tells Express to execute the subsequent middleware in the pipeline."
                    }
                ]
            },
            {
                "chapter_id": 5,
                "name": "Modern Frontend Framework Architecture & State Flow",
                "about": "Understand Virtual DOM diffing, component lifecycle, unidirectional data flow, and state stores.",
                "duration": "25 mins",
                "explanation": "Modern frontend architectures (React, Vue, Angular) decompose complex user interfaces into isolated, composable components. Unidirectional data flow ensures predictable updates, while Virtual DOM reconciliation calculates minimal browser DOM patches.",
                "key_takeaways": [
                    "Props flow downwards; events and callbacks bubble state updates upwards.",
                    "Virtual DOM reconciliation computes optimal DOM diffs, avoiding expensive reflows.",
                    "Immutable state updates prevent unintended side effects and stale renders."
                ],
                "code_examples": [
                    {
                        "title": "Custom Reactive State Store (Observer Pattern)",
                        "language": "javascript",
                        "code": """class Store {
    constructor(initialState) {
        this.state = initialState;
        this.listeners = [];
    }
    getState() { return this.state; }
    subscribe(listener) { this.listeners.push(listener); }
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.listeners.forEach(cb => cb(this.state));
    }
}

const userStore = new Store({ name: 'Alex', loggedIn: true });
userStore.subscribe(state => console.log('State updated:', state));
userStore.setState({ role: 'Lead Architect' });""",
                        "explanation": "Implements an immutable state store using the classic observer pattern."
                    }
                ],
                "coding_challenge": {
                    "title": "Deep Clone Object",
                    "description": "Write a function that creates a deep clone of a plain object.",
                    "starter_code": """function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

const original = { a: 1, b: { c: 2 } };
const copy = deepClone(original);
console.log(copy.b.c === 2);""",
                    "language": "javascript",
                    "test_cases": [
                        {"input": "{'x': 10, 'y': {'z': 20}}", "expected_output": "{'x':10,'y':{'z':20}}"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the primary purpose of the Virtual DOM in modern UI frameworks?",
                        "options": ["To eliminate the need for CSS", "To batch DOM updates and minimize expensive browser repaints/reflows", "To compile JavaScript to native C code", "To enforce strict typing"],
                        "correct_answer": 1,
                        "explanation": "The Virtual DOM calculates minimal diffs in memory, applying only necessary mutations to the real browser DOM."
                    },
                    {
                        "question": "In unidirectional data flow, how do parent and child components communicate?",
                        "options": ["Parent passes props down; child triggers callbacks up", "Child modifies parent memory directly", "Components share global unrestricted pointers", "Via HTTP WebSockets only"],
                        "correct_answer": 0,
                        "explanation": "Unidirectional data flow mandates data passes down via props and state mutations notify upwards via callbacks."
                    }
                ]
            }
        ]
    },
    "machine learning": {
        "name": "Machine Learning Foundations & Deep Learning Systems",
        "category": "AI & Data Science",
        "summary": "Master core machine learning principles, feature engineering, neural networks, Sentence-BERT semantic models, and model evaluation.",
        "chapters": [
            {
                "chapter_id": 1,
                "name": "ML Pipeline: Data Preprocessing & Feature Engineering",
                "about": "Understand training/validation splits, normalization, categorical encoding, and semantic vector embeddings.",
                "duration": "20 mins",
                "explanation": "Machine learning systems learn mapping functions from input features to target predictions. Data preprocessing ensures models receive clean, scaled inputs without data leakage. Feature scaling (MinMaxScaler, StandardScaler) and text embeddings (such as Sentence-BERT) convert unstructured content into dense vector representations.",
                "key_takeaways": [
                    "Always split data into train, validation, and test sets before fitting transformers.",
                    "High-cardinality categorical features can be encoded using embeddings or target encoding.",
                    "Dense sentence embeddings preserve semantic relationships via cosine similarity."
                ],
                "code_examples": [
                    {
                        "title": "Cosine Similarity for Embedding Comparison",
                        "language": "python",
                        "code": """import math

def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm1 * norm2) if (norm1 * norm2) > 0 else 0.0

emb1 = [0.8, 0.6, 0.1]
emb2 = [0.75, 0.65, 0.05]
print(f"Similarity: {cosine_similarity(emb1, emb2):.4f}")""",
                        "explanation": "Computes cosine similarity between two dense embedding vectors."
                    }
                ],
                "coding_challenge": {
                    "title": "Calculate Mean Squared Error (MSE)",
                    "description": "Calculate the Mean Squared Error between true values and predicted values.",
                    "starter_code": """def calculate_mse(y_true, y_pred):
    n = len(y_true)
    return sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred)) / n

print(f"{calculate_mse([1.0, 2.0, 3.0], [1.1, 1.9, 3.2]):.4f}")""",
                    "language": "python",
                    "test_cases": [
                        {"input": "y_true=[1.0, 2.0, 3.0], y_pred=[1.0, 2.0, 3.0]", "expected_output": "0.0000"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the primary danger of normalizing features using statistics calculated from the entire dataset before splitting?",
                        "options": ["High memory consumption", "Data leakage from test to train set", "Syntax errors", "Gradient explosion"],
                        "correct_answer": 1,
                        "explanation": "Fitting scalers on test data leaks future information into the training phase, giving falsely optimistic evaluations."
                    },
                    {
                        "question": "In semantic vector spaces, what metric measures the orientation angle between two embedding vectors?",
                        "options": ["Euclidean distance", "Cosine similarity", "Manhattan distance", "Hamming distance"],
                        "correct_answer": 1,
                        "explanation": "Cosine similarity calculates the cosine of the angle between two vectors, normalized between -1 and 1."
                    }
                ]
            },
            {
                "chapter_id": 2,
                "name": "Supervised Learning: Classification & Model Evaluation",
                "about": "Master Logistic Regression, Decision Trees, Precision, Recall, F1-Score, and ROC-AUC curves.",
                "duration": "25 mins",
                "explanation": "Supervised classification assigns input instances into discrete classes. Because accuracy is misleading on imbalanced datasets, practitioners evaluate Precision (exactness), Recall (completeness), and F1-Score (harmonic mean).",
                "key_takeaways": [
                    "Accuracy is inadequate for imbalanced datasets; use Precision, Recall, and F1.",
                    "Regularization (L1/L2) penalizes large weights to mitigate overfitting.",
                    "Cross-validation provides robust generalization estimates."
                ],
                "code_examples": [
                    {
                        "title": "Precision and Recall Calculation",
                        "language": "python",
                        "code": """def evaluate_classification(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return {"precision": precision, "recall": recall, "f1": f1}

print(evaluate_classification(80, 20, 10))""",
                        "explanation": "Computes Precision, Recall, and F1-score from a confusion matrix."
                    }
                ],
                "coding_challenge": {
                    "title": "Accuracy Metric Calculation",
                    "description": "Calculate prediction accuracy as the ratio of correct predictions to total samples.",
                    "starter_code": """def calculate_accuracy(y_true, y_pred):
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    return round(correct / len(y_true), 2)

print(calculate_accuracy([1, 0, 1, 1], [1, 0, 0, 1]))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "y_true=[1, 0, 1, 1], y_pred=[1, 0, 0, 1]", "expected_output": "0.75"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which evaluation metric is the harmonic mean of Precision and Recall?",
                        "options": ["Accuracy", "ROC-AUC", "F1-Score", "Mean Absolute Error"],
                        "correct_answer": 2,
                        "explanation": "F1-Score combines Precision and Recall through harmonic mean, penalizing extreme trade-offs."
                    },
                    {
                        "question": "What is the primary role of L2 (Ridge) regularization?",
                        "options": ["Zeroes out non-informative features completely", "Penalizes squared magnitude of weights to prevent overfitting", "Speeds up data loading", "Performs one-hot encoding"],
                        "correct_answer": 1,
                        "explanation": "L2 regularization adds a penalty proportional to the square of model coefficients, shrinking weights smoothly."
                    }
                ]
            }
,
            {
                "chapter_id": 3,
                "name": "Unsupervised Learning: Clustering (K-Means) & PCA",
                "about": "Discover hidden structures in unlabeled data using K-Means clustering, hierarchical clustering, and Principal Component Analysis.",
                "duration": "25 mins",
                "explanation": "Unsupervised learning extracts latent patterns, groupings, and low-dimensional representations without labeled ground truth. K-Means partitions feature spaces into Voronoi cells around cluster centroids, while PCA rotates axes to maximize variance and compress high-dimensional feature vectors.",
                "key_takeaways": [
                    "K-Means minimizes within-cluster sum of squares (inertia).",
                    "The Elbow method and Silhouette score guide the optimal number of clusters (k).",
                    "PCA projects data onto orthogonal principal components to reduce dimensionality without heavy information loss."
                ],
                "code_examples": [
                    {
                        "title": "Euclidean Distance and Centroid Assignment",
                        "language": "python",
                        "code": """import math

def euclidean_distance(p1, p2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

centroids = [[1.0, 1.0], [5.0, 5.0]]
sample = [2.0, 1.5]

distances = [euclidean_distance(sample, c) for c in centroids]
assigned_cluster = distances.index(min(distances))
print(f'Sample {sample} assigned to Centroid {assigned_cluster}')""",
                        "explanation": "Calculates distance to centroids to determine cluster assignment."
                    }
                ],
                "coding_challenge": {
                    "title": "Find Nearest Neighbor",
                    "description": "Given a query point and a list of points, return the point with the smallest Euclidean distance.",
                    "starter_code": """def nearest_point(query, points):
    def dist(p):
        return sum((a - b) ** 2 for a, b in zip(query, p))
    return min(points, key=dist)

print(nearest_point([0, 0], [[5, 5], [1, 1], [3, 2]]))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "query=[0, 0], points=[[5, 5], [1, 1], [3, 2]]", "expected_output": "[1, 1]"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the primary mathematical objective of Principal Component Analysis (PCA)?",
                        "options": ["To maximize target classification accuracy", "To find orthogonal directions of maximum variance in the feature space", "To remove outliers from datasets", "To generate synthetic training data"],
                        "correct_answer": 1,
                        "explanation": "PCA identifies principal axes along which variance is maximized, minimizing projection reconstruction error."
                    },
                    {
                        "question": "Which heuristic is commonly used to pick the number of clusters (k) in K-Means?",
                        "options": ["The Gini Impurity index", "The Elbow Method on within-cluster sum of squares", "The Softmax distribution", "The ROC curve"],
                        "correct_answer": 1,
                        "explanation": "The Elbow Method plots inertia against k to detect the point of diminishing returns."
                    }
                ]
            },
            {
                "chapter_id": 4,
                "name": "Deep Learning Foundations: Neural Networks & PyTorch",
                "about": "Understand artificial neurons, activation functions (ReLU, Sigmoid), backpropagation, gradient descent, and training loops.",
                "duration": "30 mins",
                "explanation": "Deep learning architectures chain non-linear affine transformations across multiple layers. The backpropagation algorithm computes analytical gradients of the loss function via the calculus chain rule, enabling stochastic gradient descent (SGD/Adam) to update millions of parameters.",
                "key_takeaways": [
                    "Activation functions introduce non-linearity, allowing networks to approximate arbitrary functions.",
                    "Backpropagation applies the chain rule to compute loss gradients with respect to every weight.",
                    "Optimizers like Adam combine momentum and adaptive learning rates for fast, stable convergence."
                ],
                "code_examples": [
                    {
                        "title": "Single Neuron Forward Pass with ReLU",
                        "language": "python",
                        "code": """def relu(x):
    return max(0.0, x)

def forward_neuron(inputs, weights, bias):
    total = sum(i * w for i, w in zip(inputs, weights)) + bias
    return relu(total)

x = [0.5, 0.8, -0.2]
w = [0.4, -0.6, 1.2]
b = 0.1
print('Neuron Output:', forward_neuron(x, w, b))""",
                        "explanation": "Computes affine sum plus bias through non-linear ReLU activation."
                    }
                ],
                "coding_challenge": {
                    "title": "Compute Cross-Entropy Loss",
                    "description": "Calculate binary cross-entropy loss given ground truth y (0 or 1) and predicted probability p.",
                    "starter_code": """import math

def binary_cross_entropy(y_true, y_pred):
    eps = 1e-15
    p = max(eps, min(1.0 - eps, y_pred))
    return - (y_true * math.log(p) + (1.0 - y_true) * math.log(1.0 - p))

print(f'{binary_cross_entropy(1, 0.9):.4f}')""",
                    "language": "python",
                    "test_cases": [
                        {"input": "y_true=1, y_pred=1.0", "expected_output": "0.0000"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Why are non-linear activation functions essential in deep neural networks?",
                        "options": ["They speed up data serialization", "Without non-linearity, stacking multiple layers collapses mathematically into a single linear transformation", "They eliminate floating point errors", "They prevent learning rate decay"],
                        "correct_answer": 1,
                        "explanation": "A composition of linear functions is just another linear function; non-linearities allow networks to learn complex curves and boundaries."
                    },
                    {
                        "question": "Which algorithm computes gradients of the loss function with respect to weights using the chain rule?",
                        "options": ["Dijkstra's algorithm", "Backpropagation", "K-Means", "A* search"],
                        "correct_answer": 1,
                        "explanation": "Backpropagation recursively propagates errors from the output layer backwards through hidden layers."
                    }
                ]
            },
            {
                "chapter_id": 5,
                "name": "MLOps, Model Serialization & Production Inference APIs",
                "about": "Package trained models with ONNX, containerize inference with FastAPI, and monitor data drift in production.",
                "duration": "25 mins",
                "explanation": "Productionizing machine learning requires reliable serving pipelines. MLOps bridges data science and software engineering by standardizing model versioning (MLflow), efficient serialization (ONNX/TorchScript), low-latency inference APIs (FastAPI), and continuous telemetry for concept drift.",
                "key_takeaways": [
                    "Export models to standardized formats (ONNX) for cross-platform hardware acceleration.",
                    "Expose predictions through lightweight REST APIs with request validation (Pydantic).",
                    "Monitor input distributions over time to catch covariate shift and model performance degradation."
                ],
                "code_examples": [
                    {
                        "title": "FastAPI Model Inference Endpoint",
                        "language": "python",
                        "code": """from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictionRequest(BaseModel):
    features: list[float]

@app.post('/predict')
def predict(req: PredictionRequest):
    # Simulated model inference
    score = sum(req.features) / len(req.features) if req.features else 0.0
    return {'prediction': 1 if score > 0.5 else 0, 'confidence': round(score, 4)}""",
                        "explanation": "Lightweight, production-ready inference API with typed request validation."
                    }
                ],
                "coding_challenge": {
                    "title": "Normalize Feature Vector",
                    "description": "Write a function that normalizes a feature vector so its sum of squares equals 1.0 (L2 norm).",
                    "starter_code": """import math

def l2_normalize(vector):
    norm = math.sqrt(sum(x**2 for x in vector))
    if norm == 0:
        return vector
    return [round(x / norm, 4) for x in vector]

print(l2_normalize([3.0, 4.0]))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "[3.0, 4.0]", "expected_output": "[0.6, 0.8]"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the primary danger when production input data distribution changes from training data?",
                        "options": ["Syntax errors", "Concept drift / Data drift causing model degradation", "CPU overheating", "Corrupted git commits"],
                        "correct_answer": 1,
                        "explanation": "Data drift occurs when real-world distributions shift, invalidating the statistical patterns the model learned."
                    },
                    {
                        "question": "What is the main benefit of ONNX (Open Neural Network Exchange)?",
                        "options": ["An open format that allows models trained in any framework to run on diverse hardware runtimes", "A new relational database", "A replacement for HTTP", "An encryption algorithm"],
                        "correct_answer": 0,
                        "explanation": "ONNX provides an open standard for machine learning interoperability between training frameworks and inference engines."
                    }
                ]
            }
        ]
    },
    "sql": {
        "name": "SQL & Relational Database Architecture",
        "category": "Software & Coding",
        "summary": "Master relational database management, schema design, complex joins, subqueries, indexing, and query optimization.",
        "chapters": [
            {
                "chapter_id": 1,
                "name": "SQL Fundamentals: Schema & Queries",
                "about": "Learn DDL, DML, SELECT statements, WHERE filtering, and table constraints.",
                "duration": "15 mins",
                "explanation": "Structured Query Language (SQL) is the standard language for relational database management systems. DDL (CREATE, ALTER, DROP) manages schema, while DML (SELECT, INSERT, UPDATE, DELETE) manipulates data rows with ACID guarantees.",
                "key_takeaways": [
                    "Relational databases ensure ACID transactions (Atomicity, Consistency, Isolation, Durability).",
                    "Primary keys enforce unique entity identification; foreign keys guarantee referential integrity.",
                    "WHERE filters individual rows before grouping; HAVING filters aggregated groups."
                ],
                "code_examples": [
                    {
                        "title": "Basic SQL Filtering & Aggregation",
                        "language": "sql",
                        "code": "SELECT department, COUNT(*) AS employee_count, AVG(salary) AS avg_salary\nFROM employees\nWHERE status = 'ACTIVE'\nGROUP BY department\nHAVING COUNT(*) > 5\nORDER BY avg_salary DESC;",
                        "explanation": "Aggregates active employees per department and filters groups with more than 5 members."
                    }
                ],
                "coding_challenge": {
                    "title": "Select High Earners",
                    "description": "Write a query to retrieve active employees with salary greater than 50000.",
                    "starter_code": "SELECT name, salary FROM employees WHERE salary > 50000;",
                    "language": "sql",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "Which SQL clause filters records after GROUP BY aggregation?",
                        "options": ["WHERE", "HAVING", "LIMIT", "ORDER BY"],
                        "correct_answer": 1,
                        "explanation": "HAVING filters aggregate groups, whereas WHERE filters individual rows before grouping."
                    }
                ]
            }
,
            {
                "chapter_id": 2,
                "name": "Advanced Joins, Multi-Table Relations & Subqueries",
                "about": "Master INNER, LEFT, RIGHT, FULL OUTER joins, self-joins, correlated subqueries, and EXISTS operators.",
                "duration": "20 mins",
                "explanation": "Relational databases derive their power from joining normalized tables. INNER joins return matching records; OUTER joins preserve unmatched rows from one or both tables. Correlated subqueries evaluate row-by-row against outer queries for advanced filtering.",
                "key_takeaways": [
                    "INNER JOIN returns intersection; LEFT JOIN retains all records from the left table.",
                    "Self-joins link a table to itself to model hierarchical structures like employee-manager relations.",
                    "EXISTS is often more efficient than IN when evaluating subqueries with large result sets."
                ],
                "code_examples": [
                    {
                        "title": "Multi-Table Join with Aggregation",
                        "language": "sql",
                        "code": """SELECT 
    d.department_name,
    COUNT(e.employee_id) AS total_staff,
    COALESCE(AVG(e.salary), 0) AS average_salary
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
WHERE d.is_active = TRUE
GROUP BY d.department_id, d.department_name
ORDER BY average_salary DESC;""",
                        "explanation": "Joins departments with employees, including departments with zero staff."
                    }
                ],
                "coding_challenge": {
                    "title": "Left Join Customers and Orders",
                    "description": "Write a query to retrieve customer names and order IDs, including customers with no orders.",
                    "starter_code": """SELECT c.name, o.order_id 
FROM customers c 
LEFT JOIN orders o ON c.id = o.customer_id;""",
                    "language": "sql",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "Which join type returns all rows from the left table and matching rows from the right table?",
                        "options": ["INNER JOIN", "LEFT OUTER JOIN", "CROSS JOIN", "RIGHT OUTER JOIN"],
                        "correct_answer": 1,
                        "explanation": "LEFT JOIN returns all records from the left table and matching rows from the right, filling non-matching right columns with NULL."
                    },
                    {
                        "question": "What is the result of a CROSS JOIN between a table with 5 rows and a table with 10 rows?",
                        "options": ["15 rows", "5 rows", "50 rows", "0 rows"],
                        "correct_answer": 2,
                        "explanation": "A CROSS JOIN produces the Cartesian product: 5 * 10 = 50 rows."
                    }
                ]
            },
            {
                "chapter_id": 3,
                "name": "Aggregations, Grouping Sets & Window Functions",
                "about": "Master ROW_NUMBER(), RANK(), DENSE_RANK(), PARTITION BY, running totals, and sliding window frames.",
                "duration": "25 mins",
                "explanation": "Window functions perform calculations across a set of table rows related to the current row without collapsing rows like GROUP BY does. This makes them indispensable for calculating running totals, moving averages, and top-N rankings.",
                "key_takeaways": [
                    "Window functions use the OVER (PARTITION BY ... ORDER BY ...) clause.",
                    "DENSE_RANK() does not skip rank numbers after ties; RANK() does.",
                    "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW computes cumulative running totals."
                ],
                "code_examples": [
                    {
                        "title": "Top Earners per Department using DENSE_RANK()",
                        "language": "sql",
                        "code": """WITH RankedSalaries AS (
    SELECT 
        employee_id,
        first_name,
        department_id,
        salary,
        DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank_in_dept
    FROM employees
)
SELECT department_id, first_name, salary, rank_in_dept
FROM RankedSalaries
WHERE rank_in_dept <= 3;""",
                        "explanation": "Calculates top 3 earners within every department using window functions and CTEs."
                    }
                ],
                "coding_challenge": {
                    "title": "Running Total Query",
                    "description": "Write a query that computes a running sum of order amounts ordered by order_date.",
                    "starter_code": """SELECT order_id, order_date, amount,
       SUM(amount) OVER (ORDER BY order_date) as running_total
FROM orders;""",
                    "language": "sql",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "What is the primary difference between GROUP BY and Window Functions?",
                        "options": ["GROUP BY collapses rows into single summaries, while window functions retain individual row identities", "Window functions cannot calculate sums", "GROUP BY only works on strings", "Window functions run before WHERE filtering"],
                        "correct_answer": 0,
                        "explanation": "GROUP BY aggregates multiple rows into one; window functions compute calculations over a window frame while retaining all individual rows."
                    },
                    {
                        "question": "If two rows tie for 1st place, what will DENSE_RANK() assign to the next row?",
                        "options": ["1", "2", "3", "0"],
                        "correct_answer": 1,
                        "explanation": "DENSE_RANK() assigns consecutive integers without gaps, so the next row receives rank 2."
                    }
                ]
            },
            {
                "chapter_id": 4,
                "name": "B-Tree Indexing, Query Optimization & Execution Plans",
                "about": "Understand B-Tree indexes, composite indexes, analyzing EXPLAIN ANALYZE output, and eliminating table scans.",
                "duration": "25 mins",
                "explanation": "Database queries slow down when engines perform sequential full-table scans. B-Tree indexes provide O(log N) lookup speeds. Understanding query execution plans (EXPLAIN) allows engineers to create composite indexes matching query WHERE and ORDER BY clauses.",
                "key_takeaways": [
                    "B-Tree indexes speed up equality and range searches significantly.",
                    "Index column order matters: leftmost prefix rule dictates how composite indexes are utilized.",
                    "Over-indexing hurts INSERT/UPDATE throughput because every write must update index trees."
                ],
                "code_examples": [
                    {
                        "title": "Creating Composite Index and Query Inspection",
                        "language": "sql",
                        "code": """-- Create composite index covering filter and sort
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date DESC);

-- Analyze execution plan to ensure index scan is utilized
EXPLAIN ANALYZE
SELECT order_id, amount
FROM orders
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 10;""",
                        "explanation": "Creates a covering composite index and verifies index scan via EXPLAIN ANALYZE."
                    }
                ],
                "coding_challenge": {
                    "title": "Create Index Statement",
                    "description": "Write a DDL statement to create an index named idx_user_email on the email column of users table.",
                    "starter_code": """CREATE INDEX idx_user_email ON users(email);""",
                    "language": "sql",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "Which data structure is most commonly used for standard relational database indexes?",
                        "options": ["Linked List", "B-Tree / B+ Tree", "Stack", "Binary Heap"],
                        "correct_answer": 1,
                        "explanation": "B-Trees keep data sorted and allow search, sequential access, insertions, and deletions in logarithmic time."
                    },
                    {
                        "question": "What is a major trade-off of adding too many indexes to a database table?",
                        "options": ["SELECT queries become slower", "Write operations (INSERT, UPDATE, DELETE) become slower and consume more disk space", "Network bandwidth is blocked", "ACID transactions are disabled"],
                        "correct_answer": 1,
                        "explanation": "Every write operation must modify both the table and all associated index trees."
                    }
                ]
            },
            {
                "chapter_id": 5,
                "name": "Transactions, ACID Guarantees, Isolation Levels & Triggers",
                "about": "Master BEGIN/COMMIT/ROLLBACK, Read Committed, Repeatable Read, Serializable, and avoiding deadlocks.",
                "duration": "25 mins",
                "explanation": "Transactions guarantee database consistency across multi-step operations. ACID ensures atomic execution, valid invariants, isolated concurrent reads/writes, and durable persistence. Configuring transaction isolation levels balances data integrity against concurrent throughput.",
                "key_takeaways": [
                    "Atomicity guarantees all steps succeed or all are rolled back.",
                    "Isolation levels prevent concurrency phenomena like Dirty Reads and Phantom Reads.",
                    "Always acquire resources in a consistent global order to prevent deadlocks."
                ],
                "code_examples": [
                    {
                        "title": "Safe Atomic Fund Transfer Transaction",
                        "language": "sql",
                        "code": """BEGIN TRANSACTION;

UPDATE accounts 
SET balance = balance - 500.00 
WHERE account_id = 101 AND balance >= 500.00;

UPDATE accounts 
SET balance = balance + 500.00 
WHERE account_id = 202;

INSERT INTO audit_log(action, from_acc, to_acc, amount, created_at)
VALUES ('TRANSFER', 101, 202, 500.00, CURRENT_TIMESTAMP);

COMMIT;""",
                        "explanation": "Enforces atomicity and balance safety across bank accounts."
                    }
                ],
                "coding_challenge": {
                    "title": "Begin Transaction Block",
                    "description": "Write a SQL block that begins a transaction, deletes inactive users, and commits.",
                    "starter_code": """BEGIN;
DELETE FROM users WHERE is_active = FALSE;
COMMIT;""",
                    "language": "sql",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "In ACID, what does the 'I' (Isolation) property guarantee?",
                        "options": ["Immediate disk synchronization", "Concurrent transactions execute without interfering with one another's intermediate states", "Identical data types across tables", "In-memory caching"],
                        "correct_answer": 1,
                        "explanation": "Isolation prevents concurrent transactions from seeing uncommitted or conflicting intermediate modifications."
                    },
                    {
                        "question": "Which phenomenon occurs when a transaction reads uncommitted changes from another concurrent transaction?",
                        "options": ["Dirty Read", "Phantom Read", "Non-Repeatable Read", "Deadlock"],
                        "correct_answer": 0,
                        "explanation": "A Dirty Read happens when a transaction reads data that another transaction has modified but not yet committed."
                    }
                ]
            }
        ]
    },
    "docker": {
        "name": "Docker & Containerization for Developers",
        "category": "Software & Coding",
        "summary": "Learn container packaging, Dockerfile instructions, image layers, volumes, and multi-container orchestration.",
        "chapters": [
            {
                "chapter_id": 1,
                "name": "Docker Basics: Containers & Images",
                "about": "Understand container virtualization, Docker CLI, running containers, and port mapping.",
                "duration": "15 mins",
                "explanation": "Docker packages applications and dependencies into standardized containers that execute consistently across development, staging, and production environments using kernel namespaces and cgroups.",
                "key_takeaways": [
                    "Containers share the host OS kernel and startup in milliseconds.",
                    "A Docker image is an immutable template; a container is a running instance.",
                    "Port forwarding (-p host:container) allows external network traffic to reach internal ports."
                ],
                "code_examples": [
                    {
                        "title": "Multi-stage Dockerfile Example",
                        "language": "bash",
                        "code": "FROM eclipse-temurin:17-jdk-alpine AS builder\nWORKDIR /app\nCOPY . .\nRUN ./mvnw clean package -DskipTests\n\nFROM eclipse-temurin:17-jre-alpine\nWORKDIR /app\nCOPY --from=builder /app/target/*.jar app.jar\nEXPOSE 8080\nENTRYPOINT [\"java\", \"-jar\", \"app.jar\"]",
                        "explanation": "Multi-stage Dockerfile produces a lightweight final image without build-time dependencies."
                    }
                ],
                "coding_challenge": {
                    "title": "Define Base Dockerfile",
                    "description": "Write a basic Dockerfile that sets WORKDIR and runs a script.",
                    "starter_code": "FROM alpine:3.19\nWORKDIR /app\nCMD [\"echo\", \"Success\"]",
                    "language": "bash",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "What is the primary benefit of multi-stage Docker builds?",
                        "options": ["Faster compile times only", "Significantly smaller and more secure production images", "Enables direct root kernel access", "Eliminates network requirements"],
                        "correct_answer": 1,
                        "explanation": "Multi-stage builds discard build tools and intermediate artifacts, producing lean production images."
                    }
                ]
            }
,
            {
                "chapter_id": 2,
                "name": "Building Optimized Images with Multi-Stage Dockerfiles",
                "about": "Learn layer caching, .dockerignore best practices, reducing image size, and non-root security.",
                "duration": "20 mins",
                "explanation": "Production Docker images must be lean, secure, and fast to pull. Multi-stage builds separate compilation environments from lightweight production runtimes, discarding compilers, SDKs, and source files from the final container artifact.",
                "key_takeaways": [
                    "Order Dockerfile instructions from least-frequently changed to most-frequently changed to maximize build cache hits.",
                    "Use multi-stage builds (FROM ... AS builder) to keep final production images tiny.",
                    "Always run containers as a non-root user (USER node / USER 1001) for security hardening."
                ],
                "code_examples": [
                    {
                        "title": "Production Node.js Multi-Stage Dockerfile",
                        "language": "bash",
                        "code": """# Multi-stage production build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]""",
                        "explanation": "Builds assets in stage 1 and executes as non-root user in lightweight stage 2."
                    }
                ],
                "coding_challenge": {
                    "title": "Expose Container Port",
                    "description": "Write a Dockerfile instruction that documents that the container listens on port 8080.",
                    "starter_code": """EXPOSE 8080""",
                    "language": "bash",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "What is the primary role of a .dockerignore file?",
                        "options": ["Prevents containers from communicating on the network", "Prevents unnecessary local files (node_modules, .git) from being sent to the Docker build context", "Ignores compiler warnings", "Deletes old images automatically"],
                        "correct_answer": 1,
                        "explanation": ".dockerignore excludes patterns from the build context, speeding up image creation and avoiding leaking sensitive files."
                    },
                    {
                        "question": "Why should Dockerfiles copy package.json and install dependencies before copying the rest of source code?",
                        "options": ["It is a mandatory syntax requirement", "To leverage Docker layer caching so npm install runs only when dependencies change", "To ensure packages are encrypted", "To automatically format code"],
                        "correct_answer": 1,
                        "explanation": "Docker caches image layers; copying dependencies first prevents re-running slow package downloads on every code edit."
                    }
                ]
            },
            {
                "chapter_id": 3,
                "name": "Container Networking, Port Mapping & Storage Volumes",
                "about": "Master bridge networks, container DNS discovery, named volumes, and host bind mounts.",
                "duration": "25 mins",
                "explanation": "Containers are ephemeral by default. Docker volumes provide persistent storage decoupled from container lifecycles. User-defined bridge networks provide internal DNS resolution so containers can address one another by service name without hardcoded IPs.",
                "key_takeaways": [
                    "Named volumes persist data even after containers are stopped or removed.",
                    "Bind mounts map a specific host directory directly into a container (ideal for local dev).",
                    "Containers on the same user-defined bridge network resolve each other by container name."
                ],
                "code_examples": [
                    {
                        "title": "Creating Network and Volume CLI Commands",
                        "language": "bash",
                        "code": """# Create custom bridge network
docker network create backend-net

# Create persistent data volume
docker volume create pgdata

# Run PostgreSQL container connected to network with volume
docker run -d --name db --network backend-net -v pgdata:/var/lib/postgresql/data -e POSTGRES_PASSWORD=secret postgres:16-alpine

# Run web app on same network communicating via 'db' hostname
docker run -d --name web --network backend-net -p 8080:8080 my-web-app:latest""",
                        "explanation": "Illustrates inter-container DNS discovery and decoupled persistent volume storage."
                    }
                ],
                "coding_challenge": {
                    "title": "Run Container with Port Mapping",
                    "description": "Write a docker run command that forwards host port 80 to container port 80 in detached mode using nginx image.",
                    "starter_code": """docker run -d -p 80:80 nginx""",
                    "language": "bash",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "What happens to data stored in a Docker named volume when the associated container is deleted?",
                        "options": ["The volume and all its data are deleted immediately", "The volume and its data persist intact on the host", "The data is converted to a zip file", "The host machine reboots"],
                        "correct_answer": 1,
                        "explanation": "Named volumes exist independently of container lifecycles; deleting a container does not delete its volumes."
                    },
                    {
                        "question": "How do containers communicate with each other on a user-defined bridge network?",
                        "options": ["Through automatic DNS resolution using container/service names", "Only through the public internet", "Via Bluetooth", "Only via hardcoded MAC addresses"],
                        "correct_answer": 0,
                        "explanation": "Docker includes an embedded DNS server that resolves container names to IP addresses on user-defined networks."
                    }
                ]
            },
            {
                "chapter_id": 4,
                "name": "Multi-Container Orchestration with Docker Compose",
                "about": "Define multi-tier stacks (frontend, backend, database, cache) declaratively using docker-compose.yml.",
                "duration": "25 mins",
                "explanation": "Modern software applications involve multiple cooperating services. Docker Compose allows teams to define, configure, and boot an entire multi-container architecture with a single declarative YAML file and the 'docker compose up' command.",
                "key_takeaways": [
                    "docker-compose.yml defines services, networks, volumes, and environment variables.",
                    "depends_on specifies startup ordering between interdependent services.",
                    "docker compose up -d launches the entire multi-tier stack in background detached mode."
                ],
                "code_examples": [
                    {
                        "title": "Full-Stack docker-compose.yml Specification",
                        "language": "yaml",
                        "code": """version: '3.8'

services:
  web:
    build: .
    ports:
      - '3000:3000'
    environment:
      - DATABASE_URL=postgres://user:password@db:5432/appdb
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: appdb
    volumes:
      - db-data:/var/lib/postgresql/data

  cache:
    image: redis:7-alpine

volumes:
  db-data:""",
                        "explanation": "Orchestrates web app, PostgreSQL database, and Redis cache on an auto-created network."
                    }
                ],
                "coding_challenge": {
                    "title": "Start Compose Stack",
                    "description": "Write the CLI command to start all services in docker-compose.yml in detached mode.",
                    "starter_code": """docker compose up -d""",
                    "language": "bash",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "Which CLI command stops all running containers defined in a Compose file and removes their networks?",
                        "options": ["docker compose stop", "docker compose down", "docker compose rm", "docker compose kill"],
                        "correct_answer": 1,
                        "explanation": "'docker compose down' stops containers, removes internal networks, and frees assigned ports."
                    },
                    {
                        "question": "What is the function of the 'depends_on' key in Docker Compose?",
                        "options": ["Expresses dependency and dictates startup sequence between services", "Installs host operating system updates", "Compiles source code", "Generates API keys"],
                        "correct_answer": 0,
                        "explanation": "depends_on tells Docker Compose to start dependent containers (like databases) before starting the consuming application."
                    }
                ]
            },
            {
                "chapter_id": 5,
                "name": "Container Security, Registries & Production CI/CD",
                "about": "Master vulnerability scanning (Trivy), pushing to Docker Hub/ECR, secrets management, and health checks.",
                "duration": "25 mins",
                "explanation": "Deploying containers to production requires strict security boundaries. This includes automated vulnerability scanning of base images, preventing container root privileges, managing credentials through environment secrets rather than hardcoded image layers, and implementing container HEALTHCHECK probes.",
                "key_takeaways": [
                    "Never bake credentials, tokens, or private keys into Docker images.",
                    "Use HEALTHCHECK directives so orchestrators detect hung or unresponsive processes.",
                    "Tag images with semantic versions or git commit hashes rather than relying on mutable 'latest' tags."
                ],
                "code_examples": [
                    {
                        "title": "Container Healthcheck and Security Hardening",
                        "language": "bash",
                        "code": """# Add health check to ensure API endpoint is responding
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Security scan using Trivy CLI before deployment
# trivy image --severity HIGH,CRITICAL my-app:v1.2.0

# Push versioned image to registry
# docker tag my-app:latest myregistry.io/org/my-app:1.2.0
# docker push myregistry.io/org/my-app:1.2.0""",
                        "explanation": "Shows container health probes and automated image security verification."
                    }
                ],
                "coding_challenge": {
                    "title": "Tag Docker Image",
                    "description": "Write a command to tag local image 'web:latest' as 'registry.com/web:v1'.",
                    "starter_code": """docker tag web:latest registry.com/web:v1""",
                    "language": "bash",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "Why is relying on the 'latest' image tag in production deployments considered an anti-pattern?",
                        "options": ["The tag is immutable and cannot be updated", "The tag is mutable, making deployments non-deterministic and rollback difficult", "It disables SSL/TLS", "It causes high memory consumption"],
                        "correct_answer": 1,
                        "explanation": "The 'latest' tag changes whenever a new image is pushed, preventing reproducible deployments and reliable rollbacks."
                    },
                    {
                        "question": "What is the purpose of the HEALTHCHECK instruction in a Dockerfile?",
                        "options": ["Profiles CPU temperature", "Periodically tests whether the application running inside the container is operational", "Scans code for syntax bugs", "Checks internet speed"],
                        "correct_answer": 1,
                        "explanation": "HEALTHCHECK tells Docker how to test a container to check that it is still working properly."
                    }
                ]
            }
        ]
    },
    "soft skills": {
        "name": "Workplace Communication & Interview Soft Skills",
        "category": "Technology & Science",
        "summary": "Master technical communication, the STAR interview methodology, conflict resolution, and agile collaboration.",
        "chapters": [
            {
                "chapter_id": 1,
                "name": "STAR Method & Verbal Technical Walkthroughs",
                "about": "Structure behavioral and technical answers using Situation, Task, Action, and Result.",
                "duration": "15 mins",
                "explanation": "The STAR framework is the industry-standard methodology for answering behavioral and technical scenario interview questions. It ensures answers remain concise, structured, and grounded in measurable results.",
                "key_takeaways": [
                    "Situation: Set the context and business problem clearly in 1-2 sentences.",
                    "Task: Define your specific ownership and deliverable.",
                    "Action: Detail your technical and collaborative execution.",
                    "Result: Quantify the outcome (performance improvements, user satisfaction, deadlines met)."
                ],
                "code_examples": [
                    {
                        "title": "STAR Response Framework Script",
                        "language": "python",
                        "code": "# STAR response template\nsituation = 'Our backend API experienced latency spikes under peak user traffic.'\ntask = 'My goal was to diagnose bottlenecks and maintain < 200ms response SLA.'\naction = 'I profiled database queries, added Redis caching, and indexed active columns.'\nresult = 'Average latency dropped by 45%, successfully handling 10k concurrent requests.'\nprint(f'{situation}\\n{task}\\n{action}\\n{result}')",
                        "explanation": "Structured template converting raw work experience into compelling interview narratives."
                    }
                ],
                "coding_challenge": {
                    "title": "Format STAR Response",
                    "description": "Write a function that outputs a concise STAR answer summary.",
                    "starter_code": "def solution():\n    return 'Success'\n\nprint(solution())",
                    "language": "python",
                    "test_cases": [{"input": "default", "expected_output": "Success"}]
                },
                "quiz": [
                    {
                        "question": "Which phase of the STAR method highlights the measurable business or engineering outcome?",
                        "options": ["Situation", "Task", "Action", "Result"],
                        "correct_answer": 3,
                        "explanation": "The Result phase concludes the answer with concrete metrics and achievements."
                    }
                ]
            }
,
            {
                "chapter_id": 2,
                "name": "Active Listening, Cross-Functional Teamwork & Empathy",
                "about": "Master active listening techniques, empathizing with product managers and designers, and bridging technical and business vocabularies.",
                "duration": "20 mins",
                "explanation": "High-performing engineers excel not just at coding, but at understanding the core motivations of cross-functional partners. Active listening involves validating understanding before offering solutions, asking probing clarifying questions, and explaining technical constraints in terms of business impact.",
                "key_takeaways": [
                    "Summarize and repeat what you heard before proposing technical architectures.",
                    "Frame technical debt and refactoring in terms of business velocity, risk, and cost.",
                    "Empathy prevents adversarial relationships between engineering, product, and design."
                ],
                "code_examples": [
                    {
                        "title": "Cross-Functional Requirement Alignment Template",
                        "language": "python",
                        "code": """# Structured cross-functional check-in
def align_requirements(feature_name, user_pain_point, technical_tradeoff):
    return {
        'feature': feature_name,
        'user_value': user_pain_point,
        'engineering_approach': technical_tradeoff,
        'shared_kpi': 'Reduce checkout drop-off by 15%'
    }

print(align_requirements('1-Click Checkout', 'Too many checkout steps', 'Cache user address safely'))""",
                        "explanation": "Demonstrates translating engineering decisions into user and business value."
                    }
                ],
                "coding_challenge": {
                    "title": "Format Meeting Action Items",
                    "description": "Write a function that accepts a list of action items and owners and formats them as a clean summary string.",
                    "starter_code": """def format_actions(items):
    return '\n'.join(f'- [{owner}]: {task}' for task, owner in items)

print(format_actions([('API spec', 'Alex'), ('DB migration', 'Sam')]))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "[('Design review', 'Taylor')]", "expected_output": "- [Taylor]: Design review"}
                    ]
                },
                "quiz": [
                    {
                        "question": "Which active listening practice most effectively prevents misunderstandings during technical planning?",
                        "options": ["Interrupting immediately with your design", "Paraphrasing the speaker's main points to confirm alignment before proposing solutions", "Staying completely silent", "Taking notes without asking any questions"],
                        "correct_answer": 1,
                        "explanation": "Paraphrasing confirms mutual understanding and catches subtle misalignments early."
                    },
                    {
                        "question": "How should an engineer communicate technical debt to a product manager?",
                        "options": ["Complain about old code", "Explain how technical debt impacts feature delivery speed, system stability, and customer experience", "Refuse to build new features", "Ignore technical debt completely"],
                        "correct_answer": 1,
                        "explanation": "Framing technical debt in business terms (feature velocity, uptime, bug reduction) aligns priorities with product goals."
                    }
                ]
            },
            {
                "chapter_id": 3,
                "name": "Constructive Code Reviews, Feedback Culture & Conflict Management",
                "about": "Learn how to write blameless code review comments, manage design disagreements, and foster psychological safety.",
                "duration": "25 mins",
                "explanation": "Code reviews are primarily educational and quality-assurance conversations. Constructive reviewers separate the author from the code, praise thoughtful solutions, label non-blocking suggestions (nitpicks), and transition heated asynchronous debates into quick synchronous discussions.",
                "key_takeaways": [
                    "Ask curious questions ('What do you think about using X here?') rather than making rigid demands.",
                    "Differentiate between blocking security/correctness bugs and non-blocking stylistic preferences (nit:).",
                    "Fostering psychological safety empowers junior and senior engineers to collaborate openly."
                ],
                "code_examples": [
                    {
                        "title": "Blameless Code Review Comment Checklist",
                        "language": "python",
                        "code": """# Constructive review prefix conventions
REVIEW_PREFIXES = {
    'BLOCKER': 'Critical bug, memory leak, or security vulnerability that must be addressed.',
    'QUESTION': 'Clarifying question to understand the design rationale.',
    'SUGGESTION': 'Alternative approach that might improve readability or performance.',
    'NIT': 'Minor style or naming preference; completely optional for merge.',
    'PRAISE': 'Highlighting clean, elegant, or well-tested code.'
}

for prefix, desc in REVIEW_PREFIXES.items():
    print(f'[{prefix}]: {desc}')""",
                        "explanation": "Standardized review prefixes reduce friction and clarify intent."
                    }
                ],
                "coding_challenge": {
                    "title": "Classify Review Comment",
                    "description": "Write a function that tags a comment as 'Blocking' if it contains 'security' or 'bug', otherwise 'Non-blocking'.",
                    "starter_code": """def classify_comment(comment):
    c = comment.lower()
    if 'security' in c or 'bug' in c:
        return 'Blocking'
    return 'Non-blocking'

print(classify_comment('Potential memory leak bug in loop'))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "'Critical security issue'", "expected_output": "Blocking"},
                        {"input": "'nit: rename variable'", "expected_output": "Non-blocking"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What is the recommended approach when a pull request discussion exceeds 5-6 back-and-forth comments without consensus?",
                        "options": ["Reject the pull request immediately", "Switch from text comments to a quick 5-10 minute 1-on-1 voice/video call or huddle", "Tag the CEO", "Merge the code without testing"],
                        "correct_answer": 1,
                        "explanation": "Direct voice or video syncs resolve nuances in minutes that could take days of text debates."
                    },
                    {
                        "question": "What distinguishes blameless feedback from critical feedback?",
                        "options": ["Blameless feedback focuses on the system, code, and outcome rather than personal ability", "Blameless feedback avoids pointing out errors", "Blameless feedback is only written by managers", "There is no difference"],
                        "correct_answer": 0,
                        "explanation": "Focusing on the code and system mechanisms fosters learning and psychological safety without defensiveness."
                    }
                ]
            },
            {
                "chapter_id": 4,
                "name": "Technical Storytelling & High-Impact Architecture Presentations",
                "about": "Present complex engineering trade-offs, lead architecture review boards (RFCs), and communicate with executives.",
                "duration": "25 mins",
                "explanation": "Great engineers must be able to persuade others. Technical storytelling structures complex decisions around context, challenges, evaluated options, and measurable recommendations. Writing Requests for Comments (RFCs) builds organizational consensus before large-scale implementation.",
                "key_takeaways": [
                    "Bottom-line upfront (BLUF): State the recommendation and key impact in the first 60 seconds.",
                    "Present evaluated alternatives alongside their pros, cons, and operational trade-offs.",
                    "Use clear visual diagrams (architecture flowcharts) rather than dense walls of text."
                ],
                "code_examples": [
                    {
                        "title": "Architecture RFC Structure Template",
                        "language": "python",
                        "code": """# RFC (Request For Comments) Outline
RFC_DOCUMENT = '''
# RFC 104: Migration to Event-Driven Order Processing

## 1. Executive Summary
Decouple payment and fulfillment services using Kafka to support 5x Black Friday traffic.

## 2. Problem Statement & Metrics
Current synchronous REST calls result in 3% timeouts under peak load.

## 3. Evaluated Options
- Option A: Horizontal pod scaling (High infrastructure cost, DB bottlenecks remain).
- Option B: Kafka message broker (Optimal: asynchronous decoupling, replayable events).

## 4. Rollout & Rollback Strategy
Canary deployment with 5% traffic split; automated rollback on error rate > 0.1%.
'''
print(RFC_DOCUMENT.strip())""",
                        "explanation": "Industry-standard architectural proposal framework."
                    }
                ],
                "coding_challenge": {
                    "title": "Format Executive Summary",
                    "description": "Write a function that returns an executive summary formatted with 'Goal:' and 'Impact:'.",
                    "starter_code": """def make_summary(goal, impact):
    return f'Goal: {goal} | Impact: {impact}'

print(make_summary('Migrate DB', 'Reduce latency by 40%'))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "goal='Add cache', impact='2x throughput'", "expected_output": "Goal: Add cache | Impact: 2x throughput"}
                    ]
                },
                "quiz": [
                    {
                        "question": "What does the BLUF (Bottom Line Up Front) presentation principle advise?",
                        "options": ["Place technical background at the very end of slides", "State the core conclusion, recommendation, and impact immediately at the beginning", "Never present numbers", "Speak as quietly as possible"],
                        "correct_answer": 1,
                        "explanation": "Executives and busy stakeholders value knowing the core takeaway and ask upfront before diving into details."
                    },
                    {
                        "question": "What is the primary function of an engineering RFC (Request for Comments)?",
                        "options": ["A legally binding contract", "A written proposal to gather feedback and achieve consensus before building significant technical changes", "A bug report", "A job application"],
                        "correct_answer": 1,
                        "explanation": "RFCs solicit peer review, surface unforeseen edge cases, and align teams on technical decisions."
                    }
                ]
            },
            {
                "chapter_id": 5,
                "name": "Adaptability, Negotiation & Continuous Professional Growth",
                "about": "Navigate ambiguous priorities, negotiate engineering timelines with stakeholders, and build continuous learning habits.",
                "duration": "25 mins",
                "explanation": "Software engineering evolves rapidly. Thriving engineers embrace ambiguity, prioritize high-leverage outcomes, manage scope creep through trade-off negotiation (time vs scope vs quality), and dedicate regular time to mastering emerging tools and patterns.",
                "key_takeaways": [
                    "Negotiate with the iron triangle: if timeline is fixed, scope or resources must adjust.",
                    "Embrace ambiguity by running small proof-of-concept spikes before committing.",
                    "Cultivate T-shaped skills: broad familiarity across the stack with deep mastery in primary domains."
                ],
                "code_examples": [
                    {
                        "title": "Scope vs Timeline Trade-off Negotiation Helper",
                        "language": "python",
                        "code": """def scope_negotiation(requested_features, deadline_weeks):
    core_features = requested_features[:2]
    nice_to_haves = requested_features[2:]
    return {
        'phase_1_mvp': core_features,
        'phase_2_future': nice_to_haves,
        'recommendation': f'Deliver MVP within {deadline_weeks} weeks with zero quality compromise.'
    }

print(scope_negotiation(['User Auth', 'Checkout', 'Loyalty Points', 'Dark Mode'], 4))""",
                        "explanation": "Structures realistic release milestones without compromising software quality."
                    }
                ],
                "coding_challenge": {
                    "title": "Split MVP Features",
                    "description": "Write a function that takes a list of features and returns the first n features as MVP.",
                    "starter_code": """def get_mvp(features, n):
    return features[:n]

print(get_mvp(['Auth', 'Billing', 'Analytics'], 2))""",
                    "language": "python",
                    "test_cases": [
                        {"input": "features=['A', 'B', 'C'], n=1", "expected_output": "['A']"}
                    ]
                },
                "quiz": [
                    {
                        "question": "According to the Project Management Iron Triangle, if deadline and quality are fixed, what variable must be flexible?",
                        "options": ["Scope", "Physics", "Git commit history", "Database normalization"],
                        "correct_answer": 0,
                        "explanation": "When timeline and budget/quality are constrained, scope is the primary lever to adjust to deliver on time."
                    },
                    {
                        "question": "What is a 'T-shaped' engineering skill profile?",
                        "options": ["Deep specialization in one domain with broad working knowledge across related fields", "Only knowing frontend frameworks", "Writing code in capital letters", "Testing only on Thursdays"],
                        "correct_answer": 0,
                        "explanation": "The vertical bar represents deep expertise in a specialty, while the horizontal bar represents broad foundational literacy."
                    }
                ]
            }
        ]
    }
}


def generate_smart_curriculum(topic_str: str) -> Dict[str, Any]:
    """Generates a high-fidelity, distinct 5-module curriculum for any technical topic."""
    clean_topic = topic_str.strip() or "Software Engineering"
    t_lower = clean_topic.lower()

    if "angular" in t_lower:
        modules = [
            ("Angular Architecture & Component Essentials", "Explore Angular CLI, standalone components, template syntax, and modular application architecture."),
            ("Data Binding, Directives & Event Handling", "Master property binding, two-way ngModel, structural directives (*ngIf, *ngFor), and custom pipes."),
            ("Services, Dependency Injection & RxJS", "Build reusable injectable services, manage asynchronous state streams using RxJS Subjects and Observables."),
            ("Routing, Navigation & Angular Forms", "Implement client-side routing, route guards, reactive forms, and real-time input validation."),
            ("HTTP Client, API Integration & Deployment", "Connect to REST backends with HttpClient, interceptors, error handling, and production build optimization.")
        ]
        category = "Frontend Development"
        lang = "typescript"
        code_snip = "import { Component } from '@angular/core';\n\n@Component({\n  selector: 'app-root',\n  template: '<h1>Hello {{ title }}!</h1>'\n})\nexport class AppComponent {\n  title = 'Angular Application';\n}"
    elif "oop" in t_lower or "object" in t_lower:
        modules = [
            ("Foundations of OOP: Classes, Objects & State", "Understand object-oriented paradigms, class blueprints, instance attributes, and constructor lifecycle."),
            ("Encapsulation & Data Hiding", "Protect internal object state using access modifiers (private/protected), getters, and setters."),
            ("Inheritance & Code Reusability", "Derive child classes from parent abstractions, utilize super calls, and understand hierarchical modeling."),
            ("Polymorphism & Dynamic Method Dispatch", "Implement method overriding and overloading to enable flexible, interchangeable component behavior."),
            ("Abstraction, Interfaces & SOLID Principles", "Design loosely coupled, maintainable software systems using abstract contracts and SOLID design guidelines.")
        ]
        category = "Core Computer Science"
        lang = "python"
        code_snip = "class Animal:\n    def __init__(self, name: str):\n        self._name = name\n    def speak(self) -> str:\n        return 'Generic animal sound'\n\nclass Dog(Animal):\n    def speak(self) -> str:\n        return f'{self._name} barks!'\n\ndog = Dog('Buddy')\nprint(dog.speak())"
    elif "react" in t_lower:
        modules = [
            ("React Fundamentals, JSX & Virtual DOM", "Understand React component rendering, JSX syntax, and the reconciliation algorithm."),
            ("Components, Props & State Management", "Build functional components, pass immutable props, and manage component state with useState."),
            ("React Hooks: useEffect, useMemo & useRef", "Handle side-effects, API calls, performance memoization, and DOM element references."),
            ("Client Routing & Controlled Forms", "Implement React Router for single-page navigation and manage validated form inputs."),
            ("Global State, Context API & Production Build", "Share app-wide state without prop drilling and optimize bundles for production deployment.")
        ]
        category = "Frontend Development"
        lang = "javascript"
        code_snip = "import React, { useState } from 'react';\n\nexport function Counter() {\n  const [count, setCount] = useState(0);\n  return (\n    <button onClick={() => setCount(count + 1)}>\n      Clicked {count} times\n    </button>\n  );\n}"
    elif "typescript" in t_lower:
        modules = [
            ("TypeScript Foundations & Static Type System", "Configure tsconfig.json, primitives, type inference, and compile-time verification."),
            ("Interfaces, Custom Types & Unions", "Model structured domain data using interfaces, type aliases, union types, and type narrowing."),
            ("Generics & Reusable Code Patterns", "Write type-safe generic functions, classes, and constraints that adapt to any data structure."),
            ("Object-Oriented TypeScript & Access Modifiers", "Implement classes, interfaces, abstract classes, and encapsulation modifiers in TypeScript."),
            ("Modules, Utility Types & Framework Integration", "Master Partial, Omit, Pick utility types and integrate TypeScript into modern frontend/backend stacks.")
        ]
        category = "Programming Languages"
        lang = "typescript"
        code_snip = "interface User {\n  id: number;\n  name: string;\n  role: 'admin' | 'user';\n}\n\nfunction printUser(u: User): void {\n  console.log(`User ${u.name} has role: ${u.role}`);\n}\nprintUser({ id: 1, name: 'Alice', role: 'admin' });"
    elif any(k in t_lower for k in ["cucumber", "bdd", "gherkin"]):
        modules = [
            ("Introduction to BDD & Cucumber Architecture", "Understand Behavior-Driven Development principles, business-readable specifications, and Cucumber framework components."),
            ("Gherkin Syntax & Feature Files", "Master Feature, Scenario, Given-When-Then-And-But steps, Backgrounds, and Scenario Outlines with Examples tables."),
            ("Step Definitions & Regex Glue Code", "Implement step definition methods in Java matching Gherkin patterns, step arguments, and data table conversions."),
            ("Test Runner, Hooks (@Before/@After) & Tagging", "Configure JUnit TestRunner, cucumberOptions, scenario execution hooks, and smoke/regression tags."),
            ("Framework Integration: Selenium & Page Object Model", "Integrate Cucumber with Selenium WebDriver, Page Object Model design pattern, and generate HTML reports.")
        ]
        category = "Software Testing & QA"
        lang = "java"
        code_snip = """// Gherkin Feature & Java Step Definition
// Feature: User Login
// Scenario: Successful login with valid credentials
//   Given user navigates to login page
//   When user enters username and password
//   Then user is redirected to dashboard

import io.cucumber.java.en.*;

public class LoginStepDefinitions {
    @Given("user navigates to login page")
    public void navigateToLogin() {
        System.out.println("Navigating to login page...");
    }

    @When("user enters username and password")
    public void enterCredentials() {
        System.out.println("Entering user credentials...");
    }

    @Then("user is redirected to dashboard")
    public void verifyDashboard() {
        System.out.println("Verifying dashboard redirection...");
    }
}"""
    elif any(k in t_lower for k in ["selenium", "automation testing", "software testing", "qa", "sdet"]):
        modules = [
            ("Software Testing Principles & Test Automation Foundations", "Understand QA lifecycle (STLC), verification vs validation, and the test automation pyramid."),
            ("Selenium WebDriver Architecture & Element Locators", "Configure WebDriver instances, browser options, and locate elements via ID, CSS selectors, and XPath."),
            ("Synchronization, Dynamic Waits & Event Handling", "Handle race conditions using WebDriverWait, ExpectedConditions, and avoid fragile thread sleeps."),
            ("Page Object Model (POM) Design Pattern", "Design robust, maintainable test frameworks separating page web elements from test assertion logic."),
            ("Cross-Browser Testing, TestNG & CI/CD Integration", "Run automated test suites across Chrome/Firefox, execute data-driven tests, and integrate with CI/CD.")
        ]
        category = "Software Testing & QA"
        lang = "java"
        code_snip = """import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.By;

public class SeleniumDemo {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        try {
            driver.get("https://example.com");
            System.out.println("Page Title: " + driver.getTitle());
            driver.findElement(By.tagName("h1"));
        } finally {
            driver.quit();
        }
    }
}"""
    elif any(k in t_lower for k in ["aws", "cloud", "azure", "gcp"]):
        modules = [
            ("Cloud Architecture & AWS Core Infrastructure", "Understand cloud deployment models, shared responsibility, regions, and availability zones."),
            ("Compute Services: EC2, Containers & Serverless Lambda", "Provision virtual compute instances, configure security groups, and deploy event-driven serverless functions."),
            ("Storage & Database Solutions: S3, RDS & DynamoDB", "Manage scalable object storage buckets, provision relational SQL instances, and configure NoSQL tables."),
            ("Cloud Networking & Security: VPC, IAM & Policies", "Architect isolated Virtual Private Clouds, configure subnets, route tables, and enforce least-privilege IAM policies."),
            ("High Availability, Auto Scaling & CloudWatch Observability", "Configure Auto Scaling Groups, Elastic Load Balancers, and monitor performance metrics with CloudWatch alarms.")
        ]
        category = "Cloud Computing & Architecture"
        lang = "bash"
        code_snip = """# AWS CLI: Provision an S3 Bucket and EC2 instance
aws s3 mb s3://my-enterprise-data-bucket-prod --region us-east-1
aws ec2 run-instances --image-id ami-0c55b159cbfafe1f0 --instance-type t2.micro --key-name MyKeyPair
echo "Cloud resources initialized successfully." """
    elif any(k in t_lower for k in ["kubernetes", "k8s"]):
        modules = [
            ("Kubernetes Architecture, Control Plane & Worker Nodes", "Master kube-apiserver, etcd, kube-scheduler, kubelet, and container runtime architecture."),
            ("Pods, ReplicaSets & Declarative Deployments", "Define declarative YAML specs, manage application replicas, and execute zero-downtime rolling updates."),
            ("Networking, Services (ClusterIP, NodePort) & Ingress", "Expose microservices internally and externally with Ingress controllers and DNS service discovery."),
            ("Configuration & State: ConfigMaps, Secrets & Volumes", "Decouple environment configs, manage sensitive credentials securely, and mount persistent volume claims."),
            ("Horizontal Pod Autoscaling (HPA) & Helm Package Management", "Scale workloads dynamically under CPU/memory load and package deployments with reusable Helm charts.")
        ]
        category = "Cloud Native & Container Orchestration"
        lang = "yaml"
        code_snip = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80"""
    elif any(k in t_lower for k in ["docker", "container"]):
        modules = [
            ("Container Virtualization & Docker Engine Fundamentals", "Understand Linux cgroups and namespaces, compare virtual machines with lightweight containers."),
            ("Building Custom Images with Optimized Dockerfiles", "Write multi-stage Dockerfiles, minimize image layers, and implement security best practices."),
            ("Container Networking & Persistent Storage Volumes", "Manage bridge networks, port mappings, named volumes, and host bind mounts."),
            ("Multi-Container Applications with Docker Compose", "Orchestrate dependent services (API, database, Redis cache) using declarative docker-compose.yml."),
            ("Image Registries, Vulnerability Scanning & Production Run", "Push images to Docker Hub/ECR, run security vulnerability scans, and manage container lifecycles.")
        ]
        category = "DevOps & Containerization"
        lang = "bash"
        code_snip = """# Multi-stage Dockerfile example
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]"""
    elif any(k in t_lower for k in ["git", "github", "version control"]):
        modules = [
            ("Git Internal Architecture, Working Tree & Staging", "Understand Git blobs, trees, commits, HEAD pointer, and atomic commit workflows."),
            ("Branching Strategies, Isolation & Feature Delivery", "Implement Trunk-Based Development vs GitFlow, manage local and remote feature branches."),
            ("Merging, Rebasing & Resolving Merge Conflicts", "Compare fast-forward merges, three-way merges, interactive rebase, and conflict resolution."),
            ("Remote Collaboration: Pull Requests & Protected Branches", "Configure GitHub protected branch rules, code review conventions, and automated status checks."),
            ("Advanced Git Mastery: Cherry-Pick, Reflog & Bisect", "Recover lost commits with git reflog, selectively backport commits with cherry-pick, and debug bugs with git bisect.")
        ]
        category = "Developer Workflows & Tooling"
        lang = "bash"
        code_snip = """# Essential Git Workflow Commands
git checkout -b feature/auth-service
git add src/auth/
git commit -m "feat(auth): implement JWT token verification middleware"
git push -u origin feature/auth-service
git rebase main"""
    elif any(k in t_lower for k in ["linux", "bash", "shell"]):
        modules = [
            ("Linux Filesystem Hierarchy & Terminal Navigation", "Understand FHS (/etc, /var, /usr), absolute vs relative paths, and essential file manipulation."),
            ("Permissions, Ownership & Security Controls", "Master octal and symbolic permissions (chmod, chown), umask, and sudo privilege escalation."),
            ("Process Management, Daemons & System Diagnostics", "Monitor system load (top, htop), manage background jobs (ps, kill), and control systemd services."),
            ("Shell Scripting: Variables, Loops, Conditionals & Functions", "Write robust Bash automation scripts with error trapping (set -euo pipefail) and argument parsing."),
            ("Networking, SSH, Package Management & Cron Automation", "Diagnose network connections (netstat, curl, iptables), configure SSH keys, and schedule automated cron tasks.")
        ]
        category = "Operating Systems & Administration"
        lang = "bash"
        code_snip = """#!/usr/bin/env bash
set -euo pipefail

echo "=== System Health Check ==="
UPTIME=$(uptime -p)
MEMORY=$(free -m | awk '/Mem:/ { printf("%.1f%%", $3/$2 * 100) }')
echo "Uptime: ${UPTIME}"
echo "Memory Utilization: ${MEMORY}"
echo "Status: Optimal" """
    elif any(k in t_lower for k in ["system design", "microservices"]):
        modules = [
            ("System Architecture: Monoliths vs Distributed Microservices", "Evaluate architectural trade-offs, vertical vs horizontal scaling, and domain-driven service decomposition."),
            ("Load Balancing, Reverse Proxies (Nginx) & API Gateways", "Distribute traffic with round-robin and least-connection algorithms, manage rate limiting and SSL termination."),
            ("Caching Strategies (Redis/Memcached) & Invalidation", "Implement Cache-Aside, Write-Through patterns, manage cache thundering herd, and set intelligent TTL eviction."),
            ("Database Scaling: Replication, Sharding & CAP Theorem", "Design master-replica topologies, partition keys, manage eventual consistency vs strict consistency."),
            ("Asynchronous Event-Driven Architecture & Fault Tolerance", "Decouple systems using message brokers (Kafka/RabbitMQ), implement Circuit Breaker (Resilience4j) and Saga patterns.")
        ]
        category = "Software Architecture & Scalability"
        lang = "python"
        code_snip = """# Cache-Aside Strategy Implementation in Python
import redis, json

r = redis.Redis(host='localhost', port=6379, db=0)

def get_user_profile(user_id: str) -> dict:
    cache_key = f"user:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss: fetch from primary DB
    user_data = {"id": user_id, "name": "Alex Taylor", "role": "Engineer"}
    r.setex(cache_key, 3600, json.dumps(user_data))
    return user_data"""
    elif any(k in t_lower for k in ["data structures", "dsa", "algorithms"]):
        modules = [
            ("Algorithmic Complexity (Big-O) & Linear Data Structures", "Analyze time/space complexity, implement dynamic arrays, doubly linked lists, and circular buffers."),
            ("Stacks, Queues, Hash Tables & Collision Resolution", "Implement LIFO/FIFO mechanics, hash functions, separate chaining, and open addressing."),
            ("Binary Trees, Binary Search Trees & Balanced Trees", "Execute tree traversals (Inorder, Preorder, Postorder, Level-order) and balance BSTs (AVL/Red-Black)."),
            ("Graph Representations, Traversals & Shortest Paths", "Model adjacency matrices/lists, execute Breadth-First Search (BFS), Depth-First Search (DFS), and Dijkstra's algorithm."),
            ("Dynamic Programming, Memoization & Greedy Paradigms", "Solve optimal substructure problems, compare top-down memoization with bottom-up tabulation.")
        ]
        category = "Algorithms & Computer Science"
        lang = "python"
        code_snip = """# Binary Search Algorithm - O(log N) Time Complexity
def binary_search(arr: list, target: int) -> int:
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

nums = [1, 3, 5, 7, 9, 11, 13, 15]
print("Found target index:", binary_search(nums, 7))"""
    elif any(k in t_lower for k in ["sql", "mysql", "postgresql", "database"]):
        modules = [
            ("Relational Modeling, Normalization (1NF-3NF) & Schema Design", "Design normalized schemas, define foreign key constraints, cascade rules, and entity-relationship models."),
            ("Advanced SQL Queries, Multi-Table Joins & Subqueries", "Master INNER, LEFT, FULL OUTER joins, subqueries, and set operations (UNION, INTERSECT)."),
            ("Window Functions, Aggregations & Grouping Sets", "Calculate running totals and rankings using ROW_NUMBER(), RANK(), DENSE_RANK(), and PARTITION BY."),
            ("B-Tree Indexing, Execution Plans (EXPLAIN) & Optimization", "Analyze query plans, eliminate costly full-table scans, and create composite and covering indexes."),
            ("Transactions, ACID Guarantees, Isolation Levels & Locking", "Enforce atomic transactions, understand Dirty Reads, Phantom Reads, and optimistic vs pessimistic concurrency.")
        ]
        category = "Relational Databases & SQL"
        lang = "sql"
        code_snip = """-- Complex Analysis with Window Functions and CTE
WITH EmployeeRankings AS (
    SELECT 
        department_id,
        first_name,
        salary,
        DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank_in_dept
    FROM employees
)
SELECT department_id, first_name, salary
FROM EmployeeRankings
WHERE rank_in_dept <= 3;"""
    elif any(k in t_lower for k in ["mongodb", "nosql"]):
        modules = [
            ("NoSQL Document Architecture & BSON Data Types", "Understand non-relational document models, embedding vs referencing, and schema flexibility."),
            ("CRUD Operations, Complex Filtering & Projections", "Execute find, insert, updateMany, deleteOne with atomic field modifiers ($set, $inc, $push)."),
            ("The Aggregation Pipeline: Multi-Stage Transformations", "Chain stages ($match, $group, $lookup, $unwind, $sort, $project) for high-performance data pipelines."),
            ("Indexing Strategies, Compound Keys & Performance Profiling", "Create single-field, compound, TTL, and text indexes; analyze queries using explain('executionStats')."),
            ("Replica Sets, High Availability & Horizontal Sharding", "Configure primary-secondary election topologies, read preferences, write concerns, and shard keys.")
        ]
        category = "NoSQL Databases"
        lang = "javascript"
        code_snip = """// MongoDB Aggregation Pipeline
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: {
      _id: "$customerId",
      totalSpent: { $sum: "$totalAmount" },
      orderCount: { $sum: 1 }
  }},
  { $sort: { totalSpent: -1 } },
  { $limit: 10 }
]);"""
    elif any(k in t_lower for k in ["redis", "caching"]):
        modules = [
            ("In-Memory Computing & Redis Internal Architecture", "Understand single-threaded event loop architecture, RAM storage, and microsecond latency operations."),
            ("Core Data Structures: Strings, Hashes, Lists, Sets & Sorted Sets", "Manipulate key-value pairs, hash objects, queues (LPUSH/RPOP), and leaderboards with ZSETs."),
            ("Caching Patterns: Cache-Aside, Write-Through & TTL Policies", "Implement resilient application caching, configure TTL expiration, and select eviction policies (LRU/LFU)."),
            ("Pub/Sub Messaging, Redis Streams & Distributed Locks", "Publish events to channels, process continuous message streams, and acquire atomic distributed locks with Redlock."),
            ("Persistence (RDB/AOF), Clustering & High Availability", "Configure background snapshots (RDB), Append-Only Files (AOF), Sentinel monitoring, and Redis Cluster sharding.")
        ]
        category = "In-Memory Systems & Caching"
        lang = "python"
        code_snip = """# Redis Leaderboard Implementation with Sorted Sets
import redis

client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Update player scores
client.zadd('leaderboard:gaming', {'Alice': 1500, 'Bob': 2300, 'Charlie': 1850})

# Get top 3 players
top_players = client.zrevrange('leaderboard:gaming', 0, 2, withscores=True)
for rank, (player, score) in enumerate(top_players, 1):
    print(f"#{rank} {player}: {score} pts")"""
    elif any(k in t_lower for k in ["kafka", "event"]):
        modules = [
            ("Event-Driven Architecture & Apache Kafka Core Architecture", "Understand distributed commit logs, brokers, ZooKeeper/KRaft consensus, and pub/sub decoupling."),
            ("Topics, Partitions, Message Ordering & Retention", "Design partition keys, guarantee per-partition message ordering, and configure log compaction and retention."),
            ("Kafka Producers: Serialization, Batching & Delivery Semantics", "Configure producer idempotence, batch sizing (linger.ms), compression (snappy/gzip), and ACKs (all)."),
            ("Kafka Consumers: Consumer Groups, Offsets & Rebalancing", "Scale horizontal consumption with consumer groups, manage manual commit offsets, and handle consumer rebalance."),
            ("Kafka Streams, Kafka Connect & Enterprise Production Deployment", "Build real-time stream processing topologies, stream-table duality (KTable), and mirror clusters across clouds.")
        ]
        category = "Distributed Streaming & Messaging"
        lang = "java"
        code_snip = """// Kafka Producer Configuration in Java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("acks", "all");
props.put("enable.idempotence", "true");

Producer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("orders-topic", "order-101", "{\"amount\": 99.99}"));
producer.close();"""
    elif any(k in t_lower for k in ["c#", ".net"]):
        modules = [
            ("C# Language Fundamentals, Type System & CLR Runtime", "Master modern C# syntax, value vs reference types, nullable types, and garbage collection in the CLR."),
            ("Object-Oriented Design, Interfaces & Generics", "Implement clean OOP hierarchies, generic collections, interface contracts, and dependency injection."),
            ("LINQ (Language Integrated Query) & Functional Transformations", "Write expressive data queries with LINQ syntax, projection, filtering, grouping, and lazy evaluation."),
            ("Asynchronous Programming with async/await & TPL", "Manage non-blocking asynchronous operations, prevent UI freezing, and handle cancellation tokens."),
            ("Building Web APIs with ASP.NET Core & Entity Framework", "Architect RESTful services, configure middleware pipelines, and manage database migrations with EF Core.")
        ]
        category = "Enterprise Software Development"
        lang = "csharp"
        code_snip = """// ASP.NET Core Web API Controller
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase {
    [HttpGet("{id}")]
    public async Task<IActionResult> GetUserById(int id) {
        var user = new { Id = id, Name = "Alex Taylor", Status = "Active" };
        return Ok(user);
    }
}"""
    elif any(k in t_lower for k in ["golang", "go"]):
        modules = [
            ("Go Syntax, Types, Structs & Pointers", "Explore clean Go syntax, zero values, explicit error handling, and pointer memory semantics."),
            ("Concurrency in Go: Goroutines & Channels", "Launch lightweight goroutines, communicate via unbuffered/buffered channels, and select statement coordination."),
            ("Interfaces, Composition & Object Design Without Classes", "Implement implicit interfaces, struct embedding, and idiomatic Go architectural composition."),
            ("Building Production REST Microservices with Go", "Utilize the standard library net/http, structured logging, middleware wrapping, and JSON serialization."),
            ("Go Modules, Unit Testing, Benchmarking & Tooling", "Write table-driven tests (testing.T), benchmark execution speed (testing.B), and manage dependencies with go.mod.")
        ]
        category = "Systems Programming & Backend"
        lang = "go"
        code_snip = """package main
import (
    "fmt"
    "time"
)

func worker(id int, ch chan string) {
    time.Sleep(100 * time.Millisecond)
    ch <- fmt.Sprintf("Worker %d completed task", id)
}

func main() {
    ch := make(chan string, 2)
    go worker(1, ch)
    go worker(2, ch)
    fmt.Println(<-ch)
    fmt.Println(<-ch)
}"""
    elif any(k in t_lower for k in ["rust"]):
        modules = [
            ("Rust Syntax, Primitive Types & Memory Safety Paradigm", "Understand strong static typing, immutable variables by default, and compiling with cargo."),
            ("Ownership, Borrowing Rules & Lifetime Mechanics", "Master Rust's flagship ownership rules: single owner, mutable vs immutable references, and lifetimes."),
            ("Structs, Enums, Pattern Matching & Error Handling", "Model domain data with custom structs and enums; handle errors gracefully using Result<T, E> and Option<T>."),
            ("Traits, Generics & Functional Programming with Iterators", "Define reusable shared behavior with traits, implement generic constraints, and use zero-cost iterators."),
            ("Fearless Concurrency, Multithreading & Safe Data Sharing", "Spawn OS threads safely, transfer ownership across threads, and share mutable state using Arc<Mutex<T>>.")
        ]
        category = "Systems Programming"
        lang = "rust"
        code_snip = """// Rust Ownership and Pattern Matching Example
fn find_even(num: i32) -> Result<String, String> {
    if num % 2 == 0 {
        Ok(format!("{} is an even number", num))
    } else {
        Err(format!("{} is an odd number", num))
    }
}

fn main() {
    match find_even(42) {
        Ok(msg) => println!("Success: {}", msg),
        Err(err) => println!("Error: {}", err),
    }
}"""
    elif any(k in t_lower for k in ["postman", "api testing", "rest api"]):
        modules = [
            ("REST Architecture, HTTP Methods & Status Code Best Practices", "Master GET, POST, PUT, PATCH, DELETE operations, request headers, query parameters, and JSON payloads."),
            ("Postman Collections, Environments & Variable Scopes", "Organize requests into logical collections, manage environment, collection, and global variables dynamically."),
            ("Automated Test Scripting & Schema Validation with Chai.js", "Write assertions using pm.test and pm.expect, validate response status, latency, and JSON schema compliance."),
            ("Data-Driven Testing with CSV/JSON & Newman CLI Integration", "Execute collection runs with external dataset iterations and integrate Newman into CI/CD pipelines."),
            ("Mock Servers, Team Workspaces & Interactive API Documentation", "Create mock endpoints for frontend parallel development and generate public/private API documentation.")
        ]
        category = "API Engineering & Quality Assurance"
        lang = "javascript"
        code_snip = """// Postman Chai.js Test Script
pm.test("Status code is 200 OK", function () {
    pm.response.to.have.status(200);
});

pm.test("Response time is under 300ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(300);
});

pm.test("Payload contains required user ID", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.id).to.be.a('number');
});"""
    elif "c++" in t_lower or "cpp" in t_lower:
        modules = [
            ("C++ Syntax, Pointers & Memory Architecture", "Master basic syntax, pointer arithmetic, memory references, and stack vs heap allocation."),
            ("Object-Oriented Programming in C++", "Implement classes, destructors, copy constructors, operator overloading, and RAII patterns."),
            ("Standard Template Library (STL) Mastery", "Leverage vectors, maps, sets, iterators, and high-performance algorithms."),
            ("Smart Pointers & Modern C++ Idioms", "Use unique_ptr, shared_ptr, move semantics, and lambda expressions in C++14/17/20."),
            ("Performance Optimization & Concurrency", "Utilize multi-threading (std::thread), mutex synchronization, and compiler profiling flags.")
        ]
        category = "Systems Programming"
        lang = "cpp"
        code_snip = "#include <iostream>\n#include <vector>\n\nint main() {\n    std::vector<int> nums = {1, 2, 3, 4, 5};\n    for (int n : nums) {\n        std::cout << n << \" \";\n    }\n    std::cout << std::endl;\n    return 0;\n}"
    else:
        # Universal pedagogical 5-module structure for any technical topic
        modules = [
            (f"Architecture, Ecosystem & Fundamentals of {clean_topic}", f"Understand the core architecture, foundational building blocks, and setup requirements for {clean_topic}."),
            (f"Core Syntax, Primitives & Working Mechanisms of {clean_topic}", f"Explore essential syntax, primary operations, and standard methodologies in {clean_topic}."),
            (f"Practical Implementation & Component Design in {clean_topic}", f"Build hands-on implementations and apply proven architectural design patterns with {clean_topic}."),
            (f"Data Flow, API Integration & State Handling in {clean_topic}", f"Manage input/output streams, error boundaries, and external data services in {clean_topic}."),
            (f"Advanced Optimization, Testing & Production Deployment of {clean_topic}", f"Deploy, secure, unit test, and profile performance benchmarks for enterprise {clean_topic} applications.")
        ]
        category = "Technology & Computer Science"
        lang = "python"
        code_snip = f"# Demonstration of {clean_topic} core logic\ndef run_demo():\n    topic = '{clean_topic}'\n    print(f'Initializing {{topic}} module...')\n    return True\n\nif __name__ == '__main__':\n    run_demo()"

    chapters = []
    for idx, (title, desc) in enumerate(modules, 1):
        chapters.append({
            "chapter_id": idx,
            "name": title,
            "about": desc,
            "duration": "15 mins",
            "explanation": f"### Overview of {title}\n\nIn this comprehensive module, we dive deep into {title.lower()}.\n\n#### Key Objectives\n1. Gain practical conceptual and operational fluency in {clean_topic}.\n2. Apply idiomatic industry conventions and avoid common design anti-patterns.\n3. Integrate these methodologies into real-world software engineering workflows.\n\n#### Conceptual Breakdown\n{desc} Professional software teams rely on these proven patterns to write testable, decoupled, and maintainable software.",
            "key_takeaways": [
                f"Master the core operational principles of {title.split(':')[0]}.",
                f"Follow industry best practices for code reliability and maintainability.",
                f"Understand how {clean_topic} fits into end-to-end software delivery."
            ],
            "code_examples": [
                {
                    "title": f"Practical Implementation: {title.split(':')[0]}",
                    "language": lang,
                    "code": code_snip,
                    "explanation": f"This code demonstrates practical implementation of {title.split(':')[0]}."
                }
            ],
            "coding_challenge": {
                "title": f"{clean_topic} Practical Challenge",
                "description": f"Implement a basic function illustrating the primary mechanism of {title.split(':')[0]}.",
                "starter_code": code_snip,
                "language": lang,
                "test_cases": [
                    {"input": "default", "expected_output": "True"}
                ]
            },
            "quiz": [
                {
                    "question": f"What is the main objective of {title.split(':')[0]}?",
                    "options": [
                        f"To build structured, reliable, and testable code for {clean_topic}",
                        "To bypass compiler and runtime type checks",
                        "To replace all operating system memory controls",
                        "None of the above"
                    ],
                    "correct_answer": 0,
                    "explanation": f"This module provides the structural and functional core for {clean_topic}."
                }
            ]
        })

    return {
        "name": clean_topic,
        "category": category,
        "summary": f"A comprehensive, industry-aligned course covering fundamental to advanced concepts in {clean_topic}.",
        "chapters": chapters
    }


def get_curated_course(topic: Any) -> Dict[str, Any]:
    """Retrieve pre-curated full-fidelity course if matching topic, else generate structured curriculum."""
    if isinstance(topic, dict):
        topic = topic.get("topic") or topic.get("name") or topic.get("title") or ""
    topic_lower = (topic or "").lower().strip()
    # Remove leading punctuation
    topic_lower = re.sub(r"^[&\s+\-•*,]+", "", topic_lower).strip()

    for key, data in SYLLABUS_KNOWLEDGE_BASE.items():
        if key in topic_lower or topic_lower in key:
            return data

    aliases = {
        "node": "javascript",
        "web": "javascript",
        "frontend": "javascript",
        "backend": "python",
        "django": "python",
        "flask": "python",
        "fastapi": "python",
        "ai": "machine learning",
        "deep learning": "machine learning",
        "nlp": "machine learning",
        "data science": "machine learning",
        "spring": "java",
        "spring boot": "java",
        "sql": "sql",
        "mysql": "sql",
        "postgres": "sql",
        "postgresql": "sql",
        "database": "sql",
        "docker": "docker",
        "container": "docker",
        "soft skills": "soft skills",
        "soft skill": "soft skills",
        "communication": "soft skills",
        "interview": "soft skills",
    }
    for alias, target in aliases.items():
        if alias in topic_lower:
            return SYLLABUS_KNOWLEDGE_BASE.get(target)

    # Return dynamically generated high-fidelity curriculum for any technical topic
    return generate_smart_curriculum(topic)
