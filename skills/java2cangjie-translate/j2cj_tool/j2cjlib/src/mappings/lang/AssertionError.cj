package j2cjlib.mappings.lang

import std.reflect.TypeInfo

func asString<T>(value: ?T): String {
    match (value) {
        case Some(x: String) => x
        case Some(x: ToString) => x.toString()
        case Some(x) =>
            match (x) {
                case v: String => v
                case v: ToString => v.toString()
                case o: Object => "${TypeInfo.of(value).name}@${o.hashCodeImpl()}"
                case _ => TypeInfo.of(value).name
            }
        case None => "null"
    }
}

public open class AssertionError <: Exception & Equatable<AssertionError> & Hashable {
    public init() {
        super()
    }

    private init(detailMessage: ?String) {
        super(detailMessage ?? "")
    }

    public init(detailMessage: ?Object) {
        this(asString(detailMessage))
    }

    public init(detailMessage: Bool) {
        this(detailMessage.toString())
    }

    public init(detailMessage: Rune) {
        this(detailMessage.toString())
    }

    public init(detailMessage: Int32) {
        this(detailMessage.toString())
    }

    public init(detailMessage: Int64) {
        this(detailMessage.toString())
    }

    public init(detailMessage: Float32) {
        this(detailMessage.toString())
    }

    public init(detailMessage: Float64) {
        this(detailMessage.toString())
    }

    public init(message: ?String, cause: ?Exception) {
        this(message)
    }

    public init(message: ?String, cause: ?Error) {
        this(message)
    }

    protected open override func getClassName(): String {
        "AssertionError"
    }

    public open func hashCode(): Int64 {
        return this.hashCodeImpl()
    }

    public open func toString(): String {
        return "AssertionError@${this.hashCodeImpl()}"
    }

    public operator func == (that: AssertionError): Bool {
        return refEq(this, that)
    }

    public operator func != (that: AssertionError): Bool {
        return !(this == that)
    }
}