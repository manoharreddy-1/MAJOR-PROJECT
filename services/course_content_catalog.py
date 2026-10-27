"""Comprehensive syllabus, concept breakdowns, code examples, coding questions, test cases, and quizzes for popular topics."""
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
        ]
    }
}


def get_curated_course(topic: str) -> Dict[str, Any]:
    """Retrieve pre-curated full-fidelity course if matching topic, else generate structured curriculum."""
    topic_lower = (topic or "").lower().strip()
    # Remove leading punctuation
    topic_lower = re.sub(r"^[&\s+\-•*,]+", "", topic_lower).strip()

    for key, data in SYLLABUS_KNOWLEDGE_BASE.items():
        if key in topic_lower or topic_lower in key:
            return data

    aliases = {
        "react": "javascript",
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
        "microservices": "java",
        "sql": "sql",
        "mysql": "sql",
        "postgres": "sql",
        "postgresql": "sql",
        "database": "sql",
        "docker": "docker",
        "kubernetes": "docker",
        "container": "docker",
        "soft skills": "soft skills",
        "soft skill": "soft skills",
        "communication": "soft skills",
        "interview": "soft skills",
    }
    for alias, target in aliases.items():
        if alias in topic_lower:
            return SYLLABUS_KNOWLEDGE_BASE.get(target)

    return None
