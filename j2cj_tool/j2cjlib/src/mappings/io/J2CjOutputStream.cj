package j2cjlib.mappings.io

import std.io.OutputStream

public open class J2CjOutputStream <: OutputStream {
    override public open func write(buffer: Array<Byte>): Unit {
        write(Some(buffer))
    }

    public open func write(var1: Int32): Unit {
        // TODO
    }

    public open func write(var1: ?Array<UInt8>): Unit {
        // TODO
    }

    public open func write(var1: ?Array<UInt8>, var2: Int32, var3: Int32): Unit {
        // TODO
    }

    override public open func flush(): Unit {}

    public open func close(): Unit {}
}