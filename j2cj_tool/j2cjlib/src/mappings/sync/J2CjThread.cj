package j2cjlib.mappings.sync

import std.collection.HashMap
import std.math.MathExtension
import std.sync.Monitor

import j2cjlib.utils.Synchronizable
import j2cjlib.mappings.lang.HashableImpl

public open class J2CjThread <: J2CjRunnable & Synchronizable & Hashable & ToString {
    private let runnable: ?J2CjRunnable
    private var future: ?Future<Unit> = None
    private var pendingName: ?String = None
    private var thread: ?Thread = None
    private var alive: Bool = false

    private static let nonOwnedThreads = HashMap<ThreadWrapper, J2CjThread>()

    private let lockObject = Monitor()
    private static let staticLockObject = Monitor()
    public open func getMonitor(): Monitor { return lockObject }

    public static prop currentThread: J2CjThread {
        get() {
            synchronized (staticLockObject) {
                let thread = Thread.currentThread
                let key = ThreadWrapper(thread)
                let found = nonOwnedThreads.get(key)
                match (found) {
                    case Some(t) => return t
                    case None =>
                        let created = J2CjThread(None, None, ())
                        created.thread = thread
                        created.alive = true
                        nonOwnedThreads[key] = created
                        return nonOwnedThreads[key]
                }
            }
        }
    }

    public static func sleep(millis: Int64): Unit {
        sleep(Duration.millisecond * millis)
    }

    public static func sleep(millis: Int64, nanos: Int32): Unit {
        if (millis < 0) {
            throw IllegalArgumentException("timeout value is negative")
        }

        if (nanos < 0 || nanos > 999999) {
            throw IllegalArgumentException("nanosecond timeout value out of range")
        }

        var target = millis

        if (nanos > 0 && millis < Int64.Max) {
            target++
        }

        sleep(target)
    }

    public init() {
        this(None, None, ())
    }

    public init(name: String) {
        this(None, name, ())
    }

    public init(runnable: ?J2CjRunnable) {
        this(runnable, None, ())
    }

    public init(runnable: ?J2CjRunnable, name: String) {
        this(runnable, name, ())
    }

    private init(runnable: ?J2CjRunnable, name: ?String, marker: Unit) {
        this.runnable = runnable
        this.pendingName = name
    }

    public func start() {
        synchronized (lockObject) {
            alive = true
            let f = spawn {
                start0()
            }
            future = f
        }
    }

    private func start0(): Unit {
        var t = Thread.currentThread
        thread = t
        synchronized (staticLockObject) {
            nonOwnedThreads[ThreadWrapper(t)] = this
        }
        match (pendingName) {
            case Some(name) => t.name = name
            case None => ()
        }
        run()
        alive = false
    }

    public prop id: Int64 {
        get() {
            match (thread) {
                case Some(t) => t.id
                case None => this.hashCodeImpl()
            }
        }
    }

    public mut prop name: String {
        get() {
            match (thread) {
                case Some(t) => t.name
                case None =>
                    match (pendingName) {
                        case Some(n) => n
                        case None => "Thread-${id}"
                    }
            }
        }
        set(newName) {
            synchronized (lockObject) {
                match (thread) {
                    case Some(t) => t.name = newName
                    case None => pendingName = newName
                }
            }
        }
    }

    public prop isAlive: Bool {
        get() {
            alive
        }
    }

    public open func run(): Unit {
        runnable?.run()
    }

    public func join(): Unit {
        join(0)
    }

    public func join(millis: Int64): Unit {
        synchronized (lockObject) {
            future?.get(millis * Duration.millisecond)
        }
    }

    public func join(millis: Int64, nanos: Int32): Unit {
        if (millis < 0) {
            throw IllegalArgumentException("timeout value is negative")
        }

        if (nanos < 0 || nanos > 999999) {
            throw IllegalArgumentException("nanosecond timeout value out of range")
        }

        var target = millis

        if (nanos > 0 && millis < Int64.Max) {
            target++
        }

        join(target)
    }

    public open func hashCode(): Int64 {
        return this.hashCodeImpl()
    }

    public open func toString(): String {
        return "Thread[${name}]"
    }
}

extend J2CjThread <: Equatable<J2CjThread> {
    public operator func == (that: J2CjThread): Bool {
        return this.id == that.id
    }

    public operator func != (that: J2CjThread): Bool {
        return this.id != that.id
    }
}

struct ThreadWrapper <: Equatable<ThreadWrapper> & Hashable {
    private let thread: Thread

    public init(thread: Thread) {
        this.thread = thread
    }

    public func hashCode(): Int64 {
        return thread.hashCodeImpl()
    }

    public operator func == (that: ThreadWrapper): Bool {
        return refEq(this.thread, that.thread)
    }

    public operator func != (that: ThreadWrapper): Bool {
        return !(this == that)
    }
}