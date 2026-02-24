package j2cjlib.utils

import std.collection.ArrayList
import std.io.StringReader
import std.time.DateTime
import std.unicode.UnicodeStringExtension
import j2cjlib.mappings.lang.HashableImpl

public interface AsAny {
    func asAny(): ?Any
}

extend<T> Option<T> <: AsAny {
    public func asAny(): ?Any {
        match (this) {
            case Some(v: Any) => Some(v)
            case _ => None
        }
    }
}

public interface J2CjStringReaderExtension {
    func read(buf: Array<Rune>): Int32
}

extend<T> StringReader<T> <: J2CjStringReaderExtension {
    public func read(buf: Array<Rune>): Int32 {
        for (i in 0..buf.size) {
            buf[i] = match (read()) {
                case Some(c) => c
                case None => return if (i == 0) { -1 } else { Int32(i) }
            }
        }
        return Int32(buf.size)
    }
}

public interface J2CjStringBuilderExtension {
    func setLength(newLength: Int64): Unit
    func reverse(): StringBuilder
    func get(i: Int64): ?Rune
    func insert(index: Int64, rn: Rune): StringBuilder
    func replace(start: Int64, end: Int64, str: String): StringBuilder
    func deleteRuneAt(index: Int64): StringBuilder
    func indexOf(str: String): Int32
    func lastIndexOf(str: String): Int32
    func append(str: Array<Rune>, offset: Int32, len: Int32): StringBuilder
    func delete(start: Int32, end: Int32): StringBuilder
    func substring(start: Int32, end: Int32): String
    func substring(start: Int32): String
}

extend StringBuilder <: J2CjStringBuilderExtension {
    public func setLength(newLength: Int64) {
        let asString = toString()
        let content = String(Array<Rune>(newLength) {
                i => if (i < min(newLength, size)) { Rune(asString[i]) } else { r'\u{0000}' }
        })
        reset(capacity: if (newLength > 0) { newLength } else { None })
        append(content)
    }

    public func reverse(): StringBuilder {
        return StringBuilder(toString().toArray().reverse().toString())
    }

    public func get(i: Int64): ?Rune {
        return Rune(toString()[i])
    }

    // Warning!
    // The function doesn't consider charset change for char -> Rune, java.lang.String -> std$core.String
    // and java.lang.StringBuilder -> std$core.StringBuilder
    // Semantic preservation is guaranteed only for ASCII-defined characters
    // To Be Reimplemented
    public func insert(index: Int64, rn: Rune): StringBuilder {
        let asString = toString()
        let incSize = size + 1
        reset(capacity: incSize)
        let content = String(Array<Rune>(incSize) {
            i => if (i == index) { rn }
                 else if (i < index) { Rune(asString[i]) }
                 else { Rune(asString[i - 1]) }
        })
        append(content)
        return this
    }

    // Warning!
    // The function doesn't consider charset change for char -> Rune, java.lang.String -> std$core.String
    // and java.lang.StringBuilder -> std$core.StringBuilder
    // Semantic preservation is guaranteed only for strings of ASCII-defined characters
    // To Be Reimplemented
    public func replace(start: Int64, end: Int64, str: String): StringBuilder {
        let asString = toString()
        let incSize = max(capacity, size + str.size)
        reset(capacity: incSize)
        append(asString[..start])
        append(str)
        append(asString[end..])
        this
    }

    // Warning!
    // The function doesn't consider charset change for char -> Rune, java.lang.String -> std$core.String
    // and java.lang.StringBuilder -> std$core.StringBuilder
    // Semantic preservation is guaranteed only for string builders of ASCII-defined characters
    // To Be Reimplemented
    public func deleteRuneAt(index: Int64): StringBuilder {
        let asString = toString()
        reset(capacity: capacity)
        append(asString[..index])
        append(asString[index + 1..])
        this
    }

    public func indexOf(str: String): Int32 {
        indexOfWrap(toString().indexOf(str))
    }

    public func lastIndexOf(str: String): Int32 {
        indexOfWrap(toString().lastIndexOf(str))
    }

    public func append(str: Array<Rune>, offset: Int32, len: Int32): StringBuilder {        
        append(str[Int64(offset)..Int64(offset+len)])
        this
    }

    public func delete(start: Int32, end: Int32): StringBuilder {
        let asString = toString()        
        reset(capacity: capacity)
        append(asString[..Int64(start)])
        append(asString[Int64(end)..])
        this
    }

    public func substring(start: Int32, end: Int32): String {
        toString()[Int64(start)..Int64(end)]
    }

    public func substring(start: Int32): String {
        substring(start, Int32(size))
    }
}

public interface J2CjOrderingExtension {
    func value(): Int32
}

extend Ordering <: J2CjOrderingExtension {
    public func value(): Int32 {
        return match (this) {
            case LT => -1
            case GT => 1
            case EQ => 0
        }
    }
}

public interface J2CjStringExtension {
    func equals(other: String): Bool
    func equals(other: ?String): Bool
    func equalsIgnoreCase(other: String): Bool
    func equalsIgnoreCase(other: ?String): Bool
}

extend String <: J2CjStringExtension {
    public func equals(other: String): Bool {
        return this == other
    }

    public func equals(other: ?String): Bool {
        return match (other) {
            case Some(o) => this == o
            case None => false
        }
    }

    public func equalsIgnoreCase(other: String): Bool {
        return this.toUpper() == other.toUpper() || this.toLower() == other.toLower()
    }

    public func equalsIgnoreCase(other: ?String): Bool {
        return match (other) {
            case Some(o) => equalsIgnoreCase(o)
            case None => false
        }
    }
}

public interface J2CjBoolExtension {
    operator func |(right: Bool): Bool
    operator func &(right: Bool): Bool
}

extend Bool <: J2CjBoolExtension {
    public operator func |(right: Bool): Bool {
        return this || right;
    }

    public operator func &(right: Bool): Bool {
        return this && right;
    }
}
