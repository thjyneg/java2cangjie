package j2cjlib.utils

import std.collection.ReadOnlySet
import std.collection.Set
import std.collection.EquatableCollection

public class SetCollectionView<T> <: Set<T> & EquatableCollection<T> & Equatable<SetCollectionView<T>> & ToString where T <: Equatable<T> {
    private let collection: Collection<T>

    public init(collection: Collection<T>) {
        this.collection = collection
    }

    public func iterator(): Iterator<T> {
        return collection.iterator()
    }

    public prop size: Int64 {
        get() {
            return collection.size
        }
    }

    public func isEmpty(): Bool {
        return collection.isEmpty()
    }

    public func toArray(): Array<T> {
        return collection.toArray()
    }

    public func contains(element: T): Bool {
        match (collection) {
            case set: Set<T> => set.contains(element)
            case coll: EquatableCollection<T> => coll.contains(element)
            case _ => contains0(element)
        }
    }

    private func contains0(element: T): Bool {
        for (item in this where element == item) {
            return true
        }
        return false
    }

    public func contains(all!: Collection<T>): Bool {
        for (element in all where !this.contains(element)) {
            return false
        }
        return true
    }

    public func subsetOf(other: ReadOnlySet<T>): Bool {
        for (element in this where !other.contains(element)) {
            return false
        }
        return true
    }

    public func add(element: T): Bool {
        throw modificationException
    }

    public func add(all!: Collection<T>): Unit {
        throw modificationException
    }

    public func remove(element: T): Bool {
        throw modificationException
    }

    public func remove(all!: Collection<T>): Unit {
        throw modificationException
    }

    public func removeIf(predicate: (T) -> Bool): Unit {
        throw modificationException
    }

    public func clear(): Unit {
        throw modificationException
    }

    public func retain(all!: Set<T>): Unit {
        throw modificationException
    }

    private prop modificationException: UnsupportedException {
        get() {
            UnsupportedException("SetCollectionView is unmodifiable")
        }
    }

    public func clone(): Set<T> {
        return SetCollectionView<T>(collection.toArray())
    }

    public operator func ==(that: SetCollectionView<T>): Bool {
        if (this.size != that.size) {
            return false
        }
        return contains(all: that)
    }

    public operator func !=(that: SetCollectionView<T>): Bool {
        return !(this == that)
    }

    public func toString(): String {
        if (collection.isEmpty()) {
            return "[]"
        }
        let emptyString: String = String.empty
        let elementSize: Int64 = collection.size * 2 + 1
        let stringArray: Array<String> = Array<String>(elementSize, repeat: emptyString)
        stringArray[0] = "["
        var index: Int64 = 1
        for (v in collection) {
            stringArray[index] = toString(v)
            stringArray[index + 1] = ", "
            index += 2
        }
        stringArray[elementSize - 1] = "]"
        return String.join(stringArray)
    }
}
