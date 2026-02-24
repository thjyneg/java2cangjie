package j2cjlib.mappings.io

import std.fs.exists
import std.fs.removeIfExists
import std.fs.File
import std.fs.FileInfo
import std.fs.Path
import j2cjlib.mappings.lang.HashableImpl

public class J2CjFile <: Hashable & ToString & Equatable<J2CjFile> {
    private let path: Path

    public init(pathname: String) {
        path = Path(pathname)
    }

    public func exists(): Bool {
        return exists(path)
    }

    public func getName(): String {
        return path.fileName
    }

    public func isFile(): Bool {
        return exists() && FileInfo(path).isRegular()
    }

    public func isDirectory(): Bool {
        return exists() && FileInfo(path).isDirectory()
    }

    public func getParent(): String {
        return path.parent.toString()
    }

    public func isAbsolute(): Bool {
        return path.isAbsolute()
    }

    public func canRead(): Bool {
        return exists() && FileInfo(path).canRead()
    }

    public func canWrite(): Bool {
        return exists() && FileInfo(path).canWrite()
    }

    public func canExecute(): Bool {
        return exists() && FileInfo(path).canExecute()
    }
    
    public func isHidden(): Bool {
        return exists() && FileInfo(path).isHidden()
    }

    public func lastModified(): Int64 {
        if (!exists()) {
            return 0
        }
        return FileInfo(path).lastModificationTime.toUnixTimeStamp().toMilliseconds()
    }

    public func length(): Int64 {
        if (!exists()) {
            return 0
        }
        return FileInfo(path).size
    }

    public func createNewFile(): Bool {
        if (exists()) {
            return false
        }
        File.create(path)
        return true
    }

    public func delete(): Bool {
        return removeIfExists(path)
    }

    public open func hashCode(): Int64 {
        return this.hashCodeImpl()
    }

    public func toString(): String {
        return path.toString()
    }

    public operator func == (that: J2CjFile): Bool {
        return this.path == that.path
    }

    public operator func != (that: J2CjFile): Bool {
        return !(this == that)
    }
}