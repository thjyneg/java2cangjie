package j2cjlib.utils

import std.sync.Monitor
import std.reflect.TypeInfo
import j2cjlib.mappings.lang.ClassCastException

public class ValueBox<T> <: ToString {
    public let value: T

    public init(value: T) {
        this.value = value
    }

    public func toString(): String {
        toString(value)
    }

    public static func check<V>(optional: ?V): Bool {
        match (optional) {
            case Some(_: ValueBox<T>) | Some(_: T) => true
            case _ => false
        }
    }

    public static func cast<V>(optional: ?V): ?T {
        match (optional) {
            case Some(v: ValueBox<T>) => Some(v.value)
            case Some(v: T) => Some(v)
            case None => None
            case Some(v) =>
                throw ClassCastException("${TypeInfo.of(v).qualifiedName} cannot be cast to ${TypeInfo.of<T>().qualifiedName}")
        }
    }
}

extend<T> ValueBox<T> <: Hashable where T <: Hashable {
    public func hashCode(): Int64 {
        value.hashCode()
    }
}

extend<T> ValueBox<T> <: Equatable<T> & Equatable<ValueBox<T>> where T <: Equatable<T> {
    public operator func == (that: T): Bool {
        this.value == that
    }

    public operator func != (that: T): Bool {
        this.value != that
    }

    public operator func == (that: ValueBox<T>): Bool {
        this.value == that.value
    }

    public operator func != (that: ValueBox<T>): Bool {
        this.value != that.value
    }
}

extend<T> ValueBox<T> <: Comparable<T> & Comparable<ValueBox<T>> where T <: Comparable<T> {
    public func compare(that: T): Ordering {
        this.value.compare(that)
    }

    public operator func < (that: T): Bool {
        this.value < that
    }

    public operator func <= (that: T): Bool {
        this.value <= that
    }

    public operator func > (that: T): Bool {
        this.value > that
    }

    public operator func >= (that: T): Bool {
        this.value >= that
    }

    public func compare(that: ValueBox<T>): Ordering {
        this.value.compare(that.value)
    }

    public operator func < (that: ValueBox<T>): Bool {
        this.value < that.value
    }

    public operator func <= (that: ValueBox<T>): Bool {
        this.value <= that.value
    }

    public operator func > (that: ValueBox<T>): Bool {
        this.value > that.value
    }

    public operator func >= (that: ValueBox<T>): Bool {
        this.value >= that.value
    }
}

extend<T> ValueBox<T> <: Synchronizable where T <: Synchronizable {
    public func getMonitor(): Monitor {
        value.getMonitor()
    }
}