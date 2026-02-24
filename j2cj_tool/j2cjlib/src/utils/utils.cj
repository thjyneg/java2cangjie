package j2cjlib.utils

import std.math.trunc
import std.reflect.TypeInfo
import std.regex.Regex
import std.collection.ArrayList
import std.collection.List
import std.sort.sort
import j2cjlib.mappings.lang.HashableImpl
import j2cjlib.mappings.util.Comparator

public func arraycopy<T>(src: ?Array<T>, srcPos: Int64, dest: ?Array<T>, destPos: Int64, length: Int64): Unit {
    let srcArray = src.getOrThrow()
    let destArray = dest.getOrThrow()
    destArray[destPos..destPos + length] = srcArray[srcPos..srcPos + length]
}

public func arraycopy<S, T>(src: ?Array<S>, srcPos: Int64, dest: ?Array<T>, destPos: Int64, length: Int64): Unit {
    let srcArray = src.getOrThrow()
    let destArray = dest.getOrThrow()
    for (i in 0..length) {
        destArray[destPos + i] = (srcArray[srcPos + i] as T).getOrThrow()
    }
}

public func indexOfWrap(index: ?Int64): Int32 {
    return match (index) {
        case Some(v) => Int32(v)
        case None => -1
    }
}

public func readWrap(rune: ?Rune): Int32 {
    return match (rune) {
        case Some(r) => Int32(UInt32(r))
        case None => -1
    }
}

public func stringValueOf(value: Any): String {
    match (toStringImpl(value)) {
        case Some(v) => v
        case None => "null"
    }
}

public func toString(value: Any): String {
    match (toStringImpl(value)) {
        case Some(v) => v
        case None => throw NoneValueException()
    }
}

public func toStringImpl(value: Any): ?String {
    match (value) {
        case v: AsAny => match (v.asAny()) {
            case Some(a) => toStringImpl(a)
            case None => None
        }
        case v: ToString => Some(v.toString())
        case o: Object => Some("${TypeInfo.of(value).name}@${o.hashCodeImpl()}")
        case _ => Some(TypeInfo.of(value).name)
    }
}

public func hashCode(value: Any): Int64 {
    match (value) {
        case v: AsAny => match (v.asAny()) {
            case Some(a) => hashCode(a)
            case None => throw NoneValueException()
        }
        case v: Hashable => v.hashCode()
        case v: HashableImpl => v.hashCodeImpl()
        case _ => throw UnsupportedException()
    }
}

public func refEquals<T, U>(a: T, b: U): Bool {
    match ((a, b)) {
        case (o1: Object, o2: Object) => refEq(o1, o2)
        case (o1: AsAny, o2: AsAny) => match ((o1.asAny(), o2.asAny())) {
            case (Some(v1), Some(v2)) => refEquals(v1, v2)
            case (None, None) => true
            case _ => false
        }
        case (o: Object, objLike: AsAny) => match (objLike.asAny()) {
            case Some(value) => refEquals(o, value)
            case None => false
        }
        case (objLike: AsAny, o: Object) => match (objLike.asAny()) {
            case Some(value) => refEquals(value, o)
            case None => false
        }
        case _ => false
    }
}

public func equals<T, U>(a: T, b: U): Bool {
    match ((a, b)) {
        case (o1: AsAny, o2: AsAny) => match ((o1.asAny(), o2.asAny())) {
            case (Some(v1), Some(v2)) => equals(v1, v2)
            case (None, _) => throw NoneValueException()
            case _ => false
        }
        case (o1: AsAny, _) => match (o1.asAny()) {
            case Some(v) => equals(v, b)
            case _ => throw NoneValueException()
        }
        case (_, o2: AsAny) => match (o2.asAny()) {
            case Some(v) => equals(a, v)
            case _ => false
        }
        case (e1: Equatable<Object>, e2: Object) => e1 == e2
        case (e1: Object, e2: Equatable<Object>) => e2 == e1
        case (e1: Equatable<U>, _) => e1 == b
        case (_, e2: Equatable<T>) => e2 == a
        case _ => refEquals(a, b)
    }
}

