# Changelog

## 2026-02-08

* Support Java 18 to Java 25 source code and libraries.
* JDK 21 is now required to run J2CJ.
* Run the tool using `--patch-module jdk.compiler=j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main` instead of `-jar j2cj.jar`.
* Nullability analysis is now used in "code style first" mode to automatically resolve `<-- null -->` markers.

## 2025-12-18

* Introduce partial translation: a side panel in IDE that shows the Cangjie version of any Java file (#193).
* Improve method references translation.
* Minor fixes to the translation of `for` loops over numeric ranges.
* Fix unexpected `prop super` in generated `.cjmap` files (#213).
* Fix synthetic main generation in "code style first" mode.
* IntelliJ IDEA Plugin: support `.cjmap` syntax highlighting.

## 2025-11-07

* Use `AtomicReference<T>` to represent volatile fields (#155).
* Fix wrong translation of interface static variables (#154).
* CJMAP now supports file-level package and import declarations.
* Improve `java.util.Optional` mappings.
* Fix issues with conversion of Java primitive types, arrays and `java.lang.String` instances to `Object`.
* IntelliJ IDEA Plugin: add initial Chinese translation to the IDE plugin for recent IDE versions.
* Update documentation.

## 2025-10-08

* Remove j2cjlib dependency in `Code style first` mode (#172, #188).
* Disable `Option<T>` wrapping of every potentially nullable value in `Code style first` mode (#171).
* Simple cases of Java enum types now translate into Cangjie enums, instead of classes with static let variables (#168).
* Improve translation of enums, support for generation of 4 built-in methods of Java enums (partially #191).
* Disable unnecessary marking of calls with completely missing mappings.
* Map functional interfaces usages to function types (#192).
* Translate `for` loops more idiomatically using Cangjie ranges when possible.
* Generate `static const` instead of `static let` when it is possible for field's initializer (#196).
* Fix `StringBuilder` and `TextUtils` mappings for Android.
* Add mappings for `String.getBytes` if charset is UTF-8, `String.equalsIgnoreCase`, `String.toString`.
* Update target Cangjie version to 0.63.3.
* IntelliJ IDEA Plugin: more customizable & more introspectable new J2CJ IDE plugin UI.
* Update documentation.

## 2025-07-31

* Introduce `Code style first` and `Preserve semantics` translation modes (previously known as `idiomatic` and default modes respectively).
* Add mappings for sorting and regex (#165, #169).
* Map `java.util.List` to `std.collection.List` instead of `ArrayList` (#167).
* Omit 'open' modifier for translated types by default in `Code style first` mode (#171).
* Fix wrong translation of interface static variables (#154).
* IntelliJ IDEA Plugin: add option to switch translation mode value.
* Update documentation.

## 2025-06-04

* Fix translator failing on some method overrides (#156).
* Sort and fix mapping statistics in log reports.
* Suppress more useless markers.
* Add support of tuple and function types (#132, #145).
* Fix wait/notify/notifyAll calls when there is no receiver (#131).
* Enable lambda translation in initializers.
* Add idiomatic translation mode by option `-Didiomatic=true` not to generate synthetic members of Equatable, Hashable, ToString (#174).
* IntelliJ IDEA Plugin: add option for idiomatic mode.
* Improve support of method references.
* Update documentation.

## 2025-02-21

* Update documentation.
* IntelliJ IDEA Plugin: introduce advanced options.
* Fix CJMAP generation.
* Fix final variables usage in inner classes.
* Add mappings for `android.text.TextUtils`, `android.content.SharedPreferences`, `android.util.Pair`, `android.util.ArrayMap`, `android.util.ArraySet`, `android.util.LongSparseArray`, `android.util.SparseArray`, `android.util.SparseBooleanArray`, `android.util.SparseIntArray`, `android.util.SparseLongArray`, `android.database.sqlite.SQLiteDatabase`, `android.database.Cursor`.
* Detect Android translation and use mappings for Android.
* Add mapping for `java.io.File`.

## 2025-16-01

* Update cjc version to 0.59.3.
* Update documentation.
* IntelliJ IDEA Plugin: numerous enhancements.
* Add mappings for `java.util.Date` and `CharSequence.length`.
* Fix type parameter erasure in nested class.

## 2024-11-29

* Update documentation.
* IntelliJ IDEA Plugin: add feature to restore JDK path and output directory (#94).
* IntelliJ IDEA Plugin: wrap sourcepath and classpath in quotes (#124).
* Change plugin distribution format to ZIP.

## 2024-11-20

* Update documentation.
* Update J2CJ jar inside IntelliJ IDEA Plugin.
* Fix path separator in IntelliJ IDEA Plugin.

## 2024-11-11

* Fix error occurred during translation of OpenCSV (issue #120).

## 2024-11-05

* Add translation of all kinds of source comments.
* Preserve empty lines in the translated source as the first step towards preserving source formatting.
* Add lambda translation into classes.
* Add method reference translation.
* Add support for the new `extend` Cangjie syntax and behavior.
* Migrate many complex mappings to CJMAP.
* Support tuple types in CJMAP format.
* Add simple mapping correctness analyzer.
* Add ability to filter method candidates from CJMAP.
* Speed up Equatable<T> implementation.
* Improve synthetic enum methods (fix #98).
* Add `module.name` and `module.version` options.
* Provide option to customize generated Cangjie module version (issue #108).
* Add bitwise `|` and `&` operators for boolean support (issue #9).
* Enable switch expressions.
* Enable switch on enum constants.
* Warn if using fall-through strategy in switch statements.
* Update target Cangjie version to 0.57.1.
* Legacy qualified names (with '$' separator of module and package) are no longer supported.
* Improve handling of nullable generic type parameters.
* Provide more useful diagnostics when translator fails.
* Remove primitive JSON-based mapping declaration system in favor of CJMAP.
* Fixes for issues #38, #52, #83, and other unreported problems.

## 2024-09-04

* Android Studio support in J2CJ IntelliJ Plugin.
* Improve documentation.
* Updates for 0.55.1 Cangjie standard library changes.
* Fix translation of the loop with continue inside (#81).
* 新增StringBuilder方法适配.
* Migrate CJMAP syntax from `$` to `.` in qualified names.
* Huge architectural refactoring.
* Fix spaces in generated CJMAP.
* Stricter types in our APIs.
* Fix `compareTo` mapping.
* Fix mangling of module and package names.
* Add some methods of `java.util.Set` mappings.
* Fix multiple module project enhancement (#40).
* Add import for library annotations (#80).
* Prohibit incorrect translation of switch expressions.
* Prohibit incorrect translation of switch statements on enum constants.
* Adapt to new StringBuilder.append API (#75).
* Add some `java.lang.Math` mappings, adjust translation of existed ones (#89).
* Translate Object methods into util functions (#23, #49, #95).
* Unwrap expression when comparing to null (#69).

## 2024-07-15

* Fix remaining fatal failures on ICT codebase.
* Improve documentation.

## 2024-07-08

* Fix translation where last expression is infinite for loop (#56).
* Fix translation of non-ASCII Unicode characters (#25).
* Add TimeUnit.sleep mapping (#17).
* Drop breaks in case block bodies (#51).
* Fix ClassCastException in NCE 1.3.0 log.
* Translate case body statements in a single scope to support inner blocks.
* Collect and log translation ratio.
* Improve documentation. 

## 2024-06-28

* Fix IntelliJ IDEA J2CJ Plugin compatibility with IntelliJ IDEA >=2024.1.
* Synchronize with the 0.53.3 cjc version.
* Expand user documentation for new 1.3.0 features (CJMAP generation, annotation support). 
* Fix ConcurrentModificationException on 1.3.0.
* Fix custom annotations with mixed positional and named init parameters.
* Report using array as annotation element value is forbidden in Cangjie.
* Log J2CJ version (#63).

## 2024-06-20

* Introduce experimental IntelliJ IDEA plugin for translating Java to Cangjie via "Convert Project to Cangjie" action. The plugin can be manually installed with j2cj-plugin-0.0.1.zip.
* Introduce experimental annotation translation that include user annotation translation (both decl- and use- site) and library annotations mappings via standard CJMAP syntax.
* Introduce CJMAP file generation for using mappings from previously translated modules with the new "generate.mapping.file" option.
* Introduce new user documentation.
* Refactor type mapping system (#20).
* Simplify type system.
* Introduce full hierarchy for custom symbols.
* More immutability in semantic model.
* Refactor logging.
* Introduce new semantics for the "extra.log" option.
* Support more cases for type casts.
* Do not wrap type parameters in Option where possible.
* Better Method printing.
* Preserve type arguments for unsupported type names.
* Do not check natural constraints when iterating type closure.
* Prevent more invalid casts.
* Allow more valid casts.
* Suppress receiver conversion for calls with bad receiver instances.
* Fix `j2cjlib.utils.toString` mapping.
* Micro optimizations.
* Fix structure of no-package projects (#33).
* Find real call owner with proper type arguments for mappings.
* Add atan2 mapping.
* Synchronize with the 0.53.2 cjc version.
* Do not add 'open' modifier to interface and interface members.
* Add supported cjc version to README (#42).

## 2024-04-27

* Add and consolidate Unicode test cases in docs.
* Move hashCode implementation in j2cjlib
* Fix typo for enum mapping (#35).
* Do not crash translator when failed to make call.

## 2024-04-15

* Fix `Map.keySet()` and `Arrays.asList()` mappings.
* Finalize custom symbols hierarchy.
* Search for the call candidate in custom symbols taking call owner into account.
* Introduce initial projection phase.
* Separate Java world from Cangjie world during translation.
* Suppress extra "No transform" markers.
* Add import for package-level methods automatically.
* Parse mapping target owner specification.
* Adjust diagnostics for invalid nodes.
* Adjust diagnostics for missing methods.
* Make maximum expression depth configurable with the `max.expression.depth` property.
* Add detailed information about unsupported Java features.
* Add detailed information about existing markers.

## 2024-03-05

* Migrate to TOML format for CJPM project configuration file.
* Synchronize with the 0.49.2 cjc version.
* Preserve original Java source file structure.
* Regularize import list.
* Use ANTLR for parsing .cjmap files.
* Drop unneeded parentheses for type casts.
* Speed up long-chained expression translation.
* Fix reference equality translation.
* Introduce extra.log option for logging currently processed class.
* Introduce analyze.expression.depth option for logging maximum expression depth in project.
* Enhance internal architecture by partially migrating to custom symbols.

## 2024-02-06

* Move J2CJ from OpenJDK 18 to LTS OpenJDK 17 base.
* Fix custom `hashCode()` method translation. The return type is now `Int64` as expected.
* `TypeInfo.find(String)` -> `TypeInfo.get(String)`.
* Preserve all annotations (with error markers, skipping `@SuppressWarnings`).
* Consider Java skip statements (`;`) in switch-case and blocks.
* Provide proper error message for `OutputStream.write()` overrides mappings when more than 1 argument.
* Support private visibility on multi-declaration inside nested class.
* Provide full Java class signature inside error message if no type mapping found.
* Provide more information about missing method mapping.

## 2023-11-17

* Add JSON custom mapping system developed by ICT.
* Existing `.cjmap` configuration files are now embedded inside `j2cj.jar`, but can be overriden by files in current working directory.
* The translator now considers the entire method override chain when searching for Java method mappings.
* Fix support for multiple type parameters in `.cjmap` files.
* Add numerous trivial mappings (thanks to contributions from ICT!).
* Move more trivial mappings from translator source code into the `mappings.cjmap` file.
* Add `Arrays.asList(T...)` mapping that handles cases when only a `Collection` is expected (not `List`), or when the items are specified as variadic arguments.
* Fix `StringBuilder.setLength(int)` mapping.
* Fix `Map.keySet()` mapping.
* Add `MIN_VALUE` and `MAX_VALUE` mappings for Java numeric types.
* Improve support for Java `enum` types.
* Generalize `String` box support to also handle primitive types.
* Improve unsigned shifts implementation in _j2cjlib_.
* Fix rare case of mappings failing to find obviously existing Cangjie properties in case of Java override of a method with missing mapping.
* Calls to Java methods that never return `null` in variable and field initializers now make the variable or field type non-nullable.
* Fix bug with `final` or effectively final variables and fields omitting the type specification, when the expected type is a supertype of the initializer value type.
* Drop `access` methods, increase access modifier level instead. The only regressing case (when `public` modifier has to be used) is when an inner class accesses a `protected` field or method, declared in the supertype of outer class. This case is quite rare, but it will be fixed in the future.
* Slightly improve code quality with `equals` mapping.
* Fix unary logical negation operator not wrapping binary operators in parentheses.
* Simplify Java assertions logic.
* Remove unnecessary casts of array length to `Int32` and back to `Int64`.
* Make it more difficult for translator to automatically select method overload that requires narrowing numeric casts.
* Fix missing `static` modifier on fields of Java interfaces.

## 2023-11-05

* Mappings can now be specified using `.cjmap` configuration files (see README and existing `.cjmap` files for detailed description).
* Add short descriptions of error conditions to the most popular incompilable code markers to assist the user of the translator.
* Add `java.lang.Throwable` mapping. Fixes CodeHub issue 37.
* Add `java.lang.StringBuilder.reverse` mapping.
* Add many mappings for Java `Byte`, `Short`, `Integer`, `Long`, `Float`, `Double`, `Character` and `String` types. Fixes CodeHub issues 34, 35, 36.1, 36.3.
* Fix correctness of `java.util.HashMap` constructor mappings. Fixes CodeHub issue 39.
* Fix correctness of signed shifts.
* Fix correctness of `java.lang.String.equals` mapping.
* Fix correctness of `java.lang.Object.wait` mapping.
* Improve correctness of Java `short` literals in type inference contexts, such literals now always have type suffixes.
* Translator no longer replaces references to `static final` Java fields with their constant values.
* Restore missing incompilable code markers for impossible casts between primitive Cangjie types.
* Fix crash on `for` loops in initializer blocks.
* Fix internal crash during type inference on some method calls with complex expressions as arguments.
* Better resilience against recursive type definitions.
* Support `static final` fields as case labels while matching on characters.
* Detect clashes between fields and methods, or between static and instance methods. Prevent such clashes by renaming methods.
* Take advantage of recently-introduced Cangjie reflection to map some simple Java reflective operations.
* Support unary numeric promotion for shifts.
* Restore missing Option type specification in some variable declarations.
* Overridden methods now have public visibility, since open methods must always be public or protected.
* Be more silent with the console output when some internal failure is properly handled.
* Adapt to latest Cangjie standard library changes.

## 2023-09-29

* Support anonymous and local classes.
* Support compound assignment with unsigned right shift operator.
* Improve support for switch statements and expressions on String values.
* Add `java.lang.Object.equals(java.lang.Object)` mapping.
* Add `java.lang.StringIndexOutOfBoundsException` mapping.
* Add `java.lang.ArithmeticException` mapping.
* Add `java.io.EOFException` mapping.
* Fix `java.io.IOException` mapping.
* Add `java.lang.String.contains(java.lang.CharSequence)` mapping.
* Add `java.lang.String.getChars(int,int,char[],int)` mapping.
* Add `java.lang.Integer.toBinaryString(int)` mapping.
* Add `java.util.Stack` mapping.
* Add `java.lang.Character.isUpperCase(char)` mapping.
* Add `java.util.List.addAll(java.util.Collection)` mapping.
* Add `java.util.LinkedList` mapping.
* Add `java.util.Optional` mapping.
* Add `java.lang.Iterable` mapping.
* Add `java.util.Iterator` mapping.
* Add `java.lang.Error` mapping.
* Fix `java.util.ArrayList` constructors' mappings.
* Fix `java.lang.String` constructors' mappings.
* Improve correctness of Java `int` literals in type inference contexts. The literals now always have type suffixes. Despite being more correct, this decreases code quality, and will be fixed in the future.
* Fix combination of array element access and unary increment/decrement operators.
* Fix translation of switch expressions.
* Fix translation of constant non-literal switch case labels.
* Fix `break label` and `continue label` Java statements not being marked.
* Fix incorrect synthetic accessors for overloaded methods.
* Remove more unnecessary parentheses.
* Disable buggy inheritance from `Equatable` for generic classes.
* Use `refEq` Cangjie intrinsic to compare objects.
* Mark unsupported declaration modifiers (like `volatile` or `transient`) as incompilable code.
* Mark initializer blocks as incompilable code.
* Mark references to types without mappings in source code as incompilable code.
* Fix bug with `java.lang.Object.toString()` calls negatively affecting translation of unrelated code.
* Detect infinite loops when doing initial analysis of the project before translation.
* Fix infinite loop with `final` fields and variables initialized with class literals.
* More uniform output code formatting style.
* All nested Java classes are now placed in the same Cangjie output file as their outermost class.
* Adapt to latest Cangjie standard library changes.
* Prepare J2CJ source tree for external contributors.
* Create stable J2CJ API for mapping declarations.

## 2023-08-25

* Correctness fixes for `java.io.ByteArrayInputStream` mapping.
* Avoid warnings in array initializer lambdas.
* Fix mutation of method parameters using compound assignments.
* Add `java.lang.String.getBytes()` mapping.
* Fix `ushr` implementation in _j2cjlib_.
* CJPM project now sets `--int-overflow=wrapping`, casts are now generated without using _j2cjlib_ helpers.
* Internal exceptions are wrapped into incompilable code markers. Failure in one input .java file shouldn't affect translation of another.
* Improve internal exceptions logging to simplify reading the translation logs.
* Fixed conversion from Java `char` to Cangjie numeric types.
* Expanded the list of Cangjie keywords that are now escaped using backticks.
* Fix internal exception due to constructor calls with enclosing instance (`encl.new MyClass()`).
* Workaround internal exception with block lambdas returning values.
* Fix internal exception with empty arrays (and calls of variadic methods with no variadic arguments).
* Fix support for Java 9+ Project Jigsaw modules.
* Adapt to latest Cangjie standard library changes.

## 2023-08-14

Initial early-access release
