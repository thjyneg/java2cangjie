package j2cjlib_android.mappings

import kit.ArkData.*

public class SharedPreferences {

    private let preferences: Preferences

    public init(preferences: Preferences) {
        this.preferences = preferences
    }

    public func getString(key: ?String, defValue: ?String): ?String {
        let result = preferences.get(key, PreferencesValueType.string(defValue))
        match (result) {
            case PreferencesValueType.string(n) => return n
            case _ => throw Exception()
        }
    }

    public func getBoolean(key: ?String, defValue: Boolean): Boolean {
        let result = preferences.get(key, PreferencesValueType.bool(defValue))
        match (result) {
            case PreferencesValueType.bool(n) => return n
            case _ => throw Exception()
        }
    }

    public func getFloat(key: ?String, defValue: Float64): Float64 {
        let result = preferences.get(key, PreferencesValueType.double(defValue))
        match (result) {
            case PreferencesValueType.double(n) => return n
            case _ => throw Exception()
        }
    }

    public func getInt(key: ?String, defValue: Int32): Int32 {
        return Int32(getLong(key, Int64(defValue)))
    }

    public func getLong(key: ?String, defValue: Int64): Int64 {
        let result = preferences.get(key, PreferencesValueType.integer(defValue))
        match (result) {
            case PreferencesValueType.integer(n) => return n
            case _ => throw Exception()
        }
    }
}
