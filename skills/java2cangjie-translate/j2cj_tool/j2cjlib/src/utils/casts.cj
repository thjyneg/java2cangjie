package j2cjlib.utils

import std.reflect.TypeInfo
import j2cjlib.mappings.lang.ClassCastException

public func checkOptionalIs<T, U>(optional: Option<U>): Bool {
    return match (optional) {
        case Some(_: T) => true
        case _          => false
    }
}

public func castOrThrow<T, U>(optional: Option<T>): Option<U> {
    return match (optional) {
        case Some(v: U) => v
        case None => None
        case Some(v) =>
            throw ClassCastException("${TypeInfo.of(v).qualifiedName} cannot be cast to ${TypeInfo.of<U>().qualifiedName}")
    }
}
