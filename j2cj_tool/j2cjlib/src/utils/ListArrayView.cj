package j2cjlib.utils

import std.collection.List

public class ListArrayView<T> <: List<T> {
    private let array: Array<T>

    public init(array: Array<T>) {
        this.array = array
    }

    public prop size: Int64 {
        get() {
            return array.size
        }
    }

    public func isEmpty(): Bool {
        return size == 0
    }

    public prop first: ?T {
        get() {
            get(0)
        }
    }

    public prop last: ?T {
        get() {
            get(size - 1)
        }
    }

    public func get(index: Int64): ?T {
        if (index >= size || index < 0) {
            return None
        }
        return array.get(index)
    }

    public operator func [](index: Int64): T {
        if (index >= size || index < 0) {
            throw IndexOutOfBoundsException("index: ${index}, size: ${size}")
        }
        return array[index]
    }

    public func add(element: T): Unit {
        throw modificationException
    }

    public func add(all!: Collection<T>): Unit {
        throw modificationException
    }

    public func add(element: T, at!: Int64): Unit {
        throw modificationException
    }

    public func add(all!: Collection<T>, at!: Int64): Unit {
        throw modificationException
    }

    public func remove(at!: Int64): T {
        throw modificationException
    }

    public func remove(range: Range<Int64>): Unit {
        throw modificationException
    }

    public func removeIf(predicate: (T) -> Bool): Unit {
        throw modificationException
    }

    public func clear(): Unit {
        throw modificationException
    }

    public operator func [](index: Int64, value!: T): Unit {
        if (index >= size || index < 0) {
            throw IndexOutOfBoundsException("index: ${index}, size: ${size}")
        }
        array[index] = value
    }

    public func iterator(): Iterator<T> {
        return array.iterator()
    }

    private prop modificationException: UnsupportedException {
        get() {
            UnsupportedException("ListArrayView size is fixed")
        }
    }
}
