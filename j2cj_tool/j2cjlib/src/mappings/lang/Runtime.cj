package j2cjlib.mappings.lang

import std.runtime.getMaxHeapSize
import std.runtime.getAllocatedHeapSize

public class Runtime {

    public static let runtime = Runtime()

    private init() {
    }

    public prop maxMemory: Int64 {
        get() {
            getMaxHeapSize()
        }
    }

    public prop totalMemory: Int64 {
        get() {
            getAllocatedHeapSize()
        }
    }

    public prop freeMemory: Int64 {
        get() {
            // TODO: request API to fetch proper free memory information
            let totalMemory = this.totalMemory
            max(min(this.maxMemory - totalMemory, totalMemory - 1024), 64)
        }
    }
}