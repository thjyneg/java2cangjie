package j2cjlib.mappings.util

public interface Enumeration<E> <: Iterable<?E> {
    func hasMoreElements(): Bool
    func nextElement(): ?E

    func iterator(): Iterator<?E> {
        return EnumerationIterator<E>(this)
    }
}

class EnumerationIterator<E> <: Iterator<?E> {
    private let enumeration: Enumeration<E>

    public init(enumeration: Enumeration<E>) {
        this.enumeration = enumeration
    }

    public func next(): ??E {
        if (enumeration.hasMoreElements()) {
            return Some(enumeration.nextElement())
        } else {
            return None
        }
    }
}