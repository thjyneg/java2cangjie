package j2cjlib.mappings.io

import std.io.StringWriter
import std.io.OutputStream

public open class J2CjPrintStream <: J2CjWriter {
    private let stringWriter: StringWriter<OutputStream>

    public init(output: OutputStream) {
        stringWriter = StringWriter<OutputStream>(output)
    }

    override public open func flush(): Unit {
        stringWriter.flush()
    }

    override public open func close(): Unit {}

    override public open func write(s: String): Unit {
        stringWriter.write(s)
    }

    public open func println(v: String): Unit {
        stringWriter.writeln(v)
    }

    public func println<T>(v: T): Unit where T <: ToString {
        stringWriter.writeln(v.toString())
    }

    public open func println(): Unit {
        stringWriter.writeln()
    }

    public open func println(rn: Rune): Unit {
        stringWriter.writeln(rn)
    }

    public open func println(b: Bool): Unit {
        stringWriter.writeln(b)
    }

    public open func println(i: Int8): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: Int16): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: Int32): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: Int64): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: UInt8): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: UInt16): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: UInt32): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: UInt64): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: Float16): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: Float32): Unit {
        stringWriter.writeln(i)
    }

    public open func println(i: Float64): Unit {
        stringWriter.writeln(i)
    }

    public open func print(v: String): Unit {
        stringWriter.write(v)
    }

    public func print<T>(v: T): Unit where T <: ToString {
        stringWriter.write(v.toString())
    }

    public open func print(rn: Rune): Unit {
        stringWriter.write(rn)
    }

    public open func print(b: Bool): Unit {
        stringWriter.write(b)
    }

    public open func print(i: Int8): Unit {
        stringWriter.write(i)
    }

    public open func print(i: Int16): Unit {
        stringWriter.write(i)
    }

    public open func print(i: Int32): Unit {
        stringWriter.write(i)
    }

    public open func print(i: Int64): Unit {
        stringWriter.write(i)
    }

    public open func print(i: UInt8): Unit {
        stringWriter.write(i)
    }

    public open func print(i: UInt16): Unit {
        stringWriter.write(i)
    }

    public open func print(i: UInt32): Unit {
        stringWriter.write(i)
    }

    public open func print(i: UInt64): Unit {
        stringWriter.write(i)
    }

    public open func print(i: Float16): Unit {
        stringWriter.write(i)
    }

    public open func print(i: Float32): Unit {
        stringWriter.write(i)
    }

    public open func print(i: Float64): Unit {
        stringWriter.write(i)
    }
}