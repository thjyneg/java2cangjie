package j2cjlib.mappings.io

import std.io.InputStream
import std.sync.Monitor
import j2cjlib.utils.Synchronizable
import j2cjlib.utils.arraycopy
import j2cjlib.mappings.lang.HashableImpl

public open class J2CjByteArrayInputStream <: InputStream & Synchronizable & Hashable & ToString {
    private let j2cjGeneratedLockObject = Monitor()
    override public func getMonitor(): Monitor { return j2cjGeneratedLockObject }

    protected var buf: ?Array<UInt8> = None

    protected var pos: Int32 = 0

    protected var mark1 = 0i32

    protected var count: Int32 = 0

    public prop length: Int64 {
        get() {
            Int64(count)
        }
    }

    public init(buf: ?Array<UInt8>) {
        this.buf = buf
        this.pos = 0
        this.count = Int32(buf.getOrThrow().size)
    }

    public init(buf: ?Array<UInt8>, offset: Int32, length: Int32) {
        this.buf = buf
        this.pos = offset
        this.count = min(offset + length, Int32(buf.getOrThrow().size))
        this.mark1 = offset
    }

    public open func read(): Int32 {
        synchronized (j2cjGeneratedLockObject) {
            return if (pos < count) { (Int32(buf.getOrThrow()[Int64(match (0) { case _ => pos++; pos - 1 })]) & 255) } else { -1 }
        }
    }

    override public func read(buffer: Array<Byte>): Int64 {
        return Int64(read(buffer, 0, Int32(buffer.size)))
    }

    public open func read(b: ?Array<UInt8>, off: Int32, len: Int32): Int32 {
        synchronized (j2cjGeneratedLockObject) {
            var j2cj_param_generated_len = len
            if ((Int32(b.getOrThrow().size) | off | j2cj_param_generated_len) < 0 || j2cj_param_generated_len > Int32(b.getOrThrow().size) - off) {
                throw Exception()
            }
            if (pos >= count) {
                return -1
            }
            let avail = count - pos
            if (j2cj_param_generated_len > avail) {
                j2cj_param_generated_len = avail
            }
            if (j2cj_param_generated_len <= 0) {
                return 0
            }
            arraycopy(buf, Int64(pos), b, Int64(off), Int64(j2cj_param_generated_len))
            pos += j2cj_param_generated_len
            return j2cj_param_generated_len
        }
    }

    public open func readNBytes(b: ?Array<UInt8>, off: Int32, len: Int32): Int32 {
        let n = read(b, off, len)
        return if (n == -1) { 0 } else { n }
    }

    public open func skip(n: Int64): Int64 {
        synchronized (j2cjGeneratedLockObject) {
            var k = Int64(count - pos)
            if (n < k) {
                k = if (n < 0) { 0 } else { n }
            }
            pos += Int32(k)
            return k
        }
    }

    public open func available(): Int32 {
        synchronized (j2cjGeneratedLockObject) {
            return count - pos
        }
    }

    public open func markSupported(): Bool {
        return true
    }

    public open func mark(readAheadLimit: Int32): Unit {
        mark1 = pos
    }

    public open func reset(): Unit {
        synchronized (j2cjGeneratedLockObject) {
            pos = mark1
        }
    }

    public open func close(): Unit {}

    public open func hashCode(): Int64 {
        return this.hashCodeImpl()
    }

    public open func toString(): String {
        return "J2CjByteArrayInputStream@${this.hashCodeImpl()}"
    }
}

extend J2CjByteArrayInputStream <: Equatable<J2CjByteArrayInputStream> {
    public operator func == (that: J2CjByteArrayInputStream): Bool {
        return refEq(this, that)
    }

    public operator func != (that: J2CjByteArrayInputStream): Bool {
        return !(this == that)
    }
}