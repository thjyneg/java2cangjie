package j2cjlib.mappings.sync

import std.reflect.ClassTypeInfo
import std.reflect.TypeInfo

import j2cjlib.mappings.lang.Enum

public class TimeUnit <: Enum<TimeUnit> {

    public static let NANOSECONDS = TimeUnit("NANOSECONDS", 0i32, Duration.nanosecond)

    public static let MICROSECONDS = TimeUnit("MICROSECONDS", 1i32, Duration.microsecond)

    public static let MILLISECONDS = TimeUnit("MILLISECONDS", 2i32, Duration.millisecond)

    public static let SECONDS = TimeUnit("SECONDS", 3i32, Duration.second)

    public static let MINUTES = TimeUnit("MINUTES", 4i32, Duration.minute)

    public static let HOURS = TimeUnit("HOURS", 5i32, Duration.hour)

    public static let DAYS = TimeUnit("DAYS", 6i32, Duration.day)

    private static func _values(): ?Array<?TimeUnit> {
        return [TimeUnit.NANOSECONDS, TimeUnit.MICROSECONDS, TimeUnit.MILLISECONDS, TimeUnit.SECONDS, TimeUnit.MINUTES, TimeUnit.HOURS, TimeUnit.DAYS]
    }

    private static let _VALUES = TimeUnit._values()

    public static func values(): ?Array<?TimeUnit> {
        return _VALUES.getOrThrow().clone()
    }

    public static func valueOf(name: String): ?TimeUnit {
        return (TypeInfo.of<TimeUnit>() as ClassTypeInfo).getOrThrow().getStaticVariable(name).getValue() as TimeUnit
    }

    private let duration: Duration

    private init(_enum_name: String, _enum_ordinal: Int32, duration: Duration) {
        super(_enum_name, _enum_ordinal)
        this.duration = duration
    }

    public func sleep(timeout: Int64): Unit {
        sleep(duration * timeout)
    }
}
