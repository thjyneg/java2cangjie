package j2cjlib.mappings.lang

public abstract class Enum<E> <: Comparable<E> & Equatable<E> & Hashable & ToString where E <: Enum<E> {
    private let name_value: String
    private let ordinal_value: Int32

    protected init(name: String, ordinal: Int32) {
        this.name_value = name
        this.ordinal_value = ordinal
    }

    public prop name: String {
        get() {
            name_value
        }
    }

    public prop ordinal: Int32 {
        get() {
            ordinal_value
        }
    }

    public operator func < (rhs: E): Bool {
        this.ordinal < rhs.ordinal
    }

    public operator func <= (rhs: E): Bool {
        this.ordinal <= rhs.ordinal
    }

    public operator func > (rhs: E): Bool {
        this.ordinal > rhs.ordinal
    }

    public operator func >= (rhs: E): Bool {
        this.ordinal >= rhs.ordinal
    }

    public func compare(rhs: E): Ordering {
        this.ordinal.compare(rhs.ordinal)
    }

    public func hashCode(): Int64 {
        ordinal_value.hashCode()
    }

    public open func toString(): String {
        name_value
    }

    public operator func == (that: E): Bool {
        refEq(this, that)
    }

    public operator func != (that: E): Bool {
        !(this == that)
    }
}