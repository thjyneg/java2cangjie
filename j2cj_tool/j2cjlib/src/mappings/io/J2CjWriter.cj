package j2cjlib.mappings.io

public abstract class J2CjWriter {
    public open func write(var1: ?Array<Rune>, var2: Int32, var3: Int32): Unit {}

    public open func write(s: String): Unit {}

    public open func flush(): Unit {}

    public open func close(): Unit {}
}