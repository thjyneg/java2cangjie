package j2cjlib.utils

import std.sync.Monitor
import std.collection.HashMap
import j2cjlib.mappings.lang.HashableImpl

public interface Synchronizable {
    func getMonitor(): Monitor
}

class KeyWrapper <: Hashable & Equatable<KeyWrapper> {
    let obj: Object

    init(obj: Object) {
        this.obj = obj
    }

    public func hashCode(): Int64 {
        return obj.hashCodeImpl()
    }

    public operator func == (that: KeyWrapper): Bool {
        return refEq(obj, that.obj)
    }

    public operator func != (that: KeyWrapper): Bool {
        return !(this == that)
    }
}

let OBJECTS_WITH_MONITOR = HashMap<KeyWrapper, Monitor>()
let OBJECTS_WITH_MONITOR_LOCK_OBJECT = Monitor()

public func getMonitorByObject(obj: Object): Monitor {
    match (obj) {
        case v: Synchronizable => v.getMonitor()
        case _ =>
            let wrapped = KeyWrapper(obj)
            synchronized (OBJECTS_WITH_MONITOR_LOCK_OBJECT) {
                match (OBJECTS_WITH_MONITOR.get(wrapped)) {
                     case Some(m) => m
                     case None =>
                         let newMonitor = Monitor()
                         OBJECTS_WITH_MONITOR.add(wrapped, newMonitor)
                         newMonitor
                }
            }
    }
}
