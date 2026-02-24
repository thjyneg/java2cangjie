package com.com.example

import UNSUPPORTED.java.lang.Integer
import UNSUPPORTED.java.lang.String
import UNSUPPORTED.java.util.AbstractMap
import std.collection.ArrayList
import std.collection.HashMap
import std.collection.List

public class HelloWorld {
    public init() { }
    public static func javaMain(args: ?Array<?String>): Unit {
        println("Hello, World!")

        let names: List<String> = ArrayList<String>()
        names.add("Alice")
        names.add("Bob")
        names.add("Charlie")

        for (name in names) {
            println("Hello, " + name + "!")
        }

        let scores = HashMap<String, Int32>()
        scores.add("Alice", 95i32)
        scores.add("Bob", 87i32)
        scores.add("Charlie", 92i32)

        println("Scores: " + scores.toString())
    }
}