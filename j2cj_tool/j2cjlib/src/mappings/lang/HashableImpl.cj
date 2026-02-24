package j2cjlib.mappings.lang

public interface HashableImpl {
    func hashCodeImpl(): Int64
}

extend Object <: HashableImpl {
    public func hashCodeImpl(): Int64 {
        return 42
    }
}
