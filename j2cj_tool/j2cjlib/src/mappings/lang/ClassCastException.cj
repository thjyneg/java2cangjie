package j2cjlib.mappings.lang

public open class ClassCastException <: Exception {
    public init() {
        super()
    }

    public init(message: String) {
        super(message)
    }

    protected open override func getClassName(): String {
        "ClassCastException"
    }
}