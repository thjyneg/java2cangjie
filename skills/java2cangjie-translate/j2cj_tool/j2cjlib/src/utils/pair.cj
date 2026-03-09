package j2cjlib.utils

import j2cjlib.mappings.lang.HashableImpl

public open class Pair<F, S> <: ToString {
    public let first: ?F
    public let second: ?S

    public init(first: ?F, second: ?S) {
        this.first = first
        this.second = second
    }

    public open func toString(): String {
        return "Pair{${stringValueOf(first)} ${stringValueOf(second)}}"
    }
}

extend<F, S> Pair<F, S> <: Hashable where F <: Hashable, S <: Hashable {
    public func hashCode(): Int64 {
        return first.hashCode() ^ second.hashCode()
    }
}

extend<F, S> Pair<F, S> <: Equatable<Pair<F, S>> where F <: Equatable<F>, S <: Equatable<S> {
    public operator func == (that: Pair<F, S>): Bool {
        return first == that.first && second == that.second
    }

    public operator func != (that: Pair<F, S>): Bool {
        return !(this == that)
    }
}