public func safeEquals<T, U>(a: T, b: U): Bool {
    match ((a, b)) {
        case (o1: AsAny, o2: AsAny) => match ((o1.asAny(), o2.asAny())) {
            case (Some(v1), Some(v2)) => equals(v1, v2)
            case (None, None) => true
            case _ => false
        }
        case (o1: AsAny, _) => match (o1.asAny()) {
            case Some(v) => equals(v, b)
            case _ => false
        }
        case (_, o2: AsAny) => match (o2.asAny()) {
            case Some(v) => equals(a, v)
            case _ => false
        }
        case (e1: Equatable<Object>, e2: Object) => e1 == e2
        case (e1: Object, e2: Equatable<Object>) => e2 == e1
        case (e1: Equatable<U>, _) => e1 == b
        case (_, e2: Equatable<T>) => e2 == a
        case _ => refEquals(a, b)
    }
}

func iterableToStringArray<T>(elements: Iterable<T>): Array<String> {
    let list = ArrayList<String>()
    for (element in elements) {
        list.add(toString(element))
    }
    return list.toArray()
}

public func join<T>(delimiter: String, elements: Iterable<T>): String {
    let arr = match (elements) {
        case coll: Collection<T> =>
            let iterator = coll.iterator()
            Array<String>(coll.size) { _ => toString(iterator.next().getOrThrow()) }
        case _ => iterableToStringArray(elements)
    }
    return String.join(arr, delimiter: delimiter)
}

public func rem(n: Float16, d: Float16): Float16 {
    // TODO: correct implementation of fmod
    return n - trunc(n / d) * d;
}

public func rem(n: Float32, d: Float32): Float32 {
    // TODO: correct implementation of fmod
    return n - trunc(n / d) * d;
}

public func rem(n: Float64, d: Float64): Float64 {
    // TODO: correct implementation of fmod
    return n - trunc(n / d) * d;
}

public func isEmpty(str: ?String): Bool {
    return match (str) {
        case Some(v) => v.isEmpty()
        case None => true
    }
}

public func removeObject<T>(list: List<T>, element: T): Bool where T <: Equatable<T> {
    for (i in 0..list.size) {
        if (list.get(i) == element) {
            list.remove(at: i)
            return true
        }
    }
    return false
}

public func split(regex: Regex, str: ?String): Array<?String> {
    let result = regex.split(str.getOrThrow())

    var end = result.size
    while (end > 0) {
        if (!result[end - 1].isEmpty()) {
            return result[..end].map { x => Some(x) }
        }
        end--
    }
    return []
}

public func sort<T>(list: ?ArrayList<?T>): Unit where T <: Comparable<T> {
    sort<?T>(list.getOrThrow(), stable: true, by: convertComparator(None))
}

public func sort<T>(list: ?ArrayList<?T>, comparator: ?Comparator<T>): Unit {
    sort<?T>(list.getOrThrow(), stable: true, by: convertComparator(comparator))
}

public func sort<T>(array: ?Array<?T>, comparator: ?Comparator<T>): Unit {
    sort<?T>(array.getOrThrow(), stable: true, by: convertComparator(comparator))
}

public func sort<T>(array: ?Array<?T>): Unit where T <: Comparable<T> {
    sort<?T>(array.getOrThrow(), stable: true, by: convertComparator(None))
}

func convertComparator<T>(comparator: ?Comparator<T>): (?T, ?T) -> Ordering {
    match (comparator) {
        case Some(c) => { a: ?T, b: ?T => intToOrdering(c.compare(a, b)) }
        case None => { a: ?T, b: ?T => (a.getOrThrow() as Comparable<T>).getOrThrow().compare(b.getOrThrow()) }
    }
}

func intToOrdering(ordering: Int32): Ordering {
    if (ordering < 0) {
        return Ordering.LT
    }
    if (ordering > 0) {
        return Ordering.GT
    }
    return Ordering.EQ
}

func orderingToInt(ordering: Ordering): Int32 {
    match (ordering) {
        case Ordering.LT => -1
        case Ordering.EQ => 0
        case Ordering.GT => 1
    }
}
