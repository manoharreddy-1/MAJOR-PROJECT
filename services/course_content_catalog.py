"""Comprehensive syllabus, concept breakdowns, code examples, coding questions, and test cases for popular topics."""
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
        // Primitive variables
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
        // Write your solution here
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
                        {"input": "0", "expected_output": "Even"},
                        {"input": "-3", "expected_output": "Odd"}
                    ]
                }
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
                        {"input": "0", "expected_output": "1"},
                        {"input": "1", "expected_output": "1"},
                        {"input": "5", "expected_output": "120"},
                        {"input": "6", "expected_output": "720"}
                    ]
                }
            },
            {
                "chapter_id": 3,
                "name": "Object-Oriented Programming (OOP) in Java",
                "about": "Explore the 4 pillars of OOP: Encapsulation, Inheritance, Polymorphism, and Abstraction.",
                "duration": "25 mins",
                "explanation": "OOP structures software around real-world entities. Encapsulation hides private fields with public getters/setters. Inheritance allows subclasses to extend base classes with 'extends'. Polymorphism enables method overriding (@Override) and dynamic method dispatch. Abstraction uses abstract classes and interfaces with 'implements'.",
                "key_takeaways": [
                    "Classes are blueprints; objects are instantiated runtime instances.",
                    "Encapsulation protects class invariants from direct external manipulation.",
                    "Java supports single class inheritance and multiple interface implementation.",
                    "Polymorphism allows treating derived objects as their parent type."
                ],
                "code_examples": [
                    {
                        "title": "Inheritance and Polymorphism",
                        "language": "java",
                        "code": """abstract class Animal {
    protected String name;
    public Animal(String name) { this.name = name; }
    public abstract void speak();
}

class Dog extends Animal {
    public Dog(String name) { super(name); }
    @Override
    public void speak() {
        System.out.println(name + " says: Woof!");
    }
}

public class OOPDemo {
    public static void main(String[] args) {
        Animal pet = new Dog("Buddy");
        pet.speak();
    }
}""",
                        "explanation": "Demonstrates an abstract class with a polymorphic method implemented by Dog."
                    }
                ],
                "coding_challenge": {
                    "title": "Reverse a String",
                    "description": "Implement a method that takes a String and returns its reversed version without using built-in StringBuilder.reverse().",
                    "starter_code": """public class Solution {
    public static String reverseString(String s) {
        char[] chars = s.toCharArray();
        int left = 0, right = chars.length - 1;
        while (left < right) {
            char temp = chars[left];
            chars[left] = chars[right];
            chars[right] = temp;
            left++;
            right--;
        }
        return new String(chars);
    }

    public static void main(String[] args) {
        System.out.println(reverseString("java"));
    }
}""",
                    "language": "java",
                    "test_cases": [
                        {"input": "java", "expected_output": "avaj"},
                        {"input": "hello", "expected_output": "olleh"},
                        {"input": "racecar", "expected_output": "racecar"},
                        {"input": "a", "expected_output": "a"}
                    ]
                }
            },
            {
                "chapter_id": 4,
                "name": "Java Collections Framework (ArrayList, HashMap, HashSet)",
                "about": "Learn data structures in Java: List, Set, Map, and generic algorithms.",
                "duration": "20 mins",
                "explanation": "The Java Collections Framework provides standardized interfaces and high-performance data structures. ArrayList offers dynamic arrays with O(1) random access. LinkedList provides fast insertions. HashSet prevents duplicates with O(1) lookup. HashMap stores key-value pairs with hashing algorithms.",
                "key_takeaways": [
                    "List maintains insertion order; Set stores only unique elements.",
                    "Map stores key-value associations; keys are unique.",
                    "Always use generics (e.g. List<String> list = new ArrayList<>()) for compile-time type safety."
                ],
                "code_examples": [
                    {
                        "title": "HashMap & Frequency Counting",
                        "language": "java",
                        "code": """import java.util.HashMap;
import java.util.Map;

public class CollectionsDemo {
    public static void main(String[] args) {
        String[] words = {"apple", "banana", "apple", "orange", "banana", "apple"};
        Map<String, Integer> freq = new HashMap<>();

        for (String word : words) {
            freq.put(word, freq.getOrDefault(word, 0) + 1);
        }

        System.out.println("Word Frequencies: " + freq);
    }
}""",
                        "explanation": "Uses Map.getOrDefault to calculate frequency distribution."
                    }
                ],
                "coding_challenge": {
                    "title": "Find Maximum in Array",
                    "description": "Write a method that takes an array of integers and returns the maximum element.",
                    "starter_code": """public class Solution {
    public static int findMax(int[] arr) {
        int max = arr[0];
        for (int num : arr) {
            if (num > max) {
                max = num;
            }
        }
        return max;
    }

    public static void main(String[] args) {
        int[] nums = {3, 7, 2, 9, 5};
        System.out.println(findMax(nums));
    }
}""",
                    "language": "java",
                    "test_cases": [
                        {"input": "[3, 7, 2, 9, 5]", "expected_output": "9"},
                        {"input": "[-10, -3, -50]", "expected_output": "-3"},
                        {"input": "[100]", "expected_output": "100"}
                    ]
                }
            },
            {
                "chapter_id": 5,
                "name": "Exception Handling & Robust File I/O",
                "about": "Handle runtime errors gracefully using try-catch-finally, custom exceptions, and try-with-resources.",
                "duration": "20 mins",
                "explanation": "Exceptions in Java are recoverable conditions represented as objects inheriting from Throwable. Checked exceptions must be caught or declared with 'throws'. Unchecked exceptions (RuntimeException) occur at runtime like NullPointerException or IndexOutOfBoundsException. try-with-resources ensures auto-closing of streams.",
                "key_takeaways": [
                    "Use try-catch to intercept expected failures without crashing.",
                    "finally blocks always execute, guaranteeing cleanup operations.",
                    "try-with-resources automatically closes AutoCloseable resources like files."
                ],
                "code_examples": [
                    {
                        "title": "Safe Parsing & Try-Catch Block",
                        "language": "java",
                        "code": """public class ExceptionDemo {
    public static void main(String[] args) {
        String[] inputs = {"100", "250", "invalid_num", "400"};

        for (String str : inputs) {
            try {
                int val = Integer.parseInt(str);
                System.out.println("Parsed: " + val);
            } catch (NumberFormatException e) {
                System.err.println("Warning: Cannot parse '" + str + "': " + e.getMessage());
            }
        }
    }
}""",
                        "explanation": "Handles NumberFormatException when iterating over user input."
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
        System.out.println(isPalindrome("A man, a plan, a canal: Panama"));
    }
}""",
                    "language": "java",
                    "test_cases": [
                        {"input": "racecar", "expected_output": "true"},
                        {"input": "hello", "expected_output": "false"},
                        {"input": "Madam", "expected_output": "true"}
                    ]
                }
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
                        "code": """# List of numbers
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Filter even squares
even_squares = [x**2 for x in numbers if x % 2 == 0]
print(f"Even squares: {even_squares}")

# Dictionary mapping
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
                        {"input": "nums=[3, 2, 4], target=6", "expected_output": "[1, 2]"},
                        {"input": "nums=[3, 3], target=6", "expected_output": "[0, 1]"}
                    ]
                }
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

print(f"Result: {compute_sum(1000000)}")""",
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
                        {"input": "s='rat', t='car'", "expected_output": "False"},
                        {"input": "s='listen', t='silent'", "expected_output": "True"}
                    ]
                }
            }
        ]
    }
}


def get_curated_course(topic: str) -> Dict[str, Any]:
    """Retrieve pre-curated full-fidelity course if matching topic, else generate structured curriculum."""
    topic_lower = topic.lower().strip()
    for key, data in SYLLABUS_KNOWLEDGE_BASE.items():
        if key in topic_lower or topic_lower in key:
            return data
    return None
